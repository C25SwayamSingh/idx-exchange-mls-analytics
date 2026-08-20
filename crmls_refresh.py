from pathlib import Path
from datetime import datetime
import csv
import re
import requests


SCRIPT_DIR = Path(__file__).resolve().parent
CSV_DIR = SCRIPT_DIR.parent / "csv"

URL = "https://api-trestle.corelogic.com/trestle/odata/Property"

# months to pull
MONTHS = [(2026, 6), (2026, 7)]


def read_old_script(name):
    return (SCRIPT_DIR / name).read_text()


# reuse the key already in the older scripts instead of writing it out again
AUTH = re.search(
    r"auth_endpoint = '([^']+)'",
    read_old_script("crmls_sold_202605.py")
).group(1)


def get_fields(name):
    # same columns the earlier months used, so the files line up
    block = re.search(r"fieldnames=\[(.*?)\]", read_old_script(name), re.S)

    return re.findall(r"'([^']+)'", block.group(1))


def month_bounds(year, month):
    start = datetime(year, month, 1)
    end = datetime(year + (month == 12), month % 12 + 1, 1)

    return (
        f"{start.isoformat(timespec='milliseconds')}Z",
        f"{end.isoformat(timespec='milliseconds')}Z"
    )


def pull(kind, year, month, fields, token):
    start, end = month_bounds(year, month)

    if kind == "Sold":
        where = (
            f"MlsStatus eq 'Closed' "
            f"and CloseDate ge {start} and CloseDate lt {end}"
        )
    else:
        where = (
            f"ListingContractDate ge {start} "
            f"and ListingContractDate lt {end}"
        )

    out_path = CSV_DIR / f"CRMLS{kind}{year}{month:02d}.csv"

    # the listing column list repeats a few names, dedupe for the request
    selected = list(dict.fromkeys(fields))

    url = URL
    params = {
        "$select": ",".join(selected),
        "$filter": where,
        "$top": 1000
    }

    headers = {"Authorization": f"Bearer {token}"}
    total = 0

    print(f"\nPulling {out_path.name}...")

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        while True:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=120
            )

            response.raise_for_status()
            data = response.json()

            for observation in data.get("value", []):
                writer.writerow(
                    {name: observation.get(name, "") for name in fields}
                )
                total += 1

            # more pages
            if "@odata.nextLink" in data:
                url = data["@odata.nextLink"]
                params = None
            else:
                break

    print(f"{out_path.name}: {total} records")

    return total


response = requests.get(AUTH, timeout=30)
response.raise_for_status()
token = response.json()["access_token"]

sold_fields = get_fields("crmls_sold_202605.py")
listing_fields = get_fields("crmls_listed_202605.py")

for year, month in MONTHS:
    pull("Sold", year, month, sold_fields, token)
    pull("Listing", year, month, listing_fields, token)

print("\nRefresh completed successfully.")
