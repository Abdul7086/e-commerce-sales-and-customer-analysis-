# Project Walkthrough and Interview Q&A

This guide explains the project from the original file to the Power BI report, using the actual project design and verified figures. Learn the story and the reasoning; you do not need to memorize every number.

## 1. Project in one minute

This is a reproducible sales and customer analysis project built from the Sample Superstore dataset. It takes the original order-line CSV, profiles and cleans it with Python, creates an Excel analysis workbook, loads a relational star schema into SQLite, and supplies a Power BI report with a dimensional model, DAX measures, slicers, and visuals.

The business goal is to understand sales, profit, customer and product performance, geography, discounts, and shipping. The report follows the layout of an e-commerce dashboard reference, but uses the fields in this dataset. It is important to describe the source honestly: this is US retail order data, not website clickstream data or a live online store. It has no payment method, marketing spend, sessions, returns, or customer acquisition cost.

**Verified headline figures:** 9,994 order lines; 5,009 distinct orders; 793 customers; sales of $2,297,200.65; profit of $286,396.54; quantity of 37,873; overall profit margin of 12.47%; and an average order value of $458.61. The dates run from January 3, 2014 to December 30, 2017.

## 2. The business questions

The project is designed to help a manager answer:

1. How much did we sell, how much profit did we make, and how did these change over time?
2. Which categories, sub-categories, regions, states, and customers contribute most to sales and profit?
3. Which products or sub-categories lose money?
4. How do customer segments and shipping modes compare?
5. How are discounts associated with profit outcomes?
6. Can a manager filter the report by time and state and inspect the same metrics consistently?

The central distinction is **sales versus profit**. High sales do not guarantee high profit.

## 3. End-to-end project flow

```text
Original Sample Superstore CSV
              |
              v
Python: profile -> clean/types -> derive fields -> validate
       |                     |                         |
       v                     v                         v
Excel workbook          Clean CSV + profile      Validation JSON
       |
       +-----------------------> SQLite star schema <--- SQL queries
                                      |
                                      v
                          Power BI semantic model
                          dimensions + fact + DAX
                                      |
                                      v
                       Interactive report and preview
```

The pipeline keeps the raw CSV unchanged. The cleaned file is the shared analysis-ready source. Excel, SQLite, and Power BI then serve different purposes: spreadsheet review, relational querying, and interactive visual analysis.

## 4. Repository map

- `data/raw/`: original input CSV, kept unchanged.
- `src/pipeline.py`: reads, profiles, cleans, validates, and writes the analysis workbook and processed outputs.
- `data/processed/`: generated clean CSV, profile, validation report, Excel workbook, and local database (generated outputs may be ignored by Git).
- `src/load_sqlite.py`: creates and loads the local relational database.
- `sql/01_schema.sql`: database tables and relationships.
- `sql/02_analysis_queries.sql`: example business questions expressed in SQL.
- `powerbi/measures.dax`: reusable measures for report calculations.
- `powerbi/date_table.dax`: calendar table logic.
- `src/build_powerbi.py`: generates the source-controlled Power BI Project and model definition.
- `Superstore Sales Analysis.pbip`: entry point to open the project in Power BI Desktop.
- `Superstore Sales Analysis.Report/`: report page and visual definitions.
- `Superstore Sales Analysis.SemanticModel/`: model tables, relationships, measures, and source expressions.
- `docs/DATA_DICTIONARY.md`: field descriptions and definitions.
- `docs/POWER_BI.md`: report layout and Power BI setup notes.
- `docs/dashboard-preview.png`: static image preview for GitHub; it is not an interactive report.

## 5. Data grain and cleaning

### What one row means

The dataset is at **order-line grain**: one record represents one product line on an order. An order with several products appears on several rows. Therefore:

- `SUM(Sales)`, `SUM(Profit)`, and `SUM(Quantity)` can be calculated across rows.
- Orders must be counted as distinct `Order ID`, not as rows.
- Customers must be counted as distinct `Customer ID`, not as rows.
- A customer or product can appear in many rows.

### Python preparation

The pipeline:

1. Reads the supplied CSV using the encoding needed for its special characters.
2. Produces a profile of columns, types, missing values, and basic statistics.
3. Standardizes field names for consistent use in code and SQL.
4. Parses order and ship dates as dates and converts sales, profit, quantity, and discount to numeric values.
5. Keeps postal codes as text so formatting such as leading zeroes is not lost.
6. Rounds currency fields to cents and keeps discount precision.
7. Derives calendar fields such as year, month, and quarter, plus `ship_days` (ship date minus order date).
8. Adds `is_valid` and runs checks for required values, unique row identifiers, positive quantity, valid discount range, and sensible date order.
9. Writes the cleaned CSV, a profile, a validation summary, and an Excel workbook.

