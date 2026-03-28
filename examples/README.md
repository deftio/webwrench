# webwrench Examples

Self-contained example scripts demonstrating the webwrench Python UI framework.

## Running

Each example is a standalone script. Run from the project root:

```bash
python examples/01_hello_world.py
```

Then open `http://localhost:6502` in your browser (unless the example exports a static file).

## Examples

| # | File | Description |
|---|------|-------------|
| 01 | `01_hello_world.py` | Simplest app: title, text, and serve |
| 02 | `02_interactive_chart.py` | Bar chart with a slider that multiplies data values |
| 03 | `03_multi_chart.py` | Multiple chart types on one page (bar, line, pie) |
| 04 | `04_dashboard.py` | Metrics, charts, and a table in a column layout |
| 05 | `05_form_widgets.py` | All widget types with a submit button and toast |
| 06 | `06_data_table.py` | Sortable, searchable, paginated data table |
| 07 | `07_theming.py` | Switch between theme presets with a dropdown |
| 08 | `08_static_export.py` | Export a report to a static HTML file (no server) |
| 09 | `09_multi_page_app.py` | App mode with three pages: home, about, contact |
| 10 | `10_tabs_and_accordion.py` | Tabbed layout with accordion sections |
| 11 | `11_sidebar_nav.py` | Sidebar with navigation and main content area |
| 12 | `12_chart_datasets.py` | Chart with multiple datasets overlaid |
| 13 | `13_dataframe_plot.py` | Using plot() with dict-based data |
| 14 | `14_live_updates.py` | Progress bar updated via button callbacks |
| 15 | `15_grid_layout.py` | CSS grid layout with cards |
| 16 | `16_modal_dialog.py` | Modal dialog triggered by a button |
