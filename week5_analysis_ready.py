from pathlib import Path
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
CSV_DIR = PROJECT_DIR / "csv"
REPORTS_DIR = PROJECT_DIR / "reports"

REPORTS_DIR.mkdir(exist_ok=True)


def read_csv_safely(path):
    try:
        return pd.read_csv(path, low_memory=False)
    except UnicodeDecodeError:
        return pd.read_csv(
            path,
            low_memory=False,
            encoding="ISO-8859-1"
        )


def make_analysis_ready(input_name, output_name, report_name):
    input_path = CSV_DIR / input_name
    output_path = CSV_DIR / output_name
    report_path = REPORTS_DIR / report_name

    print(f"\nPreparing {input_name} for analysis...")

    df = read_csv_safely(input_path)

    starting_rows = len(df)
    starting_columns = len(df.columns)

    report = [
        f"Input file: {input_name}",
        f"Starting shape: {df.shape}",
        ""
    ]

    # ---------------------------------------------------------
    # 1. Fill useful categorical fields as Unknown
    # ---------------------------------------------------------
    categorical_columns_to_keep = [
        "City",
        "CountyOrParish",
        "PostalCode",
        "PropertySubType",
        "Levels",
        "Flooring",
        "ListAgentFullName",
        "BuyerAgentFullName",
        "ListOfficeName",
        "BuyerOfficeName"
    ]

    filled_unknown_columns = []

    for col in categorical_columns_to_keep:
        if col in df.columns:
            missing_before = int(df[col].isna().sum())

            df[col] = df[col].fillna("Unknown")

            filled_unknown_columns.append(
                f"{col}: {missing_before} missing values filled as Unknown"
            )

    report.append("Categorical fields filled as Unknown:")
    report.extend(
        filled_unknown_columns
        or ["No selected categorical fields found"]
    )
    report.append("")

    # ---------------------------------------------------------
    # 2. Make sure analysis-use flags exist
    # ---------------------------------------------------------
    if "geographic_issue_flag" in df.columns:
        df["use_for_map_analysis"] = ~df["geographic_issue_flag"]

    if "invalid_close_price_flag" in df.columns:
        df["use_for_price_analysis"] = ~df["invalid_close_price_flag"]

    if "invalid_living_area_flag" in df.columns:
        df["use_for_living_area_analysis"] = ~df["invalid_living_area_flag"]

    if "negative_dom_flag" in df.columns:
        df["use_for_dom_analysis"] = ~df["negative_dom_flag"]

    timeline_flags = [
        "listing_after_close_flag",
        "purchase_after_close_flag",
        "negative_timeline_flag"
    ]

    existing_timeline_flags = [
        col for col in timeline_flags if col in df.columns
    ]

    if existing_timeline_flags:
        df["use_for_timeline_analysis"] = (
            ~df[existing_timeline_flags].any(axis=1)
        )

    # ---------------------------------------------------------
    # 3. Add simple date helper columns for Tableau
    # ---------------------------------------------------------
    if "CloseDate" in df.columns:
        close_date = pd.to_datetime(
            df["CloseDate"],
            errors="coerce"
        )

        df["close_year"] = close_date.dt.year
        df["close_month"] = close_date.dt.month
        df["close_year_month"] = close_date.dt.to_period("M").astype(str)

    if "ListingContractDate" in df.columns:
        listing_date = pd.to_datetime(
            df["ListingContractDate"],
            errors="coerce"
        )

        df["listing_year"] = listing_date.dt.year
        df["listing_month"] = listing_date.dt.month
        df["listing_year_month"] = listing_date.dt.to_period("M").astype(str)

    # ---------------------------------------------------------
    # 4. Report analysis-use counts
    # ---------------------------------------------------------
    analysis_use_columns = [
        col for col in df.columns
        if col.startswith("use_for_")
    ]

    report.append("Analysis-use counts:")
    for col in analysis_use_columns:
        report.append(f"{col}: {int(df[col].sum())}")

    report.append("")

    ending_rows = len(df)
    ending_columns = len(df.columns)

    assert ending_rows == starting_rows

    report.extend([
        f"Final shape: {df.shape}",
        f"Rows preserved: {starting_rows == ending_rows}",
        f"Columns before: {starting_columns}",
        f"Columns after: {ending_columns}",
        ""
    ])

    df.to_csv(output_path, index=False)

    report_path.write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    print(f"Starting shape: ({starting_rows}, {starting_columns})")
    print(f"Final shape: ({ending_rows}, {ending_columns})")
    print(f"Saved analysis-ready file: {output_path}")
    print(f"Saved report: {report_path}")


make_analysis_ready(
    input_name="sold_week4_cleaned.csv",
    output_name="sold_week5_analysis_ready.csv",
    report_name="sold_week5_analysis_ready_report.txt"
)

make_analysis_ready(
    input_name="listings_week4_cleaned.csv",
    output_name="listings_week5_analysis_ready.csv",
    report_name="listings_week5_analysis_ready_report.txt"
)

print("\nWeek 5 analysis-ready preparation completed successfully.")