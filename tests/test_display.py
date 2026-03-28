"""Tests for webwrench.display -- display elements."""

import json

import pytest

from webwrench._context import Page, get_default_page
from webwrench.display import (
    code,
    divider,
    heading,
    html_element,
    image,
    json_viewer,
    markdown,
    metric,
    progress,
    table,
    text,
    title,
    toast,
    _normalize_table_data,
    _build_table_taco,
)


class TestTitle:
    def test_creates_h1(self):
        el = title("Hello")
        assert el.tag == "h1"
        assert el.content == "Hello"

    def test_added_to_default_page(self):
        title("X")
        assert len(get_default_page().elements) == 1

    def test_custom_page(self):
        page = Page()
        el = title("Y", page=page)
        assert len(page.elements) == 1
        assert el in page.elements


class TestHeading:
    def test_default_level(self):
        el = heading("Test")
        assert el.tag == "h2"

    def test_custom_level(self):
        el = heading("Test", level=4)
        assert el.tag == "h4"

    def test_clamp_low(self):
        el = heading("Test", level=0)
        assert el.tag == "h1"

    def test_clamp_high(self):
        el = heading("Test", level=9)
        assert el.tag == "h6"


class TestText:
    def test_creates_p(self):
        el = text("Hello world")
        assert el.tag == "p"
        assert el.content == "Hello world"


class TestMarkdown:
    def test_creates_div_with_class(self):
        el = markdown("# Title")
        assert el.tag == "div"
        assert "ww-markdown" in el.attrs["class"]
        assert el.attrs["data-md"] == "# Title"
        assert el.content == "# Title"


class TestCode:
    def test_creates_pre_code(self):
        el = code("print('hi')")
        assert el.tag == "pre"
        assert "language-python" in el.attrs["class"]
        assert el.content.tag == "code"

    def test_custom_lang(self):
        el = code("var x;", lang="javascript")
        assert "language-javascript" in el.attrs["class"]

    def test_escapes_html(self):
        el = code("<script>alert(1)</script>")
        assert "<script>" not in el.content.content
        assert "&lt;script&gt;" in el.content.content


class TestHtmlElement:
    def test_escaped_by_default(self):
        el = html_element("<b>bold</b>")
        assert "&lt;b&gt;" in el.content

    def test_raw_mode(self):
        el = html_element("<b>bold</b>", raw=True)
        assert el.content == "<b>bold</b>"
        assert el.attrs.get("data-raw") == "true"


class TestImage:
    def test_basic(self):
        el = image("photo.png")
        assert el.tag == "img"
        assert el.attrs["src"] == "photo.png"
        assert el.attrs["alt"] == ""

    def test_with_alt_and_width(self):
        el = image("pic.jpg", alt="A picture", width=300)
        assert el.attrs["alt"] == "A picture"
        assert el.attrs["width"] == "300"

    def test_no_width_when_none(self):
        el = image("x.png")
        assert "width" not in el.attrs


class TestDivider:
    def test_creates_hr(self):
        el = divider()
        assert el.tag == "hr"


class TestNormalizeTableData:
    def test_list_of_dicts(self):
        data = [{"name": "Alice", "score": 95}, {"name": "Bob", "score": 87}]
        headers, rows = _normalize_table_data(data)
        assert headers == ["name", "score"]
        assert rows == [["Alice", 95], ["Bob", 87]]

    def test_list_of_lists(self):
        data = [["Name", "Score"], ["Alice", 95], ["Bob", 87]]
        headers, rows = _normalize_table_data(data)
        assert headers == ["Name", "Score"]
        assert rows == [["Alice", 95], ["Bob", 87]]

    def test_empty_list(self):
        headers, rows = _normalize_table_data([])
        assert headers == []
        assert rows == []

    def test_non_list(self):
        headers, rows = _normalize_table_data("not a list")
        assert headers == []
        assert rows == []

    def test_list_of_tuples(self):
        data = [("H1", "H2"), ("a", "b")]
        headers, rows = _normalize_table_data(data)
        assert headers == ["H1", "H2"]
        assert rows == [["a", "b"]]

    def test_dataframe_like(self):
        """Test with a mock DataFrame-like object."""
        class FakeDF:
            columns = ["x", "y"]
            def iterrows(self):
                yield 0, [1, 2]
                yield 1, [3, 4]
        headers, rows = _normalize_table_data(FakeDF())
        assert headers == ["x", "y"]
        assert rows == [[1, 2], [3, 4]]


class TestBuildTableTaco:
    def test_basic(self):
        result = _build_table_taco(["A", "B"], [[1, 2]])
        assert len(result) == 1
        tbl = result[0]
        assert tbl["t"] == "table"
        assert len(tbl["c"]) == 2  # thead + tbody


class TestTable:
    def test_basic(self):
        data = [{"a": 1, "b": 2}]
        el = table(data)
        assert el.tag == "div"
        assert "ww-table" in el.attrs["class"]

    def test_options_in_config(self):
        el = table([{"x": 1}], sortable=True, searchable=True, paginate=10)
        config = json.loads(el.attrs["data-config"])
        assert config["sortable"] is True
        assert config["searchable"] is True
        assert config["paginate"] == 10

    def test_no_paginate(self):
        el = table([{"x": 1}])
        config = json.loads(el.attrs["data-config"])
        assert "paginate" not in config


class TestMetric:
    def test_basic(self):
        el = metric("Revenue", "$1.2M")
        assert el.tag == "div"
        assert "ww-metric" in el.attrs["class"]
        assert len(el.content) == 2  # label + value

    def test_with_delta(self):
        el = metric("Rev", "$1M", delta="+12%", delta_color="green")
        assert len(el.content) == 3  # label + value + delta
        delta_el = el.content[2]
        assert "color:green" in delta_el.attrs.get("style", "")

    def test_no_delta(self):
        el = metric("X", "Y")
        assert len(el.content) == 2


class TestJsonViewer:
    def test_basic(self):
        el = json_viewer({"key": "value"})
        assert el.tag == "pre"
        assert "ww-json" in el.attrs["class"]
        assert '"key"' in el.content

    def test_collapsed_attr(self):
        el = json_viewer({}, collapsed=3)
        assert el.attrs["data-collapsed"] == "3"


class TestProgress:
    def test_basic(self):
        el = progress(50, max_val=100)
        assert el.tag == "div"
        assert el.attrs["aria-valuenow"] == "50"
        assert el.attrs["aria-valuemax"] == "100"

    def test_zero(self):
        el = progress(0, max_val=200)
        assert el.attrs["aria-valuenow"] == "0"

    def test_is_widget_handle(self):
        from webwrench._context import WidgetHandle
        el = progress()
        assert isinstance(el, WidgetHandle)
        assert el._widget_type == "progress"


class TestToast:
    def test_returns_call_message(self):
        msg = toast("Saved!", type="success", duration=5000)
        assert msg["type"] == "call"
        assert msg["name"] == "wwToast"
        assert msg["args"] == ["Saved!", "success", 5000]

    def test_defaults(self):
        msg = toast("hi")
        assert msg["args"] == ["hi", "info", 3000]
