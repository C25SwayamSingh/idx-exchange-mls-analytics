# Weeks 6-7 Summary

## Main Goal

Finish the remaining Week 6 deliverables (segment tables and school districts) and complete Week 7 outlier detection using the IQR method.

As always: no rows were deleted from the main datasets. Outliers are flagged, and the filtered version is a separate copy.

---

## New Scripts

| Script | What It Does |
|---|---|
| `week6_segments.py` | Groups both datasets by county and property subtype and saves median summary tables |
| `week6_school_districts.py` | Spatial join that adds each property's Unified school district from lat/long |
| `week7_outliers.py` | Flags ClosePrice/ListPrice, LivingArea, and DaysOnMarket outliers using IQR |

---

## Week 6 – Segment Tables

Each table shows property count, median price, median price per sqft, and median days on market per group.

Main finding:

> The most expensive counties sell the fastest. Santa Clara (median $1.6M) sells in 10 days while Riverside (median $600K) takes 30. Expensive coastal markets have much tighter supply than inland ones.

---

## Week 6 – School Districts

- Boundary file: California School District Areas 2025-26 GeoJSON from data.ca.gov
- Filtered to Unified districts only (345 of California's 936 districts)
- The GeoJSON uses Web Mercator (EPSG:3857), so it is reprojected to EPSG:4326 before joining — without this step every property silently matches nothing

| Dataset | Matched to a District |
|---|---:|
| Sold | 73.1% |
| Listings | 66.5% |

Why not 100%:

> Large parts of California are covered by a separate Elementary district plus High School district instead of one Unified district, so properties there correctly match nothing. The rest are rows with missing or bad coordinates already flagged in Week 4.

---

## Week 7 – Outlier Detection (IQR)

A value is an outlier if it falls more than 1.5 IQR outside the middle 50% of the data. Blanks are not counted as outliers.

| Dataset | Rows | Flagged | Removed in Filtered Copy |
|---|---:|---:|---:|
| Sold | 430,445 | 67,700 | 15.73% |
| Listings | 591,619 | 100,168 | 16.93% |

Two things worth noticing:

> Every lower fence came out negative (for example, ClosePrice lower bound = -$512,500). A home cannot have a negative price, so in practice all trimming happens on the high side. This is what right-skewed housing data does to the IQR method.

> Filtering shifts the medians. Median close price drops from $825K to $785K, and median days on market drops too — the filter removes exactly the slow sales. Use the flagged file (not the filtered one) for days-on-market dashboards, or they will understate how long homes take to sell.

---

## Where Everything Lives

| Item | Location |
|---|---|
| All scripts | `python/` (this repo) |
| Flagged + filtered datasets, district-enriched datasets | `csv/` (local only — confidential, never in git) |
| Segment tables and outlier reports | `reports/` (local only) |
| District boundary GeoJSON | project root, `DistrictAreas*.geojson` (local only) |
