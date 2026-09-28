import sqlite3
import pandas as pd


# ============================================================
# CONNECT TO DATABASE
# ============================================================

conn = sqlite3.connect("store.db")


# ============================================================
# QUERY 1 - TOP 5 CUSTOMERS BY TOTAL SPENDING
# JOIN + GROUP BY + ORDER BY
# ============================================================

query1 = """
SELECT
    c.customer_id,
    c.customer_name,
    c.city,
    SUM(s.quantity * p.price) AS total_spending
FROM customers c
JOIN sales s
    ON c.customer_id = s.customer_id
JOIN products p
    ON s.product_id = p.product_id
GROUP BY
    c.customer_id,
    c.customer_name,
    c.city
ORDER BY total_spending DESC
LIMIT 5
"""

top5_customers_df = pd.read_sql_query(query1, conn)


# ============================================================
# QUERY 2 - CUSTOMERS WITHOUT PURCHASES
# LEFT JOIN + IS NULL
# ============================================================

query2 = """
SELECT
    c.customer_id,
    c.customer_name,
    c.city,
    c.signup_date
FROM customers c
LEFT JOIN sales s
    ON c.customer_id = s.customer_id
WHERE s.sale_id IS NULL
ORDER BY c.customer_id
"""

customers_without_purchases_df = pd.read_sql_query(query2, conn)


# ============================================================
# QUERY 3 - CUSTOMER AVERAGE VS OVERALL AVERAGE
# SUBQUERY
# ============================================================

query3 = """
SELECT
    c.customer_id,
    c.customer_name,
    AVG(s.quantity * p.price) AS customer_average_purchase,

    (
        SELECT AVG(s2.quantity * p2.price)
        FROM sales s2
        JOIN products p2
            ON s2.product_id = p2.product_id
    ) AS overall_average_purchase

FROM customers c

JOIN sales s
    ON c.customer_id = s.customer_id

JOIN products p
    ON s.product_id = p.product_id

GROUP BY
    c.customer_id,
    c.customer_name

ORDER BY customer_average_purchase DESC
"""

customer_average_df = pd.read_sql_query(query3, conn)


# ============================================================
# QUERY 4 - CUSTOMER RANK WITHIN EACH CITY
# WINDOW FUNCTION
# ============================================================

query4 = """
WITH customer_city_spending AS (

    SELECT
        c.customer_id,
        c.customer_name,
        c.city,
        SUM(s.quantity * p.price) AS total_spending

    FROM customers c

    JOIN sales s
        ON c.customer_id = s.customer_id

    JOIN products p
        ON s.product_id = p.product_id

    GROUP BY
        c.customer_id,
        c.customer_name,
        c.city
)

SELECT
    customer_id,
    customer_name,
    city,
    total_spending,

    RANK() OVER (
        PARTITION BY city
        ORDER BY total_spending DESC
    ) AS city_rank

FROM customer_city_spending

ORDER BY city, city_rank
"""

customer_city_rank_df = pd.read_sql_query(query4, conn)


# ============================================================
# QUERY 5 - MONTHLY REVENUE
# GROUP BY + STRFTIME
# ============================================================

query5 = """
SELECT
    strftime('%Y-%m', s.sale_date) AS month,
    SUM(s.quantity * p.price) AS total_revenue
FROM sales s
JOIN products p
    ON s.product_id = p.product_id
GROUP BY month
ORDER BY month
"""

monthly_revenue_df = pd.read_sql_query(query5, conn)


# ============================================================
# QUERY 6 - REVENUE BY CATEGORY
# GROUP BY
# ============================================================

query6 = """
SELECT
    CASE
        WHEN p.product_name = 'Laptop'
            THEN 'Computers'

        WHEN p.product_name IN
            ('Mouse', 'Keyboard', 'Headphones', 'Webcam', 'USB Cable')
            THEN 'Accessories'

        WHEN p.product_name IN
            ('Monitor', 'Printer')
            THEN 'Office Equipment'

        ELSE 'Other'
    END AS category,

    SUM(s.quantity * p.price) AS total_revenue

FROM sales s

JOIN products p
    ON s.product_id = p.product_id

GROUP BY category
ORDER BY total_revenue DESC
"""

category_revenue_df = pd.read_sql_query(query6, conn)


# ============================================================
# QUERY 7 - SIGNUP DATE VS TOTAL SPENDING
# JOIN + GROUP BY
# ============================================================

query7 = """
SELECT
    c.customer_id,
    c.customer_name,
    c.signup_date,
    COALESCE(
        SUM(s.quantity * p.price),
        0
    ) AS total_spending

FROM customers c

LEFT JOIN sales s
    ON c.customer_id = s.customer_id

LEFT JOIN products p
    ON s.product_id = p.product_id

GROUP BY
    c.customer_id,
    c.customer_name,
    c.signup_date

ORDER BY c.signup_date
"""

signup_spending_df = pd.read_sql_query(query7, conn)


# ============================================================
# QUERY 8 - REPEAT CUSTOMER ANALYSIS
# GROUP BY + HAVING
# ============================================================

query8 = """
WITH customer_purchase_counts AS (

    SELECT
        c.customer_id,
        c.customer_name,
        COUNT(s.sale_id) AS purchase_count

    FROM customers c

    LEFT JOIN sales s
        ON c.customer_id = s.customer_id

    GROUP BY
        c.customer_id,
        c.customer_name
)

SELECT
    COUNT(*) AS total_customers,

    SUM(
        CASE
            WHEN purchase_count > 1 THEN 1
            ELSE 0
        END
    ) AS repeat_customers,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN purchase_count > 1 THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS repeat_customer_percentage

FROM customer_purchase_counts
"""

repeat_customer_df = pd.read_sql_query(query8, conn)


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n" + "=" * 70)
print("1. TOP 5 CUSTOMERS BY TOTAL SPENDING")
print("=" * 70)
print(top5_customers_df)


print("\n" + "=" * 70)
print("2. CUSTOMERS WITHOUT PURCHASES")
print("=" * 70)
print(customers_without_purchases_df)


print("\n" + "=" * 70)
print("3. CUSTOMER AVERAGE VS OVERALL AVERAGE")
print("=" * 70)
print(customer_average_df)


print("\n" + "=" * 70)
print("4. CUSTOMER RANK WITHIN EACH CITY")
print("=" * 70)
print(customer_city_rank_df)


print("\n" + "=" * 70)
print("5. MONTHLY REVENUE")
print("=" * 70)
print(monthly_revenue_df)


print("\n" + "=" * 70)
print("6. REVENUE BY CATEGORY")
print("=" * 70)
print(category_revenue_df)


print("\n" + "=" * 70)
print("7. SIGNUP DATE VS TOTAL SPENDING")
print("=" * 70)
print(signup_spending_df)


print("\n" + "=" * 70)
print("8. REPEAT CUSTOMER ANALYSIS")
print("=" * 70)
print(repeat_customer_df)


# ============================================================
# CLOSE DATABASE
# ============================================================

conn.close()

print("\n" + "=" * 70)
print("8 ANALYTICAL QUERIES COMPLETED SUCCESSFULLY!")
print("=" * 70)