"""15 - Grid Layout with Cards

Uses ww.grid("1fr 1fr 1fr") to arrange cards in a CSS Grid.
The template string maps directly to grid-template-columns, so
"1fr 1fr 1fr" gives three equal-width columns.

Concepts: ww.grid(), ww.card(), ww.metric(), ww.chart(),
          CSS Grid via grid-template-columns.

Run: python examples/15_grid_layout.py
"""

import webwrench as ww

ww.theme("ocean")

# -- Header --
ww.title("Grid Layout")
ww.text(
    "ww.grid('1fr 1fr 1fr') creates a CSS Grid container with three "
    "equal-width columns. The string maps directly to the CSS "
    "grid-template-columns property. Cards placed inside flow left-to-right, "
    "wrapping to the next row automatically."
)
ww.code('with ww.grid("1fr 1fr 1fr"):', lang="python")

ww.divider()

# -- 3-column grid --
ww.heading("Business Dashboard", level=2)

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
