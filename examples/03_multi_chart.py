"""03 - Multiple Chart Types

Displays bar, line, and pie charts side by side using a column layout.
Each chart uses the same underlying data presented in a different format.

Run: python examples/03_multi_chart.py
"""

import webwrench as ww

ww.title("Multi-Chart Overview")
ww.text("The same quarterly revenue data shown in three different chart types.")

labels = ["Q1", "Q2", "Q3", "Q4"]
revenue = [48, 62, 55, 71]

cols = ww.columns(3)

with cols[0]:
    ww.heading("Bar Chart", level=3)
    ww.chart(revenue, type="bar", labels=labels, title="Quarterly Revenue (Bar)")

with cols[1]:
    ww.heading("Line Chart", level=3)
    ww.chart(revenue, type="line", labels=labels, title="Quarterly Revenue (Line)")

with cols[2]:
    ww.heading("Pie Chart", level=3)
    ww.chart(revenue, type="pie", labels=labels, title="Revenue Distribution")

if __name__ == "__main__":
    ww.serve()
