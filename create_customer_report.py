import sqlite3
import pandas as pd


# ============================================================
# CONNECT TO DATABASE
# ============================================================

conn = sqlite3.connect("store.db")


# ============================================================
# QUERY 1 - TOP 5 CUSTOMERS
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
GROUP BY c.customer_id, c.customer_name, c.city
ORDER BY total_spending DESC
LIMIT 5
"""

top5_df = pd.read_sql_query(query1, conn)


# ============================================================
# QUERY 2 - CUSTOMERS WITHOUT PURCHASES
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

no_purchase_df = pd.read_sql_query(query2, conn)


# ============================================================
# QUERY 3 - CUSTOMER AVERAGE VS OVERALL AVERAGE
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

GROUP BY c.customer_id, c.customer_name
ORDER BY customer_average_purchase DESC
"""

customer_average_df = pd.read_sql_query(query3, conn)


# ============================================================
# QUERY 4 - CITY RANKING
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

city_ranking_df = pd.read_sql_query(query4, conn)


# ============================================================
# QUERY 5 - MONTHLY REVENUE
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
# QUERY 6 - CATEGORY REVENUE
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
# QUERY 7 - SIGNUP DATE VS SPENDING
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
# QUERY 8 - REPEAT CUSTOMERS
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
# SUMMARY
# ============================================================

total_customers = repeat_customer_df.loc[
    0, "total_customers"
]

repeat_customers = repeat_customer_df.loc[
    0, "repeat_customers"
]

repeat_percentage = repeat_customer_df.loc[
    0, "repeat_customer_percentage"
]

total_revenue = monthly_revenue_df["total_revenue"].sum()

top_customer = top5_df.iloc[0]

top_category = category_revenue_df.iloc[0]

summary_df = pd.DataFrame({
    "Metric": [
        "Total Customers",
        "Total Sales Transactions",
        "Total Revenue",
        "Top Customer",
        "Top Customer Spending",
        "Top Product Category",
        "Top Category Revenue",
        "Repeat Customers",
        "Repeat Customer Percentage",
        "Customers Without Purchases"
    ],

    "Value": [
        total_customers,
        30,
        total_revenue,
        top_customer["customer_name"],
        top_customer["total_spending"],
        top_category["category"],
        top_category["total_revenue"],
        repeat_customers,
        repeat_percentage,
        len(no_purchase_df)
    ]
})


# ============================================================
# EXPORT TO EXCEL
# ============================================================

with pd.ExcelWriter(
    "customer_analysis_report.xlsx",
    engine="openpyxl"
) as writer:

    summary_df.to_excel(
        writer,
        sheet_name="Summary",
        index=False
    )

    top5_df.to_excel(
        writer,
        sheet_name="Top 5 Customers",
        index=False
    )

    no_purchase_df.to_excel(
        writer,
        sheet_name="No Purchases",
        index=False
    )

    customer_average_df.to_excel(
        writer,
        sheet_name="Customer Average",
        index=False
    )

    city_ranking_df.to_excel(
        writer,
        sheet_name="City Ranking",
        index=False
    )

    monthly_revenue_df.to_excel(
        writer,
        sheet_name="Monthly Revenue",
        index=False
    )

    category_revenue_df.to_excel(
        writer,
        sheet_name="Category Revenue",
        index=False
    )

    signup_spending_df.to_excel(
        writer,
        sheet_name="Signup Spending",
        index=False
    )

    repeat_customer_df.to_excel(
        writer,
        sheet_name="Repeat Customers",
        index=False
    )


# ============================================================
# CLOSE DATABASE
# ============================================================

conn.close()


print("\n" + "=" * 60)
print("EXCEL REPORT CREATED SUCCESSFULLY!")
print("=" * 60)
print("File: customer_analysis_report.xlsx")
print("Sheets created: 9")