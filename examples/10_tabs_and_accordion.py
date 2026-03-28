"""10 - Tabs and Accordion

Demonstrates tabbed navigation with ww.tabs() and collapsible
accordion sections with ww.accordion(). Content is placed inside
each tab pane or accordion using context managers.

Run: python examples/10_tabs_and_accordion.py
"""

import webwrench as ww

ww.title("Tabs and Accordion Demo")

# -- Tabs --
ww.heading("Project Overview", level=2)
tab_set = ww.tabs(["Summary", "Timeline", "Budget"])

with tab_set[0]:
    ww.text("Project Alpha aims to deliver a next-generation analytics platform.")
    ww.metric("Completion", "68%", delta="+5% this week", delta_color="green")
    ww.chart(
        [20, 35, 50, 68],
        type="line",
        labels=["Week 1", "Week 2", "Week 3", "Week 4"],
        title="Progress Over Time (%)",
    )

with tab_set[1]:
    ww.text("Key milestones for Project Alpha:")
    ww.table([
        {"Milestone": "Requirements Complete", "Date": "2025-01-15", "Status": "Done"},
        {"Milestone": "Design Review", "Date": "2025-02-01", "Status": "Done"},
        {"Milestone": "Beta Release", "Date": "2025-03-15", "Status": "In Progress"},
        {"Milestone": "GA Release", "Date": "2025-04-30", "Status": "Planned"},
    ])

with tab_set[2]:
    ww.text("Budget allocation and spending to date.")
    ww.chart(
        [150, 90, 60],
        type="pie",
        labels=["Engineering", "Marketing", "Operations"],
        title="Budget Allocation ($k)",
    )
    ww.metric("Spent", "$210k", delta="70% of $300k budget")

ww.divider()

# -- Accordions --
ww.heading("Frequently Asked Questions", level=2)

with ww.accordion("What is webwrench?", open=True):
    ww.text(
        "webwrench is a Python UI framework for building interactive web "
        "dashboards and self-contained HTML reports."
    )

with ww.accordion("How do I install it?"):
    ww.code("pip install webwrench", lang="bash")

with ww.accordion("Does it require JavaScript knowledge?"):
    ww.text(
        "No. You write pure Python. The frontend rendering is handled "
        "automatically by bitwrench.js."
    )

if __name__ == "__main__":
    ww.serve()
