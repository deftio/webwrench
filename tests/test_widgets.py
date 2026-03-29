"""Tests for webwrench.widgets -- input widgets."""

from webwrench._context import Page, WidgetHandle, get_default_page
from webwrench.widgets import (
    button,
    checkbox,
    color_picker,
    date_picker,
    file_upload,
    input_widget,
    number,
    radio,
    select,
    slider,
    textarea,
)


class TestButton:
    def test_creates_button(self):
        b = button("Click me")
        assert isinstance(b, WidgetHandle)
        assert b.tag == "button"
        assert b.content == "Click me"
        assert b._widget_type == "button"

    def test_on_click_kwarg(self):
        calls = []
        b = button("Go", on_click=lambda: calls.append(1))
        b._fire_click()
        assert calls == [1]

    def test_added_to_default_page(self):
        button("X")
        assert len(get_default_page().elements) == 1

    def test_custom_page(self):
        page = Page()
        b = button("Y", page=page)
        assert len(page.elements) == 1

    def test_attrs(self):
        b = button("Z")
        assert "bw_btn" in b.attrs["class"]
        assert "bw_primary" in b.attrs["class"]
        assert b.attrs["type"] == "button"

    def test_variant(self):
        b = button("OK", variant="success")
        assert "bw_success" in b.attrs["class"]
        assert "bw_primary" not in b.attrs["class"]


class TestInput:
    def test_creates_input(self):
        i = input_widget("Name")
        assert isinstance(i, WidgetHandle)
        assert i._widget_type == "input"
        assert i._default_value == ""

    def test_with_placeholder_and_value(self):
        i = input_widget("Email", placeholder="you@example.com", value="test@x.com")
        assert i._default_value == "test@x.com"

    def test_taco_has_label_and_input(self):
        i = input_widget("Name")
        taco = i.to_taco()
        assert taco["t"] == "div"
        children = taco["c"]
        assert len(children) == 2  # label + input


class TestTextarea:
    def test_creates_textarea(self):
        t = textarea("Comment")
        assert t._widget_type == "textarea"

    def test_with_rows_and_value(self):
        t = textarea("Note", rows=8, value="initial")
        assert t._default_value == "initial"

    def test_taco_structure(self):
        t = textarea("Desc")
        taco = t.to_taco()
        assert taco["t"] == "div"
        assert len(taco["c"]) == 2


class TestSlider:
    def test_creates_slider(self):
        s = slider("Volume", min=0, max=100, value=50, step=1)
        assert s._widget_type == "slider"
        assert s._default_value == 50
        assert s._min == 0
        assert s._max == 100
        assert s._step == 1

    def test_taco_structure(self):
        s = slider("X")
        taco = s.to_taco()
        children = taco["c"]
        assert len(children) == 3  # label + input + value display


class TestSelect:
    def test_creates_select(self):
        s = select("Color", ["red", "green", "blue"])
        assert s._widget_type == "select"
        assert s._default_value == "red"  # first option
        assert s._options == ["red", "green", "blue"]

    def test_explicit_value(self):
        s = select("Color", ["red", "green"], value="green")
        assert s._default_value == "green"

    def test_empty_options(self):
        s = select("Empty", [])
        assert s._default_value == ""

    def test_taco_has_options(self):
        s = select("X", ["a", "b"])
        taco = s.to_taco()
        children = taco["c"]
        select_el = children[1]  # second child is the select
        assert select_el["t"] == "select"
        assert len(select_el["c"]) == 2  # 2 option elements


class TestCheckbox:
    def test_creates_checkbox(self):
        c = checkbox("Accept terms")
        assert c._widget_type == "checkbox"
        assert c._default_value is False

    def test_checked(self):
        c = checkbox("On", value=True)
        assert c._default_value is True

    def test_taco_structure(self):
        c = checkbox("Test")
        taco = c.to_taco()
        children = taco["c"]
        assert len(children) == 2  # input + label

    def test_checked_attr(self):
        c = checkbox("On", value=True)
        taco = c.to_taco()
        input_el = taco["c"][0]  # first child is checkbox input
        assert input_el["a"].get("checked") == "checked"


class TestRadio:
    def test_creates_radio(self):
        r = radio("Size", ["S", "M", "L"])
        assert r._widget_type == "radio"
        assert r._default_value == "S"
        assert r._options == ["S", "M", "L"]

    def test_explicit_value(self):
        r = radio("Size", ["S", "M", "L"], value="M")
        assert r._default_value == "M"

    def test_empty_options(self):
        r = radio("Empty", [])
        assert r._default_value == ""

    def test_taco_structure(self):
        r = radio("X", ["a", "b"])
        taco = r.to_taco()
        assert taco["t"] == "fieldset"
        # legend + 2 radio options
        assert len(taco["c"]) == 3


class TestFileUpload:
    def test_creates_file_upload(self):
        f = file_upload("Upload CSV")
        assert f._widget_type == "file_upload"
        assert f._default_value is None

    def test_accept_attr(self):
        f = file_upload("Upload", accept=".csv,.json")
        taco = f.to_taco()
        # Find the input element in children
        input_el = taco["c"][1]
        assert input_el["a"].get("accept") == ".csv,.json"

    def test_no_accept(self):
        f = file_upload("File")
        taco = f.to_taco()
        input_el = taco["c"][1]
        assert "accept" not in input_el["a"]


class TestDatePicker:
    def test_creates(self):
        d = date_picker("Start date")
        assert d._widget_type == "date_picker"

    def test_with_value(self):
        d = date_picker("Date", value="2026-01-01")
        assert d._default_value == "2026-01-01"


class TestColorPicker:
    def test_creates(self):
        c = color_picker("Color")
        assert c._widget_type == "color_picker"
        assert c._default_value == "#3366cc"

    def test_custom_value(self):
        c = color_picker("Color", value="#ff0000")
        assert c._default_value == "#ff0000"


class TestNumber:
    def test_creates(self):
        n = number("Count", min=0, max=10, step=1, value=5)
        assert n._widget_type == "number"
        assert n._default_value == 5

    def test_taco_structure(self):
        n = number("N")
        taco = n.to_taco()
        assert len(taco["c"]) == 2  # label + input
