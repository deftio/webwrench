"""Core element model and page context.

Defines the Element base class, WidgetHandle, and Page container.
Uses contextvars for per-session dispatch in callbacks.
"""

from __future__ import annotations

import contextvars
from typing import Any

from webwrench.state import Session


# Context variable: the session currently handling a callback.
_active_session: contextvars.ContextVar[Session | None] = contextvars.ContextVar(
    "_active_session", default=None
)


def get_active_session() -> Session | None:
    """Return the currently active session, or None."""
    return _active_session.get()


def set_active_session(session: Session | None) -> contextvars.Token:
    """Set the active session. Returns a token to restore the previous value."""
    return _active_session.set(session)


def restore_active_session(token: contextvars.Token) -> None:
    """Restore the active session to its previous value using a token."""
    _active_session.reset(token)


class Element:
    """Base class for all UI elements.

    Each element has a unique ID, a tag, optional attributes, and optional
    content. It can serialize itself to a TACO dict.
    """

    _counter: int = 0

    def __init__(
        self,
        tag: str,
        attrs: dict[str, Any] | None = None,
        content: Any = None,
        element_id: str | None = None,
    ) -> None:
        if element_id is None:
            Element._counter += 1
            element_id = f"ww-{Element._counter}"
        self.id = element_id
        self.tag = tag
        self.attrs = dict(attrs) if attrs else {}
        self.content = content

    def to_taco(self) -> dict[str, Any]:
        """Convert to a TACO dict."""
        taco: dict[str, Any] = {"t": self.tag}
        attrs = dict(self.attrs)
        attrs["id"] = self.id
        taco["a"] = attrs
        if self.content is not None:
            if isinstance(self.content, list):
                taco["c"] = [
                    c.to_taco() if isinstance(c, Element) else c
                    for c in self.content
                ]
            elif isinstance(self.content, Element):
                taco["c"] = self.content.to_taco()
            else:
                taco["c"] = self.content
        return taco

    @classmethod
    def reset_counter(cls) -> None:
        """Reset the ID counter (for testing)."""
        cls._counter = 0


class WidgetHandle(Element):
    """Handle returned by widget-creating functions.

    Provides .value, .on_change(), .on_click(), and .update().
    """

    def __init__(
        self,
        tag: str,
        attrs: dict[str, Any] | None = None,
        content: Any = None,
        element_id: str | None = None,
        default_value: Any = None,
        widget_type: str = "generic",
    ) -> None:
        super().__init__(tag, attrs, content, element_id)
        self._default_value = default_value
        self._widget_type = widget_type
        self._on_change_callbacks: list[Any] = []
        self._on_click_callbacks: list[Any] = []

    @property
    def value(self) -> Any:
        session = _active_session.get()
        if session is not None:
            return session.get_widget_value(self.id, self._default_value)
        return self._default_value

    def on_change(self, callback: Any) -> Any:
        """Register a callback for value changes. Works as a decorator."""
        self._on_change_callbacks.append(callback)
        return callback

    def on_click(self, callback: Any) -> Any:
        """Register a click callback. Works as a decorator."""
        self._on_click_callbacks.append(callback)
        return callback

    def update(self, value: Any) -> None:
        """Update the widget's display value."""
        self._default_value = value
        session = _active_session.get()
        if session is not None:
            session.send_patch(self.id, value)

    def _fire_change(self, value: Any) -> None:
        """Invoke all on_change callbacks."""
        for cb in self._on_change_callbacks:
            cb(value)

    def _fire_click(self) -> None:
        """Invoke all on_click callbacks."""
        for cb in self._on_click_callbacks:
            cb()


class Page:
    """Collects elements in order for rendering."""

    def __init__(self) -> None:
        self.elements: list[Element] = []
        self._widgets: dict[str, WidgetHandle] = {}
        self._theme: str | dict[str, Any] | None = None
        self._custom_css: dict[str, Any] | None = None
        self._libs_used: set[str] = set()

    def add(self, element: Element) -> Element:
        """Add an element to this page."""
        self.elements.append(element)
        if isinstance(element, WidgetHandle):
            self._widgets[element.id] = element
        return element

    def get_widget(self, widget_id: str) -> WidgetHandle | None:
        """Look up a widget by ID."""
        return self._widgets.get(widget_id)

    def to_taco_list(self) -> list[dict[str, Any]]:
        """Serialize all elements to TACO dicts."""
        return [el.to_taco() for el in self.elements]

    def require_lib(self, lib: str) -> None:
        """Record that a JS library is needed (e.g. 'chartjs')."""
        self._libs_used.add(lib)

    def reset(self) -> None:
        """Clear all elements and state."""
        self.elements.clear()
        self._widgets.clear()
        self._theme = None
        self._custom_css = None
        self._libs_used.clear()
        Element.reset_counter()


# Module-level default page used in script mode.
_default_page = Page()


def get_default_page() -> Page:
    """Return the module-level default page."""
    return _default_page


def reset_default_page() -> None:
    """Reset the default page (used between tests / script runs)."""
    _default_page.reset()
