from pathlib import Path
import geopandas as gpd
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
CSV_DIR = PROJECT_DIR / "csv"

# whatever the download was named
GEOJSON = next(PROJECT_DIR.glob("DistrictAreas*.geojson"))


def load_districts():
    districts = gpd.read_file(GEOJSON)

    # unified only
    districts = districts[districts["DistrictType"] == "Unified"]

    # file is web mercator, our coords are lat/long
    districts = districts.to_crs("EPSG:4326")

    return districts[["DistrictName", "geometry"]]


def add_districts(input_name, output_name, districts):
    print(f"\nAdding school districts to {input_name}...")

    df = pd.read_csv(CSV_DIR / input_name, low_memory=False)
    starting_rows = len(df)

    # lat/long into map points
    points = gpd.GeoDataFrame(
        df[["Latitude", "Longitude"]],
        geometry=gpd.points_from_xy(df["Longitude"], df["Latitude"]),
        crs="EPSG:4326"
    )

    # which district contains each property
    joined = gpd.sjoin(points, districts, how="left", predicate="within")

    # a point on a shared border can match twice
    joined = joined[~joined.index.duplicated()]

    df["DistrictName"] = joined["DistrictName"]

    # joining must not drop rows
    assert len(df) == starting_rows

    matched = int(df["DistrictName"].notna().sum())

    print(f"Rows matched to a district: {matched} "
          f"({matched / starting_rows * 100:.1f}%)")

    df.to_csv(CSV_DIR / output_name, index=False)

    print(f"Saved: {output_name}")


districts = load_districts()

print(f"Unified districts loaded: {len(districts)}")

add_districts(
    "sold_week6_metrics.csv",
    "sold_week6_districts.csv",
    districts
)

add_districts(
    "listings_week6_metrics.csv",
    "listings_week6_districts.csv",
    districts
)

print("\nWeek 6 school district join completed successfully.")
