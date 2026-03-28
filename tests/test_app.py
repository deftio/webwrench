"""Tests for webwrench.app -- App class with multi-page routing."""

import pytest

from webwrench._context import get_default_page
from webwrench.app import App, PageContext
from webwrench.state import Session, SharedState


class TestApp:
    def test_create(self):
        app = App()
        assert app._transport == "sse"
        assert isinstance(app.state, SharedState)

    def test_custom_transport(self):
        app = App(transport="websocket")
        assert app._transport == "websocket"

    def test_page_decorator(self):
        app = App()

        @app.page("/")
        def home(ctx):
            ctx.title("Home")

        assert "/" in app._pages
        assert app.get_page_handler("/") is home

    def test_get_page_handler_missing(self):
        app = App()
        assert app.get_page_handler("/missing") is None

    def test_registered_paths(self):
        app = App()

        @app.page("/")
        def home(ctx):
            pass

        @app.page("/about")
        def about(ctx):
            pass

        paths = app.registered_paths
        assert "/" in paths
        assert "/about" in paths

    def test_build_page(self):
        app = App()

        @app.page("/test")
        def test_page(ctx):
            ctx.title("Test Title")
            ctx.text("Some text")

        session = Session("c1")
        page = app.build_page("/test", session)
        assert len(page.elements) == 2
        assert page.elements[0].tag == "h1"
        assert page.elements[0].content == "Test Title"

    def test_build_page_missing_raises(self):
        app = App()
        session = Session("c1")
        with pytest.raises(ValueError, match="No page registered"):
            app.build_page("/missing", session)

    def test_shared_state(self):
        app = App()
        app.state["user"] = "alice"
        assert app.state["user"] == "alice"


class TestPageContext:
    def _make_ctx(self):
        app = App()
        session = Session("test")
        from webwrench._context import Page
        page = Page()
        return PageContext(session=session, page=page, app=app)

    def test_title(self):
        ctx = self._make_ctx()
        el = ctx.title("Hello")
        assert el.tag == "h1"
        assert len(ctx.page.elements) == 1

    def test_text(self):
        ctx = self._make_ctx()
        el = ctx.text("content")
        assert el.tag == "p"

    def test_heading(self):
        ctx = self._make_ctx()
        el = ctx.heading("Head", level=3)
        assert el.tag == "h3"

    def test_markdown(self):
        ctx = self._make_ctx()
        el = ctx.markdown("# MD")
        assert "ww-markdown" in el.attrs["class"]

    def test_code(self):
        ctx = self._make_ctx()
        el = ctx.code("x = 1", lang="python")
        assert el.tag == "pre"

    def test_image(self):
        ctx = self._make_ctx()
        el = ctx.image("pic.png", alt="pic")
        assert el.tag == "img"

    def test_divider(self):
        ctx = self._make_ctx()
        el = ctx.divider()
        assert el.tag == "hr"

    def test_table(self):
        ctx = self._make_ctx()
        el = ctx.table([{"a": 1}])
        assert "ww-table" in el.attrs["class"]

    def test_metric(self):
        ctx = self._make_ctx()
        el = ctx.metric("Rev", "$1M")
        assert "ww-metric" in el.attrs["class"]

    def test_json(self):
        ctx = self._make_ctx()
        el = ctx.json({"k": "v"})
        assert el.tag == "pre"

    def test_progress(self):
        ctx = self._make_ctx()
        el = ctx.progress(50)
        assert el.attrs["aria-valuenow"] == "50"

    def test_button(self):
        ctx = self._make_ctx()
        b = ctx.button("Go")
        assert b._widget_type == "button"

    def test_button_on_click(self):
        ctx = self._make_ctx()
        clicks = []
        b = ctx.button("Go", on_click=lambda: clicks.append(1))
        b._fire_click()
        assert clicks == [1]

    def test_input(self):
        ctx = self._make_ctx()
        i = ctx.input("Name")
        assert i._widget_type == "input"

    def test_slider(self):
        ctx = self._make_ctx()
        s = ctx.slider("Vol", min=0, max=100, value=50)
        assert s._widget_type == "slider"

    def test_select(self):
        ctx = self._make_ctx()
        s = ctx.select("Option", ["a", "b"])
        assert s._widget_type == "select"

    def test_checkbox(self):
        ctx = self._make_ctx()
        c = ctx.checkbox("Agree")
        assert c._widget_type == "checkbox"

    def test_chart(self):
        ctx = self._make_ctx()
        c = ctx.chart([1, 2, 3])
        assert c._chart_type == "bar"

    def test_plot(self):
        ctx = self._make_ctx()
        p = ctx.plot([1, 2])
        assert p._chart_type == "line"

    def test_redirect(self):
        ctx = self._make_ctx()
        ctx.redirect("/other")
        msgs = ctx.session.drain_messages()
        assert len(msgs) == 1
        assert msgs[0]["name"] == "redirect"
        assert msgs[0]["args"] == ["/other"]

    def test_set_theme(self):
        ctx = self._make_ctx()
        ctx.set_theme("dark")
        msgs = ctx.session.drain_messages()
        assert len(msgs) == 1
        assert msgs[0]["name"] == "loadStyles"

    def test_screenshot(self):
        ctx = self._make_ctx()
        ctx.screenshot("shot.png")
        msgs = ctx.session.drain_messages()
        assert msgs[0]["name"] == "wwScreenshot"

    def test_compute(self):
        ctx = self._make_ctx()
        result = ctx.compute("key", lambda: 42)
        assert result == 42

    def test_recompute(self):
        ctx = self._make_ctx()
        ctx.compute("key", lambda: 1)
        result = ctx.recompute("key", lambda: 2)
        assert result == 2

    def test_remove(self):
        ctx = self._make_ctx()
        ctx.remove("#old-el")
        msgs = ctx.session.drain_messages()
        assert msgs[0] == {"type": "remove", "target": "#old-el"}

    def test_patch(self):
        ctx = self._make_ctx()
        ctx.patch("el1", content="new", attr={"class": "x"})
        msgs = ctx.session.drain_messages()
        assert msgs[0]["type"] == "patch"
        assert msgs[0]["content"] == "new"
        assert msgs[0]["attr"] == {"class": "x"}

    def test_patch_content_only(self):
        ctx = self._make_ctx()
        ctx.patch("el1", content="text")
        msgs = ctx.session.drain_messages()
        assert "attr" not in msgs[0]

    def test_patch_attr_only(self):
        ctx = self._make_ctx()
        ctx.patch("el1", attr={"style": "color:red"})
        msgs = ctx.session.drain_messages()
        assert "content" not in msgs[0]

    def test_state_access(self):
        ctx = self._make_ctx()
        ctx.state.foo = "bar"
        assert ctx.state.foo == "bar"
