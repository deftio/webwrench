"""04 - Dashboard Layout

A structured dashboard with KPI metrics across the top, a chart and table
arranged in columns below. Demonstrates metrics, charts, tables, and
the column layout system working together.

Run: python examples/04_dashboard.py
"""

import webwrench as ww

ww.title("Company Dashboard")

# -- KPI row --
kpi_cols = ww.columns(4)

with kpi_cols[0]:
    ww.metric("Revenue", "$1.2M", delta="+12%", delta_color="green")

with kpi_cols[1]:
    ww.metric("Users", "8,420", delta="+340", delta_color="green")

with kpi_cols[2]:
    ww.metric("Churn", "2.4%", delta="-0.3%", delta_color="green")

with kpi_cols[3]:
    ww.metric("NPS", "72", delta="-2", delta_color="red")

ww.divider()

# -- Chart + table row --
body_cols = ww.columns([2, 1])

with body_cols[0]:
    ww.heading("Monthly Revenue", level=3)
    ww.chart(
        [65, 59, 80, 81, 56, 55, 72, 88, 91, 76, 85, 101],
        type="line",
        labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        title="Revenue Trend ($k)",
    )

with body_cols[1]:
    ww.heading("Top Customers", level=3)
    ww.table([
        {"Customer": "Acme Corp", "Revenue": "$180k", "Growth": "+15%"},
        {"Customer": "Globex Inc", "Revenue": "$145k", "Growth": "+8%"},
        {"Customer": "Initech", "Revenue": "$132k", "Growth": "+22%"},
        {"Customer": "Umbrella", "Revenue": "$98k", "Growth": "-3%"},
        {"Customer": "Wonka Ltd", "Revenue": "$87k", "Growth": "+11%"},
    ])

if __name__ == "__main__":
    ww.serve()
