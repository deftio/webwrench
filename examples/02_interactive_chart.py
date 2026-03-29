"""02 - Interactive Chart

Teaches the callback pattern: a slider fires @slider.on_change, which
updates both a chart and a metric in real time over SSE.

Concepts: ww.chart(), ww.slider(), @widget.on_change, widget.update(),
          ww.metric(), ww.card(), ww.columns(), ww.theme().

Run: python examples/02_interactive_chart.py
"""

import webwrench as ww

# -- Theme --
ww.theme("ocean")

# -- Header --
ww.title("Interactive Chart")
ww.text(
    "Drag the slider to multiply every bar value by the selected factor. "
    "The chart and the multiplier metric update in real time via SSE."
)

ww.divider()

# -- Data --
base_data = [12, 19, 3, 5, 2, 3]
labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]

# -- Layout: metric + slider on top, chart below --
ww.heading("Controls", level=2)
ww.text(
    "The @slider.on_change decorator registers a Python function that runs "
    "on the server each time the slider value changes. Inside the callback, "
    "chart.update() and multiplier_metric.update() push new data to the "
    "browser over the SSE connection."
)

top = ww.columns(2)
with top[0]:
    multiplier_metric = ww.metric("Multiplier", "1x")
with top[1]:
    slider = ww.slider("Multiplier", min=1, max=10, value=1)

ww.divider()

ww.heading("Sales Data", level=2)
chart = ww.chart(
    base_data,
    type="bar",
    labels=labels,
    title="Monthly Sales (units)",
)


@slider.on_change
def on_multiplier_change(value):
    """Callback: multiply base data and push updates to the client."""
    scaled = [d * value for d in base_data]
    chart.update(scaled)
    multiplier_metric.update(f"{value}x")


if __name__ == "__main__":
    ww.serve()
