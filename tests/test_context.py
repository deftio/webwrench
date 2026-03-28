"""Tests for webwrench._context -- Element, WidgetHandle, Page, context vars."""

import pytest

from webwrench._context import (
    Element,
    Page,
    WidgetHandle,
    get_active_session,
    get_default_page,
    reset_default_page,
    restore_active_session,
    set_active_session,
)
from webwrench.state import Session


class TestElement:
    def test_auto_id(self):
        a = Element("div")
        b = Element("span")
        assert a.id.startswith("ww-")
        assert b.id.startswith("ww-")
        assert a.id != b.id

    def test_explicit_id(self):
        e = Element("div", element_id="my-el")
        assert e.id == "my-el"

    def test_to_taco_minimal(self):
        e = Element("br", element_id="x")
        taco = e.to_taco()
        assert taco["t"] == "br"
        assert taco["a"]["id"] == "x"
        assert "c" not in taco

    def test_to_taco_string_content(self):
        e = Element("p", content="hello", element_id="p1")
        taco = e.to_taco()
        assert taco["c"] == "hello"

    def test_to_taco_child_element(self):
        child = Element("span", content="inner", element_id="c1")
        parent = Element("div", content=child, element_id="p1")
        taco = parent.to_taco()
        assert taco["c"]["t"] == "span"
        assert taco["c"]["c"] == "inner"

    def test_to_taco_list_content(self):
        children = [
            Element("li", content="a", element_id="li1"),
            "plain text",
        ]
        e = Element("ul", content=children, element_id="ul1")
        taco = e.to_taco()
        assert isinstance(taco["c"], list)
        assert taco["c"][0]["t"] == "li"
        assert taco["c"][1] == "plain text"

    def test_to_taco_preserves_attrs(self):
        e = Element("div", attrs={"class": "foo"}, element_id="d1")
        taco = e.to_taco()
        assert taco["a"]["class"] == "foo"
        assert taco["a"]["id"] == "d1"

    def test_reset_counter(self):
        Element.reset_counter()
        e1 = Element("div")
        assert e1.id == "ww-1"
        Element.reset_counter()
        e2 = Element("div")
        assert e2.id == "ww-1"

    def test_attrs_default_empty(self):
        e = Element("div", element_id="x")
        assert e.attrs == {}

    def test_attrs_not_shared_between_instances(self):
        a = Element("div", attrs={"class": "a"}, element_id="a")
        b = Element("div", attrs={"class": "b"}, element_id="b")
        assert a.attrs["class"] == "a"
        assert b.attrs["class"] == "b"


class TestWidgetHandle:
    def test_default_value(self):
        w = WidgetHandle("button", default_value="x")
        assert w.value == "x"

    def test_value_from_session(self):
        w = WidgetHandle("input", default_value="default", element_id="w1")
        session = Session("test")
        session.set_widget_value("w1", "override")
        token = set_active_session(session)
        try:
            assert w.value == "override"
        finally:
            restore_active_session(token)

    def test_value_fallback_to_default_when_no_session(self):
        w = WidgetHandle("input", default_value=42)
        assert w.value == 42

    def test_on_change_decorator(self):
        w = WidgetHandle("slider")
        calls = []

        @w.on_change
        def handler(val):
            calls.append(val)

        w._fire_change(10)
        assert calls == [10]

    def test_on_click_decorator(self):
        w = WidgetHandle("button")
        clicked = []

        @w.on_click
        def handler():
            clicked.append(True)

        w._fire_click()
        assert clicked == [True]

    def test_multiple_callbacks(self):
        w = WidgetHandle("button")
        results = []
        w.on_click(lambda: results.append("a"))
        w.on_click(lambda: results.append("b"))
        w._fire_click()
        assert results == ["a", "b"]

    def test_multiple_change_callbacks(self):
        w = WidgetHandle("slider")
        results = []
        w.on_change(lambda v: results.append(v))
        w.on_change(lambda v: results.append(v * 2))
        w._fire_change(5)
        assert results == [5, 10]

    def test_update_sets_default(self):
        w = WidgetHandle("slider", default_value=0)
        w.update(50)
        assert w._default_value == 50

    def test_update_sends_patch_with_session(self):
        w = WidgetHandle("div", element_id="el1")
        session = Session("test")
        token = set_active_session(session)
        try:
            w.update("new-value")
            messages = session.drain_messages()
            assert len(messages) == 1
            assert messages[0]["type"] == "patch"
            assert messages[0]["target"] == "el1"
        finally:
            restore_active_session(token)

    def test_update_no_session_no_crash(self):
        w = WidgetHandle("div")
        w.update("val")  # Should not raise

    def test_widget_type(self):
        w = WidgetHandle("div", widget_type="slider")
        assert w._widget_type == "slider"


class TestPage:
    def test_add_element(self):
        page = Page()
        el = Element("div")
        result = page.add(el)
        assert result is el
        assert el in page.elements

    def test_add_widget_tracks_in_dict(self):
        page = Page()
        w = WidgetHandle("button", element_id="btn1")
        page.add(w)
        assert page.get_widget("btn1") is w

    def test_get_widget_missing(self):
        page = Page()
        assert page.get_widget("nonexistent") is None

    def test_to_taco_list(self):
        page = Page()
        page.add(Element("p", content="hi", element_id="p1"))
        page.add(Element("hr", element_id="hr1"))
        taco_list = page.to_taco_list()
        assert len(taco_list) == 2
        assert taco_list[0]["t"] == "p"
        assert taco_list[1]["t"] == "hr"

    def test_require_lib(self):
        page = Page()
        page.require_lib("chartjs")
        page.require_lib("d3")
        assert "chartjs" in page._libs_used
        assert "d3" in page._libs_used

    def test_reset(self):
        page = Page()
        page.add(Element("div"))
        page._theme = "dark"
        page._custom_css = {"a": {"b": "c"}}
        page._libs_used.add("chartjs")
        page.reset()
        assert page.elements == []
        assert page._widgets == {}
        assert page._theme is None
        assert page._custom_css is None
        assert page._libs_used == set()


class TestContextVars:
    def test_default_is_none(self):
        assert get_active_session() is None

    def test_set_and_get(self):
        session = Session("ctx-test")
        token = set_active_session(session)
        try:
            assert get_active_session() is session
        finally:
            restore_active_session(token)

    def test_restore(self):
        session = Session("ctx-test")
        token = set_active_session(session)
        restore_active_session(token)
        assert get_active_session() is None


class TestDefaultPage:
    def test_get_default_page(self):
        page = get_default_page()
        assert isinstance(page, Page)

    def test_reset_clears(self):
        page = get_default_page()
        page.add(Element("div"))
        assert len(page.elements) == 1
        reset_default_page()
        assert len(page.elements) == 0
