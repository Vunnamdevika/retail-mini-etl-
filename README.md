# Retail Mini ETL

A small starter project that creates sample orders when needed, cleans the
order data, and saves it as a CSV and in SQLite. Run all commands from the
project root.

## 1. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 2. Install dependencies

```text
python -m pip install -r requirements.txt
```

## 3. Run the ETL script

```text
python -m src.etl
```

If `data/raw/orders.csv` does not exist, the script creates it with 30 sample
orders, including a few blank quantities. It fills blank quantities with `1`,
calculates revenue, and saves the cleaned data to
`data/processed/orders_clean.csv` and the `orders_clean` table in
`db/orders.db`. It also prints order count, total revenue, and the top product
by revenue.

## 4. Run the tests

```text
python -m pytest
```
