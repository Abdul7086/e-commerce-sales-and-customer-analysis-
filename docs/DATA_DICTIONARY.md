# Data dictionary

**Grain:** one row per product line on an order. `Row ID` is the source row identifier. The extract contains 9,994 lines, 5,009 orders, and 793 customers (recomputed by pipeline for the supplied file).

| Clean field | Source field | Meaning |
|---|---|---|
| row_id | Row ID | Unique source line identifier |
| order_id | Order ID | Order identifier; multiple lines can share it |
| order_date / ship_date | Order Date / Ship Date | Parsed calendar dates |
| ship_mode | Ship Mode | Service level selected |
| customer_id / customer_name | Customer ID / Customer Name | Customer key and display name |
| segment | Segment | Consumer, Corporate, or Home Office |
| country, city, state, postal_code, region | same | Order destination attributes; postal code is text and may be blank |
| product_id / product_name | Product ID / Product Name | Product key and display name |
| category / sub_category | Category / Sub-Category | Product hierarchy |
| sales | Sales | Line revenue in source currency (USD) |
| quantity | Quantity | Units on line |
| discount | Discount | Fractional discount (0.2 = 20%) |
| profit | Profit | Line profit in source currency (USD); can be negative |
| ship_days | derived | Calendar days from order to shipment |
| order_year, order_month, order_month_name, order_quarter | derived | Calendar attributes from order date |
| is_valid | derived | Passes core field, quantity, discount, and date-order checks |

The source file does not document tax, currency conversion, returns, or marketing attribution. Treat source dollars as USD based on the Sample Superstore convention.
