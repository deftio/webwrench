"""Display elements: title, text, heading, markdown, divider, image, table, code, html.

Each function creates an Element and adds it to the given page (or the default page).
"""

from __future__ import annotations

import html as html_mod
import json
from typing import Any

from webwrench._context import Element, Page, get_default_page


def title(text: str, page: Page | None = None) -> Element:
    """Create an <h1> title element."""
    p = page or get_default_page()
    el = Element("h1", content=text)
    p.add(el)
    return el


def heading(text: str, level: int = 2, page: Page | None = None) -> Element:
    """Create an <h2>..<h6> heading element."""
    level = max(1, min(6, level))
    p = page or get_default_page()
    el = Element(f"h{level}", content=text)
    p.add(el)
    return el


def text(content: str, page: Page | None = None) -> Element:
    """Create a <p> text element."""
    p = page or get_default_page()
    el = Element("p", content=content)
    p.add(el)
    return el


def markdown(md_string: str, page: Page | None = None) -> Element:
    """Create a markdown element.

    The markdown is sent as-is in a div with class 'ww-markdown'.
    bitwrench handles rendering on the client side.
    """
    p = page or get_default_page()
    el = Element("div", attrs={"class": "ww-markdown", "data-md": md_string}, content=md_string)
    p.add(el)
    return el


def code(code_string: str, lang: str = "python", page: Page | None = None) -> Element:
    """Create a syntax-highlighted code block."""
    p = page or get_default_page()
    pre = Element(
        "pre",
        attrs={"class": f"ww-code language-{lang}"},
        content=Element("code", content=html_mod.escape(code_string)),
    )
    p.add(pre)
    return pre


def html_element(raw_html: str, raw: bool = False, page: Page | None = None) -> Element:
    """Insert HTML content.

    If raw=True, the HTML is inserted as-is (use with care).
    Otherwise it is escaped.
    """
    p = page or get_default_page()
    content = raw_html if raw else html_mod.escape(raw_html)
    el = Element("div", attrs={"class": "ww-html"}, content=content)
    if raw:
        el.attrs["data-raw"] = "true"
    p.add(el)
    return el


def image(
    src: str,
    alt: str = "",
    width: int | str | None = None,
    page: Page | None = None,
) -> Element:
    """Create an image element."""
    p = page or get_default_page()
    attrs: dict[str, Any] = {"src": src, "alt": alt}
    if width is not None:
        attrs["width"] = str(width)
    el = Element("img", attrs=attrs)
    p.add(el)
    return el


def divider(page: Page | None = None) -> Element:
    """Create an <hr> divider."""
    p = page or get_default_page()
    el = Element("hr")
    p.add(el)
    return el


def table(
    data: Any,
    sortable: bool = False,
    searchable: bool = False,
    paginate: int | None = None,
    page: Page | None = None,
) -> Element:
    """Create a data table.

    data can be:
      - list of dicts (records)
      - list of lists (rows, first row = headers)
      - a pandas DataFrame (detected at runtime)
    """
    p = page or get_default_page()

    headers, rows = _normalize_table_data(data)

    table_config = {
        "headers": headers,
        "rows": rows,
        "sortable": sortable,
        "searchable": searchable,
    }
    if paginate is not None:
        table_config["paginate"] = paginate

    attrs: dict[str, Any] = {
        "class": "ww-table bw_table",
        "data-config": json.dumps(table_config),
    }
    el = Element("div", attrs=attrs, content=_build_table_taco(headers, rows))
    p.add(el)
    return el


def _normalize_table_data(data: Any) -> tuple[list[str], list[list[Any]]]:
    """Convert various data formats to (headers, rows)."""
    # Check for pandas DataFrame
    if hasattr(data, "columns") and hasattr(data, "iterrows"):
        headers = list(data.columns)
        rows = [list(row) for _, row in data.iterrows()]
        return headers, rows

    if isinstance(data, list) and len(data) > 0:
        if isinstance(data[0], dict):
            headers = list(data[0].keys())
            rows = [[record.get(h) for h in headers] for record in data]
            return headers, rows
        if isinstance(data[0], (list, tuple)):
            headers = [str(h) for h in data[0]]
            rows = [list(row) for row in data[1:]]
            return headers, rows

    return [], []


def _build_table_taco(
    headers: list[str], rows: list[list[Any]]
) -> list[dict[str, Any]]:
    """Build TACO children for a table element."""
    thead = {
        "t": "thead",
        "c": [
            {
                "t": "tr",
                "c": [{"t": "th", "c": str(h)} for h in headers],
            }
        ],
    }
    tbody_rows = []
    for row in rows:
        tbody_rows.append(
            {"t": "tr", "c": [{"t": "td", "c": str(cell)} for cell in row]}
        )
    tbody = {"t": "tbody", "c": tbody_rows}
    return [{"t": "table", "a": {"class": "bw_table"}, "c": [thead, tbody]}]


def metric(
    label: str,
    value: str,
    delta: str | None = None,
    delta_color: str | None = None,
    page: Page | None = None,
) -> Element:
    """Create a KPI / metric card."""
    p = page or get_default_page()
    children: list[Any] = [
        Element("div", attrs={"class": "ww-metric-label"}, content=label),
        Element("div", attrs={"class": "ww-metric-value"}, content=value),
    ]
    if delta is not None:
        delta_attrs: dict[str, Any] = {"class": "ww-metric-delta"}
        if delta_color:
            delta_attrs["style"] = f"color:{delta_color}"
        children.append(Element("div", attrs=delta_attrs, content=delta))
    el = Element("div", attrs={"class": "ww-metric"}, content=children)
    p.add(el)
    return el


def json_viewer(
    data: Any, collapsed: int = 1, page: Page | None = None
) -> Element:
    """Display JSON data in a collapsible viewer."""
    p = page or get_default_page()
    el = Element(
        "pre",
        attrs={"class": "ww-json", "data-collapsed": str(collapsed)},
        content=json.dumps(data, indent=2, default=str),
    )
    p.add(el)
    return el


def progress(
    value: int = 0, max_val: int = 100, page: Page | None = None
) -> Element:
    """Create a progress bar. Returns a handle that supports .update(n)."""
    from webwrench._context import WidgetHandle

    p = page or get_default_page()
    handle = WidgetHandle(
        "div",
        attrs={
            "class": "ww-progress",
            "role": "progressbar",
            "aria-valuenow": str(value),
            "aria-valuemax": str(max_val),
        },
        content=Element(
            "div",
            attrs={
                "class": "ww-progress-bar",
                "style": f"width:{int(value / max_val * 100)}%",
            },
        ),
        default_value=value,
        widget_type="progress",
    )
    handle._max_val = max_val
    p.add(handle)
    return handle


def toast(
    message: str,
    type: str = "info",
    duration: int = 3000,
    page: Page | None = None,
) -> dict[str, Any]:
    """Queue a toast notification.

    Returns the bwserve call message (not an element, since toasts are ephemeral).
    """
    p = page or get_default_page()
    return {
        "type": "call",
        "name": "wwToast",
        "args": [message, type, duration],
    }
