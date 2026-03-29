"""Tests for webwrench._shell -- HTML template generation."""

import json

from webwrench._context import Page, Element
from webwrench._shell import (
    CDN_URLS,
    _base_css,
    _build_custom_css,
    _build_inline_scripts,
    _build_scripts,
    _build_theme_css,
    _is_stub_asset,
    _lib_filename,
    _read_asset,
    generate_export_html,
    generate_shell_html,
)


class TestReadAsset:
    def test_missing_file(self):
        result = _read_asset("nonexistent.js")
        assert "not found" in result

    def test_existing_file(self):
        result = _read_asset("bitwrench.min.js")
        assert "bitwrench" in result.lower() or "bw" in result.lower()


class TestLibFilename:
    def test_known_libs(self):
        assert _lib_filename("chartjs") == "chart.min.js"
        assert _lib_filename("d3") == "d3.min.js"
        assert _lib_filename("leaflet") == "leaflet.min.js"
        assert _lib_filename("threejs") == "three.min.js"
        assert _lib_filename("html2canvas") == "html2canvas.min.js"

    def test_unknown_lib(self):
        assert _lib_filename("unknown") is None


class TestBuildScripts:
    def test_local_mode_stub_falls_back_to_cdn(self):
        scripts = _build_scripts({"chartjs"}, "local")
        assert "/ww/lib/bitwrench.min.js" in scripts
        # chart.min.js is a stub, so CDN URL should be used instead
        assert CDN_URLS["chartjs"] in scripts
        assert "/ww/lib/bwclient.js" in scripts

    def test_local_mode_real_asset_stays_local(self, tmp_path, monkeypatch):
        """When a lib asset is a real file (>1024 bytes), serve locally."""
        fake_assets = tmp_path / "assets"
        fake_assets.mkdir()
        (fake_assets / "chart.min.js").write_text("x" * 2000)
        monkeypatch.setattr("webwrench._shell._ASSETS_DIR", str(fake_assets))
        scripts = _build_scripts({"chartjs"}, "local")
        assert "/ww/lib/chart.min.js" in scripts
        assert CDN_URLS["chartjs"] not in scripts

    def test_cdn_mode(self):
        scripts = _build_scripts({"chartjs"}, "cdn")
        assert CDN_URLS["bitwrench"] in scripts
        assert CDN_URLS["chartjs"] in scripts
        assert "/ww/lib/bwclient.js" in scripts

    def test_empty_libs(self):
        scripts = _build_scripts(set(), "local")
        assert "bitwrench" in scripts
        assert "bwclient" in scripts

    def test_cdn_unknown_lib_skipped(self):
        scripts = _build_scripts({"unknown_lib"}, "cdn")
        assert "unknown_lib" not in scripts

    def test_local_mode_unknown_lib_no_cdn(self):
        """Libs without a CDN URL and without a filename are simply skipped."""
        scripts = _build_scripts({"unknown_lib"}, "local")
        assert "unknown_lib" not in scripts


class TestIsStubAsset:
    def test_stub_file(self):
        assert _is_stub_asset("chart.min.js") is True

    def test_real_file(self):
        assert _is_stub_asset("bitwrench.min.js") is False

    def test_missing_file(self):
        assert _is_stub_asset("nonexistent.js") is True


class TestBuildInlineScripts:
    def test_includes_bitwrench(self):
        result = _build_inline_scripts(set())
        assert "<script>" in result

    def test_stub_chartjs_uses_cdn(self):
        result = _build_inline_scripts({"chartjs"})
        assert result.count("</script>") == 3  # bitwrench + quikdown + chartjs CDN
        assert CDN_URLS["chartjs"] in result

    def test_real_asset_inlined(self, tmp_path, monkeypatch):
        fake_assets = tmp_path / "assets"
        fake_assets.mkdir()
        (fake_assets / "bitwrench.min.js").write_text("/* bw */")
        (fake_assets / "quikdown.min.js").write_text("/* qd */")
        (fake_assets / "chart.min.js").write_text("/* real chart lib */" + "x" * 2000)
        monkeypatch.setattr("webwrench._shell._ASSETS_DIR", str(fake_assets))
        result = _build_inline_scripts({"chartjs"})
        assert CDN_URLS["chartjs"] not in result
        assert "real chart lib" in result

    def test_unknown_lib_skipped(self):
        result = _build_inline_scripts({"unknown_lib"})
        assert result.count("</script>") == 2  # bitwrench + quikdown


class TestBuildThemeCss:
    def test_no_theme(self):
        page = Page()
        assert _build_theme_css(page) == ""

    def test_with_theme(self):
        page = Page()
        page._theme = {"primary": "#333"}
        css = _build_theme_css(page)
        assert "--bw-primary" in css


class TestBuildCustomCss:
    def test_no_css(self):
        page = Page()
        assert _build_custom_css(page) == ""

    def test_with_css(self):
        page = Page()
        page._custom_css = {".box": {"color": "red"}}
        css = _build_custom_css(page)
        assert ".box {" in css
        assert "color: red;" in css


class TestBaseCss:
    def test_returns_string(self):
        css = _base_css()
        assert isinstance(css, str)
        assert "box-sizing" in css


class TestGenerateShellHtml:
    def test_basic(self):
        page = Page()
        page.add(Element("p", content="hello", element_id="p1"))
        html = generate_shell_html(page)
        assert "<!DOCTYPE html>" in html
        assert "ww-root" in html
        assert "wwBoot" in html

    def test_contains_client_id(self):
        page = Page()
        html = generate_shell_html(page, client_id="test-123")
        assert "test-123" in html

    def test_contains_title(self):
        page = Page()
        html = generate_shell_html(page, title="My App")
        assert "<title>My App</title>" in html

    def test_cdn_mode(self):
        page = Page()
        html = generate_shell_html(page, assets_mode="cdn")
        assert "cdn.jsdelivr.net" in html

    def test_local_mode(self):
        page = Page()
        html = generate_shell_html(page, assets_mode="local")
        assert "/ww/lib/" in html

    def test_init_data_is_json(self):
        page = Page()
        page.add(Element("div", content="test", element_id="d1"))
        html = generate_shell_html(page)
        # The initData should be a valid JSON array embedded in the HTML
        assert "initData" in html


class TestGenerateExportHtml:
    def test_basic(self):
        page = Page()
        page.add(Element("p", content="report", element_id="p1"))
        html = generate_export_html(page)
        assert "<!DOCTYPE html>" in html
        assert "ww-root" in html
        assert "wwRenderStatic" in html

    def test_self_contained(self):
        page = Page()
        html = generate_export_html(page)
        # Should NOT have CDN URLs or /ww/lib/ references
        assert "/ww/lib/" not in html
        assert "EventSource" not in html

    def test_contains_title(self):
        page = Page()
        html = generate_export_html(page, title="Q1 Report")
        assert "<title>Q1 Report</title>" in html

    def test_minify(self):
        page = Page()
        page.add(Element("p", content="x", element_id="p1"))
        normal = generate_export_html(page, minify=False)
        minified = generate_export_html(page, minify=True)
        assert len(minified) <= len(normal)

    def test_includes_chartjs_when_used(self):
        page = Page()
        page._libs_used.add("chartjs")
        html = generate_export_html(page)
        # Should inline Chart.js
        assert html.count("<script>") >= 2
