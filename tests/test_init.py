"""Tests for webwrench.__init__ -- public API surface."""

import platform
import re

import webwrench as ww
from webwrench._context import get_default_page


class TestVersion:
    def test_version(self):
        assert ww.__version__ == "0.1.0"

    def test_get_version_keys(self):
        v = ww.get_version()
        assert set(v.keys()) == {"webwrench", "python", "bitwrench", "platform"}

    def test_get_version_webwrench(self):
        v = ww.get_version()
        assert v["webwrench"] == ww.__version__

    def test_get_version_python(self):
        v = ww.get_version()
        assert v["python"] == platform.python_version()

    def test_get_version_bitwrench(self):
        v = ww.get_version()
        assert re.match(r"\d+\.\d+\.\d+", v["bitwrench"])


class TestAllExports:
    def test_all_exists(self):
        assert isinstance(ww.__all__, list)
        assert len(ww.__all__) > 0

    def test_all_items_are_importable(self):
        for name in ww.__all__:
            assert hasattr(ww, name), f"ww.{name} not found"


class TestDisplayAPI:
    def test_title(self):
        el = ww.title("Hello")
        assert el.tag == "h1"

    def test_text(self):
        el = ww.text("para")
        assert el.tag == "p"

    def test_heading(self):
        el = ww.heading("h2", level=2)
        assert el.tag == "h2"

    def test_markdown(self):
        el = ww.markdown("# Hi")
        assert "ww-markdown" in el.attrs["class"]

    def test_code(self):
        el = ww.code("x = 1")
        assert el.tag == "pre"

    def test_html(self):
        el = ww.html("<b>bold</b>", raw=True)
        assert el.content == "<b>bold</b>"

    def test_image(self):
        el = ww.image("pic.png")
        assert el.tag == "img"

    def test_divider(self):
        el = ww.divider()
        assert el.tag == "hr"

    def test_table(self):
        el = ww.table([{"a": 1}])
        assert "ww-table" in el.attrs["class"]

    def test_metric(self):
        el = ww.metric("Rev", "$1M")
        assert "ww-metric" in el.attrs["class"]

    def test_json(self):
        el = ww.json({"k": "v"})
        assert "ww-json" in el.attrs["class"]

    def test_progress(self):
        el = ww.progress(50)
        assert el.attrs["aria-valuenow"] == "50"

    def test_toast(self):
        msg = ww.toast("done")
        assert msg["name"] == "wwToast"


class TestWidgetAPI:
    def test_button(self):
        b = ww.button("Go")
        assert b._widget_type == "button"

    def test_input(self):
        i = ww.input("Name")
        assert i._widget_type == "input"

    def test_textarea(self):
        t = ww.textarea("Desc")
        assert t._widget_type == "textarea"

    def test_slider(self):
        s = ww.slider("Vol")
        assert s._widget_type == "slider"

    def test_select(self):
        s = ww.select("X", ["a", "b"])
        assert s._widget_type == "select"

    def test_checkbox(self):
        c = ww.checkbox("On")
        assert c._widget_type == "checkbox"

    def test_radio(self):
        r = ww.radio("Size", ["S", "M"])
        assert r._widget_type == "radio"

    def test_file_upload(self):
        f = ww.file_upload("File")
        assert f._widget_type == "file_upload"

    def test_date_picker(self):
        d = ww.date_picker("Date")
        assert d._widget_type == "date_picker"

    def test_color_picker(self):
        c = ww.color_picker("Color")
        assert c._widget_type == "color_picker"

    def test_number(self):
        n = ww.number("N")
        assert n._widget_type == "number"


class TestChartAPI:
    def test_chart(self):
        c = ww.chart([1, 2, 3])
        assert c._chart_type == "bar"

    def test_plot(self):
        p = ww.plot([1, 2], type="line")
        assert p._chart_type == "line"


class TestLayoutAPI:
    def test_columns(self):
        col_set = ww.columns(2)
        assert len(col_set) == 2

    def test_tabs(self):
        tab_set = ww.tabs(["A", "B"])
        assert len(tab_set) == 2

    def test_accordion(self):
        a = ww.accordion("Options")
        assert a.tag == "details"

    def test_sidebar(self):
        s = ww.sidebar()
        assert s.tag == "aside"

    def test_card(self):
        c = ww.card(title="Info")
        assert "bw_card" in c.attrs["class"]

    def test_grid(self):
        g = ww.grid("1fr 1fr")
        assert "display:grid" in g.attrs["style"]

    def test_modal(self):
        m = ww.modal("Confirm")
        assert m.attrs["role"] == "dialog"

    def test_nav(self):
        n = ww.nav([{"text": "Home", "href": "/"}])
        assert n.tag == "nav"


class TestThemeAPI:
    def test_theme_preset(self):
        palette = ww.theme("dark")
        assert "primary" in palette

    def test_theme_custom(self):
        palette = ww.theme(primary="#ff0000")
        assert palette["primary"] == "#ff0000"

    def test_toggle_theme(self):
        msg = ww.toggle_theme()
        assert msg["name"] == "toggleStyles"

    def test_css(self):
        ww.css({".x": {"color": "red"}})
        assert get_default_page()._custom_css is not None


class TestExportAPI:
    def test_export_string(self):
        ww.title("Test")
        html = ww.export_string()
        assert "<!DOCTYPE html>" in html

    def test_screenshot(self):
        msg = ww.screenshot()
        assert msg["name"] == "wwScreenshot"

    def test_download(self):
        msg = ww.download("f.txt", content="data")
        assert msg["name"] == "download"

    def test_export_pdf(self):
        msg = ww.export_pdf()
        assert msg["name"] == "wwExportPDF"


class TestAppAPI:
    def test_app_class(self):
        app = ww.App()
        assert app is not None


class TestOptionsAPI:
    def test_options(self):
        assert ww.options.assets == "local"
