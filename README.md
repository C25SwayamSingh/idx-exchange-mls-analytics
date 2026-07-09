# IDX Exchange MLS Analytics

## Project Overview

This project processes monthly California Regional MLS listing and sold-property data for the IDX Exchange Data Analyst Internship.

The workflow combines monthly CRMLS files from January 2024 through May 2026, filters the data to Residential properties, validates the datasets, adds monthly 30-year mortgage rates from FRED, and performs data-quality checks.

Raw MLS data is confidential and is not included in this public repository.

## Project Workflow

1. Combine monthly Sold files into one cumulative dataset.
2. Combine monthly Listing files into one cumulative dataset.
3. Filter both datasets to `PropertyType == "Residential"`.
4. Review dataset dimensions, data types, missing values, and numeric distributions.
5. Add monthly 30-year mortgage rates from FRED.
6. Create histograms and boxplots for key numeric fields.
7. Remove confirmed duplicate columns and columns with more than 90% missing data.
8. Standardize date and numeric data types.
9. Add quality flags for invalid numeric values, transaction timelines, and geographic coordinates.

## Scripts

### `combine_sold.py`

- Finds the monthly CRMLS Sold files.
- Selects one file per month.
- Handles `_filled` files by removing their two additional columns.
- Combines files from January 2024 through May 2026.
- Filters the dataset to Residential properties.
- Produces the cumulative `sold.csv`.
- Creates a Sold validation report.

### `combine_listings.py`

- Finds the monthly CRMLS Listing files.
- Selects one file per month.
- Handles regular and `_filled` file versions.
- Combines files from January 2024 through May 2026.
- Filters the dataset to Residential properties.
- Produces the cumulative `listings.csv`.
- Creates a Listings validation report.

### `week2_3_validation.py`

- Reviews dataset dimensions and property types.
- Calculates missing counts and percentages.
- Identifies columns with more than 90% missing data.
- Produces numeric summaries for `ClosePrice`, `LivingArea`, and `DaysOnMarket`.
- Saves missing-value and numeric-summary reports.

### `mortgage_rate_merge.py`

- Downloads the FRED `MORTGAGE30US` series.
- Converts weekly mortgage rates into monthly averages.
- Matches Sold records using `CloseDate`.
- Matches Listing records using `ListingContractDate`.
- Confirms that no rows are lost during the merge.
- Saves mortgage-rate-enriched datasets locally.

### `week2_3_plots.py`

- Creates histograms and boxplots for:
  - `ClosePrice`
  - `LivingArea`
  - `DaysOnMarket`
- Limits the visualizations to the 1st through 99th percentiles for readability without changing the underlying data.
- Saves the images in the local `plots` folder.

### `week4_cleaning.py`

- Reviews and safely handles duplicate `.1` columns.
- Drops columns with more than 90% missing values.
- Converts important date fields to datetime.
- Converts analytical fields to numeric data types.
- Flags invalid prices, living areas, days on market, bedrooms, and bathrooms.
- Checks whether transaction dates occur in the correct order.
- Flags missing, zero, positive, or implausible coordinates.
- Creates an overall data-quality flag.
- Confirms that no rows are accidentally removed.
- Saves cleaned local datasets and cleaning reports.

## Dataset Results

### Residential datasets before mortgage-rate enrichment

| Dataset | Rows | Columns |
|---|---:|---:|
| Sold | 430,445 | 82 |
| Listings | 591,619 | 84 |

### Week 4 cleaning results

| Dataset | Starting Shape | Final Shape | Rows Flagged |
|---|---:|---:|---:|
| Sold | 430,445 × 84 | 430,445 × 83 | 16,813 |
| Listings | 591,619 × 86 | 591,619 × 76 | 81,836 |

All original rows were preserved. Questionable records were flagged for review rather than automatically deleted.

Both mortgage-rate-enriched datasets had zero missing mortgage-rate values before the Week 4 cleaning process.

## Folder Structure

```text
IDX Exchange Internship/
├── csv/
│   ├── sold.csv
│   ├── listings.csv
│   ├── sold_with_rates.csv
│   ├── listings_with_rates.csv
│   ├── sold_week4_cleaned.csv
│   └── listings_week4_cleaned.csv
├── plots/
├── reports/
│   ├── sold_week4_cleaning_report.txt
│   └── listings_week4_cleaning_report.txt
└── python/
    ├── combine_sold.py
    ├── combine_listings.py
    ├── week2_3_validation.py
    ├── mortgage_rate_merge.py
    ├── week2_3_plots.py
    ├── week4_cleaning.py
    ├── README.md
    └── .gitignore