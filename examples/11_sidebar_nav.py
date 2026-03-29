"""11 - Sidebar Navigation

Uses ww.sidebar() inside a column layout to create a classic
sidebar + main-content dashboard. The sidebar holds navigation
links and branding; the main area holds metrics, a chart, and
an activity table.

Concepts: ww.sidebar(), ww.columns([1, 3]), ww.nav(),
          ww.metric(), ww.chart(), ww.table().

Run: python examples/11_sidebar_nav.py
"""

import webwrench as ww

ww.theme("ocean")

# -- Header --
ww.title("Sidebar Navigation")
ww.text(
    "The sidebar + main-content pattern uses ww.columns([1, 3]) for a "
    "1:3 width ratio, with ww.sidebar() as a context manager in the "
    "narrow column. The sidebar provides navigation links and branding "
    "while the main column holds the dashboard content."
)

ww.divider()

# -- Layout: sidebar (1fr) + main content (3fr) --
cols = ww.columns([1, 3])

with cols[0]:
    with ww.sidebar():
        ww.heading("Navigation", level=3)
        ww.nav([
            {"text": "Dashboard", "href": "/"},
            {"text": "Reports", "href": "/reports"},
            {"text": "Settings", "href": "/settings"},
            {"text": "Help", "href": "/help"},
        ])
        ww.divider()
        ww.text("webwrench v0.1.0")

with cols[1]:
    ww.heading("Dashboard", level=2)
    ww.text("Main content area with metrics, charts, and tables.")

    # Metrics row
    metric_cols = ww.columns(3)
    with metric_cols[0]:
        ww.metric("Visitors", "12,340", delta="+8%", delta_color="green")
    with metric_cols[1]:
        ww.metric("Conversions", "1,891", delta="+3%", delta_color="green")
    with metric_cols[2]:
        ww.metric("Bounce Rate", "34%", delta="-2%", delta_color="green")

    # Chart
    ww.chart(
        [120, 190, 150, 220, 180, 260, 300],
        type="line",
        labels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        title="Daily Visitors",
    )

    # Activity table
    ww.heading("Recent Activity", level=3)
    ww.table([
        {"Time": "10:32 AM", "Event": "New signup", "User": "alice@example.com"},
        {"Time": "10:15 AM", "Event": "Purchase", "User": "bob@example.com"},
        {"Time": "09:48 AM", "Event": "Support ticket", "User": "carol@example.com"},
        {"Time": "09:22 AM", "Event": "New signup", "User": "dave@example.com"},
    ])

if __name__ == "__main__":
    ww.serve()
