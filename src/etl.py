import sqlite3
from datetime import date, timedelta
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "orders.csv"
PROCESSED_FILE = PROJECT_ROOT / "data" / "processed" / "orders_clean.csv"
DATABASE_FILE = PROJECT_ROOT / "db" / "orders.db"

PRODUCT_PRICES = {
    "Notebook": 4.50,
    "Pen": 1.25,
    "Backpack": 24.00,
    "Water Bottle": 12.50,
    "Desk Lamp": 18.00,
}
SAMPLE_QUANTITIES = [
    2, 1, 3, 2, None, 4, 1, 2, 3, 1,
    2, None, 5, 1, 2, 3, 1, 4, 2, None,
    1, 3, 2, 1, 4, 2, 3, None, 1, 2,
]


def create_sample_orders(path):
    """Create 30 repeatable sample orders, including a few blank quantities."""
    path.parent.mkdir(parents=True, exist_ok=True)
    first_order_date = date(2025, 1, 1)
    products = list(PRODUCT_PRICES)
    orders = []

    for index, quantity in enumerate(SAMPLE_QUANTITIES):
        product = products[index % len(products)]
        orders.append(
            {
                "order_id": 1001 + index,
                "order_date": (first_order_date + timedelta(days=index)).isoformat(),
                "product": product,
                "quantity": quantity,
                "unit_price": PRODUCT_PRICES[product],
            }
        )

    pd.DataFrame(orders).to_csv(path, index=False)


def run_etl(input_path=None, output_path=None, db_path=None):
    """Clean orders, save them as CSV and SQLite, and print summary KPIs."""
    source = Path(input_path) if input_path is not None else RAW_FILE
    destination = Path(output_path) if output_path is not None else PROCESSED_FILE
    database = Path(db_path) if db_path is not None else DATABASE_FILE

    if not source.exists():
        create_sample_orders(source)

    orders = pd.read_csv(source)
    orders["quantity"] = orders["quantity"].fillna(1).astype(int)
    orders["unit_price"] = orders["unit_price"].astype(float)
    orders["revenue"] = orders["quantity"] * orders["unit_price"]

    destination.parent.mkdir(parents=True, exist_ok=True)
    orders.to_csv(destination, index=False)

    database.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database) as connection:
        orders.to_sql("orders_clean", connection, if_exists="replace", index=False)

    revenue_by_product = orders.groupby("product", sort=False)["revenue"].sum()
    top_product = revenue_by_product.idxmax()
    print("total_orders: {}".format(len(orders)))
    print("total_revenue: {:.2f}".format(orders["revenue"].sum()))
    print("top_product_by_revenue: {}".format(top_product))

    return destination


def main():
    output_path = run_etl()
    print("Cleaned orders saved to: {}".format(output_path))


if __name__ == "__main__":
    main()