All 9,994 source rows are retained and pass the project's validity checks. Retaining rows makes the process auditable; questionable records would be flagged rather than silently deleted. Missing postal codes are not guessed or filled in.

### Excel output

The workbook is a convenient review deliverable, not a separate source of truth. It includes clean order-line data, a data profile, and summary views such as year/category and region/segment. The CSV and scripts allow the workbook to be regenerated.

## 6. SQL model

SQLite stores the data in a star schema:

- **FactOrderLine / fact_order_line:** numeric events such as sales, profit, quantity, discount, dates, and keys to descriptive dimensions.
- **DimCustomer:** customer ID, name, and segment.
- **DimProduct:** product ID, name, category, and sub-category.
- **DimGeography:** country, region, state, city, and postal code.
- **DimShipMode:** ship mode.
- **DimDate:** calendar attributes for filtering and grouping by time.

The fact table is the center of the star. Dimensions describe the event. Integer surrogate keys connect dimensions to facts, while source business IDs remain available for tracing records. One-to-many relationships let one dimension member filter many order lines. Foreign-key checks help catch orphaned records.

Why a star schema? It is easier to understand, query, and use in a BI model than one large repeated flat table. It also gives a clear place for reusable descriptions and calendar attributes.

## 7. Power BI report and model

The project is stored as a **Power BI Project (PBIP)**: a text-based report definition plus a semantic model definition. This makes the report structure inspectable and versionable. It is not the same as a binary `.pbix` file. Power BI Desktop opens the `.pbip`; the user can save/export a `.pbix` there if needed. GitHub can show the screenshot and source files, but does not host an interactive Power BI report by itself.

The model has one order-line fact table and customer, date, geography, product, and ship-mode dimensions. Dimension filters flow to the fact table. The date dimension is related to the fact's order date and must be typed as Date, marked as the date table, and sorted with its sort columns. The generated query explicitly sets the date type to avoid the month visual issue encountered during setup.

The one-page report includes a title, four KPI cards, month profit trend, profit by sub-category, quantity by category and ship mode, sales by state, top customers, quarter and state slicers, and a city map. The layout adapts the visual structure of the reference dashboard to this dataset.

### Field substitutions and honest descriptions

- The reference uses Payment Mode. This dataset has **Ship Mode**, so the report uses Ship Mode in that comparison slot. They are different concepts; do not call Ship Mode a payment method.
- The city map plots city locations with **Orders as bubble size** in the generated report. It is a geographic view, not proof of sales concentration by itself. The reference's map title/metric may differ; explain the actual plotted field shown by the report.
- A month chart must use a real date or chronologically sorted year-month field. Alphabetical month sorting gives an incorrect timeline.
- The map depends on Power BI geocoding and map settings. If it locates a city incorrectly, use a state/city bar chart or matrix instead.

### Main measures

- **Total Sales** = sum of line sales.
- **Total Profit** = sum of line profit.
- **Total Quantity** = sum of quantity.
- **Orders** = distinct count of order IDs.
- **Customers** = distinct count of customer IDs.
- **Average Order Value** = total sales / distinct orders.
- **Profit Margin** = total profit / total sales.
- **Sales per Customer** = total sales / distinct customers.
- **Sales YoY / Profit YoY** compare the current date context with the same period in the previous year.
- **Loss Making Lines** counts lines with profit below zero; **Loss Line %** divides that count by line count.

Margin should be calculated from aggregated profit and sales, not by averaging row-level percentages. Averages and distinct counts are non-additive: for example, adding monthly average order values does not produce annual AOV.

## 8. Results and what they mean

