"""13 - DataFrame-style Plot

Demonstrates ww.plot() with dict-based data that simulates a
pandas DataFrame. This approach works without pandas installed --
each key becomes a column name and values are lists of data.

Run: python examples/13_dataframe_plot.py
"""

import webwrench as ww

ww.title("DataFrame-style Plot")
ww.text("Using ww.plot() with dict data to simulate DataFrame-like charting.")

# Simulated DataFrame as a dict-like object with .columns and .iterrows()
# Since we do not require pandas, we build a lightweight wrapper.

class SimpleFrame:
    """Minimal DataFrame-like object for demonstration purposes."""

    def __init__(self, data: dict):
        self._data = data
        self.columns = list(data.keys())

    def __getitem__(self, key):
        return self._data[key]

    def iterrows(self):
        n = len(next(iter(self._data.values())))
        for i in range(n):
            yield i, [self._data[col][i] for col in self.columns]


# Monthly temperature data for two cities
df = SimpleFrame({
    "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "New York": [0, 1, 7, 13, 18, 24, 27, 26, 22, 15, 9, 3],
    "Los Angeles": [14, 15, 16, 17, 18, 20, 22, 23, 22, 19, 16, 14],
})

ww.plot(df, x="Month", y=["New York", "Los Angeles"], type="line",
        title="Average Monthly Temperature (C)")

ww.divider()

# Single series plot
sales_df = SimpleFrame({
    "Quarter": ["Q1", "Q2", "Q3", "Q4"],
    "Revenue": [320, 480, 410, 560],
})

ww.heading("Single Series", level=2)
ww.plot(sales_df, x="Quarter", y="Revenue", type="bar",
        title="Quarterly Revenue ($k)")

if __name__ == "__main__":
    ww.serve()
