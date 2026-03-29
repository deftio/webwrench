"""Input widgets: button, input, slider, select, checkbox, textarea, radio, etc.

Each function creates a WidgetHandle and adds it to the given page (or the default).
"""

from __future__ import annotations

from typing import Any

from webwrench._context import Element, Page, WidgetHandle, get_default_page


def button(
    label: str,
    on_click: Any = None,
    variant: str = "primary",
    page: Page | None = None,
) -> WidgetHandle:
    """Create a button widget."""
    p = page or get_default_page()
    handle = WidgetHandle(
        "button",
        attrs={"class": f"bw_btn bw_{variant} ww-button", "type": "button"},
        content=label,
        widget_type="button",
    )
    if on_click is not None:
        handle.on_click(on_click)
    p.add(handle)
    return handle


def input_widget(
    label: str,
    placeholder: str = "",
    value: str = "",
    page: Page | None = None,
) -> WidgetHandle:
    """Create a text input widget."""
    p = page or get_default_page()
    input_el = Element(
        "input",
        attrs={
            "type": "text",
            "placeholder": placeholder,
            "value": value,
            "class": "bw_form_control ww-input-field",
        },
    )
    label_el = Element("label", attrs={"class": "bw_form_label ww-label"}, content=label)
    handle = WidgetHandle(
        "div",
        attrs={"class": "bw_form_group ww-input-group"},
        content=[label_el, input_el],
        default_value=value,
        widget_type="input",
    )
    p.add(handle)
    return handle


def textarea(
    label: str,
    rows: int = 4,
    value: str = "",
    page: Page | None = None,
) -> WidgetHandle:
    """Create a multi-line text input."""
    p = page or get_default_page()
    ta_el = Element(
        "textarea",
        attrs={"rows": str(rows), "class": "bw_form_control ww-textarea-field"},
        content=value,
    )
    label_el = Element("label", attrs={"class": "bw_form_label ww-label"}, content=label)
    handle = WidgetHandle(
        "div",
        attrs={"class": "bw_form_group ww-textarea-group"},
        content=[label_el, ta_el],
        default_value=value,
        widget_type="textarea",
    )
    p.add(handle)
    return handle


def slider(
    label: str,
    min: int | float = 0,
    max: int | float = 100,
    value: int | float = 50,
    step: int | float = 1,
    page: Page | None = None,
) -> WidgetHandle:
    """Create a range slider widget."""
    p = page or get_default_page()
    input_el = Element(
        "input",
        attrs={
            "type": "range",
            "min": str(min),
            "max": str(max),
            "value": str(value),
            "step": str(step),
            "class": "bw_range ww-slider-input",
        },
    )
    label_el = Element("label", attrs={"class": "bw_form_label ww-label"}, content=label)
    value_el = Element("span", attrs={"class": "ww-slider-value"}, content=str(value))
    handle = WidgetHandle(
        "div",
        attrs={"class": "bw_form_group ww-slider-group"},
        content=[label_el, input_el, value_el],
        default_value=value,
        widget_type="slider",
    )
    handle._min = min
    handle._max = max
    handle._step = step
    p.add(handle)
    return handle


def select(
    label: str,
    options: list[str],
    value: str | None = None,
    page: Page | None = None,
) -> WidgetHandle:
    """Create a dropdown select widget."""
    p = page or get_default_page()
    default = value if value is not None else (options[0] if options else "")
    option_els = [
        Element("option", attrs={"value": opt}, content=opt) for opt in options
    ]
    select_el = Element("select", attrs={"class": "bw_form_control ww-select-field"}, content=option_els)
    label_el = Element("label", attrs={"class": "bw_form_label ww-label"}, content=label)
    handle = WidgetHandle(
        "div",
        attrs={"class": "bw_form_group ww-select-group"},
        content=[label_el, select_el],
        default_value=default,
        widget_type="select",
    )
    handle._options = options
    p.add(handle)
    return handle


