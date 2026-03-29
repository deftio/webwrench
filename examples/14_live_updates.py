"""14 - Live Updates with Progress Bar

A progress bar that advances by 10% each time the button is clicked.
Demonstrates the callback -> update -> SSE -> DOM cycle: clicking a
button fires a Python callback on the server, which calls
widget.update() to push a patch message over SSE to the browser.

Concepts: ww.progress(), ww.button(), @btn.on_click,
          widget.update(), ww.toast(), ww.metric(), ww.card().

Run: python examples/14_live_updates.py
"""

import webwrench as ww

ww.theme("ocean")

# -- Header --
ww.title("Live Updates")
ww.text(
    "Click the Advance button to move the progress bar forward by 10%. "
    "Each click fires a Python callback on the server, which calls "
    "bar.update() and counter.update() to push new values to the "
    "browser over SSE."
)

ww.divider()

# -- Explanation --
ww.heading("How it works", level=2)
ww.text(
    "1. Browser sends POST to /bw/return/action/:id with the button's widget ID. "
    "2. Server looks up the widget and fires its @on_click callback. "
    "3. The callback calls widget.update(new_value), which queues an SSE patch. "
    "4. The browser receives the patch and updates the DOM in place."
)

ww.divider()

# -- Progress section inside a card --
ww.heading("Progress", level=2)

with ww.card(title="Task Progress"):
    counter = ww.metric("Clicks", "0")
    bar = ww.progress(value=0, max_val=100)
    status = ww.text("Progress: 0%")

    cols = ww.columns(2)
    with cols[0]:
        advance_btn = ww.button("Advance +10%")
    with cols[1]:
        reset_btn = ww.button("Reset")

current = {"value": 0, "clicks": 0}


@advance_btn.on_click
def on_advance():
    current["value"] = min(current["value"] + 10, 100)
    current["clicks"] += 1
    bar.update(current["value"])
    counter.update(str(current["clicks"]))
    status.update(f"Progress: {current['value']}%")
    if current["value"] >= 100:
        ww.toast("Complete!", type="success")


@reset_btn.on_click
def on_reset():
    current["value"] = 0
    current["clicks"] = 0
    bar.update(0)
    counter.update("0")
    status.update("Progress: 0%")
    ww.toast("Progress reset.", type="info")


if __name__ == "__main__":
    ww.serve()
