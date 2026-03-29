"""07 - Theming

Dynamic theme switching between light, dark, ocean, and forest presets.
Selecting a theme from the dropdown calls ww.theme() inside a callback,
which sends a bw.loadStyles() message over SSE so the browser restyles
every element immediately.

Concepts: ww.theme(), @select.on_change, ww.card(), ww.metric(),
          ww.chart(), ww.table(), ww.columns().

Run: python examples/07_theming.py
"""

import webwrench as ww

# -- Start with ocean theme --
ww.theme("ocean")

# -- Header --
ww.title("Theme Gallery")
ww.text(
    "Pick a preset from the dropdown to restyle the entire page. "
    "Every colour -- headings, cards, charts, tables, inputs -- updates "
    "in one call via bitwrench's loadStyles()."
)

ww.divider()

# -- Theme selector --
ww.heading("Choose a Theme", level=2)
ww.text(
    "The @theme_select.on_change callback calls ww.theme(value), which "
    "sets CSS custom properties (--bw-primary, --bw-background, etc.) and "
    "pushes them to the browser over SSE."
)
theme_select = ww.select(
    "Theme Preset",
    options=["ocean", "light", "dark", "forest"],
    value="ocean",
)


@theme_select.on_change
def on_theme_change(value):
    ww.theme(value)


ww.divider()

# -- Sample content --
ww.heading("Sample Components", level=2)
ww.text("The cards, metrics, chart, and table below let you judge each theme at a glance.")

# Metrics row
kpi = ww.columns(3)
with kpi[0]:
    ww.metric("Users", "12,482", delta="+8.3%", delta_color="green")
with kpi[1]:
    ww.metric("Revenue", "$1.24M", delta="+14%", delta_color="green")
with kpi[2]:
    ww.metric("Churn", "2.1%", delta="-0.4%", delta_color="green")

# Cards with charts
row = ww.columns(2)
with row[0]:
    with ww.card(title="Weekly Activity"):
        ww.chart(
            [28, 48, 40, 19, 86, 27, 63],
            type="bar",
            labels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            title="Commits per Day",
        )
with row[1]:
    with ww.card(title="Traffic Sources"):
        ww.chart(
            [45, 25, 20, 10],
            type="pie",
            labels=["Organic", "Direct", "Referral", "Social"],
            title="Visitor Breakdown",
        )

ww.divider()

# Table
ww.heading("Inventory Snapshot", level=3)
ww.table([
    {"Item": "Widget A", "Status": "Active", "Stock": 140, "Trend": "+12%"},
    {"Item": "Widget B", "Status": "Low Stock", "Stock": 38, "Trend": "-5%"},
    {"Item": "Widget C", "Status": "Active", "Stock": 97, "Trend": "+3%"},
    {"Item": "Widget D", "Status": "Inactive", "Stock": 0, "Trend": "--"},
])

# Markdown
ww.divider()
ww.heading("Formatted Text", level=3)
ww.markdown(
    "Themes affect **bold**, *italic*, and `inline code` text. "
    "They also change link colours, borders, and surface tones so the "
    "entire page feels cohesive."
)

if __name__ == "__main__":
    ww.serve()
