from pathlib import Path
import pandas as pd

project_folder = Path(__file__).resolve().parent.parent
csv_folder = project_folder / "csv"

sold = pd.read_csv(csv_folder / "sold.csv", low_memory=False)
listings = pd.read_csv(csv_folder / "listings.csv", low_memory=False)

numeric_fields = ["ClosePrice", "LivingArea", "DaysOnMarket"]

def validate_data(df, name):
    print(f"\n{name.upper()} DATASET")
    print("Shape:", df.shape)
    print("Property types:", df["PropertyType"].dropna().unique())

    # make the required fields numeric
    for column in numeric_fields:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # missing value report
    missing = pd.DataFrame({
        "missing_count": df.isnull().sum(),
        "missing_percent": df.isnull().mean() * 100
    }).sort_values("missing_percent", ascending=False)

    high_missing = missing[missing["missing_percent"] > 90]

    # required numeric summary
    summary = df[numeric_fields].describe(
        percentiles=[0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
    ).T

    summary = summary.rename(columns={"50%": "median"})
    summary = summary[
        ["min", "max", "mean", "median", "25%", "75%", "90%", "95%", "99%"]
    ]

    missing.to_csv(project_folder / f"{name}_missing_report.csv")
    summary.to_csv(project_folder / f"{name}_numeric_summary.csv")

    print("Columns above 90% missing:", len(high_missing))
    print("\nColumns above 90% missing:")
    print(high_missing)

    print("\nNumeric summary:")
    print(summary)

validate_data(sold, "sold")
validate_data(listings, "listings")