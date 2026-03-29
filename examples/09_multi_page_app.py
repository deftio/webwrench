"""09 - Multi-Page App

Uses App mode with @app.page() decorators to register three URL routes.
The server routes GET requests to the matching handler, builds a fresh
Page, and serves it. Each handler receives a PageContext (ctx) with the
same API as module-level functions (ctx.title, ctx.chart, etc.).

Concepts: ww.App(), @app.page(), PageContext, app.serve(),
          cross-page navigation with ww.nav().

Run: python examples/09_multi_page_app.py
     then visit http://localhost:6502, /about, /contact
"""

import webwrench as ww
from webwrench.display import metric
from webwrench.layout import columns, nav

app = ww.App()

# Shared navigation for all pages
NAV_ITEMS = [
    {"text": "Home", "href": "/"},
    {"text": "About", "href": "/about"},
    {"text": "Contact", "href": "/contact"},
]


@app.page("/")
def home(ctx):
    ctx.title("Home")
    nav(NAV_ITEMS, page=ctx.page)
    ctx.divider()
    ctx.text(
        "Welcome to the multi-page webwrench demo. Each page is a "
        "separate Python function decorated with @app.page(path). "
        "Click the links above to navigate between pages."
    )
    ctx.heading("Quick Stats", level=2)
    kpi = columns(3, page=ctx.page)
    with kpi[0]:
        metric("Active Users", "1,204", delta="+56", delta_color="green", page=ctx.page)
    with kpi[1]:
        metric("Signups Today", "83", delta="+12", delta_color="green", page=ctx.page)
    with kpi[2]:
        metric("Bounce Rate", "24%", delta="-3%", delta_color="green", page=ctx.page)
    ctx.chart(
        [30, 45, 28, 60, 52, 71],
        type="line",
        labels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        title="Daily Signups",
    )


@app.page("/about")
def about(ctx):
    ctx.title("About")
    nav(NAV_ITEMS, page=ctx.page)
    ctx.divider()
    ctx.text(
        "webwrench is a Python UI framework for building interactive web "
        "dashboards and self-contained HTML reports. It uses bitwrench.js "
        "on the frontend and communicates via the bwserve protocol (SSE + POST)."
    )
    ctx.heading("Features", level=2)
    ctx.markdown(
        "- **Zero runtime Python dependencies** -- only the standard library\n"
        "- **Script mode** for quick dashboards (ww.title / ww.serve)\n"
        "- **App mode** for multi-page routing (@app.page)\n"
        "- Charts, tables, widgets, and layout primitives\n"
        "- Static HTML export with ww.export()\n"
        "- Theme presets and custom CSS"
    )
    ctx.heading("App mode vs Script mode", level=2)
    ctx.text(
        "Script mode uses module-level calls (ww.title, ww.chart) on a "
        "shared default page. App mode gives each URL its own handler "
        "function and a PageContext object scoped to that request."
    )
    ctx.code(
        '@app.page("/about")\n'
        "def about(ctx):\n"
        '    ctx.title("About")\n'
        '    ctx.text("Page content here")',
        lang="python",
    )


@app.page("/contact")
def contact(ctx):
    ctx.title("Contact Us")
    nav(NAV_ITEMS, page=ctx.page)
    ctx.divider()
    ctx.text("Get in touch with the team.")
    ctx.table([
        {"Name": "Support", "Email": "support@example.com", "Hours": "9am-5pm ET"},
        {"Name": "Sales", "Email": "sales@example.com", "Hours": "9am-6pm ET"},
        {"Name": "Engineering", "Email": "eng@example.com", "Hours": "10am-6pm PT"},
    ])


if __name__ == "__main__":
    app.serve()
