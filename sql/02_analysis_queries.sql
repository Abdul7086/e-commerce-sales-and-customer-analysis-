-- Sales and profit trend by month
SELECT substr(order_date,1,7) AS order_month, ROUND(SUM(sales),2) AS sales,
       ROUND(SUM(profit),2) AS profit, COUNT(DISTINCT order_id) AS orders
FROM fact_order_line GROUP BY 1 ORDER BY 1;

-- Category and subcategory performance
SELECT p.category, p.sub_category, ROUND(SUM(f.sales),2) sales,
       ROUND(SUM(f.profit),2) profit,
       ROUND(100.0*SUM(f.profit)/NULLIF(SUM(f.sales),0),2) profit_margin_pct
FROM fact_order_line f JOIN dim_product p USING(product_key)
GROUP BY 1,2 ORDER BY profit DESC;

-- Discount bands: expose the relationship between discounting and profitability
SELECT CASE WHEN discount=0 THEN '0%'
            WHEN discount<=0.2 THEN '>0% to 20%'
            WHEN discount<=0.5 THEN '>20% to 50%'
            ELSE '>50%' END AS discount_band,
       COUNT(*) AS order_lines, ROUND(AVG(profit),2) avg_line_profit,
       ROUND(SUM(sales),2) sales, ROUND(SUM(profit),2) profit
FROM fact_order_line GROUP BY 1 ORDER BY MIN(discount);

-- Customer value ranking
SELECT c.customer_id, c.customer_name, COUNT(DISTINCT f.order_id) orders,
       ROUND(SUM(f.sales),2) sales, ROUND(SUM(f.profit),2) profit
FROM fact_order_line f JOIN dim_customer c USING(customer_key)
GROUP BY 1,2 ORDER BY sales DESC LIMIT 20;

-- Regional performance, including loss-making state/category combinations
SELECT g.region, g.state, p.category, ROUND(SUM(f.sales),2) sales,
       ROUND(SUM(f.profit),2) profit
FROM fact_order_line f JOIN dim_geography g USING(geography_key)
JOIN dim_product p USING(product_key) GROUP BY 1,2,3 ORDER BY profit ASC;
