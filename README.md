# IDX Exchange MLS Analytics

Python scripts for combining monthly CRMLS listing and sold files into cumulative datasets and filtering the results to Residential properties.

## Scripts

* `combine_listings.py` combines the monthly listing files and creates `listings.csv`.
* `combine_sold.py` combines the monthly sold files and creates `sold.csv`.

## Data

The MLS CSV files are excluded from this repository because the source data is proprietary and should not be publicly uploaded.

# IDX Exchange MLS Analytics

## Project Overview

This project processes monthly California Regional MLS listing and sold-property data for the IDX Exchange Data Analyst Internship.

The Python workflow combines monthly CRMLS files from January 2024 through May 2026, filters the data to Residential properties, performs dataset validation and exploratory analysis, and adds monthly 30-year mortgage rates from FRED.

Raw MLS data is confidential and is not included in this public repository.

## Project Workflow

1. Combine the monthly Sold files into one cumulative dataset.
2. Combine the monthly Listing files into one cumulative dataset.
3. Filter both datasets to `PropertyType == "Residential"`.
4. Review dataset dimensions, column types, and missing values.
5. Flag columns with more than 90% missing data.
6. Produce numeric summaries for `ClosePrice`, `LivingArea`, and `DaysOnMarket`.
7. Fetch weekly 30-year mortgage rates from FRED and calculate monthly averages.
8. Merge the monthly mortgage rates onto both datasets.
9. Generate histograms and boxplots for key numeric fields.

## Scripts

### `combine_sold.py`

* Finds the monthly CRMLS Sold files.
* Selects one file per month.
* Handles `_filled` files by removing their two extra columns.
* Combines January 2024 through May 2026.
* Filters to Residential properties.
* Produces the cumulative `sold.csv`.
* Creates a Sold validation report.

### `combine_listings.py`

* Finds the monthly CRMLS Listing files.
* Selects one file per month.
* Combines January 2024 through May 2026.
* Filters to Residential properties.
* Produces the cumulative `listings.csv`.
* Creates a Listings validation report.

### `week2_3_validation.py`

* Reviews dataset dimensions and property types.
* Calculates missing counts and percentages.
* Flags columns above 90% missing.
* Produces numeric summaries for price, living area, and days on market.
* Saves missing-value and numeric-summary reports.

### `mortgage_rate_merge.py`

* Downloads the FRED `MORTGAGE30US` series.
* Converts weekly mortgage rates into monthly averages.
* Matches Sold records using `CloseDate`.
* Matches Listing records using `ListingContractDate`.
* Validates that no rows are lost and no mortgage rates are missing.
* Saves mortgage-rate-enriched datasets locally.

### `week2_3_plots.py`

* Creates histograms and boxplots for:

  * `ClosePrice`
  * `LivingArea`
  * `DaysOnMarket`
* Saves the images in the local `plots` folder.

## Current Dataset Results

| Dataset  |    Rows | Columns |
| -------- | ------: | ------: |
| Sold     | 430,445 |      82 |
| Listings | 591,619 |      84 |

* Sold columns above 90% missing: 15
* Listing columns above 90% missing: 13
* Sold rows missing mortgage rates: 0
* Listing rows missing mortgage rates: 0

## Folder Structure

```text
IDX Exchange Internship/
├── csv/
├── plots/
├── python/
│   ├── combine_sold.py
│   ├── combine_listings.py
│   ├── week2_3_validation.py
│   ├── mortgage_rate_merge.py
│   └── week2_3_plots.py
├── sold_validation.txt
└── listings_validation.txt
```

## Requirements

* Python 3
* pandas
* matplotlib
* Internet connection for downloading FRED mortgage-rate data

Install the required packages with:

```bash
pip install pandas matplotlib
```

## Running the Project

Run the scripts in this order:

```bash
python combine_sold.py
python combine_listings.py
python week2_3_validation.py
python mortgage_rate_merge.py
python week2_3_plots.py
```

The scripts expect the `python` and `csv` folders to be located inside the same main project folder.

## Data Confidentiality

CRMLS monthly files, cumulative datasets, enriched datasets, and API extraction scripts are excluded from this repository. Only code and project documentation are publicly shared.
