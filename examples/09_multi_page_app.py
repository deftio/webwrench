"""09 - Multi-Page App

Uses App mode with the @app.page decorator to register three pages:
home (/), about (/about), and contact (/contact). Each page handler
receives a PageContext (ctx) with the same API as module-level functions.

Run: python examples/09_multi_page_app.py
"""

import webwrench as ww

app = ww.App()


@app.page("/")
def home(ctx):
    ctx.title("Home")
    ctx.text("Welcome to the multi-page webwrench demo.")
    ctx.markdown(
        "Navigate to **About** or **Contact** using the paths below:\n"
        "- [About](/about)\n"
        "- [Contact](/contact)"
    )
    ctx.divider()
    ctx.heading("Quick Stats", level=2)
    ctx.metric("Active Users", "1,204", delta="+56", delta_color="green")
    ctx.chart(
        [30, 45, 28, 60, 52, 71],
        type="line",
        labels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        title="Daily Signups",
    )


@app.page("/about")
def about(ctx):
    ctx.title("About")
    ctx.text(
        "webwrench is a Python UI framework for building interactive web "
        "dashboards and self-contained HTML reports. It uses bitwrench.js "
        "on the frontend and communicates via the bwserve protocol."
    )
    ctx.heading("Features", level=2)
    ctx.markdown(
        "- Zero runtime Python dependencies\n"
        "- Script mode and App mode\n"
        "- Charts, tables, widgets, and layout primitives\n"
        "- Static HTML export\n"
        "- Theme presets and custom CSS"
    )


@app.page("/contact")
def contact(ctx):
    ctx.title("Contact Us")
    ctx.text("Get in touch with the team.")
    ctx.table([
        {"Name": "Support", "Email": "support@example.com"},
        {"Name": "Sales", "Email": "sales@example.com"},
        {"Name": "Engineering", "Email": "eng@example.com"},
    ])


if __name__ == "__main__":
    app.serve()
