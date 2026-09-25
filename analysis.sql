SELECT ROUND(SUM(total_amount), 2) AS total_revenue
FROM sales;


SELECT COUNT(*) AS total_orders
FROM sales;


SELECT ROUND(AVG(total_amount), 2) AS average_order_value
FROM sales;


SELECT product, SUM(quantity) AS total_units_sold
FROM sales
GROUP BY product
ORDER BY total_units_sold DESC
LIMIT 1;


SELECT category, ROUND(SUM(total_amount), 2) AS category_revenue
FROM sales
GROUP BY category
ORDER BY category_revenue DESC
LIMIT 1;


SELECT
    substr(order_date, 1, 7) AS year_month,
    ROUND(SUM(total_amount), 2) AS monthly_revenue
FROM sales
GROUP BY year_month
ORDER BY year_month;