def checkbox(
    label: str,
    value: bool = False,
    page: Page | None = None,
) -> WidgetHandle:
    """Create a checkbox widget."""
    p = page or get_default_page()
    input_attrs: dict[str, Any] = {"type": "checkbox", "class": "ww-checkbox-input"}
    if value:
        input_attrs["checked"] = "checked"
    input_el = Element("input", attrs=input_attrs)
    label_el = Element("label", attrs={"class": "bw_form_label ww-label"}, content=label)
    handle = WidgetHandle(
        "div",
        attrs={"class": "bw_form_group ww-checkbox-group"},
        content=[input_el, label_el],
        default_value=value,
        widget_type="checkbox",
    )
    p.add(handle)
    return handle


def radio(
    label: str,
    options: list[str],
    value: str | None = None,
    page: Page | None = None,
) -> WidgetHandle:
    """Create a radio button group."""
    p = page or get_default_page()
    default = value if value is not None else (options[0] if options else "")
    radio_els = []
    for opt in options:
        radio_attrs: dict[str, Any] = {
            "type": "radio",
            "name": "",  # Will be set to element ID on render
            "value": opt,
            "class": "ww-radio-input",
        }
        if opt == default:
            radio_attrs["checked"] = "checked"
        radio_els.append(
            Element(
                "div",
                attrs={"class": "ww-radio-option"},
                content=[
                    Element("input", attrs=radio_attrs),
                    Element("span", content=opt),
                ],
            )
        )
    legend = Element("legend", attrs={"class": "bw_form_label ww-label"}, content=label)
    handle = WidgetHandle(
        "fieldset",
        attrs={"class": "bw_form_group ww-radio-group"},
        content=[legend, *radio_els],
        default_value=default,
        widget_type="radio",
    )
    handle._options = options
    p.add(handle)
    return handle


def file_upload(
    label: str,
    accept: str = "",
    page: Page | None = None,
) -> WidgetHandle:
    """Create a file upload widget."""
    p = page or get_default_page()
    input_attrs: dict[str, Any] = {"type": "file", "class": "ww-file-input"}
    if accept:
        input_attrs["accept"] = accept
    input_el = Element("input", attrs=input_attrs)
    label_el = Element("label", attrs={"class": "bw_form_label ww-label"}, content=label)
    handle = WidgetHandle(
        "div",
        attrs={"class": "bw_form_group ww-file-group"},
        content=[label_el, input_el],
        default_value=None,
        widget_type="file_upload",
    )
    p.add(handle)
    return handle


def date_picker(
    label: str,
    value: str = "",
    page: Page | None = None,
) -> WidgetHandle:
    """Create a date picker widget."""
    p = page or get_default_page()
    input_el = Element(
        "input",
        attrs={"type": "date", "value": value, "class": "bw_form_control ww-date-input"},
    )
    label_el = Element("label", attrs={"class": "bw_form_label ww-label"}, content=label)
    handle = WidgetHandle(
        "div",
        attrs={"class": "bw_form_group ww-date-group"},
        content=[label_el, input_el],
        default_value=value,
        widget_type="date_picker",
    )
    p.add(handle)
    return handle


def color_picker(
    label: str,
    value: str = "#3366cc",
    page: Page | None = None,
) -> WidgetHandle:
    """Create a color picker widget."""
    p = page or get_default_page()
    input_el = Element(
        "input",
        attrs={"type": "color", "value": value, "class": "bw_form_control ww-color-input"},
    )
    label_el = Element("label", attrs={"class": "bw_form_label ww-label"}, content=label)
    handle = WidgetHandle(
        "div",
        attrs={"class": "bw_form_group ww-color-group"},
        content=[label_el, input_el],
        default_value=value,
        widget_type="color_picker",
    )
    p.add(handle)
    return handle


def number(
    label: str,
    min: int | float = 0,
    max: int | float = 100,
    step: int | float = 1,
    value: int | float = 0,
    page: Page | None = None,
) -> WidgetHandle:
    """Create a number input widget."""
    p = page or get_default_page()
    input_el = Element(
        "input",
        attrs={
            "type": "number",
            "min": str(min),
            "max": str(max),
            "step": str(step),
            "value": str(value),
            "class": "bw_form_control ww-number-input",
        },
    )
    label_el = Element("label", attrs={"class": "bw_form_label ww-label"}, content=label)
    handle = WidgetHandle(
        "div",
        attrs={"class": "bw_form_group ww-number-group"},
        content=[label_el, input_el],
        default_value=value,
        widget_type="number",
    )
    p.add(handle)
    return handle
