"""webwrench -- Python UI framework for interactive web dashboards and HTML reports.

Build interactive dashboards and self-contained HTML reports with pure Python.
Powered by bitwrench.js on the frontend, using the bwserve protocol for
server-driven updates.

Quick start (script mode):

    import webwrench as ww

    ww.title("Hello World")
    ww.text("My first webwrench app")
    ww.serve()

Static export:

    import webwrench as ww

    ww.title("Report")
    ww.chart([12, 19, 3], type='bar', labels=['A', 'B', 'C'])
    ww.export('report.html')

Multi-page app:

    import webwrench as ww

    app = ww.App()

    @app.page('/')
    def home(ctx):
        ctx.title("Home")
        ctx.text("Welcome")

    app.serve()
"""

from __future__ import annotations

from webwrench._context import Page, get_default_page, reset_default_page

# Re-export the App class
from webwrench.app import App

# Re-export options
from webwrench.options import options

# ---------------------------------------------------------------------------
# Display elements
# ---------------------------------------------------------------------------

from webwrench.display import (
    code,
    divider,
    heading,
    html_element as html,
    image,
    json_viewer as json,
    markdown,
    metric,
    progress,
    table,
    text,
    title,
    toast,
)

# ---------------------------------------------------------------------------
# Input widgets
# ---------------------------------------------------------------------------

from webwrench.widgets import (
    button,
    checkbox,
    color_picker,
    date_picker,
    file_upload,
    input_widget as input,
    number,
    radio,
    select,
    slider,
    textarea,
)

# ---------------------------------------------------------------------------
# Charts / visualization
# ---------------------------------------------------------------------------

from webwrench.charts import chart, plot

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

from webwrench.layout import (
    accordion,
    card,
    columns,
    grid,
    modal,
    nav,
    sidebar,
    tabs,
)

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

from webwrench.theme import (
    css_dict_to_string as _css_to_str,
    set_custom_css as _set_css,
    set_theme as _set_theme,
)


def theme(name: str | None = None, **kwargs: str) -> dict[str, str]:
    """Set the theme for the current page.

    Use a preset name:
        ww.theme('dark')
        ww.theme('ocean')

    Or custom colors:
        ww.theme(primary='#006666', secondary='#333')
    """
    return _set_theme(name=name, **kwargs)


def toggle_theme() -> dict:
    """Toggle between light and dark themes at runtime.

    Returns a bwserve 'call' message for bw.toggleStyles().
    """
    from webwrench.theme import make_toggle_styles_call
    return make_toggle_styles_call()


def css(rules: dict) -> None:
    """Inject custom CSS rules.

    Example:
        ww.css({'.my-card': {'border-radius': '12px'}})
    """
    _set_css(rules)


# ---------------------------------------------------------------------------
# Export / screenshot / download
# ---------------------------------------------------------------------------

from webwrench.export import (
    download,
    export,
    export_pdf,
    export_string,
    screenshot,
)

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

from webwrench.server import serve

# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------

__version__ = "0.1.0"

__all__ = [
    # Core
    "App",
    "options",
    "__version__",
    # Display
    "title",
    "heading",
    "text",
    "markdown",
    "code",
    "html",
    "image",
    "divider",
    "table",
    "metric",
    "json",
    "progress",
    "toast",
    # Widgets
    "button",
    "input",
    "textarea",
    "slider",
    "select",
    "checkbox",
    "radio",
    "file_upload",
    "date_picker",
    "color_picker",
    "number",
    # Charts
    "chart",
    "plot",
    # Layout
    "columns",
    "tabs",
    "accordion",
    "sidebar",
    "card",
    "grid",
    "modal",
    "nav",
    # Theme
    "theme",
    "toggle_theme",
    "css",
    # Export
    "export",
    "export_string",
    "export_pdf",
    "screenshot",
    "download",
    # Server
    "serve",
]
