import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


# ============================================================
# CONNECT TO DATABASE
# ============================================================

conn = sqlite3.connect("store.db")


# ============================================================
# 1. MONTHLY REVENUE
# ============================================================

monthly_revenue = pd.read_sql_query("""
SELECT
    strftime('%Y-%m', s.sale_date) AS month,
    SUM(s.quantity * p.price) AS total_revenue
FROM sales s
JOIN products p
    ON s.product_id = p.product_id
GROUP BY month
ORDER BY month
""", conn)


# ============================================================
# 2. CUSTOMER SPENDING
# ============================================================

customer_spending = pd.read_sql_query("""
SELECT
    c.customer_name,
    SUM(s.quantity * p.price) AS total_spending
FROM customers c
JOIN sales s
    ON c.customer_id = s.customer_id
JOIN products p
    ON s.product_id = p.product_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_spending DESC
""", conn)


# ============================================================
# 3. REVENUE BY CATEGORY
# ============================================================

category_revenue = pd.read_sql_query("""
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
""", conn)


# ============================================================
# 4. CUSTOMER SPENDING BY CITY
# ============================================================

city_customer_spending = pd.read_sql_query("""
SELECT
    c.city,
    c.customer_name,
    SUM(s.quantity * p.price) AS total_spending
FROM customers c
JOIN sales s
    ON c.customer_id = s.customer_id
JOIN products p
    ON s.product_id = p.product_id
GROUP BY c.city, c.customer_id, c.customer_name
ORDER BY c.city, total_spending DESC
""", conn)


conn.close()


# ============================================================
# GRAPH 1 - MONTHLY REVENUE
# MATPLOTLIB
# ============================================================

plt.figure(figsize=(10, 5))

plt.plot(
    monthly_revenue["month"],
    monthly_revenue["total_revenue"],
    marker="o"
)

plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig("customer_monthly_revenue.png")
plt.show()


# ============================================================
# GRAPH 2 - TOP CUSTOMERS
# SEABORN
# ============================================================

top_customers = customer_spending.head(10)

plt.figure(figsize=(10, 6))

sns.barplot(
    data=top_customers,
    x="total_spending",
    y="customer_name"
)

plt.title("Top Customers by Total Spending")
plt.xlabel("Total Spending")
plt.ylabel("Customer")

plt.tight_layout()

plt.savefig("top_customers.png")
plt.show()


# ============================================================
# GRAPH 3 - CATEGORY REVENUE
# MATPLOTLIB
# ============================================================

plt.figure(figsize=(8, 5))

plt.bar(
    category_revenue["category"],
    category_revenue["total_revenue"]
)

plt.title("Revenue by Product Category")
plt.xlabel("Category")
plt.ylabel("Revenue")

plt.xticks(rotation=20)
plt.tight_layout()

plt.savefig("category_revenue.png")
plt.show()


# ============================================================
# GRAPH 4 - CUSTOMER SPENDING BY CITY
# PLOTLY INTERACTIVE
# ============================================================

fig = px.bar(
    city_customer_spending,
    x="customer_name",
    y="total_spending",
    color="city",
    title="Customer Spending by City",
    labels={
        "customer_name": "Customer",
        "total_spending": "Total Spending"
    }
)

fig.update_layout(
    xaxis_tickangle=-45
)

fig.write_html("customer_spending_by_city.html")

fig.show()


print("\n" + "=" * 60)
print("4 VISUALIZATIONS CREATED SUCCESSFULLY!")
print("=" * 60)

print("1. customer_monthly_revenue.png")
print("2. top_customers.png")
print("3. category_revenue.png")
print("4. customer_spending_by_city.html")