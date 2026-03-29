"""03 - Multiple Chart Types

Displays bar, line, and pie charts side by side using a column layout.
Each chart uses the same underlying data presented in a different format.

Run: python examples/03_multi_chart.py
"""

import webwrench as ww

ww.theme("ocean")

# ── Header ──
ww.title("Quarterly Revenue Dashboard")
ww.text(
    "Acme Corp FY-2026 revenue across four quarters, visualised as bar, "
    "line, and pie charts.  All three views share the same underlying dataset "
    "so you can compare how each chart type highlights different patterns."
)

ww.divider()

# ── KPI row ──
labels = ["Q1", "Q2", "Q3", "Q4"]
revenue = [48, 62, 55, 71]

total = sum(revenue)
best_q = labels[revenue.index(max(revenue))]
growth = round((revenue[-1] - revenue[0]) / revenue[0] * 100, 1)

metrics = ww.columns(3)
with metrics[0]:
    ww.metric("Total Revenue", f"${total}M")
with metrics[1]:
    ww.metric("Best Quarter", best_q, delta=f"${max(revenue)}M")
with metrics[2]:
    ww.metric("Q1 to Q4 Growth", f"{growth}%", delta=f"+${revenue[-1] - revenue[0]}M")

ww.divider()

# ── Charts ──
ww.heading("Revenue by Chart Type", level=2)
ww.text(
    "Bar charts compare absolute values, line charts reveal trends over time, "
    "and pie charts show each quarter's share of the total."
)

cols = ww.columns(3)

with cols[0]:
    with ww.card(title="Bar Chart"):
        ww.chart(revenue, type="bar", labels=labels, title="Quarterly Revenue")

with cols[1]:
    with ww.card(title="Line Chart"):
        ww.chart(revenue, type="line", labels=labels, title="Revenue Trend")

with cols[2]:
    with ww.card(title="Pie Chart"):
        ww.chart(revenue, type="pie", labels=labels, title="Revenue Share")

ww.divider()

# ── Data table ──
ww.heading("Raw Data", level=2)
ww.text("The underlying numbers behind the charts above.")
ww.table([
    {"Quarter": q, "Revenue ($M)": r, "Share": f"{round(r / total * 100, 1)}%"}
    for q, r in zip(labels, revenue)
])

if __name__ == "__main__":
    ww.serve()
