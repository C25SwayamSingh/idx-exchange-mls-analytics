# Weeks 8-10 Summary

## Main Goal

Refresh the data through the latest completed month, then build the two Tableau workbooks: Market Analysis and Competitive Analysis.

---

## Data Refresh

`crmls_refresh.py` pulls new months from Trestle in one pass instead of one script per month. June and July 2026 were added and the full pipeline was re-run end to end with no rows lost.

| Dataset | Before | After |
|---|---:|---:|
| Sold | 430,445 | 465,284 |
| Listings | 591,619 | 637,488 |

Data now covers January 2024 through July 2026.

One fix along the way: `week7_outliers.py` now reads the district-enriched files, so `DistrictName` reaches the final dataset that Tableau uses. Before this, the school district join was written to a file nothing read.

---

## Market Analysis Workbook

Two data sources (sold and listings, kept separate - joining them would multiply rows).

| Dashboard | Sheets |
|---|---|
| Market Trends | Median Close Price, Closed Sales, Average Days on Market, Sold to List Ratio |
| Geographic Analysis | Median Price by Zip, Homes Sold by Zip |

Plus a New Listings sheet from the listings source, and County / City / Property Sub Type filters shared across every sheet.

---

## Competitive Analysis Workbook

| Sheet | What It Ranks |
|---|---|
| Top Agents by Volume | List agents by total close price |
| Top Agents by Sales | List agents by number of sales |
| Top Offices by Volume | Offices by total close price |
| Office Market Share | Each office's share of total volume |
| Fastest Agents | Average days on market, minimum 10 sales |
| Best Price Achieved | Average sold-to-list percent, minimum 10 sales |
| Agents by School District | Top agents inside each Unified district |

---

## Aggregation Choices

These matter more than they look.

> Market Analysis uses MEDIAN for prices. Tableau defaults to SUM, and a sum-of-prices chart looks completely normal - only the axis in billions gives it away. Sum mixes price with volume; average gets dragged by outliers; median ignores both.

> Competitive Analysis uses SUM. Here total dollar volume is the actual ranking metric, so the same function that was wrong above is correct here.

> No outlier filter on competitive sheets. Top producers earn their rank on the big deals.

> Days on market uses the cleaned `days_on_market_analysis` field and no outlier filter. Filtering outliers removes exactly the slow sales and makes the average look better than reality.

> The Fastest Agents and Best Price sheets require at least 10 sales, otherwise one lucky quick sale tops the list.

---

## Where Everything Lives

| Item | Location |
|---|---|
| Scripts and summaries | `python/` (this repo) |
| Refreshed datasets | `csv/` (local only, confidential) |
| Workbooks | `tableau/` (local only - a `.twbx` packages the full dataset inside it) |
