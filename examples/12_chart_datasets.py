"""12 - Chart with Multiple Datasets

Uses the datasets parameter to overlay multiple data series on a
single chart. Demonstrates a line chart comparing revenue across
three product lines over six months.

Run: python examples/12_chart_datasets.py
"""

import webwrench as ww

ww.title("Multi-Dataset Chart")
ww.text("Revenue comparison across three product lines over six months.")

ww.chart(
    datasets=[
        {"label": "Enterprise Suite", "data": [42, 49, 55, 60, 58, 72], "color": "#3366cc"},
        {"label": "Developer Tools", "data": [28, 32, 38, 45, 50, 61], "color": "#dc3912"},
        {"label": "Cloud Storage", "data": [15, 18, 20, 22, 25, 30], "color": "#109618"},
    ],
    type="line",
    labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    title="Revenue by Product Line ($k)",
)

ww.divider()

ww.heading("Stacked Bar Comparison", level=2)
ww.text("The same data shown as a bar chart.")

ww.chart(
    datasets=[
        {"label": "Enterprise Suite", "data": [42, 49, 55, 60, 58, 72], "color": "#3366cc"},
        {"label": "Developer Tools", "data": [28, 32, 38, 45, 50, 61], "color": "#dc3912"},
        {"label": "Cloud Storage", "data": [15, 18, 20, 22, 25, 30], "color": "#109618"},
    ],
    type="bar",
    labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    title="Revenue by Product Line ($k)",
)

if __name__ == "__main__":
    ww.serve()
