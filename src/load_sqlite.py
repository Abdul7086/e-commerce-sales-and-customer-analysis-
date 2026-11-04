"""Build a local SQLite star-schema database from the cleaned CSV."""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "processed" / "superstore_clean.csv"
DB = ROOT / "data" / "processed" / "superstore.db"

def main():
    df = pd.read_csv(CSV, dtype={"postal_code": "string"})
    df = df[df["is_valid"].astype(str).str.lower().eq("true")].copy()
    df["postal_code"] = df["postal_code"].fillna("")
    specs = {
        "dim_customer": ("customer_id", ["customer_id", "customer_name", "segment"]),
        "dim_product": ("product_id", ["product_id", "product_name", "category", "sub_category"]),
        "dim_geography": (None, ["country", "region", "state", "city", "postal_code"]),
        "dim_ship_mode": ("ship_mode", ["ship_mode"]),
    }
    with sqlite3.connect(DB) as con:
        con.execute("PRAGMA foreign_keys=ON")
        for table in ["fact_order_line", "dim_customer", "dim_product", "dim_geography", "dim_ship_mode"]:
            con.execute(f"DROP TABLE IF EXISTS {table}")
        con.executescript((ROOT / "sql" / "01_schema.sql").read_text(encoding="utf-8"))
        maps = {}
        for table, (key, cols) in specs.items():
            # Source labels can vary for the same business key; retain the first
            # observed description deterministically and preserve the original facts.
            dim = df[cols].drop_duplicates(subset=[key] if key else cols).sort_values(cols).reset_index(drop=True)
            dim.insert(0, table.removeprefix("dim_") + "_key", range(1, len(dim)+1))
            dim.to_sql(table, con, if_exists="append", index=False)
            if key:
                maps[table] = dict(zip(dim[key], dim.iloc[:, 0]))
            else:
                maps[table] = {tuple(row[c] for c in cols): row.iloc[0] for _, row in dim.iterrows()}
        fact = df[["row_id", "order_id", "order_date", "ship_date", "customer_id", "product_id",
                   "country", "region", "state", "city", "postal_code", "ship_mode",
                   "sales", "quantity", "discount", "profit", "ship_days"]].copy()
        fact["customer_key"] = fact.customer_id.map(maps["dim_customer"])
        fact["product_key"] = fact.product_id.map(maps["dim_product"])
        geo_cols = ["country", "region", "state", "city", "postal_code"]
        fact["geography_key"] = [maps["dim_geography"][tuple(row)] for row in fact[geo_cols].itertuples(index=False, name=None)]
        fact["ship_mode_key"] = fact.ship_mode.map(maps["dim_ship_mode"])
        fact = fact[["row_id", "order_id", "order_date", "ship_date", "customer_key", "product_key",
                     "geography_key", "ship_mode_key", "sales", "quantity", "discount", "profit", "ship_days"]]
        fact.to_sql("fact_order_line", con, if_exists="append", index=False)
        count = con.execute("SELECT COUNT(*) FROM fact_order_line").fetchone()[0]
        assert count == 9994, f"Expected 9994 fact rows, got {count}"
        assert con.execute("PRAGMA foreign_key_check").fetchall() == []
        print(f"Built {DB} with {count:,} fact rows")

if __name__ == "__main__":
    main()
