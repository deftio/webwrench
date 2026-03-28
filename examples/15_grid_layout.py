"""15 - Grid Layout with Cards

Uses ww.grid() and ww.card() to arrange content in a CSS Grid.
Each card contains a metric, a small chart, or descriptive text.

Run: python examples/15_grid_layout.py
"""

import webwrench as ww

ww.title("Grid Layout with Cards")
ww.text("A responsive grid of cards showing key business metrics and charts.")

with ww.grid("1fr 1fr 1fr"):

    with ww.card("Total Revenue"):
        ww.metric("Revenue", "$2.4M", delta="+14%", delta_color="green")

    with ww.card("Active Users"):
        ww.metric("Users", "18,302", delta="+1,203", delta_color="green")

    with ww.card("Uptime"):
        ww.metric("Availability", "99.97%", delta="+0.02%", delta_color="green")

    with ww.card("Sales Trend"):
        ww.chart(
            [22, 30, 28, 35, 40, 38],
            type="line",
            labels=["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            title="Monthly Sales ($k)",
        )

    with ww.card("Support Tickets"):
        ww.chart(
            [45, 38, 52, 30, 25, 20],
            type="bar",
            labels=["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            title="Open Tickets",
        )

    with ww.card("Customer Satisfaction"):
        ww.chart(
            [72, 18, 10],
            type="doughnut",
            labels=["Satisfied", "Neutral", "Unsatisfied"],
            title="CSAT Breakdown",
        )

if __name__ == "__main__":
    ww.serve()
