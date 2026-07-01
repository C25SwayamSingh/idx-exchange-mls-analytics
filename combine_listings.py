from pathlib import Path
import pandas as pd

# find the main project folder and csv folder
project_folder = Path(__file__).resolve().parent.parent
csv_folder = project_folder / "csv"
output_file = csv_folder / "listings.csv"

# find all the monthly listing files
listing_files = sorted(csv_folder.glob("CRMLSListing*.csv"))

# choose one file per month so duplicate versions are not counted twice
selected_files = {}

for file in listing_files:
    month = file.name.replace("CRMLSListing", "").replace("_filled", "").replace(".csv", "")

    if month not in selected_files:
        selected_files[month] = file

    # use the regular file instead if both versions exist
    elif "_filled" in selected_files[month].name and "_filled" not in file.name:
        selected_files[month] = file

chosen_files = [selected_files[month] for month in sorted(selected_files)]

print("Number of monthly Listing files selected:", len(chosen_files))

# load each monthly file
frames = []

for file in chosen_files:
    df = pd.read_csv(file, encoding="ISO-8859-1", low_memory=False)

    # remove the two extra columns if a _filled file is used
    if "_filled" in file.name:
        df = df.iloc[:, :-2]

    frames.append(df)
    print(file.name, "-", f"{len(df):,} rows")

# combine every month into one dataset
listings = pd.concat(frames, ignore_index=True, sort=False)

property_type_counts = listings["PropertyType"].value_counts(dropna=False)

print("\nListing property types before filtering:")
print(property_type_counts)

# keep only residential properties
rows_before_filter = len(listings)

# save the property types before filtering
listings = listings[
    listings["PropertyType"].astype(str).str.strip() == "Residential"
].copy()


rows_after_filter = len(listings)

# save the final cumulative listings file
listings.to_csv(output_file, index=False)

print("\nListing rows after combining:", f"{rows_before_filter:,}")
print("Listing rows after Residential filter:", f"{rows_after_filter:,}")
print("Rows removed:", f"{rows_before_filter - rows_after_filter:,}")
print("Final number of columns:", listings.shape[1])
print("Saved to:", output_file)

# week 2-3 dataset validation
print("Final Listings dataset shape:", listings.shape)

# make sure the required numeric columns are numeric
numeric_fields = ["ClosePrice", "LivingArea", "DaysOnMarket"]

for column in numeric_fields:
    listings[column] = pd.to_numeric(listings[column], errors="coerce")

# calculate missing values for every column
missing_report = pd.DataFrame({
    "missing_count": listings.isnull().sum(),
    "missing_percent": listings.isnull().mean() * 100
}).sort_values("missing_percent", ascending=False)

high_missing = missing_report[missing_report["missing_percent"] > 90]

# summarize the three required numeric fields
numeric_summary = listings[numeric_fields].describe(
    percentiles=[0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
).T

numeric_summary = numeric_summary.rename(columns={"50%": "median"})
numeric_summary = numeric_summary[
    ["min", "max", "mean", "median", "25%", "75%", "90%", "95%", "99%"]
]

# save the validation results as a text file
report_file = project_folder / "listings_validation.txt"

with open(report_file, "w") as report:
    report.write("LISTINGS DATASET VALIDATION\n\n")
    report.write(
        f"Property types before filtering:\n{property_type_counts.to_string()}\n\n"
    )
    report.write(f"Final dataset shape: {listings.shape}\n\n")

    report.write("COLUMN DATA TYPES\n")
    report.write(listings.dtypes.to_string())

    report.write("\n\nMISSING VALUE REPORT\n")
    report.write(missing_report.to_string())

    report.write("\n\nCOLUMNS ABOVE 90% MISSING\n")
    report.write(high_missing.to_string())

    report.write("\n\nNUMERIC DISTRIBUTION SUMMARY\n")
    report.write(numeric_summary.to_string())

print("\nColumns above 90% missing:", len(high_missing))
print("\nListings numeric summary:")
print(numeric_summary)
print("Validation report saved to:", report_file)
