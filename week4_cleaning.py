from pathlib import Path
import pandas as pd


# Project folders
PROJECT_DIR = Path(__file__).resolve().parent.parent
CSV_DIR = PROJECT_DIR / "csv"
REPORTS_DIR = PROJECT_DIR / "reports"

REPORTS_DIR.mkdir(exist_ok=True)


def read_csv_safely(path):
    """Read the CSV and fall back to the MLS encoding if needed."""
    try:
        return pd.read_csv(path, low_memory=False)
    except UnicodeDecodeError:
        return pd.read_csv(
            path,
            low_memory=False,
            encoding="ISO-8859-1"
        )


def clean_dataset(input_name, output_name, report_name):
    input_path = CSV_DIR / input_name
    output_path = CSV_DIR / output_name
    report_path = REPORTS_DIR / report_name

    print(f"\nCleaning {input_name}...")

    df = read_csv_safely(input_path)

    starting_rows = len(df)
    starting_columns = len(df.columns)

    report = [
        f"Input file: {input_name}",
        f"Starting shape: {df.shape}",
        ""
    ]

    # ---------------------------------------------------------
    # 1. Handle duplicate .1 columns
    # ---------------------------------------------------------
    duplicate_results = []

    for duplicate_col in [
        col for col in df.columns if col.endswith(".1")
    ]:
        original_col = duplicate_col[:-2]

        if original_col not in df.columns:
            continue

        both_present = (
            df[original_col].notna()
            & df[duplicate_col].notna()
        )

        conflicts = (
            both_present
            & (
                df[original_col].astype(str)
                != df[duplicate_col].astype(str)
            )
        ).sum()

        values_filled = (
            df[original_col].isna()
            & df[duplicate_col].notna()
        ).sum()

        if conflicts == 0:
            df[original_col] = df[original_col].combine_first(
                df[duplicate_col]
            )
            df = df.drop(columns=[duplicate_col])

            duplicate_results.append(
                f"{duplicate_col}: removed; "
                f"{values_filled} missing values filled"
            )
        else:
            duplicate_results.append(
                f"{duplicate_col}: kept because "
                f"{conflicts} conflicting values were found"
            )

    report.append("Duplicate-column review:")
    report.extend(
        duplicate_results or ["No .1 duplicate columns found"]
    )
    report.append("")

    # ---------------------------------------------------------
    # 2. Drop columns above 90% missing
    # ---------------------------------------------------------
    missing_percent = df.isna().mean() * 100

    high_missing_columns = (
        missing_percent[missing_percent > 90]
        .index
        .tolist()
    )

    df = df.drop(columns=high_missing_columns)

    report.append("Columns dropped above 90% missing:")
    report.extend(
        high_missing_columns
        or ["No columns were above 90% missing"]
    )
    report.append("")

    # ---------------------------------------------------------
    # 3. Convert date columns
    # ---------------------------------------------------------
    date_columns = [
        "CloseDate",
        "PurchaseContractDate",
        "ListingContractDate",
        "ContractStatusChangeDate"
    ]

    existing_date_columns = [
        col for col in date_columns if col in df.columns
    ]

    for col in existing_date_columns:
        df[col] = pd.to_datetime(
            df[col],
            format="mixed",
            errors="coerce"
        )

    # ---------------------------------------------------------
    # 4. Convert numeric columns
    # ---------------------------------------------------------
    numeric_columns = [
        "ClosePrice",
        "ListPrice",
        "OriginalListPrice",
        "LivingArea",
        "LotSizeAcres",
        "BedroomsTotal",
        "BathroomsTotalInteger",
        "DaysOnMarket",
        "YearBuilt",
        "Latitude",
        "Longitude",
        "rate_30yr_fixed"
    ]

    existing_numeric_columns = [
        col for col in numeric_columns if col in df.columns
    ]

    for col in existing_numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # ---------------------------------------------------------
    # 5. Add invalid numeric-value flags
    # ---------------------------------------------------------
    if "ClosePrice" in df.columns:
        df["invalid_close_price_flag"] = (
            df["ClosePrice"] <= 0
        )

    if "LivingArea" in df.columns:
        df["invalid_living_area_flag"] = (
            df["LivingArea"] <= 0
        )

    if "DaysOnMarket" in df.columns:
        df["negative_dom_flag"] = (
            df["DaysOnMarket"] < 0
        )

    if "BedroomsTotal" in df.columns:
        df["negative_bedrooms_flag"] = (
            df["BedroomsTotal"] < 0
        )

    if "BathroomsTotalInteger" in df.columns:
        df["negative_bathrooms_flag"] = (
            df["BathroomsTotalInteger"] < 0
        )

    # ---------------------------------------------------------
    # 6. Add date-consistency flags
    # ---------------------------------------------------------
    if {
        "ListingContractDate",
        "CloseDate"
    }.issubset(df.columns):
        df["listing_after_close_flag"] = (
            df["ListingContractDate"].notna()
            & df["CloseDate"].notna()
            & (
                df["ListingContractDate"]
                > df["CloseDate"]
            )
        )

    if {
        "PurchaseContractDate",
        "CloseDate"
    }.issubset(df.columns):
        df["purchase_after_close_flag"] = (
            df["PurchaseContractDate"].notna()
            & df["CloseDate"].notna()
            & (
                df["PurchaseContractDate"]
                > df["CloseDate"]
            )
        )

    if {
        "ListingContractDate",
        "PurchaseContractDate"
    }.issubset(df.columns):
        df["negative_timeline_flag"] = (
            df["ListingContractDate"].notna()
            & df["PurchaseContractDate"].notna()
            & (
                df["PurchaseContractDate"]
                < df["ListingContractDate"]
            )
        )

    # ---------------------------------------------------------
    # 7. Add geographic-quality flags
    # ---------------------------------------------------------
    if {"Latitude", "Longitude"}.issubset(df.columns):
        df["missing_coordinates_flag"] = (
            df["Latitude"].isna()
            | df["Longitude"].isna()
        )

        df["zero_coordinates_flag"] = (
            (df["Latitude"] == 0)
            | (df["Longitude"] == 0)
        )

        df["positive_longitude_flag"] = (
            df["Longitude"] > 0
        )

        # Broad California range used only as a quality check
        df["implausible_coordinates_flag"] = (
            df["Latitude"].notna()
            & df["Longitude"].notna()
            & (
                ~df["Latitude"].between(32, 42.5)
                | ~df["Longitude"].between(-125, -113)
            )
        )

        df["geographic_issue_flag"] = (
            df["missing_coordinates_flag"]
            | df["zero_coordinates_flag"]
            | df["positive_longitude_flag"]
            | df["implausible_coordinates_flag"]
        )

    # ---------------------------------------------------------
    # 8. Create one overall review flag
    # ---------------------------------------------------------
    flag_columns = [
        col for col in df.columns
        if col.endswith("_flag")
        and col != "has_data_quality_issue"
    ]

    if flag_columns:
        df["has_data_quality_issue"] = (
            df[flag_columns].any(axis=1)
        )

    # ---------------------------------------------------------
    # 9. Validate and create the report
    # ---------------------------------------------------------
    ending_rows = len(df)
    ending_columns = len(df.columns)

    # We are dropping columns, not rows
    assert ending_rows == starting_rows

    report.extend([
        f"Final shape: {df.shape}",
        f"Rows preserved: {starting_rows == ending_rows}",
        f"Columns before: {starting_columns}",
        f"Columns after: {ending_columns}",
        ""
    ])

    report.append("Date data types:")
    for col in existing_date_columns:
        report.append(f"{col}: {df[col].dtype}")

    report.append("")
    report.append("Numeric data types:")

    for col in existing_numeric_columns:
        if col in df.columns:
            report.append(f"{col}: {df[col].dtype}")

    report.append("")
    report.append("Flag totals:")

    for col in flag_columns:
        report.append(
            f"{col}: {int(df[col].sum())}"
        )

    if "has_data_quality_issue" in df.columns:
        report.append(
            "Rows with any quality issue: "
            f"{int(df['has_data_quality_issue'].sum())}"
        )

    if "rate_30yr_fixed" in df.columns:
        missing_rates = int(
            df["rate_30yr_fixed"].isna().sum()
        )
        report.extend([
            "",
            f"Missing mortgage rates: {missing_rates}"
        ])

    # Save the cleaned data and report
    df.to_csv(output_path, index=False)

    report_path.write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    print(f"Starting shape: ({starting_rows}, {starting_columns})")
    print(f"Final shape: ({ending_rows}, {ending_columns})")
    print(f"Rows with quality issues: "
          f"{int(df['has_data_quality_issue'].sum())}")
    print(f"Saved cleaned file: {output_path}")
    print(f"Saved report: {report_path}")


# Clean both mortgage-enriched datasets
clean_dataset(
    input_name="sold_with_rates.csv",
    output_name="sold_week4_cleaned.csv",
    report_name="sold_week4_cleaning_report.txt"
)

clean_dataset(
    input_name="listings_with_rates.csv",
    output_name="listings_week4_cleaned.csv",
    report_name="listings_week4_cleaning_report.txt"
)

print("\nWeek 4 cleaning completed successfully.")