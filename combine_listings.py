from pathlib import Path
import pandas as pd

# find the main project folder and csv folder
project_folder = Path(__file__).resolve().parent.parent
csv_folder = project_folder / "csv"
output_file = csv_folder / "listings.csv"

# find all of the monthly listing files
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

rows_before_filter = len(listings)

# keep only residential properties
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

