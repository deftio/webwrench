"""Chart.js integration for webwrench.

Wraps Chart.js configuration as TACO structures. Supports bar, line, pie,
doughnut, radar, polarArea, scatter, and bubble chart types.
"""

from __future__ import annotations

import json
from typing import Any

from webwrench._context import Element, Page, WidgetHandle, get_default_page


CHART_TYPES = frozenset(
    ["bar", "line", "pie", "doughnut", "radar", "polarArea", "scatter", "bubble"]
)

# Default color palette for multi-dataset charts.
DEFAULT_COLORS = [
    "#3366cc",
    "#dc3912",
    "#ff9900",
    "#109618",
    "#990099",
    "#0099c6",
    "#dd4477",
    "#66aa00",
]


class ChartHandle(WidgetHandle):
    """Handle for a Chart.js chart element."""

    def __init__(
        self,
        chart_type: str,
        data: Any = None,
        labels: list[str] | None = None,
        title: str | None = None,
        options: dict[str, Any] | None = None,
        datasets: list[dict[str, Any]] | None = None,
        x: str | None = None,
        y: Any = None,
    ) -> None:
        self._chart_type = chart_type
        self._data = data
        self._labels = labels
        self._chart_title = title
        self._chart_options = options or {}
        self._datasets = datasets
        self._x = x
        self._y = y
        super().__init__(
            "div",
            attrs={"class": "ww-chart"},
            widget_type="chart",
        )

    def update(self, data: Any) -> None:
        """Update the chart data."""
        self._data = data
        from webwrench._context import get_active_session

        session = get_active_session()
        if session is not None:
            session.send_message(
                {
                    "type": "message",
                    "target": self.id,
                    "action": "updateChart",
                    "data": {"datasets": [{"data": data}]},
                }
            )

    def build_config(self) -> dict[str, Any]:
        """Build the Chart.js configuration dict."""
        config: dict[str, Any] = {
            "type": self._chart_type,
            "data": {},
            "options": dict(self._chart_options),
        }

        data_obj, labels = self._resolve_data()
        config["data"] = data_obj
        if labels:
            config["data"]["labels"] = labels

        if self._chart_title:
            plugins = config["options"].setdefault("plugins", {})
            plugins["title"] = {"display": True, "text": self._chart_title}

        return config

    def _resolve_data(self) -> tuple[dict[str, Any], list[str] | None]:
        """Resolve data/datasets/DataFrame into Chart.js data object."""
        labels = self._labels

        # DataFrame support
        if self._x is not None and hasattr(self._data, "columns"):
            return self._resolve_dataframe(), labels

        if self._datasets:
            chart_datasets = []
            for i, ds in enumerate(self._datasets):
                chart_ds: dict[str, Any] = {
                    "label": ds.get("label", f"Dataset {i + 1}"),
                    "data": ds["data"],
                }
                color = ds.get("color", DEFAULT_COLORS[i % len(DEFAULT_COLORS)])
                chart_ds["backgroundColor"] = color
                chart_ds["borderColor"] = color
                chart_datasets.append(chart_ds)
            return {"datasets": chart_datasets}, labels

        # Simple data list
        if isinstance(self._data, list):
            return {
                "datasets": [
                    {
                        "data": self._data,
                        "backgroundColor": DEFAULT_COLORS[: len(self._data)],
                        "borderColor": DEFAULT_COLORS[0],
                    }
                ]
            }, labels

        return {"datasets": []}, labels

    def _resolve_dataframe(self) -> dict[str, Any]:
        """Extract Chart.js data from a pandas DataFrame."""
        df = self._data
        labels = [str(v) for v in df[self._x]]

        y_cols = self._y if isinstance(self._y, list) else [self._y]
        datasets = []
        for i, col in enumerate(y_cols):
            datasets.append(
                {
                    "label": str(col),
                    "data": list(df[col]),
                    "backgroundColor": DEFAULT_COLORS[i % len(DEFAULT_COLORS)],
                    "borderColor": DEFAULT_COLORS[i % len(DEFAULT_COLORS)],
                }
            )
        return {"datasets": datasets, "labels": labels}

    def to_taco(self) -> dict[str, Any]:
        """Produce the TACO structure for a chart."""
        canvas_id = f"{self.id}-canvas"
        config = self.build_config()
        return {
            "t": "div",
            "a": {"id": self.id, "class": "ww-chart"},
            "c": [
                {
                    "t": "canvas",
                    "a": {"id": canvas_id, "data-chart-config": json.dumps(config)},
                }
            ],
        }


def chart(
    data: Any = None,
    type: str = "bar",
    labels: list[str] | None = None,
    title: str | None = None,
    options: dict[str, Any] | None = None,
    datasets: list[dict[str, Any]] | None = None,
    x: str | None = None,
    y: Any = None,
    page: Page | None = None,
) -> ChartHandle:
    """Create a Chart.js chart.

    Simple usage:
        chart([12, 19, 3], type='bar', labels=['A', 'B', 'C'])

    Multi-dataset:
        chart(datasets=[{'label': 'Sales', 'data': [12, 19]}, ...], type='line')

    DataFrame:
        chart(df, x='month', y='revenue', type='line')
    """
    p = page or get_default_page()
    p.require_lib("chartjs")
    handle = ChartHandle(
        chart_type=type,
        data=data,
        labels=labels,
        title=title,
        options=options,
        datasets=datasets,
        x=x,
        y=y,
    )
    p.add(handle)
    return handle


def plot(
    data: Any,
    x: str | None = None,
    y: Any = None,
    type: str = "line",
    color: str | None = None,
    title: str | None = None,
    page: Page | None = None,
) -> ChartHandle:
    """Create a chart from a pandas DataFrame.

    Shorthand for chart(data, x=..., y=..., type=...).
    """
    opts = {}
    if color is not None:
        opts["color"] = color
    return chart(data=data, x=x, y=y, type=type, title=title, options=opts, page=page)
