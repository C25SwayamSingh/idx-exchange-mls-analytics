from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

project_folder = Path(__file__).resolve().parent.parent
csv_folder = project_folder / "csv"
plot_folder = project_folder / "plots"

plot_folder.mkdir(exist_ok=True)

sold = pd.read_csv(csv_folder / "sold_with_rates.csv", low_memory=False)
listings = pd.read_csv(csv_folder / "listings_with_rates.csv", low_memory=False)

numeric_fields = ["ClosePrice", "LivingArea", "DaysOnMarket"]


def create_plots(df, dataset_name):
    for column in numeric_fields:
        values = pd.to_numeric(df[column], errors="coerce").dropna()

        # limit the plot to the middle 98% so extreme values do not hide the pattern
        lower_limit = values.quantile(0.01)
        upper_limit = values.quantile(0.99)

        plot_values = values[
            (values >= lower_limit) &
            (values <= upper_limit)
        ]

        # histogram
        plt.figure(figsize=(8, 5))
        plt.hist(plot_values, bins=40)
        plt.title(f"{dataset_name} {column} Distribution")
        plt.xlabel(column)
        plt.ylabel("Number of Properties")
        plt.tight_layout()
        plt.savefig(
            plot_folder / f"{dataset_name.lower()}_{column.lower()}_histogram.png"
        )
        plt.close()

        # boxplot
        plt.figure(figsize=(8, 4))
        plt.boxplot(plot_values, vert=False)
        plt.title(f"{dataset_name} {column} Boxplot")
        plt.xlabel(column)
        plt.tight_layout()
        plt.savefig(
            plot_folder / f"{dataset_name.lower()}_{column.lower()}_boxplot.png"
        )
        plt.close()


create_plots(sold, "Sold")
create_plots(listings, "Listings")

print("Plots saved to:", plot_folder)


