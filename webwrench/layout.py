"""Layout primitives: columns, tabs, accordion, sidebar, card, grid, modal.

These provide context-manager-based layout for composing UI elements.
"""

from __future__ import annotations

from typing import Any

from webwrench._context import Element, Page, WidgetHandle, get_default_page


class LayoutContainer(Element):
    """An element that can be used as a context manager to collect children."""

    def __init__(
        self,
        tag: str,
        attrs: dict[str, Any] | None = None,
        page: Page | None = None,
    ) -> None:
        super().__init__(tag, attrs=attrs, content=[])
        self._page = page or get_default_page()
        self._saved_elements: list[Element] | None = None

    def __enter__(self) -> "LayoutContainer":
        # Temporarily redirect new elements into this container
        self._saved_elements = list(self._page.elements)
        # We'll capture elements added after this point
        return self

    def __exit__(self, *exc: Any) -> None:
        if self._saved_elements is not None:
            # Elements added since __enter__ are our children
            new_elements = self._page.elements[len(self._saved_elements):]
            self._page.elements = list(self._saved_elements)
            self.content = list(new_elements)
            # Re-register widgets from children
            for el in new_elements:
                if isinstance(el, WidgetHandle) and el.id in self._page._widgets:
                    pass  # already registered
            self._saved_elements = None


class ColumnSet:
    """Returned by columns() -- index into individual columns."""

    def __init__(self, cols: list[LayoutContainer], page: Page | None = None) -> None:
        self._cols = cols
        self._page = page or get_default_page()

    def __getitem__(self, idx: int) -> LayoutContainer:
        return self._cols[idx]

    def __len__(self) -> int:
        return len(self._cols)

    def __enter__(self) -> "ColumnSet":
        return self

    def __exit__(self, *exc: Any) -> None:
        pass


class TabSet:
    """Returned by tabs() -- index into individual tab panes."""

    def __init__(self, panes: list[LayoutContainer], labels: list[str]) -> None:
        self._panes = panes
        self._labels = labels

    def __getitem__(self, idx: int) -> LayoutContainer:
        return self._panes[idx]

    def __len__(self) -> int:
        return len(self._panes)

    def __enter__(self) -> "TabSet":
        return self

    def __exit__(self, *exc: Any) -> None:
        pass


def columns(
    spec: int | list[int] = 2, page: Page | None = None
) -> ColumnSet:
    """Create a column layout.

    spec: number of equal columns (int), or a list of relative widths.
    """
    p = page or get_default_page()
    if isinstance(spec, int):
        widths = [1] * spec
    else:
        widths = spec
    total = sum(widths)
    cols: list[LayoutContainer] = []
    for w in widths:
        frac = f"{w}fr"
        col = LayoutContainer(
            "div",
            attrs={"class": "ww-column", "style": f"flex:{w}"},
            page=p,
        )
        cols.append(col)
    grid_template = " ".join(f"{w}fr" for w in widths)
    wrapper = Element(
        "div",
        attrs={
            "class": "ww-columns",
            "style": f"display:grid;grid-template-columns:{grid_template};gap:1rem",
        },
        content=cols,
    )
    p.add(wrapper)
    return ColumnSet(cols, p)


def tabs(labels: list[str], page: Page | None = None) -> TabSet:
    """Create a tabbed layout using bitwrench's makeTabs."""
    p = page or get_default_page()
    panes: list[LayoutContainer] = []
    for label in labels:
        pane = LayoutContainer(
            "div",
            attrs={"class": "ww-tab-pane", "data-tab-label": label},
            page=p,
        )
        panes.append(pane)
    tab_config = {"labels": labels, "pane_ids": [pane.id for pane in panes]}
    wrapper = Element(
        "div",
        attrs={"class": "ww-tabs bw_tabs", "data-tab-config": str(tab_config)},
        content=list(panes),
    )
    p.add(wrapper)
    return TabSet(panes, labels)


def accordion(
    title: str, open: bool = False, page: Page | None = None
) -> LayoutContainer:
    """Create a collapsible accordion section."""
    p = page or get_default_page()
    attrs: dict[str, Any] = {"class": "ww-accordion"}
    if open:
        attrs["open"] = "open"
    container = LayoutContainer("details", attrs=attrs, page=p)
    summary = Element("summary", attrs={"class": "ww-accordion-title"}, content=title)
    container.content = [summary]
    p.add(container)
    return container


def sidebar(page: Page | None = None) -> LayoutContainer:
    """Create a sidebar container."""
    p = page or get_default_page()
    container = LayoutContainer(
        "aside",
        attrs={"class": "ww-sidebar"},
        page=p,
    )
    p.add(container)
    return container


def card(title: str | None = None, page: Page | None = None) -> LayoutContainer:
    """Create a card container."""
    p = page or get_default_page()
    children: list[Any] = []
    if title:
        children.append(
            Element("div", attrs={"class": "ww-card-title"}, content=title)
        )
    container = LayoutContainer(
        "div",
        attrs={"class": "ww-card bw_card"},
        page=p,
    )
    container.content = children
    p.add(container)
    return container


def grid(template: str = "1fr 1fr", page: Page | None = None) -> LayoutContainer:
    """Create a CSS Grid container."""
    p = page or get_default_page()
    container = LayoutContainer(
        "div",
        attrs={
            "class": "ww-grid",
            "style": f"display:grid;grid-template:{template};gap:1rem",
        },
        page=p,
    )
    p.add(container)
    return container


def modal(title: str, page: Page | None = None) -> LayoutContainer:
    """Create a modal dialog container."""
    p = page or get_default_page()
    header = Element("div", attrs={"class": "ww-modal-header"}, content=title)
    container = LayoutContainer(
        "div",
        attrs={"class": "ww-modal", "role": "dialog", "aria-modal": "true"},
        page=p,
    )
    container.content = [header]
    p.add(container)
    container.close = lambda: None  # Placeholder for close action
    return container


def nav(items: list[dict[str, str]], page: Page | None = None) -> Element:
    """Create a navigation component."""
    p = page or get_default_page()
    links = []
    for item in items:
        links.append(
            Element(
                "a",
                attrs={"href": item.get("href", "#"), "class": "ww-nav-link"},
                content=item.get("text", ""),
            )
        )
    el = Element("nav", attrs={"class": "ww-nav"}, content=links)
    p.add(el)
    return el
