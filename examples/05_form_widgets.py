"""05 - Form Widgets Showcase

Demonstrates every available widget type: text input, textarea, slider,
select dropdown, checkbox, radio buttons, number input, date picker,
color picker, and file upload. A submit button displays the current
values via a toast notification.

Run: python examples/05_form_widgets.py
"""

import webwrench as ww

ww.theme("ocean")

# ── Header ──
ww.title("Widget Showcase")
ww.text(
    "Every input widget webwrench offers, organised into logical groups.  "
    "Fill in the form and hit Submit to see a summary toast."
)

ww.divider()

# ── Personal info ──
ww.heading("Personal Information", level=2)
ww.text("Basic identity fields -- text input, textarea, and date picker.")

info_cols = ww.columns(2)
with info_cols[0]:
    with ww.card(title="Identity"):
        name_input = ww.input("Full Name", placeholder="e.g. Jane Doe", value="")
        start_date = ww.date_picker("Start Date", value="2025-01-15")
with info_cols[1]:
    with ww.card(title="About You"):
        bio_textarea = ww.textarea("Short Bio", rows=4, value="")

ww.divider()

# ── Preferences ──
ww.heading("Preferences", level=2)
ww.text("Dropdowns, radio buttons, and checkboxes for capturing choices.")

pref_cols = ww.columns(3)
with pref_cols[0]:
    with ww.card(title="Role"):
        role_select = ww.select("Department", options=["Developer", "Designer", "Manager", "Other"])
        experience_radio = ww.radio("Experience Level", options=["Junior", "Mid", "Senior"], value="Mid")
with pref_cols[1]:
    with ww.card(title="Ratings"):
        age_slider = ww.slider("Age", min=0, max=120, value=30, step=1)
        rating_number = ww.number("Satisfaction (1-10)", min=1, max=10, step=1, value=7)
with pref_cols[2]:
    with ww.card(title="Extras"):
        newsletter_cb = ww.checkbox("Subscribe to newsletter", value=True)
        fav_color = ww.color_picker("Favourite Colour", value="#3366cc")
        resume_upload = ww.file_upload("Upload Resume", accept=".pdf,.docx")

ww.divider()

# ── Submit ──
ww.heading("Submit", level=2)
ww.text("Click the button below to display all current widget values.")

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
        f"Colour: {fav_color.value}"
    )
    ww.toast(summary, type="success", duration=5000)

if __name__ == "__main__":
    ww.serve()
