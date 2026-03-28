"""11 - Sidebar Navigation

Uses ww.sidebar() as a context manager for a sidebar panel with
navigation links, and places the main content alongside it using
a column layout.

Run: python examples/11_sidebar_nav.py
"""

import webwrench as ww

ww.title("Sidebar Navigation Demo")

cols = ww.columns([1, 3])

with cols[0]:
    with ww.sidebar():
        ww.heading("Navigation", level=3)
        ww.nav([
            {"text": "Dashboard", "href": "#dashboard"},
            {"text": "Reports", "href": "#reports"},
            {"text": "Settings", "href": "#settings"},
            {"text": "Help", "href": "#help"},
        ])
        ww.divider()
        ww.text("webwrench v0.1.0")

with cols[1]:
    ww.heading("Dashboard", level=2)
    ww.text("Main content area. The sidebar provides navigation links on the left.")

    metric_cols = ww.columns(3)
    with metric_cols[0]:
        ww.metric("Visitors", "12,340", delta="+8%", delta_color="green")
    with metric_cols[1]:
        ww.metric("Conversions", "1,891", delta="+3%", delta_color="green")
    with metric_cols[2]:
        ww.metric("Bounce Rate", "34%", delta="-2%", delta_color="green")

    ww.chart(
        [120, 190, 150, 220, 180, 260, 300],
        type="line",
        labels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        title="Daily Visitors",
    )

    ww.heading("Recent Activity", level=3)
    ww.table([
        {"Time": "10:32 AM", "Event": "New signup", "User": "alice@example.com"},
        {"Time": "10:15 AM", "Event": "Purchase", "User": "bob@example.com"},
        {"Time": "09:48 AM", "Event": "Support ticket", "User": "carol@example.com"},
        {"Time": "09:22 AM", "Event": "New signup", "User": "dave@example.com"},
    ])

if __name__ == "__main__":
    ww.serve()
