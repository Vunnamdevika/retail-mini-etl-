import sqlite3

import pandas as pd

from src.etl import run_etl


def test_revenue_column_exists_and_non_negative(tmp_path, capsys):
    input_path = tmp_path / "data" / "raw" / "orders.csv"
    output_path = tmp_path / "data" / "processed" / "orders_clean.csv"
    database_path = tmp_path / "db" / "orders.db"

    run_etl(input_path, output_path, database_path)

    cleaned = pd.read_csv(output_path)
    assert len(cleaned) == 30
    assert "revenue" in cleaned.columns
    assert (cleaned["revenue"] >= 0).all()

    with sqlite3.connect(database_path) as connection:
        saved_orders = pd.read_sql_query("SELECT * FROM orders_clean", connection)
    pd.testing.assert_frame_equal(saved_orders, cleaned)

    printed_kpis = capsys.readouterr().out
    assert "total_orders: 30" in printed_kpis
    assert "total_revenue:" in printed_kpis
    assert "top_product_by_revenue:" in printed_kpis


def test_missing_quantity_filled_with_one(tmp_path):
    input_path = tmp_path / "orders.csv"
    output_path = tmp_path / "orders_clean.csv"
    database_path = tmp_path / "orders.db"
    pd.DataFrame(
        {
            "order_id": [1, 2],
            "order_date": ["2025-01-01", "2025-01-02"],
            "product": ["Notebook", "Pen"],
            "quantity": [None, 2],
            "unit_price": [4.5, 1.25],
        }
    ).to_csv(input_path, index=False)

    run_etl(input_path, output_path, database_path)

    cleaned = pd.read_csv(output_path)
    assert cleaned["quantity"].tolist() == [1, 2]
    assert cleaned["quantity"].dtype == "int64"
    assert cleaned["unit_price"].dtype == "float64"
    assert cleaned["revenue"].tolist() == [4.5, 2.5]
