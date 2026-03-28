"""Tests for webwrench.charts -- Chart.js integration."""

import json

from webwrench._context import Page, get_default_page, restore_active_session, set_active_session
from webwrench.charts import (
    CHART_TYPES,
    DEFAULT_COLORS,
    ChartHandle,
    chart,
    plot,
)
from webwrench.state import Session


class TestChartTypes:
    def test_expected_types(self):
        for t in ["bar", "line", "pie", "doughnut", "radar", "polarArea", "scatter", "bubble"]:
            assert t in CHART_TYPES


class TestChartHandle:
    def test_basic_config(self):
        h = ChartHandle("bar", data=[1, 2, 3])
        config = h.build_config()
        assert config["type"] == "bar"
        assert config["data"]["datasets"][0]["data"] == [1, 2, 3]

    def test_with_labels(self):
        h = ChartHandle("bar", data=[10], labels=["A"])
        config = h.build_config()
        assert config["data"]["labels"] == ["A"]

    def test_with_title(self):
        h = ChartHandle("line", data=[1], title="Sales")
        config = h.build_config()
        assert config["options"]["plugins"]["title"]["text"] == "Sales"
        assert config["options"]["plugins"]["title"]["display"] is True

    def test_with_datasets(self):
        datasets = [
            {"label": "A", "data": [1, 2], "color": "#ff0000"},
            {"label": "B", "data": [3, 4]},
        ]
        h = ChartHandle("bar", datasets=datasets)
        config = h.build_config()
        ds = config["data"]["datasets"]
        assert len(ds) == 2
        assert ds[0]["label"] == "A"
        assert ds[0]["backgroundColor"] == "#ff0000"
        assert ds[1]["label"] == "B"
        assert ds[1]["backgroundColor"] == DEFAULT_COLORS[1]

    def test_with_options(self):
        h = ChartHandle("radar", data=[1], options={"scales": {"r": {}}})
        config = h.build_config()
        assert "scales" in config["options"]

    def test_to_taco(self):
        h = ChartHandle("pie", data=[1, 2, 3])
        taco = h.to_taco()
        assert taco["t"] == "div"
        assert "ww-chart" in taco["a"]["class"]
        canvas = taco["c"][0]
        assert canvas["t"] == "canvas"
        assert "data-chart-config" in canvas["a"]
        # Verify config is valid JSON
        config = json.loads(canvas["a"]["data-chart-config"])
        assert config["type"] == "pie"

    def test_update_changes_data(self):
        h = ChartHandle("bar", data=[1, 2])
        h.update([3, 4])
        assert h._data == [3, 4]

    def test_update_sends_message_with_session(self):
        h = ChartHandle("bar", data=[1])
        session = Session("test")
        token = set_active_session(session)
        try:
            h.update([5, 6])
            msgs = session.drain_messages()
            assert len(msgs) == 1
            assert msgs[0]["type"] == "message"
            assert msgs[0]["action"] == "updateChart"
        finally:
            restore_active_session(token)

    def test_update_no_session_no_crash(self):
        h = ChartHandle("bar", data=[1])
        h.update([2])  # Should not raise

    def test_dataframe_resolve(self):
        """Test with a DataFrame-like object."""
        class FakeDF:
            columns = ["month", "revenue"]
            def __getitem__(self, key):
                if key == "month":
                    return ["Jan", "Feb"]
                return [100, 200]
        h = ChartHandle("line", data=FakeDF(), x="month", y="revenue")
        config = h.build_config()
        assert config["data"]["datasets"][0]["label"] == "revenue"
        assert config["data"]["datasets"][0]["data"] == [100, 200]

    def test_dataframe_multi_y(self):
        class FakeDF:
            columns = ["x", "a", "b"]
            def __getitem__(self, key):
                if key == "x":
                    return ["Q1", "Q2"]
                elif key == "a":
                    return [10, 20]
                return [30, 40]
        h = ChartHandle("bar", data=FakeDF(), x="x", y=["a", "b"])
        config = h.build_config()
        assert len(config["data"]["datasets"]) == 2

    def test_empty_data(self):
        h = ChartHandle("bar")
        config = h.build_config()
        # With None data, should still produce valid structure
        assert "datasets" in config["data"]

    def test_no_labels(self):
        h = ChartHandle("bar", data=[1, 2])
        config = h.build_config()
        assert "labels" not in config["data"]


class TestChartFunction:
    def test_basic(self):
        c = chart([1, 2, 3], type="bar")
        assert isinstance(c, ChartHandle)
        assert len(get_default_page().elements) == 1

    def test_with_labels(self):
        c = chart([1], labels=["A"])
        config = c.build_config()
        assert config["data"]["labels"] == ["A"]

    def test_registers_chartjs_lib(self):
        chart([1])
        assert "chartjs" in get_default_page()._libs_used

    def test_custom_page(self):
        page = Page()
        c = chart([1], page=page)
        assert len(page.elements) == 1
        assert "chartjs" in page._libs_used

    def test_all_params(self):
        c = chart(
            data=[1, 2],
            type="line",
            labels=["A", "B"],
            title="Test",
            options={"responsive": True},
            datasets=None,
            x=None,
            y=None,
        )
        config = c.build_config()
        assert config["type"] == "line"
        assert config["options"]["plugins"]["title"]["text"] == "Test"


class TestPlotFunction:
    def test_delegates_to_chart(self):
        class FakeDF:
            columns = ["x", "y"]
            def __getitem__(self, key):
                return [1, 2] if key == "x" else [3, 4]
        p = plot(FakeDF(), x="x", y="y", type="line")
        assert isinstance(p, ChartHandle)

    def test_with_color(self):
        class FakeDF:
            columns = ["x", "y"]
            def __getitem__(self, key):
                return [1] if key == "x" else [2]
        p = plot(FakeDF(), x="x", y="y", color="red")
        config = p.build_config()
        assert "color" in config["options"]

    def test_with_title(self):
        p = plot([1, 2], title="My Plot")
        config = p.build_config()
        assert config["options"]["plugins"]["title"]["text"] == "My Plot"
