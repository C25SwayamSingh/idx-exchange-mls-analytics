from pathlib import Path
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
CSV_DIR = PROJECT_DIR / "csv"
REPORTS_DIR = PROJECT_DIR / "reports"

REPORTS_DIR.mkdir(exist_ok=True)


def summarize(df, group_column, price_column, ppsf_column):
    grouped = df.groupby(group_column).agg(
        properties=(price_column, "size"),
        median_price=(price_column, "median"),
        median_ppsf=(ppsf_column, "median"),
        median_dom=("days_on_market_analysis", "median")
    )

    # busiest segments first
    grouped = grouped.sort_values("properties", ascending=False)

    return grouped.round(2)


def run_segments(input_name, output_prefix, price_column, ppsf_column):
    print(f"\nBuilding segment tables from {input_name}...")

    # only the columns this summary needs
    columns = [
        "CountyOrParish",
        "PropertySubType",
        price_column,
        ppsf_column,
        "days_on_market_analysis"
    ]

    df = pd.read_csv(CSV_DIR / input_name, usecols=columns, low_memory=False)

    for group_column in ["CountyOrParish", "PropertySubType"]:
        table = summarize(df, group_column, price_column, ppsf_column)

        out = REPORTS_DIR / f"{output_prefix}_by_{group_column.lower()}.csv"
        table.to_csv(out)

        print(f"\n{group_column} segments: {len(table)}")
        print(table.head(10))
        print(f"Saved: {out.name}")


run_segments(
    input_name="sold_week6_metrics.csv",
    output_prefix="sold_segments",
    price_column="ClosePrice",
    ppsf_column="close_price_per_sqft"
)

run_segments(
    input_name="listings_week6_metrics.csv",
    output_prefix="listings_segments",
    price_column="ListPrice",
    ppsf_column="list_price_per_sqft"
)

print("\nWeek 6 segment summary completed successfully.")