- **Overall:** $2.297M sales, $286.397K profit, 12.47% margin, 5,009 orders, and $458.61 AOV.
- **Category margin:** Technology has $836,154.02 sales and $145,455.44 profit (17.40% margin); Office Supplies has $719,046.90 sales and $122,490.00 profit (17.04%); Furniture has $741,999.73 sales but only $18,451.10 profit (2.49%). Furniture is a useful example of why revenue alone is not enough.
- **Sub-categories:** Copiers, Phones, and Accessories have the highest total profits in this extract. Tables, Bookcases, and Supplies have negative aggregate profit. This suggests where to investigate price, discount, cost, and product mix; it does not explain the cause by itself.
- **Region:** West has the highest sales ($725,457.76) and profit ($108,418.31) among the four regions in the supplied data.
- **Segment:** Consumer is the largest segment by sales ($1,161,401.12), but segment size alone does not establish customer value or future growth.
- **Discount association:** The >20–50% and >50% discount bands have negative aggregate profit in this extract, while the 0% band has positive aggregate profit. This is an association, not proof that discounts caused a loss. Product mix, order size, and other factors may differ across discount bands.
- **Shipping:** `ship_days` measures time from order to ship, not delivery to the customer. Standard Class has the most lines and a longer average order-to-ship interval than faster modes, as expected from the service level.

These are descriptive findings from this dataset. They are not a causal experiment or a forecast.

## 9. Limitations to say clearly

1. The source is Sample Superstore order data, not a real e-commerce clickstream or production company's current sales.
2. It contains no payment method, returns, delivery date, marketing cost, website sessions, inventory, or acquisition data.
3. It cannot support conversion rate, return rate, customer acquisition cost (CAC), lifetime value (LTV), or delivery-time claims.
4. Discount-profit patterns are descriptive associations, not causal conclusions.
5. The map depends on geocoding and should be checked for placement accuracy.
6. A screenshot in GitHub is a preview only. An interactive hosted report requires Power BI Service or another hosting option; Power BI Desktop and GitHub alone do not provide that public interactive link.
7. The project includes a PBIP definition; do not claim a `.pbix` was committed unless the file exists in the repository.

## 10. A 90-second interview explanation

> I built a reproducible sales and customer analysis project using the Sample Superstore order-line dataset. I used Python to profile and clean the data, standardize columns and types, derive calendar and shipping fields, and validate the records while retaining all 9,994 source rows. I produced an Excel workbook for review and loaded the cleaned data into SQLite using a star schema with an order-line fact and customer, product, geography, shipping, and date dimensions. In Power BI, I built a dimensional model and measures for sales, profit, quantity, distinct orders, customers, average order value, and margin, then created a one-page report with KPIs, time trends, category and customer comparisons, slicers, and a city map. The data totals $2.297 million in sales and $286,397 in profit, a 12.47% margin. One key finding is that Furniture has sales similar to other categories but a much lower margin, so I would investigate its product mix, costs, and discounts. I also found that high-discount lines are associated with negative profit, but I would not call that causal without controlling for product and order differences. I am clear about the data limits: it is retail order data and does not contain payment, marketing, returns, or website behavior.

## 11. Interview questions and sample answers

Practice answering in your own words. The answers are a starting point; a good interview response explains the choice and its trade-off.

### Project overview

1. **What problem does this project solve?** — It gives a manager one consistent view of sales, profit, customers, products, geography, time, and shipping so they can spot patterns and investigate them.
2. **Why did you choose this project?** — It demonstrates the full analytics workflow: data preparation, validation, spreadsheet delivery, SQL modeling, BI measures, visualization, and communication.
3. **Who is the intended user?** — A sales or operations manager who needs to monitor performance and explore where revenue and profit come from.
4. **What is the most important business distinction?** — Sales and profit are different. Revenue can be high while margin or total profit is weak, as Furniture illustrates here.
5. **What is the grain of the data?** — One row is a product line on an order. One order can occupy multiple rows.
6. **How is this an e-commerce project if it lacks web data?** — The layout follows an e-commerce dashboard reference, but the actual source is Sample Superstore retail order data. I describe it as sales and customer analysis and do not claim clickstream analysis.
7. **What would you improve with more time?** — Add returns, cost detail, inventory, campaign spend, site sessions, and delivery dates if available; then build return, stock, CAC, conversion, and delivery metrics with appropriate definitions.

### Data preparation and quality

