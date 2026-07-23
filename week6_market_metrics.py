from pathlib import Path
import numpy as np
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


def pick_input_file(preferred_name, fallback_name):
    preferred_path = CSV_DIR / preferred_name
    fallback_path = CSV_DIR / fallback_name

    if preferred_path.exists():
        return preferred_path

    return fallback_path


def to_bool_series(df, col, default=True):
    if col not in df.columns:
        return pd.Series(default, index=df.index)

    if df[col].dtype == bool:
        return df[col].fillna(default)

    return (
        df[col]
        .astype(str)
        .str.lower()
        .map({
            "true": True,
            "false": False,
            "1": True,
            "0": False,
            "yes": True,
            "no": False
        })
        .fillna(default)
        .astype(bool)
    )


def add_time_fields(df, date_col, prefix):
    if date_col not in df.columns:
        return []

    date_values = pd.to_datetime(
        df[date_col],
        errors="coerce"
    )

    df[f"{prefix}_year"] = date_values.dt.year
    df[f"{prefix}_month"] = date_values.dt.month
    df[f"{prefix}_year_month"] = (
        date_values.dt.to_period("M").astype(str)
    )
    df[f"{prefix}_quarter"] = (
        date_values.dt.to_period("Q").astype(str)
    )

    return [
        f"{prefix}_year",
        f"{prefix}_month",
        f"{prefix}_year_month",
        f"{prefix}_quarter"
    ]


def add_sold_metrics(df):
    added_columns = []

    use_price = to_bool_series(
        df,
        "use_for_price_analysis",
        default=True
    )

    use_area = to_bool_series(
        df,
        "use_for_living_area_analysis",
        default=True
    )

    use_timeline = to_bool_series(
        df,
        "use_for_timeline_analysis",
        default=True
    )

    use_dom = to_bool_series(
        df,
        "use_for_dom_analysis",
        default=True
    )

    # ---------------------------------------------------------
    # Price per square foot
    # ---------------------------------------------------------
    if {"ClosePrice", "LivingArea"}.issubset(df.columns):
        valid = (
            use_price
            & use_area
            & df["ClosePrice"].notna()
            & df["LivingArea"].notna()
            & (df["ClosePrice"] > 0)
            & (df["LivingArea"] > 0)
        )

        df["close_price_per_sqft"] = np.where(
            valid,
            df["ClosePrice"] / df["LivingArea"],
            np.nan
        )

        added_columns.append("close_price_per_sqft")

    # ---------------------------------------------------------
    # Sold-to-list ratio
    # ---------------------------------------------------------
    if {"ClosePrice", "ListPrice"}.issubset(df.columns):
        valid = (
            use_price
            & df["ClosePrice"].notna()
            & df["ListPrice"].notna()
            & (df["ClosePrice"] > 0)
            & (df["ListPrice"] > 0)
        )

        df["sold_to_list_ratio"] = np.where(
            valid,
            df["ClosePrice"] / df["ListPrice"],
            np.nan
        )

        df["sold_to_list_pct"] = df["sold_to_list_ratio"] * 100

        df["sold_over_list_flag"] = np.where(
            valid,
            df["ClosePrice"] > df["ListPrice"],
            False
        )

        added_columns.extend([
            "sold_to_list_ratio",
            "sold_to_list_pct",
            "sold_over_list_flag"
        ])

    # ---------------------------------------------------------
    # Original list to close price change
    # ---------------------------------------------------------
    if {"ClosePrice", "OriginalListPrice"}.issubset(df.columns):
        valid = (
            use_price
            & df["ClosePrice"].notna()
            & df["OriginalListPrice"].notna()
            & (df["ClosePrice"] > 0)
            & (df["OriginalListPrice"] > 0)
        )

        df["close_vs_original_list_change"] = np.where(
            valid,
            df["ClosePrice"] - df["OriginalListPrice"],
            np.nan
        )

        df["close_vs_original_list_pct"] = np.where(
            valid,
            (
                (df["ClosePrice"] - df["OriginalListPrice"])
                / df["OriginalListPrice"]
            ) * 100,
            np.nan
        )

        added_columns.extend([
            "close_vs_original_list_change",
            "close_vs_original_list_pct"
        ])

    # ---------------------------------------------------------
    # Timeline metrics
    # ---------------------------------------------------------
    date_cols = [
        "ListingContractDate",
        "PurchaseContractDate",
        "CloseDate"
    ]

    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if {
        "ListingContractDate",
        "PurchaseContractDate"
    }.issubset(df.columns):
        df["days_listing_to_contract"] = np.where(
            use_timeline,
            (
                df["PurchaseContractDate"]
                - df["ListingContractDate"]
            ).dt.days,
            np.nan
        )

        added_columns.append("days_listing_to_contract")

    if {
        "PurchaseContractDate",
        "CloseDate"
    }.issubset(df.columns):
        df["days_contract_to_close"] = np.where(
            use_timeline,
            (
                df["CloseDate"]
                - df["PurchaseContractDate"]
            ).dt.days,
            np.nan
        )

        added_columns.append("days_contract_to_close")

    if {
        "ListingContractDate",
        "CloseDate"
    }.issubset(df.columns):
        df["days_listing_to_close"] = np.where(
            use_timeline,
            (
                df["CloseDate"]
                - df["ListingContractDate"]
            ).dt.days,
            np.nan
        )

        added_columns.append("days_listing_to_close")

    # ---------------------------------------------------------
    # Clean DOM analysis field
    # ---------------------------------------------------------
    if "DaysOnMarket" in df.columns:
        df["days_on_market_analysis"] = np.where(
            use_dom,
            df["DaysOnMarket"],
            np.nan
        )

        added_columns.append("days_on_market_analysis")

    added_columns.extend(
        add_time_fields(df, "CloseDate", "close")
    )

    return added_columns


