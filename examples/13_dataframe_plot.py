"""13 - DataFrame-style Plot

Demonstrates ww.plot() with dict-based data. ww.plot() works like
pandas .plot() but without the pandas dependency. A lightweight
SimpleFrame class provides the .columns and __getitem__ interface
that ww.plot() needs.

Concepts: ww.plot(data, x=, y=), SimpleFrame pattern,
          ww.table(), ww.card(), ww.columns().

Run: python examples/13_dataframe_plot.py
"""

import webwrench as ww

ww.theme("ocean")

# -- Header --
ww.title("DataFrame-style Plot")
ww.text(
    "ww.plot() accepts any object with a .columns attribute and "
    "bracket indexing (df['col']). This lets you pass a pandas DataFrame "
    "directly, or a lightweight dict wrapper like SimpleFrame below."
)

ww.divider()


# -- SimpleFrame: pandas-like without the dependency --
class SimpleFrame:
    """Minimal DataFrame-like object for demonstration purposes.

    Provides .columns and __getitem__ so that ww.plot(df, x=, y=)
    can extract data without importing pandas.
    """

    def __init__(self, data: dict):
        self._data = data
        self.columns = list(data.keys())

    def __getitem__(self, key):
        return self._data[key]

    def iterrows(self):
        n = len(next(iter(self._data.values())))
        for i in range(n):
            yield i, [self._data[col][i] for col in self.columns]


# -- Temperature comparison --
ww.heading("Multi-Series: Temperature Comparison", level=2)
ww.text(
    "Pass a list of column names to y= to overlay multiple series. "
    "The x= column provides the axis labels."
)

temp_data = {
    "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "New York": [0, 1, 7, 13, 18, 24, 27, 26, 22, 15, 9, 3],
    "Los Angeles": [14, 15, 16, 17, 18, 20, 22, 23, 22, 19, 16, 14],
}
df = SimpleFrame(temp_data)

ww.plot(df, x="Month", y=["New York", "Los Angeles"], type="line",
        title="Average Monthly Temperature (C)")

# Show the raw data alongside the chart
ww.heading("Raw Data", level=3)
ww.table([
    {"Month": m, "New York": ny, "Los Angeles": la}
    for m, ny, la in zip(temp_data["Month"], temp_data["New York"], temp_data["Los Angeles"])
])

ww.divider()

# -- Single series --
ww.heading("Single Series: Quarterly Revenue", level=2)
ww.text(
    "When y= is a single string, ww.plot() creates a one-series chart. "
    "This is the simplest DataFrame-style call."
)
ww.code(
    'ww.plot(df, x="Quarter", y="Revenue", type="bar")',
    lang="python",
)

sales_df = SimpleFrame({
    "Quarter": ["Q1", "Q2", "Q3", "Q4"],
    "Revenue": [320, 480, 410, 560],
})

ww.plot(sales_df, x="Quarter", y="Revenue", type="bar",
        title="Quarterly Revenue ($k)")

if __name__ == "__main__":
    ww.serve()
