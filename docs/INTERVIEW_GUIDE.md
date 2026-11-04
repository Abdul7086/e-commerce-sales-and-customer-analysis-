# Interview walkthrough

## 90-second story

“I built a reproducible analytics workflow from order-line source data through profiling, typed cleaning, validation, Excel review, SQL analysis, and a Power BI star schema. I kept the fact table at line grain and modeled customer, product, geography, shipping mode, and date as dimensions. The report helps a business user see where revenue growth is profitable, where discounts erode margin, and which product and regional combinations need attention. Every KPI is defined at the right grain: distinct orders for order count and total profit divided by total sales for margin.”

## Findings to compute and present after refresh

Use the refreshed workbook/report to state exact numbers; do not memorize figures from a different Superstore extract. Focus on the strongest profitable category/subcategory, the largest loss-making combinations, the discount/profit relationship, best region/segment, and order-to-ship differences. Explain one limitation for each observation and distinguish correlation from causation.

## Likely follow-up questions

- **Why a star schema?** It keeps dimensions reusable, filters predictable, and measures easier to validate.
- **Why count distinct orders?** Each order has multiple product lines; counting rows inflates order volume.
- **Why calculate margin from totals?** Averaging line-level margins gives tiny orders the same weight as large orders.
- **How did you clean the data?** Typed dates and numerics, preserved postal IDs as text, standardized field names, derived calendar and ship-lag fields, and flagged invalid records without silently dropping them.
- **What would you do next?** Add returns, budget, inventory, delivery date, campaign/session, and cost data; then validate the measures with business owners and monitor refresh quality.

## Honest limitations

This is the classic Sample Superstore teaching dataset, not production transaction data. It has a short four-year window and no delivery date, customer acquisition, return, inventory, or advertising measures. It supports descriptive analysis, not causal claims or a full customer lifetime value calculation.
