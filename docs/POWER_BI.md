# Power BI Desktop build guide

This layout reproduces the structure of the public [E-commerce Sales Dashboard reference](https://github.com/avishek-choudhary/E-Commerce-Store-Analysis-/blob/main/E-commerce%20Sales%20Dashboard.pbix) using the fields available in this project. It is a single-page summary with KPI cards, trends and rankings, slicers, and a map. The original uses payment mode; this dataset has no payment method, so Ship Mode fills that comparison slot. This is a design adaptation, not a copy of the original dataset or its figures.

## Model

Use `data/processed/superstore_clean.csv` as the fact source. Rename it `FactOrderLine`. Keep order-line grain. Create dimensions by referencing the fact query and removing duplicate rows:

- `DimCustomer`: Customer ID, Customer Name, Segment
- `DimProduct`: Product ID, Product Name, Category, Sub-Category
- `DimGeography`: Country, Region, State, City, Postal Code
- `DimShipMode`: Ship Mode
- `DimDate`: create using `../powerbi/date_table.dax`, mark it as the date table, sort Month by Month Number, Year-Month by Year-Month Sort, and Quarter by Year-Quarter Sort.

Create one-to-many, single-direction relationships from each dimension to the fact table. Relate DimDate[Date] to FactOrderLine[Order Date]. Hide duplicated descriptive keys on the fact table from report authors. Sort month name by month number. Create the measures in `../powerbi/measures.dax`; format Sales, Profit, AOV, Sales per Customer as currency, margin/growth/discount as percentage, and counts as whole numbers.

## Reference-matched single-page report

Build a 16:9 page with a dark navy-to-teal gradient or solid navy background and high-contrast white cards. Match the reference’s clear top KPI row and compact chart grid. Use teal for sales, muted orange for comparisons, and red only for negative profit.

| Reference visual | Superstore implementation |
|---|---|
| Sales/Amount KPI | `[Total Sales]` |
| Profit KPI | `[Total Profit]` |
| Quantity KPI | `[Total Quantity]` |
| AOV KPI | `[Average Order Value]` (sales / distinct orders) |
| Profit by month column chart | DimDate year-month on axis, `[Total Profit]` as value; sort chronologically by the date/sort column |
| Profit by sub-category chart | Sub-Category on axis, `[Total Profit]`; sort ascending to expose losses |
| Category donut | Category as legend, `[Total Quantity]` as value; `[Total Profit]` in tooltip |
| Payment mode donut | Ship Mode as legend, `[Total Quantity]` as value; this is the explicit field substitution; `[Total Profit]` in tooltip |
| State amount/profit chart | State on axis, `[Total Sales]` as value; `[Total Profit]` in tooltip; allow cross-filtering |
| Top customer chart | Customer Name on axis, `[Total Sales]`, visual filter Top 10 by `[Total Sales]` |
| Quarterly slicer | DimDate[Quarter] slicer, preferably dropdown |
| State slicer | DimGeography[State] slicer, searchable dropdown |
| City map | City as location, `[Orders]` as bubble size in the generated report; tooltips include sales, profit, orders, and quantity |
Use question-led chart titles such as “Which sub-categories lose money?” Add a footer: “Source: Sample Superstore | 2014–2017 | line-level sales and profit”.

## Drill and interactions

- Date, state, category, segment, and ship mode filters should affect the full page.
- Enable drill-down on product from Category to Sub-Category and geography from Region to State to City where supported.
- Configure the state chart and city map to cross-filter other visuals; avoid highlight-only behavior if it obscures comparisons.
- Use report tooltips for Profit Margin and Orders instead of overloading each chart.

## Final QA

- Confirm the source has 9,994 rows and totals reconcile with the Excel workbook: Sales $2,297,200.65 and Profit $286,396.54.
- Check for unexpected many-to-many relationships or ambiguous filter paths.
- Validate KPI aggregation after each slicer; margin must recalculate from totals.
- Check year/month ordering and handle blank prior-year values for the first year.
- Verify map geocoding; replace it with a city/state bar or matrix if Power BI places a city incorrectly.
- Save as `Superstore_Sales_Customer_Analysis.pbix` in the project root and record the Power BI Desktop version used.

## Power BI project files

Run `python src/build_powerbi.py` after the data pipeline. This creates `Superstore Sales Analysis.pbip`, a PBIR report folder with all 14 visuals, and a TMDL semantic model with imported data and one-to-many dimensions. The builder writes the current checkout path into its `pProjectRoot` query parameter. Rerun it after cloning or moving the checkout, then open the `.pbip` in Power BI Desktop.

The generated report uses PBIR content version 2.0.0, current report/page schemas, Desktop-compatible report object IDs, registered theme resources, and `.platform` metadata. These are required for Power BI Desktop to materialize the page instead of opening a blank report canvas. The four KPIs use the current `cardVisual` format.

The reference file `E-commerce Sales Dashboard.pbix` is only a style example and contains a different dataset. Open `Superstore Sales Analysis.pbip` from this project folder. The Superstore model uses `FactOrderLine`, `DimDate`, `DimCustomer`, and other dimensions; it uses Ship Mode because the supplied data has no Payment Mode column.

The project generator uses distinct measure names (`Total Sales`, `Total Profit`, and `Total Quantity`) so they do not conflict with same-named source columns. The static validator checks these naming rules and report field references. The PBIP should still be refreshed and inspected in Power BI Desktop after generation; a binary `.pbix` is not included because the corrected project has not been exported from Desktop. Mark `DimDate` as the date table, confirm sort-by columns and relationships, then save as `Superstore_Sales_Customer_Analysis.pbix`. The Top 10 customer filter is included; verify it shows ten values after refresh.
