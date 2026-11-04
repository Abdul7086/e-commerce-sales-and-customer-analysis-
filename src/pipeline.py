"""Reproducible Superstore profiling, cleaning, validation, and Excel export."""
from pathlib import Path
import argparse
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "Sample - Superstore.csv"
OUT = ROOT / "data" / "processed"

RENAME = {
    "Row ID": "row_id", "Order ID": "order_id", "Order Date": "order_date",
    "Ship Date": "ship_date", "Ship Mode": "ship_mode", "Customer ID": "customer_id",
    "Customer Name": "customer_name", "Segment": "segment", "Country": "country",
    "City": "city", "State": "state", "Postal Code": "postal_code", "Region": "region",
    "Product ID": "product_id", "Category": "category", "Sub-Category": "sub_category",
    "Product Name": "product_name", "Sales": "sales", "Quantity": "quantity",
    "Discount": "discount", "Profit": "profit",
}
DATE_COLS = ["order_date", "ship_date"]
NUMERIC = ["row_id", "postal_code", "sales", "quantity", "discount", "profit"]

def load_clean(path=RAW):
    # The supplied Windows-exported CSV contains a non-breaking space encoded as cp1252.
    df = pd.read_csv(path, dtype={"Postal Code": "string"}, encoding="cp1252")
    df = df.rename(columns=RENAME)
    missing = sorted(set(RENAME.values()) - set(df.columns))
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")
    df["postal_code"] = df["postal_code"].fillna("").str.replace(r"\.0$", "", regex=True)
    for col in DATE_COLS:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in ["row_id", "sales", "quantity", "discount", "profit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["row_id"] = df["row_id"].astype("Int64")
    df["quantity"] = df["quantity"].astype("Int64")
    df["sales"] = df["sales"].round(2)
    df["profit"] = df["profit"].round(2)
    df["discount"] = df["discount"].round(4)
    # Keep all source rows, but explicitly identify invalid records for audit.
    df["ship_days"] = (df["ship_date"] - df["order_date"]).dt.days.astype("Int64")
    df["order_year"] = df["order_date"].dt.year.astype("Int64")
    df["order_month"] = df["order_date"].dt.month.astype("Int64")
    df["order_month_name"] = df["order_date"].dt.strftime("%B")
    df["order_quarter"] = "Q" + df["order_date"].dt.quarter.astype("string")
    df["is_valid"] = (
        df["order_id"].notna() & df["customer_id"].notna() & df["product_id"].notna()
        & df["order_date"].notna() & df["ship_date"].notna()
        & df["sales"].notna() & df["quantity"].gt(0)
        & df["discount"].between(0, 1) & df["ship_days"].ge(0)
    )
    return df

def profile(df):
    return pd.DataFrame({
        "column": df.columns,
        "dtype": [str(t) for t in df.dtypes],
        "null_count": df.isna().sum().values,
        "distinct_count": df.nunique(dropna=True).values,
    })

def validate(df):
    checks = {
        "row_count_matches_source": len(df) == 9994,
        "row_id_unique": df.row_id.is_unique,
        "required_fields_present": not df[["order_id", "customer_id", "product_id", "order_date", "sales", "quantity"]].isna().any().any(),
        "positive_quantities": bool(df.quantity.gt(0).all()),
        "discount_between_zero_and_one": bool(df.discount.between(0, 1).all()),
        "ship_date_not_before_order": bool(df.ship_days.ge(0).all()),
        "valid_record_count": int(df.is_valid.sum()),
    }
    return checks

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=RAW)
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    df = load_clean(args.input)
    checks = validate(df)
    df.to_csv(args.output_dir / "superstore_clean.csv", index=False, date_format="%Y-%m-%d")
    profile(df).to_csv(args.output_dir / "data_profile.csv", index=False)
    (args.output_dir / "validation.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    # Excel workbook is a practical handoff with filters, frozen headers, and summary tabs.
    with pd.ExcelWriter(args.output_dir / "superstore_analysis.xlsx", engine="openpyxl", date_format="yyyy-mm-dd") as writer:
        df.to_excel(writer, sheet_name="Clean Data", index=False)
        profile(df).to_excel(writer, sheet_name="Data Profile", index=False)
        df.groupby(["order_year", "category"], dropna=False).agg(
            orders=("order_id", "nunique"), sales=("sales", "sum"), profit=("profit", "sum"),
            quantity=("quantity", "sum")
        ).reset_index().to_excel(writer, sheet_name="Year Category", index=False)
        df.groupby(["region", "segment"], dropna=False).agg(
            orders=("order_id", "nunique"), customers=("customer_id", "nunique"),
            sales=("sales", "sum"), profit=("profit", "sum")
        ).reset_index().to_excel(writer, sheet_name="Region Segment", index=False)
        for ws in writer.book.worksheets:
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            ws.sheet_view.showGridLines = False
            for cell in ws[1]:
                cell.font = cell.font.copy(bold=True, color="FFFFFF")
                cell.fill = __import__("openpyxl").styles.PatternFill("solid", fgColor="17324D")
    print(json.dumps(checks, indent=2))
    if checks["valid_record_count"] != len(df) or not all(v for k, v in checks.items() if k != "valid_record_count"):
        raise SystemExit("Validation failed; review validation.json")

if __name__ == "__main__":
    main()
