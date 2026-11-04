-- SQLite-compatible star schema for the cleaned Superstore source.
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS dim_customer (
  customer_key INTEGER PRIMARY KEY, customer_id TEXT UNIQUE NOT NULL,
  customer_name TEXT NOT NULL, segment TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS dim_product (
  product_key INTEGER PRIMARY KEY, product_id TEXT UNIQUE NOT NULL,
  product_name TEXT NOT NULL, category TEXT NOT NULL, sub_category TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS dim_geography (
  geography_key INTEGER PRIMARY KEY, country TEXT NOT NULL, region TEXT NOT NULL,
  state TEXT NOT NULL, city TEXT NOT NULL, postal_code TEXT
);
CREATE TABLE IF NOT EXISTS dim_ship_mode (
  ship_mode_key INTEGER PRIMARY KEY, ship_mode TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS fact_order_line (
  row_id INTEGER PRIMARY KEY, order_id TEXT NOT NULL, order_date TEXT NOT NULL,
  ship_date TEXT NOT NULL, customer_key INTEGER NOT NULL REFERENCES dim_customer,
  product_key INTEGER NOT NULL REFERENCES dim_product,
  geography_key INTEGER NOT NULL REFERENCES dim_geography,
  ship_mode_key INTEGER NOT NULL REFERENCES dim_ship_mode,
  sales NUMERIC NOT NULL, quantity INTEGER NOT NULL, discount NUMERIC NOT NULL,
  profit NUMERIC NOT NULL, ship_days INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_fact_order_date ON fact_order_line(order_date);
CREATE INDEX IF NOT EXISTS ix_fact_order_id ON fact_order_line(order_id);