8. **What did you use Python for?** — Profiling, type conversion, standardization, derived columns, validation, and repeatable Excel/CSV output.
9. **Why keep the raw data unchanged?** — It preserves lineage and lets another analyst reproduce or audit the preparation.
10. **How did you handle missing values?** — I profiled missingness and did not invent values for missing postal codes. The validation output records the checks; all rows were retained.
11. **Why did you keep postal codes as text?** — Postal codes are identifiers, not quantities. Numeric conversion could remove leading zeroes or alter formatting.
12. **Why did you not delete invalid rows?** — Silent deletion hides data quality problems. I retain the source rows and use a validity flag so exceptions can be reviewed.
13. **What validation rules did you apply?** — Required fields, row/order identifiers, positive quantity, discount bounds, date order, and reconciled row counts/totals.
14. **How did you handle currency precision?** — Sales and profit are rounded to cents for consistent financial reporting; discount retains its numeric precision.
15. **What is `ship_days`?** — The number of days between order date and ship date. It is order-to-ship time, not customer delivery time.
16. **How did you ensure the workbook can be reproduced?** — The workbook is generated by the Python pipeline from the cleaned data, rather than treated as a manually maintained source.
17. **What encoding issue did you encounter?** — The source has special characters, so the reader uses the appropriate Windows-compatible encoding rather than assuming UTF-8.
18. **How would you handle a larger dataset?** — Profile first, use efficient column types and vectorized operations, process in chunks or a database when needed, and retain automated validation and reproducible outputs.

### Metrics and interpretation

19. **How do you calculate total sales?** — Sum `Sales` at line level in the current filter context.
20. **How do you count orders?** — Distinct count of `Order ID`; counting rows would overstate orders because orders can have multiple lines.
21. **How do you calculate average order value?** — Total sales divided by distinct orders. Here it is about $458.61.
22. **How do you calculate profit margin?** — Total profit divided by total sales, which is 12.47% overall. I do not average row-level margins.
23. **Why can average order value not be summed across months?** — It is a ratio. For a larger period, recalculate total sales divided by distinct orders in that full period.
24. **What is the difference between sales and profit?** — Sales are recorded revenue; profit is the supplied profit amount after the dataset's costs/discount effects. They answer different performance questions.
25. **What is a negative-profit line?** — An order line where the recorded profit is less than zero. There are 1,871 such lines in the supplied extract.
26. **Which category performs best by margin?** — Technology, at 17.40%, narrowly ahead of Office Supplies at 17.04%.
27. **Which category needs investigation?** — Furniture: approximately $742K sales but only $18.5K profit, about 2.49% margin.
28. **What is the discount finding?** — The higher discount bands show negative aggregate profit here. It is a signal to investigate, not proof discounts caused the losses.
29. **How would you test whether discounting causes lower profit?** — Compare similar products/orders, control for category, quantity, region, and time, and ideally use a controlled pricing experiment or causal design.
30. **What does the dataset say about customer lifetime value?** — It does not provide a defensible lifetime value measure. It has historical orders but no future behavior, margin forecast, retention horizon, or acquisition cost definition.
31. **Can you calculate return rate?** — No. There is no returns table or returned quantity/amount field.
32. **Can you calculate conversion rate or CAC?** — No. The source has no website sessions, campaign costs, or acquisition attribution.

### SQL and data modeling

33. **Why use a star schema?** — It separates measurable order-line events from descriptive dimensions, making analysis easier to understand and filter.
34. **What is the fact table?** — The order-line table. It contains sales, profit, quantity, discount, dates, and dimension keys.
35. **What are dimensions?** — Tables that describe facts, such as customer, product, geography, ship mode, and date.
36. **What is a surrogate key?** — A database-generated integer key used to identify a dimension row independently from the source business ID.
37. **Why retain the source customer/product IDs?** — They support traceability and joining back to the source, while surrogate keys provide stable model relationships.
38. **What relationship cardinality do you expect?** — One dimension row to many fact rows, such as one customer to many order lines.
39. **What is a foreign-key check for?** — It verifies that fact rows point to existing dimension members and catches orphaned keys.
40. **How would you query top customers?** — Group fact rows by customer, sum sales, sort descending, and limit to ten; use distinct order counts where the question is about orders.
41. **Why not use one wide table for everything?** — It repeats descriptive values and can make maintenance and filter behavior less clear. A star schema gives explicit reusable dimensions.
42. **How would you avoid double counting in SQL?** — Match each metric to its grain, use distinct IDs for orders/customers, and check joins do not multiply fact rows.

### Power BI and DAX

