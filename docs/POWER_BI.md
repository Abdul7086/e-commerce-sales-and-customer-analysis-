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
| Sales/Amount KPI | `[Sales]` |
| Profit KPI | `[Profit]` |
| Quantity KPI | `[Quantity]` |
| AOV KPI | `[Average Order Value]` (sales / distinct orders) |
| Profit by month column chart | DimDate month on axis, `[Profit]` as value; sort by date |
| Profit by sub-category chart | Sub-Category on axis, `[Profit]`; sort ascending to expose losses |
| Category donut | Category as legend, `[Quantity]` as value; `[Profit]` in tooltip |
| Payment mode donut | Ship Mode as legend, `[Quantity]` as value; this is the explicit field substitution; `[Profit]` in tooltip |
| State amount/profit chart | State on axis, `[Sales]` as value; `[Profit]` in tooltip; allow cross-filtering |
| Top customer chart | Customer Name on axis, `[Sales]`, visual filter Top 10 by `[Sales]` |
| Quarterly slicer | DimDate[Quarter] slicer, preferably dropdown |
| State slicer | DimGeography[State] slicer, searchable dropdown |
| City map | City as location, `[Sales]` as bubble size; tooltips include `[Profit]`, `[Orders]`, `[Quantity]` |
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

## Why no finished PBIX is included

The reference PBIX was inspected and its visual structure mapped above, but Power BI Desktop is not installed in this environment. A `.pbix` assembled without opening and validating it in Desktop would be unverified. The cleaned source, model recipe, DAX, theme, and visual mapping are provided for a Desktop build.
