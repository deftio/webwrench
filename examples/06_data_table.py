"""06 - Data Table

A richly featured data table with sortable columns, a search bar,
and pagination. Uses list-of-dicts data format.

Run: python examples/06_data_table.py
"""

import webwrench as ww

ww.theme("ocean")

employees = [
    {"ID": 1, "Name": "Alice Johnson", "Department": "Engineering", "Salary": 125000, "Location": "New York"},
    {"ID": 2, "Name": "Bob Smith", "Department": "Marketing", "Salary": 95000, "Location": "San Francisco"},
    {"ID": 3, "Name": "Carol Williams", "Department": "Engineering", "Salary": 118000, "Location": "Austin"},
    {"ID": 4, "Name": "David Brown", "Department": "Sales", "Salary": 105000, "Location": "Chicago"},
    {"ID": 5, "Name": "Eve Davis", "Department": "Engineering", "Salary": 132000, "Location": "Seattle"},
    {"ID": 6, "Name": "Frank Miller", "Department": "HR", "Salary": 88000, "Location": "New York"},
    {"ID": 7, "Name": "Grace Wilson", "Department": "Marketing", "Salary": 97000, "Location": "Austin"},
    {"ID": 8, "Name": "Hank Moore", "Department": "Sales", "Salary": 110000, "Location": "Chicago"},
    {"ID": 9, "Name": "Iris Taylor", "Department": "Engineering", "Salary": 140000, "Location": "San Francisco"},
    {"ID": 10, "Name": "Jack Anderson", "Department": "HR", "Salary": 91000, "Location": "Seattle"},
    {"ID": 11, "Name": "Karen Thomas", "Department": "Engineering", "Salary": 127000, "Location": "New York"},
    {"ID": 12, "Name": "Leo Jackson", "Department": "Sales", "Salary": 102000, "Location": "Austin"},
]

# ── Header ──
ww.title("Employee Directory")
ww.text(
    "A sortable, searchable employee table with pagination.  "
    "Use the column headers to sort and the search field to filter rows."
)

ww.divider()

# ── Summary metrics ──
ww.heading("At a Glance", level=2)

departments = {}
for e in employees:
    departments.setdefault(e["Department"], []).append(e["Salary"])

avg_salary = sum(e["Salary"] for e in employees) // len(employees)
top_dept = max(departments, key=lambda d: sum(departments[d]) / len(departments[d]))
locations = len({e["Location"] for e in employees})

metrics = ww.columns(4)
with metrics[0]:
    ww.metric("Headcount", str(len(employees)))
with metrics[1]:
    ww.metric("Avg Salary", f"${avg_salary:,}")
with metrics[2]:
    ww.metric("Top Dept (avg)", top_dept)
with metrics[3]:
    ww.metric("Office Locations", str(locations))

ww.divider()

# ── Department breakdown ──
ww.heading("Department Breakdown", level=2)
ww.text("Average salary per department, shown as a bar chart.")

dept_names = sorted(departments)
dept_avgs = [sum(departments[d]) // len(departments[d]) for d in dept_names]
ww.chart(dept_avgs, type="bar", labels=dept_names, title="Avg Salary by Department")

ww.divider()

# ── Full table ──
ww.heading("Full Directory", level=2)
ww.text("Click a column header to sort.  The table paginates at 5 rows.")

display_rows = [
    {**e, "Salary": f"${e['Salary']:,}"} for e in employees
]
ww.table(display_rows, sortable=True, searchable=True, paginate=5)

if __name__ == "__main__":
    ww.serve()
