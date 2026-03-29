"""App class for multi-page webwrench applications.

Provides decorator-based routing, shared state, and per-page contexts.
"""

from __future__ import annotations

from typing import Any, Callable

from webwrench._context import Element, Page, WidgetHandle, restore_active_session, set_active_session
from webwrench.state import Session, SessionManager, SharedState


class PageContext:
    """Per-request context passed to page handler functions.

    Provides the same API as the module-level functions (title, text, chart, etc.)
    but scoped to a specific page and session.
    """

    def __init__(self, session: Session, page: Page, app: "App") -> None:
        self.session = session
        self.page = page
        self.app = app
        self.state = session.state

    # Display elements

    def title(self, text: str) -> Element:
        from webwrench.display import title
        return title(text, page=self.page)

    def text(self, content: str) -> Element:
        from webwrench.display import text
        return text(content, page=self.page)

    def heading(self, text: str, level: int = 2) -> Element:
        from webwrench.display import heading
        return heading(text, level=level, page=self.page)

    def markdown(self, md: str) -> Element:
        from webwrench.display import markdown
        return markdown(md, page=self.page)

    def code(self, code_string: str, lang: str = "python") -> Element:
        from webwrench.display import code
        return code(code_string, lang=lang, page=self.page)

    def image(self, src: str, alt: str = "", width: Any = None) -> Element:
        from webwrench.display import image
        return image(src, alt=alt, width=width, page=self.page)

    def divider(self) -> Element:
        from webwrench.display import divider
        return divider(page=self.page)

    def table(self, data: Any, **kwargs: Any) -> Element:
        from webwrench.display import table
        return table(data, page=self.page, **kwargs)

    def metric(self, label: str, value: str, **kwargs: Any) -> Element:
        from webwrench.display import metric
        return metric(label, value, page=self.page, **kwargs)

    def json(self, data: Any, collapsed: int = 1) -> Element:
        from webwrench.display import json_viewer
        return json_viewer(data, collapsed=collapsed, page=self.page)

    def progress(self, value: int = 0, max_val: int = 100) -> Element:
        from webwrench.display import progress
        return progress(value, max_val=max_val, page=self.page)

    # Widgets

    def button(self, label: str, on_click: Any = None) -> WidgetHandle:
        from webwrench.widgets import button
        return button(label, on_click=on_click, page=self.page)

    def input(self, label: str, **kwargs: Any) -> WidgetHandle:
        from webwrench.widgets import input_widget
        return input_widget(label, page=self.page, **kwargs)

    def slider(self, label: str, **kwargs: Any) -> WidgetHandle:
        from webwrench.widgets import slider
        return slider(label, page=self.page, **kwargs)

    def select(self, label: str, options: list[str], **kwargs: Any) -> WidgetHandle:
        from webwrench.widgets import select
        return select(label, options, page=self.page, **kwargs)

    def checkbox(self, label: str, **kwargs: Any) -> WidgetHandle:
        from webwrench.widgets import checkbox
        return checkbox(label, page=self.page, **kwargs)

    # Charts

    def chart(self, data: Any = None, **kwargs: Any) -> Any:
        from webwrench.charts import chart
        return chart(data, page=self.page, **kwargs)

    def plot(self, data: Any, **kwargs: Any) -> Any:
        from webwrench.charts import plot
        return plot(data, page=self.page, **kwargs)

    # Actions

    def redirect(self, url: str) -> None:
        """Navigate to another page."""
        self.session.send_message(
            {"type": "call", "name": "redirect", "args": [url]}
        )

    def set_theme(self, name: str) -> None:
        """Set the theme for this session."""
        from webwrench.theme import resolve_theme, make_load_styles_call
        palette = resolve_theme(name)
        msg = make_load_styles_call(palette)
        self.session.send_message(msg)

    def screenshot(self, filename: str = "screenshot.png") -> None:
        """Request a screenshot from the client."""
        from webwrench.export import screenshot
        msg = screenshot(filename)
        self.session.send_message(msg)

    def compute(self, key: str, func: Any) -> Any:
        """Compute and cache a value for this session."""
        return self.session.compute(key, func)

    def recompute(self, key: str, func: Any) -> Any:
        """Invalidate and recompute a cached value."""
        return self.session.recompute(key, func)

    def remove(self, selector: str) -> None:
        """Remove an element from the DOM."""
        self.session.send_message({"type": "remove", "target": selector})

    def patch(self, target: str, content: Any = None, attr: dict | None = None) -> None:
        """Patch an element's content or attributes."""
        msg: dict[str, Any] = {"type": "patch", "target": target}
        if content is not None:
            msg["content"] = content
        if attr is not None:
            msg["attr"] = attr
        self.session.send_message(msg)


class App:
    """Multi-page webwrench application."""

    def __init__(self, transport: str = "sse") -> None:
        self._pages: dict[str, Callable[..., Any]] = {}
        self._transport = transport
        self.state = SharedState()
        self._sessions = SessionManager()

    def page(self, path: str, **kwargs: Any) -> Callable[..., Any]:
        """Decorator to register a page handler.

        Usage:
            @app.page('/')
            def home(ctx):
                ctx.title("Home")
        """
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self._pages[path] = func
            return func
        return decorator

    def get_page_handler(self, path: str) -> Callable[..., Any] | None:
        """Look up the handler for a given path."""
        return self._pages.get(path)

    def build_page(self, path: str, session: Session) -> Page:
        """Build a page by running its handler with a fresh PageContext."""
        handler = self._pages.get(path)
        if handler is None:
            raise ValueError(f"No page registered for path '{path}'")

        page = Page()
        ctx = PageContext(session=session, page=page, app=self)
        token = set_active_session(session)
        try:
            handler(ctx)
        finally:
            restore_active_session(token)
        return page

    @property
    def registered_paths(self) -> list[str]:
        """Return all registered page paths."""
        return list(self._pages.keys())

    def serve(self, host: str = "0.0.0.0", port: int = 6502, **kwargs: Any) -> None:
        """Start the app server (blocking)."""
        from webwrench.server import serve
        serve(host=host, port=port, app=self, **kwargs)
