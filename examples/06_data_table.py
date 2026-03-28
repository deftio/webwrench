"""06 - Data Table

A richly featured data table with sortable columns, a search bar,
and pagination. Uses list-of-dicts data format.

Run: python examples/06_data_table.py
"""

import webwrench as ww

ww.title("Employee Directory")
ww.text("Sortable, searchable, and paginated table with sample employee data.")

employees = [
    {"ID": 1, "Name": "Alice Johnson", "Department": "Engineering", "Salary": "$125,000", "Location": "New York"},
    {"ID": 2, "Name": "Bob Smith", "Department": "Marketing", "Salary": "$95,000", "Location": "San Francisco"},
    {"ID": 3, "Name": "Carol Williams", "Department": "Engineering", "Salary": "$118,000", "Location": "Austin"},
    {"ID": 4, "Name": "David Brown", "Department": "Sales", "Salary": "$105,000", "Location": "Chicago"},
    {"ID": 5, "Name": "Eve Davis", "Department": "Engineering", "Salary": "$132,000", "Location": "Seattle"},
    {"ID": 6, "Name": "Frank Miller", "Department": "HR", "Salary": "$88,000", "Location": "New York"},
    {"ID": 7, "Name": "Grace Wilson", "Department": "Marketing", "Salary": "$97,000", "Location": "Austin"},
    {"ID": 8, "Name": "Hank Moore", "Department": "Sales", "Salary": "$110,000", "Location": "Chicago"},
    {"ID": 9, "Name": "Iris Taylor", "Department": "Engineering", "Salary": "$140,000", "Location": "San Francisco"},
    {"ID": 10, "Name": "Jack Anderson", "Department": "HR", "Salary": "$91,000", "Location": "Seattle"},
    {"ID": 11, "Name": "Karen Thomas", "Department": "Engineering", "Salary": "$127,000", "Location": "New York"},
    {"ID": 12, "Name": "Leo Jackson", "Department": "Sales", "Salary": "$102,000", "Location": "Austin"},
]

ww.table(employees, sortable=True, searchable=True, paginate=5)

if __name__ == "__main__":
    ww.serve()
