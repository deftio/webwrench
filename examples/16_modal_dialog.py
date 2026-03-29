"""16 - Modal Dialog

A modal dialog containing a feedback form. The modal is rendered on
page load (positioned fixed, centered) and contains a textarea,
rating slider, and submit button. The submit callback fires a toast.

Concepts: ww.modal(), context manager (with dialog:),
          ww.textarea(), ww.slider(), ww.button(), ww.toast().

Note: The modal renders immediately as a fixed overlay. A future
version of webwrench will support show/hide toggling via callbacks.

Run: python examples/16_modal_dialog.py
"""

import webwrench as ww

ww.theme("ocean")

# -- Header --
ww.title("Modal Dialog")
ww.text(
    "ww.modal(title) creates a fixed-position overlay dialog. Content "
    "placed inside the 'with dialog:' block becomes the modal body. "
    "The submit button fires a callback that shows a toast notification."
)

ww.divider()

# -- Page content behind the modal --
ww.heading("Page Content", level=2)
ww.text(
    "The chart and table below sit behind the modal overlay. "
    "In a full app you would toggle modal visibility via callbacks."
)

ww.chart(
    [10, 25, 15, 30, 22],
    type="bar",
    labels=["Mon", "Tue", "Wed", "Thu", "Fri"],
    title="Weekly Feedback Count",
)

ww.table([
    {"Day": "Monday", "Responses": 10, "Avg Rating": 4.2},
    {"Day": "Tuesday", "Responses": 25, "Avg Rating": 3.8},
    {"Day": "Wednesday", "Responses": 15, "Avg Rating": 4.5},
    {"Day": "Thursday", "Responses": 30, "Avg Rating": 4.1},
    {"Day": "Friday", "Responses": 22, "Avg Rating": 3.9},
])

ww.divider()

# -- Modal dialog --
ww.heading("Feedback Form (Modal)", level=2)
ww.text(
    "The modal below demonstrates ww.modal() as a context manager. "
    "The submit button callback reads the slider value and fires a toast."
)

dialog = ww.modal("Submit Feedback")

with dialog:
    ww.text("We appreciate your feedback. Please fill out the form below.")
    feedback_input = ww.textarea("Your Feedback", rows=4, value="")
    rating = ww.slider("Rating", min=1, max=5, value=3, step=1)
    confirm_btn = ww.button("Submit")

    @confirm_btn.on_click
    def on_confirm():
        ww.toast(
            f"Thanks! Rating: {rating.value}/5",
            type="success",
            duration=4000,
        )

if __name__ == "__main__":
    ww.serve()
