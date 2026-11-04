# Power BI Desktop build guide

## Model

Use `data/processed/superstore_clean.csv` as the fact source. Rename it `FactOrderLine`. Keep order-line grain. Create dimensions by referencing the fact query and removing duplicate rows:

- `DimCustomer`: Customer ID, Customer Name, Segment
- `DimProduct`: Product ID, Product Name, Category, Sub-Category
- `DimGeography`: Country, Region, State, City, Postal Code
- `DimShipMode`: Ship Mode
- `DimDate`: a contiguous date table from the earliest order date through the latest order date, marked as the date table.

Create one-to-many, single-direction relationships from each dimension to the fact table. Relate DimDate[Date] to FactOrderLine[Order Date]. Hide duplicated descriptive keys on the fact table from report authors. Sort month name by month number. Create the measures in `../powerbi/measures.dax`; format Sales, Profit, AOV, Sales per Customer as currency, margin/growth/discount as percentage, and counts as whole numbers.

## Report pages

### 1. Executive overview

Top row KPI cards: Sales, Profit, Profit Margin, Orders, Customers, Sales YoY %. Add monthly Sales and Profit trend (line/column combo), category performance (bar with sales and profit), and region sales map or bar. Slicers: Order Date, Region, Segment, Category. Add a short dynamic subtitle explaining the active filters.

### 2. Product & discount

Category/Sub-Category matrix with Sales, Profit, Margin, Quantity, conditional red/green Profit. Scatter plot with Sales vs Profit by Sub-Category, size by Quantity. Discount band chart against average profit and loss-line percentage. Include top/bottom product table.

### 3. Customer & geography

Sales and profit by Segment, customer ranking table, customer sales distribution, and state/region matrix. Keep customer names searchable, and avoid labeling top sales as lifetime value.

### 4. Fulfillment

Orders, average ship days, and order lines by Ship Mode; distribution of ship days over time. Explain ship date is shipment date in the supplied extract, not delivery date, so this is order-to-ship time and not delivery SLA.

## Visual design

Import `../powerbi/theme.json`. Use a 16:9 canvas, light background, dark navy text, teal as the primary series, orange for comparison, and restrained red for negative profit. Add a header with project name, page navigation, date slicer, and a small source/method note. Keep visual titles question-led and currencies consistently formatted.

## Final QA checklist

- Confirm the source has 9,994 rows and totals reconcile with the Excel workbook.
- Check no unexpected many-to-many relationships or ambiguous filter paths.
- Validate KPI aggregation after each slicer; margin must recalculate from totals.
- Test date filtering and year-over-year measures, including the first year where prior-year values are blank.
- Ensure map geocoding is not treated as authoritative; use state/region bars if locations render incorrectly.
- Save as `Superstore_Sales_Customer_Analysis.pbix` in the project root and record the Power BI Desktop version used.
