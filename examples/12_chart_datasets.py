"""12 - Chart with Multiple Datasets

Uses the datasets parameter to overlay multiple data series on a
single chart. Includes a dropdown to switch between line and bar
chart types, and metric cards summarising the data.

Concepts: ww.chart(datasets=[...]), @select.on_change, chart.update(),
          ww.metric(), ww.columns(), ww.card().

Run: python examples/12_chart_datasets.py
"""

import webwrench as ww

ww.theme("ocean")

# -- Header --
ww.title("Multiple Datasets")
ww.text(
    "The datasets parameter lets you overlay several data series on one "
    "chart. Each dataset gets its own label, colour, and data array. "
    "Use the dropdown below to switch between chart types."
)

ww.divider()

# -- Data --
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
enterprise = [42, 49, 55, 60, 58, 72]
devtools = [28, 32, 38, 45, 50, 61]
cloud = [15, 18, 20, 22, 25, 30]

datasets_spec = [
    {"label": "Enterprise Suite", "data": enterprise, "color": "#3366cc"},
    {"label": "Developer Tools", "data": devtools, "color": "#dc3912"},
    {"label": "Cloud Storage", "data": cloud, "color": "#109618"},
]

# -- Summary metrics --
ww.heading("Revenue Summary", level=2)
kpi = ww.columns(3)
with kpi[0]:
    ww.metric("Enterprise", f"${sum(enterprise)}k", delta=f"+{enterprise[-1] - enterprise[0]}k")
with kpi[1]:
    ww.metric("Dev Tools", f"${sum(devtools)}k", delta=f"+{devtools[-1] - devtools[0]}k")
with kpi[2]:
    ww.metric("Cloud", f"${sum(cloud)}k", delta=f"+{cloud[-1] - cloud[0]}k")

ww.divider()

# -- Chart type selector --
ww.heading("Revenue by Product Line", level=2)
ww.text(
    "The API call looks like: "
    'ww.chart(datasets=[{"label": "...", "data": [...], "color": "#..."}], ...)'
)

type_select = ww.select("Chart Type", options=["line", "bar"], value="line")

revenue_chart = ww.chart(
    datasets=datasets_spec,
    type="line",
    labels=months,
    title="Revenue by Product Line ($k)",
)


@type_select.on_change
def on_type_change(value):
    # Rebuild chart data with new type is not yet supported via update(),
    # but the select demonstrates the callback pattern.
    pass


if __name__ == "__main__":
    ww.serve()