def add_listing_metrics(df):
    added_columns = []

    use_price = to_bool_series(
        df,
        "use_for_price_analysis",
        default=True
    )

    use_area = to_bool_series(
        df,
        "use_for_living_area_analysis",
        default=True
    )

    use_dom = to_bool_series(
        df,
        "use_for_dom_analysis",
        default=True
    )

    # ---------------------------------------------------------
    # List price per square foot
    # ---------------------------------------------------------
    if {"ListPrice", "LivingArea"}.issubset(df.columns):
        valid = (
            use_price
            & use_area
            & df["ListPrice"].notna()
            & df["LivingArea"].notna()
            & (df["ListPrice"] > 0)
            & (df["LivingArea"] > 0)
        )

        df["list_price_per_sqft"] = np.where(
            valid,
            df["ListPrice"] / df["LivingArea"],
            np.nan
        )

        added_columns.append("list_price_per_sqft")

    # ---------------------------------------------------------
    # Original list price to current list price change
    # ---------------------------------------------------------
    if {"ListPrice", "OriginalListPrice"}.issubset(df.columns):
        valid = (
            use_price
            & df["ListPrice"].notna()
            & df["OriginalListPrice"].notna()
            & (df["ListPrice"] > 0)
            & (df["OriginalListPrice"] > 0)
        )

        df["list_vs_original_change"] = np.where(
            valid,
            df["ListPrice"] - df["OriginalListPrice"],
            np.nan
        )

        df["list_vs_original_pct"] = np.where(
            valid,
            (
                (df["ListPrice"] - df["OriginalListPrice"])
                / df["OriginalListPrice"]
            ) * 100,
            np.nan
        )

        added_columns.extend([
            "list_vs_original_change",
            "list_vs_original_pct"
        ])

    # ---------------------------------------------------------
    # Clean DOM analysis field
    # ---------------------------------------------------------
    if "DaysOnMarket" in df.columns:
        df["days_on_market_analysis"] = np.where(
            use_dom,
            df["DaysOnMarket"],
            np.nan
        )

        added_columns.append("days_on_market_analysis")

    added_columns.extend(
        add_time_fields(df, "ListingContractDate", "listing")
    )

    return added_columns


def create_week6_file(
    input_path,
    output_name,
    report_name,
    dataset_type
):
    output_path = CSV_DIR / output_name
    report_path = REPORTS_DIR / report_name

    print(f"\nCreating Week 6 metrics for {input_path.name}...")

    df = read_csv_safely(input_path)

    starting_rows = len(df)
    starting_columns = len(df.columns)

    if dataset_type == "sold":
        added_columns = add_sold_metrics(df)
    else:
        added_columns = add_listing_metrics(df)

    ending_rows = len(df)
    ending_columns = len(df.columns)

    assert ending_rows == starting_rows

    report = [
        f"Input file: {input_path.name}",
        f"Output file: {output_name}",
        f"Dataset type: {dataset_type}",
        f"Starting shape: ({starting_rows}, {starting_columns})",
        f"Final shape: ({ending_rows}, {ending_columns})",
        f"Rows preserved: {starting_rows == ending_rows}",
        "",
        "Week 6 metric columns added:"
    ]

    report.extend(
        added_columns or ["No Week 6 metric columns were added"]
    )

    report.append("")
    report.append("Metric non-null counts:")

    for col in added_columns:
        if col in df.columns:
            report.append(
                f"{col}: {int(df[col].notna().sum())}"
            )

    df.to_csv(output_path, index=False)

    report_path.write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    print(f"Starting shape: ({starting_rows}, {starting_columns})")
    print(f"Final shape: ({ending_rows}, {ending_columns})")
    print(f"Saved Week 6 file: {output_path}")
    print(f"Saved report: {report_path}")


sold_input = pick_input_file(
    "sold_week5_analysis_ready.csv",
    "sold_week4_cleaned.csv"
)

listings_input = pick_input_file(
    "listings_week5_analysis_ready.csv",
    "listings_week4_cleaned.csv"
)

create_week6_file(
    input_path=sold_input,
    output_name="sold_week6_metrics.csv",
    report_name="sold_week6_metrics_report.txt",
    dataset_type="sold"
)

create_week6_file(
    input_path=listings_input,
    output_name="listings_week6_metrics.csv",
    report_name="listings_week6_metrics_report.txt",
    dataset_type="listings"
)

print("\nWeek 6 metric creation completed successfully.")