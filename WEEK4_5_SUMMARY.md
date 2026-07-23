# Weeks 4-5 Cleaning Summary

## Main Goal

The goal for Weeks 4-5 is to make the Sold and Listing datasets cleaner and easier to trust before building dashboards.

We are not deleting rows aggressively yet. We are removing unusable columns, fixing data types, and adding warning flags for rows that may need review.

---

## What We Did

| Step | Simple Meaning |
|---|---|
| Dropped columns over 90% missing | Removed columns that were mostly blank |
| Checked `.1` duplicate columns | Removed repeated columns after checking them |
| Converted dates | Made date fields work as real dates |
| Converted numbers | Made price, area, DOM, bedrooms, bathrooms, and coordinates work as numbers |
| Added quality flags | Marked suspicious rows instead of deleting them |
| Checked coordinates | Found rows that may not work well for maps |

---

## Main Results

| Dataset | Starting Rows | Final Rows | Rows Lost | Rows Flagged |
|---|---:|---:|---:|---:|
| Sold | 430,445 | 430,445 | 0 | 16,813 |
| Listings | 591,619 | 591,619 | 0 | 81,836 |

The most important result is that no rows were lost.

The script cleaned the structure of the data, but kept the full dataset available for review.

---

## Columns Removed

| Dataset | Columns Dropped |
|---|---:|
| Sold | 15 |
| Listings | 13 |

These were columns with more than 90% missing values.

Examples include:

- `ElementarySchoolDistrict`
- `TaxAnnualAmount`
- `FireplacesTotal`
- `BuilderName`
- `BuildingAreaTotal`
- `MiddleOrJuniorSchoolDistrict`

Simple explanation:

> These columns were mostly blank, so they probably would not help much with the final dashboard analysis.

---

## Duplicate `.1` Columns

The Sold dataset had no `.1` duplicate columns.

The Listing dataset had several duplicate columns removed, such as:

- `ListPrice.1`
- `Latitude.1`
- `Longitude.1`
- `DaysOnMarket.1`
- `PropertyType.1`

Simple explanation:

> A `.1` column means the same field showed up twice, so Pandas renamed the second copy. We checked the extra copy and removed it when it was safe.

---

## What Flagging Means

A flag is a True/False warning column.

## Early Week 5 Flag Rules

| Flag / Issue | What We Should Do |
|---|---|
| Missing or bad coordinates | Exclude from map visuals |
| Negative DaysOnMarket | Exclude from average DOM |
| Invalid ClosePrice | Exclude from price analysis |
| Invalid LivingArea | Exclude from price-per-square-foot or size analysis |
| Timeline/date-order issue | Review before using for time-based calculations |

The main idea is that a flagged row is not automatically deleted. It may just be excluded from the specific metric where the issue matters.