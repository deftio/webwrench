"""Tests for webwrench.export -- export, screenshot, download."""

import os
import tempfile

from webwrench._context import Page, Element, get_default_page
from webwrench.export import (
    download,
    export,
    export_pdf,
    export_string,
    screenshot,
)


class TestExport:
    def test_writes_file(self):
        page = Page()
        page.add(Element("p", content="test", element_id="p1"))
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            path = f.name
        try:
            result = export(path, page=page)
            assert os.path.exists(path)
            with open(path) as fh:
                content = fh.read()
            assert "<!DOCTYPE html>" in content
            assert result == content
        finally:
            os.unlink(path)

    def test_default_page(self):
        get_default_page().add(Element("h1", content="Title", element_id="h1"))
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            path = f.name
        try:
            export(path)
            with open(path) as fh:
                content = fh.read()
            assert "Title" in content
        finally:
            os.unlink(path)

    def test_custom_title(self):
        page = Page()
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            path = f.name
        try:
            result = export(path, page=page, title="My Report")
            assert "<title>My Report</title>" in result
        finally:
            os.unlink(path)

    def test_minify(self):
        page = Page()
        page.add(Element("p", content="x", element_id="p1"))
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            path = f.name
        try:
            export(path, page=page, minify=True)
            with open(path) as fh:
                content = fh.read()
            assert "<!DOCTYPE html>" in content
        finally:
            os.unlink(path)

    def test_exclude_3d(self):
        page = Page()
        page._libs_used.add("threejs")
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            path = f.name
        try:
            export(path, page=page, include_3d=False)
            assert "threejs" not in page._libs_used
        finally:
            os.unlink(path)


class TestExportString:
    def test_returns_html(self):
        page = Page()
        page.add(Element("div", content="hello", element_id="d1"))
        html = export_string(page=page)
        assert "<!DOCTYPE html>" in html
        assert "hello" in html

    def test_default_page(self):
        html = export_string()
        assert "<!DOCTYPE html>" in html

    def test_title(self):
        html = export_string(title="Test Report")
        assert "<title>Test Report</title>" in html

    def test_minify(self):
        page = Page()
        page.add(Element("p", content="x", element_id="p1"))
        html = export_string(page=page, minify=True)
        assert "<!DOCTYPE html>" in html


class TestScreenshot:
    def test_returns_call_msg(self):
        msg = screenshot("dash.png")
        assert msg["type"] == "call"
        assert msg["name"] == "wwScreenshot"
        assert msg["args"] == ["dash.png"]

    def test_with_selector(self):
        msg = screenshot("chart.png", selector="#my-chart")
        assert msg["args"] == ["chart.png", "#my-chart"]

    def test_default_filename(self):
        msg = screenshot()
        assert msg["args"] == ["screenshot.png"]


class TestDownload:
    def test_string_content(self):
        msg = download("data.csv", content="a,b\n1,2")
        assert msg["type"] == "call"
        assert msg["name"] == "download"
        assert msg["args"][0] == "data.csv"
        assert msg["args"][1] == "a,b\n1,2"

    def test_bytes_content(self):
        msg = download("img.png", content=b"\x89PNG", mime="image/png")
        assert msg["args"][0] == "img.png"
        # bytes should be base64 encoded
        import base64
        decoded = base64.b64decode(msg["args"][1])
        assert decoded == b"\x89PNG"
        assert msg["args"][2] == "image/png"

    def test_no_content(self):
        msg = download("file.txt")
        assert msg["args"][1] == ""


class TestExportPdf:
    def test_returns_call_msg(self):
        msg = export_pdf("report.pdf")
        assert msg["type"] == "call"
        assert msg["name"] == "wwExportPDF"
        assert msg["args"] == ["report.pdf"]

    def test_default_filename(self):
        msg = export_pdf()
        assert msg["args"] == ["report.pdf"]
