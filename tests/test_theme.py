"""Tests for webwrench.theme."""

import pytest

from webwrench._context import Page
from webwrench.theme import (
    PRESETS,
    css_dict_to_string,
    get_theme_palette,
    make_load_styles_call,
    make_toggle_styles_call,
    resolve_theme,
    set_custom_css,
    set_theme,
    theme_to_css,
)


class TestResolveTheme:
    def test_preset_name(self):
        palette = resolve_theme("dark")
        assert palette["primary"] == PRESETS["dark"]["primary"]

    def test_preset_with_override(self):
        palette = resolve_theme("dark", primary="#ff0000")
        assert palette["primary"] == "#ff0000"
        assert palette["background"] == PRESETS["dark"]["background"]

    def test_custom_from_kwargs(self):
        palette = resolve_theme(primary="#006666")
        # Should start from light defaults
        assert palette["primary"] == "#006666"
        assert palette["background"] == PRESETS["light"]["background"]

    def test_unknown_preset_raises(self):
        with pytest.raises(ValueError, match="Unknown theme 'nope'"):
            resolve_theme("nope")

    def test_all_presets_exist(self):
        for name in ["light", "dark", "ocean", "forest"]:
            assert name in PRESETS

    def test_no_args_returns_light(self):
        palette = resolve_theme()
        assert palette == PRESETS["light"]


class TestThemeToCss:
    def test_output(self):
        css = theme_to_css({"primary": "#333", "background": "#fff"})
        assert ":root {" in css
        assert "--bw-primary: #333;" in css
        assert "--bw-background: #fff;" in css


class TestSetTheme:
    def test_on_page(self):
        page = Page()
        palette = set_theme(page, name="ocean")
        assert palette["primary"] == PRESETS["ocean"]["primary"]
        assert page._theme == palette

    def test_on_default_page(self):
        palette = set_theme(name="dark")
        assert palette["primary"] == PRESETS["dark"]["primary"]

    def test_custom_kwargs(self):
        page = Page()
        palette = set_theme(page, primary="#abc")
        assert palette["primary"] == "#abc"


class TestGetThemePalette:
    def test_returns_none_when_not_set(self):
        page = Page()
        assert get_theme_palette(page) is None

    def test_returns_palette(self):
        page = Page()
        page._theme = {"primary": "#000"}
        assert get_theme_palette(page) == {"primary": "#000"}

    def test_default_page(self):
        # default page has no theme initially
        assert get_theme_palette() is None


class TestMakeMessages:
    def test_load_styles(self):
        msg = make_load_styles_call({"primary": "#123"})
        assert msg["type"] == "call"
        assert msg["name"] == "loadStyles"
        assert msg["args"] == [{"primary": "#123"}]

    def test_toggle_styles(self):
        msg = make_toggle_styles_call()
        assert msg["type"] == "call"
        assert msg["name"] == "toggleStyles"


class TestSetCustomCss:
    def test_set(self):
        page = Page()
        set_custom_css({".box": {"color": "red"}}, page)
        assert page._custom_css == {".box": {"color": "red"}}

    def test_merge(self):
        page = Page()
        set_custom_css({".a": {"x": "1"}}, page)
        set_custom_css({".b": {"y": "2"}}, page)
        assert ".a" in page._custom_css
        assert ".b" in page._custom_css

    def test_default_page(self):
        set_custom_css({".z": {"w": "0"}})
        from webwrench._context import get_default_page
        assert get_default_page()._custom_css is not None


class TestCssDictToString:
    def test_single_rule(self):
        css = css_dict_to_string({".card": {"border-radius": "12px"}})
        assert ".card {" in css
        assert "border-radius: 12px;" in css

    def test_multiple_rules(self):
        css = css_dict_to_string({
            ".a": {"color": "red"},
            ".b": {"margin": "0"},
        })
        assert ".a {" in css
        assert ".b {" in css
