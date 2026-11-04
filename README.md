# Superstore Sales & Customer Analysis

Interview-ready, reproducible analytics project built from the provided Sample Superstore data. It covers Python profiling and cleaning, an Excel analysis workbook, a relational SQL model, and a Power BI report specification. The data describes US retail order lines from 2014–2017; it is not a live e-commerce platform dataset.

## Start here

1. Install Python 3.10+ and run `python -m pip install -r requirements.txt`.
2. Run `python src/pipeline.py` from this folder.
3. Open `data/processed/superstore_analysis.xlsx` for the Excel deliverable. The cleaned CSV, profile, and validation report are created beside it.
4. Run `python src/load_sqlite.py` to create a local SQLite star schema at `data/processed/superstore.db`; query it with the scripts in `sql/`.
5. Follow [Power BI build instructions](docs/POWER_BI.md) to create the report in Power BI Desktop. A `.pbix` is intentionally not included: it cannot be authored or validated in this environment.

## Questions this dashboard answers

- How do sales, profit, order count, and margin change over time?
- Which categories, products, regions, and customer segments generate or destroy profit?
- Where does discounting correlate with losses?
- Which customers and products contribute most to sales and profit?
- How do shipping mode and fulfillment time vary?

## Project structure

```text
data/raw/                 Supplied source CSV (unchanged)
data/processed/           Generated cleaned CSV, profile, validation, Excel workbook
src/pipeline.py           Profiling, typed cleaning, checks, and Excel generation
sql/                      Star-schema DDL and analysis queries
powerbi/                   DAX measures and report theme
docs/                      Data dictionary, Power BI instructions, interview narrative
```

## Data quality choices

The pipeline preserves every original row and adds `is_valid` so questionable records are auditable. It standardizes column names, parses dates, converts numeric fields, rounds currency to cents, retains postal codes as text, derives calendar fields and ship days, and checks uniqueness, required fields, positive quantity, discount range, and date ordering. No rows are silently discarded, and no missing postal codes are imputed.

## Reproducibility and validation

`validation.json` reports source row count and key data rules. The expected row count is the known 9,994 rows in this supplied extract; change the check if using another version. See [Data Dictionary](docs/DATA_DICTIONARY.md) and [Interview Guide](docs/INTERVIEW_GUIDE.md).

## Important metric definitions

- Sales, profit, and quantity are additive at order-line grain.
- Orders count distinct Order ID; customers count distinct Customer ID.
- Profit margin is total profit divided by total sales, never an average of row margins.
- Average order value is sales divided by distinct orders.
- The source has no returns table, marketing spend, web sessions, or customer acquisition data; do not imply return rate, CAC, conversion, or LTV.

## Repository contents

The source CSV is included to make the project reproducible. Generated outputs are produced locally and excluded from Git; retain/export the Excel workbook as an interview artifact after running the pipeline.
