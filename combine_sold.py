from pathlib import Path
import pandas as pd

# find the main project folder and csv folder
project_folder = Path(__file__).resolve().parent.parent
csv_folder = project_folder / "csv"
output_file = csv_folder / "sold.csv"

# find all the monthly sold files
sold_files = sorted(csv_folder.glob("CRMLSSold*.csv"))

# choose one file per month so we do not count duplicate _filled files
selected_files = {}

for file in sold_files:
    month = file.name.replace("CRMLSSold", "").replace("_filled", "").replace(".csv", "")

    if month not in selected_files:
        selected_files[month] = file

    # use the regular file instead if both versions exist
    elif "_filled" in selected_files[month].name and "_filled" not in file.name:
        selected_files[month] = file

chosen_files = [selected_files[month] for month in sorted(selected_files)]

print("Number of monthly Sold files selected:", len(chosen_files))

# load each monthly file
frames = []

for file in chosen_files:
    df = pd.read_csv(file, encoding="ISO-8859-1", low_memory=False)

    # Aidan said the _filled files have two extra columns at the end
    if "_filled" in file.name:
        df = df.iloc[:, :-2]

    frames.append(df)
    print(file.name, "-", f"{len(df):,} rows")

# combine every month into one dataset
sold = pd.concat(frames, ignore_index=True, sort=False)

property_type_counts = sold["PropertyType"].value_counts(dropna=False)
print("\nSold property types before filtering:")
print(property_type_counts)


# Keep only residential properties
rows_before_filter = len(sold)

sold = sold[
    sold["PropertyType"].astype(str).str.strip() == "Residential"
].copy()

rows_after_filter = len(sold)

# save the final cumulative sold file
sold.to_csv(output_file, index=False)

print("\nSold rows after combining:", f"{rows_before_filter:,}")
print("Sold rows after Residential filter:", f"{rows_after_filter:,}")
print("Rows removed:", f"{rows_before_filter - rows_after_filter:,}")
print("Final number of columns:", sold.shape[1])
print("Saved to:", output_file)


# week 2-3 dataset validation
print("Final Sold dataset shape:", sold.shape)

# make sure the required numeric columns are numeric
numeric_fields = ["ClosePrice", "LivingArea", "DaysOnMarket"]

for column in numeric_fields:
    sold[column] = pd.to_numeric(sold[column], errors="coerce")

# calculate missing values for every column
missing_report = pd.DataFrame({
    "missing_count": sold.isnull().sum(),
    "missing_percent": sold.isnull().mean() * 100
}).sort_values("missing_percent", ascending=False)

high_missing = missing_report[missing_report["missing_percent"] > 90]

# summarize the three required numeric fields
numeric_summary = sold[numeric_fields].describe(
    percentiles=[0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
).T

numeric_summary = numeric_summary.rename(columns={"50%": "median"})
numeric_summary = numeric_summary[
    ["min", "max", "mean", "median", "25%", "75%", "90%", "95%", "99%"]
]

# save the validation results as a text file
report_file = project_folder / "sold_validation.txt"

with open(report_file, "w") as report:
    report.write("SOLD DATASET VALIDATION\n\n")

    report.write("PROPERTY TYPES BEFORE FILTERING\n")
    report.write(property_type_counts.to_string())

    report.write(f"\n\nFinal dataset shape: {sold.shape}\n\n")

    report.write("COLUMN DATA TYPES\n")
    report.write(sold.dtypes.to_string())

    report.write("\n\nMISSING VALUE REPORT\n")
    report.write(missing_report.to_string())

    report.write("\n\nCOLUMNS ABOVE 90% MISSING\n")
    report.write(high_missing.to_string())

    report.write("\n\nNUMERIC DISTRIBUTION SUMMARY\n")
    report.write(numeric_summary.to_string())

print("\nColumns above 90% missing:", len(high_missing))
print("\nSold numeric summary:")
print(numeric_summary)
print("Validation report saved to:", report_file)