43. **What is a semantic model?** — The model layer containing tables, relationships, data types, and reusable calculations that report visuals use.
44. **What is a measure?** — A calculation evaluated in the current filter context, such as selected dates or states.
45. **What is the difference between a calculated column and a measure?** — A calculated column is computed for each row and stored in the model; a measure is calculated dynamically for the visual's current filters.
46. **Why create a date table?** — It provides complete calendar periods, sorting, time filtering, and reliable year-over-year calculations.
47. **Why must the date field have Date type?** — Time intelligence and chronological comparisons need actual date values. A text date can break relationships or sort incorrectly.
48. **Why mark the date table and set sort-by columns?** — Marking identifies the model calendar for time calculations; sort-by columns ensure month and year-month labels follow calendar order.
49. **What is filter context?** — The selections and grouping that constrain a measure, such as a state slicer, a year on the chart, or a category row.
50. **How does a star-schema relationship affect a visual?** — A selected dimension value filters related fact rows, so measures recalculate for that subset.
51. **Why is margin a measure rather than a precomputed average?** — The correct aggregate is total profit divided by total sales for the current context. Averaging row margins weights small and large lines incorrectly.
52. **How do year-over-year measures work?** — They compare a measure with its value for the corresponding period in the prior year using the date dimension; the first year may have no prior period.
53. **Why did the month chart initially show blank or wrong categories?** — The date dimension's date was typed as text, which prevented proper date relationship/time grouping. Setting it to Date and refreshing corrected the timeline.
54. **Why use Ship Mode instead of Payment Mode?** — Payment mode is not present in this dataset. Ship Mode is an available comparison, but it describes fulfillment service and must be labeled accurately.
55. **What does the map show?** — Cities as locations, with bubble size based on distinct orders in the generated report. Geocoding should be checked; the map does not prove why sales occurred.
56. **What is the PBIP file?** — The Power BI Project entry point, with report and model definitions stored as project files. It is editable in Desktop and more source-friendly than only storing a binary file.
57. **Can GitHub display the interactive report?** — GitHub can display a static preview and host project files, but an interactive Power BI report needs Power BI Service or another web host. A `.pbix` file alone is not an interactive GitHub page.
58. **How did you validate the report?** — The project has a validator for expected data totals, workbook/database outputs, model/report structure, and field references. I also refreshed the report in Power BI Desktop and checked that date/month visuals and slicers worked. Static checks alone do not guarantee every visual is correct.

### Findings, communication, and ownership

59. **What is your strongest insight?** — Furniture produces strong sales but a much lower margin than Technology and Office Supplies, so revenue alone would hide a profitability issue.
60. **What action would you recommend?** — Review Furniture sub-categories, discount levels, pricing, and cost assumptions, then validate with more detailed cost data before changing pricing.
61. **What would you say about the discount chart to a manager?** — Higher-discount lines have worse aggregate profit in this extract. I would treat that as a warning to investigate, not evidence that discounts alone caused the loss.
62. **How did you make the project reproducible?** — Keep the raw file, centralize repeatable work in scripts, document the steps, generate outputs, and provide SQL and Power BI model definitions.
63. **What was a technical issue you solved?** — The date dimension loaded with a text type, so the month visual was not behaving chronologically. I corrected the query/model date type and refreshed the report.
64. **What would you do if totals differ between Python, SQL, Excel, and Power BI?** — Check row counts and filters first, then data types, joins, date ranges, duplicate rows, and metric definitions; reconcile at the same grain and filter context.
65. **What is the biggest risk of this analysis?** — Treating descriptive associations as causal or presenting fields the data does not contain. I address that by defining the grain and metric limits clearly.
66. **How would you present this to an executive?** — Start with sales, profit, margin, and the biggest profitability difference; show the supporting breakdown and state one action plus the data needed to validate it.
67. **What would you add next?** — A second page for product/discount drill-down, a refreshable source connector, better map validation, and (if obtained) return, cost, marketing, and delivery data.
68. **What did you learn?** — A working dashboard depends on reliable grain, types, relationships, and measure definitions as much as on visual design; the most useful result is a defensible business question, not a decorative chart.

## 12. Study plan

1. Explain the project flow without looking at the diagram.
2. Memorize the grain, four headline totals, and the distinction between order rows and distinct orders.
3. Practice explaining why margin and average order value are ratios.
4. Open the report and explain every visual and slicer in one sentence.
5. Practice the 90-second pitch, then answer questions 5, 13, 21, 27, 29, 33, 47, 51, 53, 55, and 64 without reading.
6. Be direct about limitations. Honest boundaries make the analysis more credible.

For field-level definitions see [Data Dictionary](DATA_DICTIONARY.md), and for the report configuration see [Power BI build guide](POWER_BI.md).
