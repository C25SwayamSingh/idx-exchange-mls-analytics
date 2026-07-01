from pathlib import Path
import pandas as pd

project_folder = Path(__file__).resolve().parent.parent
csv_folder = project_folder / "csv"

sold = pd.read_csv(csv_folder / "sold.csv", low_memory=False)
listings = pd.read_csv(csv_folder / "listings.csv", low_memory=False)

sold_rows_before = len(sold)
listing_rows_before = len(listings)

print("Sold rows before merge:", sold_rows_before)
print("Listing rows before merge:", listing_rows_before)

# download weekly 30-year mortgage rates from FRED
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url)

mortgage.columns = ["date", "rate_30yr_fixed"]
mortgage["date"] = pd.to_datetime(mortgage["date"], errors="coerce")
mortgage["rate_30yr_fixed"] = pd.to_numeric(
    mortgage["rate_30yr_fixed"], errors="coerce"
)

# calculate the average mortgage rate for each month
mortgage["year_month"] = mortgage["date"].dt.strftime("%Y-%m")

mortgage_monthly = (
    mortgage.groupby("year_month", as_index=False)["rate_30yr_fixed"]
    .mean()
)

# convert property dates and create matching month columns
sold["CloseDate"] = pd.to_datetime(
    sold["CloseDate"], format="mixed", errors="coerce"
)

listings["ListingContractDate"] = pd.to_datetime(
    listings["ListingContractDate"], format="mixed", errors="coerce"
)

sold["year_month"] = sold["CloseDate"].dt.strftime("%Y-%m")
listings["year_month"] = listings["ListingContractDate"].dt.strftime("%Y-%m")

print("Sold dates that could not be read:", sold["CloseDate"].isna().sum())
print(
    "Listing dates that could not be read:",
    listings["ListingContractDate"].isna().sum()
)

# left merge keeps every original property row
sold = sold.merge(
    mortgage_monthly,
    on="year_month",
    how="left",
    validate="many_to_one"
)

listings = listings.merge(
    mortgage_monthly,
    on="year_month",
    how="left",
    validate="many_to_one"
)

# confirm that no property rows were lost
if len(sold) != sold_rows_before:
    raise ValueError("Sold row count changed during the merge.")

if len(listings) != listing_rows_before:
    raise ValueError("Listing row count changed during the merge.")

print("\nSold rows after merge:", len(sold))
print("Listing rows after merge:", len(listings))

print(
    "Sold rows missing a mortgage rate:",
    sold["rate_30yr_fixed"].isna().sum()
)

print(
    "Listing rows missing a mortgage rate:",
    listings["rate_30yr_fixed"].isna().sum()
)

print("\nSold preview:")
print(
    sold[
        ["CloseDate", "year_month", "ClosePrice", "rate_30yr_fixed"]
    ].head()
)

print("\nListing preview:")
print(
    listings[
        [
            "ListingContractDate",
            "year_month",
            "ListPrice",
            "rate_30yr_fixed"
        ]
    ].head()
)

sold.to_csv(csv_folder / "sold_with_rates.csv", index=False)
listings.to_csv(csv_folder / "listings_with_rates.csv", index=False)

print("\nEnriched CSV files saved.")