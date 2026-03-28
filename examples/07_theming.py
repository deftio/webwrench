"""07 - Theming

Switch between built-in theme presets (light, dark, ocean, forest) using
a dropdown selector. The page re-renders with the selected theme.

Run: python examples/07_theming.py
"""

import webwrench as ww

ww.title("Theme Selector")
ww.text("Choose a theme preset from the dropdown to restyle the page.")

theme_select = ww.select("Theme", options=["light", "dark", "ocean", "forest"], value="light")

@theme_select.on_change
def on_theme_change(value):
    ww.theme(value)

ww.divider()

# Sample content to see the theme in action
ww.heading("Sample Content", level=2)
ww.markdown("This is **bold** and this is *italic*. Themes change colors across the page.")

ww.metric("Metric Example", "42", delta="+7%", delta_color="green")

ww.chart(
    [28, 48, 40, 19, 86, 27],
    type="bar",
    labels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
    title="Weekly Activity",
)

ww.table([
    {"Item": "Widget A", "Status": "Active", "Count": 140},
    {"Item": "Widget B", "Status": "Inactive", "Count": 38},
    {"Item": "Widget C", "Status": "Active", "Count": 97},
])

if __name__ == "__main__":
    ww.serve()
