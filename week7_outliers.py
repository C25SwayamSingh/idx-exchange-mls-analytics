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
        return pd.read_csv(path, low_memory=False, encoding="ISO-8859-1")


def find_outliers(values):
    # quartiles
    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1

    # fences
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    # blanks are not outliers
    outlier = values.notna() & ((values < lower) | (values > upper))

    return outlier, lower, upper


def run_week7(input_name, flagged_name, filtered_name, report_name, price_column):
    print(f"\nChecking outliers in {input_name}...")

    df = read_csv_safely(CSV_DIR / input_name)

    starting_rows = len(df)
    fields = [price_column, "LivingArea", "DaysOnMarket"]

    report = [
        f"Input file: {input_name}",
        f"Starting rows: {starting_rows}",
        "",
        "IQR bounds and outlier counts:"
    ]

    medians_before = {}
    flag_columns = []

    for field in fields:
        values = pd.to_numeric(df[field], errors="coerce")
        medians_before[field] = values.median()

        outlier, lower, upper = find_outliers(values)

        # one flag per field
        flag = f"{field}_outlier_flag"
        df[flag] = outlier
        flag_columns.append(flag)

        report.append(
            f"{field}: lower={lower:,.2f}  upper={upper:,.2f}  "
            f"outliers={int(outlier.sum())}"
        )

    # outlier in any field
    df["is_outlier"] = df[flag_columns].any(axis=1)

    # separate clean copy, original rows stay
    filtered = df[~df["is_outlier"]].copy()

    # flagging must not drop rows
    assert len(df) == starting_rows

    removed = starting_rows - len(filtered)

    report += [
        "",
        "Dataset size comparison:",
        f"Rows before filtering: {starting_rows}",
        f"Rows after filtering: {len(filtered)}",
        f"Rows removed: {removed} ({removed / starting_rows * 100:.2f}%)",
        "",
        "Median comparison:"
    ]

    for field in fields:
        after = pd.to_numeric(filtered[field], errors="coerce").median()

        report.append(
            f"{field}: before={medians_before[field]:,.2f}  after={after:,.2f}"
        )

    df.to_csv(CSV_DIR / flagged_name, index=False)
    filtered.to_csv(CSV_DIR / filtered_name, index=False)

    (REPORTS_DIR / report_name).write_text("\n".join(report), encoding="utf-8")

    print(f"Rows flagged as outliers: {int(df['is_outlier'].sum())}")
    print(f"Filtered rows kept: {len(filtered)}")
    print(f"Saved flagged file: {flagged_name}")
    print(f"Saved filtered file: {filtered_name}")


# sold homes have a close price
run_week7(
    input_name="sold_week6_metrics.csv",
    flagged_name="sold_week7_flagged.csv",
    filtered_name="sold_week7_filtered.csv",
    report_name="sold_week7_outlier_report.txt",
    price_column="ClosePrice"
)

# listings only have a list price
run_week7(
    input_name="listings_week6_metrics.csv",
    flagged_name="listings_week7_flagged.csv",
    filtered_name="listings_week7_filtered.csv",
    report_name="listings_week7_outlier_report.txt",
    price_column="ListPrice"
)

print("\nWeek 7 outlier detection completed successfully.")
