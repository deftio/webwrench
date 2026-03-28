"""02 - Interactive Chart

Interactive chart with slider control. Drag the slider to multiply
all bar values by the selected factor.

Run: python examples/02_interactive_chart.py
"""

import webwrench as ww

data = [12, 19, 3, 5, 2, 3]

ww.title("Sales Dashboard")
chart = ww.chart(data, type="bar", labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun"])
slider = ww.slider("Multiplier", min=1, max=10, value=1)

@slider.on_change
def update(value):
    chart.update([d * value for d in data])

if __name__ == "__main__":
    ww.serve()
