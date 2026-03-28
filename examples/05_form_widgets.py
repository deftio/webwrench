"""05 - Form Widgets Showcase

Demonstrates every available widget type: text input, textarea, slider,
select dropdown, checkbox, radio buttons, number input, date picker,
color picker, and file upload. A submit button displays the current
values via a toast notification.

Run: python examples/05_form_widgets.py
"""

import webwrench as ww

ww.title("Widget Showcase")
ww.text("Interact with the widgets below, then click Submit to see all current values.")

name_input = ww.input("Name", placeholder="Enter your name", value="")
bio_textarea = ww.textarea("Bio", rows=3, value="")
age_slider = ww.slider("Age", min=0, max=120, value=30, step=1)
role_select = ww.select("Role", options=["Developer", "Designer", "Manager", "Other"])
newsletter_cb = ww.checkbox("Subscribe to newsletter", value=True)
experience_radio = ww.radio("Experience", options=["Junior", "Mid", "Senior"], value="Mid")
rating_number = ww.number("Satisfaction (1-10)", min=1, max=10, step=1, value=7)
start_date = ww.date_picker("Start Date", value="2025-01-15")
fav_color = ww.color_picker("Favorite Color", value="#3366cc")
resume_upload = ww.file_upload("Upload Resume", accept=".pdf,.docx")

ww.divider()

submit_btn = ww.button("Submit")

@submit_btn.on_click
def on_submit():
    summary = (
        f"Name: {name_input.value}, "
        f"Role: {role_select.value}, "
        f"Age: {age_slider.value}, "
        f"Experience: {experience_radio.value}, "
        f"Rating: {rating_number.value}, "
        f"Newsletter: {newsletter_cb.value}, "
        f"Color: {fav_color.value}"
    )
    ww.toast(summary, type="success", duration=5000)

if __name__ == "__main__":
    ww.serve()
