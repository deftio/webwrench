"""16 - Modal Dialog

A modal dialog that opens when a button is clicked. The modal
contains a form with inputs and a confirm button. Demonstrates
ww.modal() as a context manager and button-driven interactivity.

Run: python examples/16_modal_dialog.py
"""

import webwrench as ww

ww.title("Modal Dialog Demo")
ww.text("Click the button below to open a modal dialog with a feedback form.")

open_btn = ww.button("Open Feedback Form")

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

ww.divider()
ww.text("The rest of the page content sits behind the modal overlay.")
ww.chart(
    [10, 25, 15, 30, 22],
    type="bar",
    labels=["Mon", "Tue", "Wed", "Thu", "Fri"],
    title="Weekly Feedback Count",
)

if __name__ == "__main__":
    ww.serve()
