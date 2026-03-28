"""14 - Live Updates with Progress Bar

A progress bar that advances by 10% each time the button is clicked.
Demonstrates widget state management and the progress.update() method
driven by button callbacks.

Run: python examples/14_live_updates.py
"""

import webwrench as ww

ww.title("Live Progress Updates")
ww.text("Click the button to advance the progress bar by 10%.")

bar = ww.progress(value=0, max_val=100)
status_text = ww.text("Progress: 0%")

advance_btn = ww.button("Advance +10%")
reset_btn = ww.button("Reset")

current = {"value": 0}

@advance_btn.on_click
def on_advance():
    current["value"] = min(current["value"] + 10, 100)
    bar.update(current["value"])
    if current["value"] >= 100:
        ww.toast("Complete!", type="success")

@reset_btn.on_click
def on_reset():
    current["value"] = 0
    bar.update(0)
    ww.toast("Progress reset.", type="info")

if __name__ == "__main__":
    ww.serve()
