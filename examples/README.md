# webwrench Examples

Sixteen progressively complex examples that teach the core concepts of
webwrench -- from a one-liner "Hello World" to multi-page apps with live
updates, theming, and modal dialogs.

## Running an example

```bash
# from the repo root
python examples/01_hello_world.py
```

Then open <http://localhost:6502> in your browser.
Example 08 exports a static HTML file instead of starting a server.

---

## Example index

| #  | File | Topic | What you learn |
|----|------|-------|----------------|
| 01 | `01_hello_world.py` | Hello World | The minimal webwrench app: `title`, `text`, `markdown`, and `serve()`. Establishes the script-mode pattern. |
| 02 | `02_interactive_chart.py` | Interactive Chart | A bar chart and metric driven by a slider. Introduces callbacks (`@slider.on_change`) and real-time multi-widget updates via SSE. |
| 03 | `03_multi_chart.py` | Multiple Chart Types | Bar, line, and pie charts in a three-column layout sharing one dataset. Uses themes, metrics, cards, dividers, and a data table. |
| 04 | `04_dashboard.py` | Dashboard Layout | KPI row + two-column body (chart and table). Shows proportional column sizing (`[2, 1]`). |
| 05 | `05_form_widgets.py` | Form Widgets | Every input widget: text, textarea, slider, select, radio, checkbox, number, date picker, colour picker, and file upload. Grouped into cards with a submit button that fires a toast. |
| 06 | `06_data_table.py` | Data Table | Sortable, searchable, paginated table with summary metrics and a department bar chart. |
| 07 | `07_theming.py` | Theming | Dynamic theme switching (light / dark / ocean / forest) via a dropdown. Shows how one `ww.theme()` call restyles every component. |
| 08 | `08_static_export.py` | Static Export | Builds a report with charts, metrics, and tables, then writes a self-contained HTML file with `ww.export()`. No server needed. |
| 09 | `09_multi_page_app.py` | Multi-Page App | App mode with `@app.page()` decorators. Three URL routes with `ww.nav()` for cross-page navigation, each with its own `PageContext`. |
| 10 | `10_tabs_and_accordion.py` | Tabs & Accordion | Tabbed navigation (`ww.tabs()`) and collapsible sections (`ww.accordion()`). Context managers organise child content. |
| 11 | `11_sidebar_nav.py` | Sidebar Navigation | Classic sidebar + main-content layout using `ww.sidebar()` and `ww.nav()`. |
| 12 | `12_chart_datasets.py` | Multiple Datasets | Overlaying several data series on one chart with the `datasets` parameter. Includes summary metrics and a chart-type selector. |
| 13 | `13_dataframe_plot.py` | DataFrame-style Plot | `ww.plot()` with dict-based data and `x`/`y` column specs -- pandas-like without the dependency. Includes raw data table alongside charts. |
| 14 | `14_live_updates.py` | Live Updates | A progress bar, click counter, and status text that advance on each button click. Demonstrates `widget.update()` and the callback-SSE-DOM cycle. |
| 15 | `15_grid_layout.py` | Grid Layout | CSS Grid via `ww.grid()` with nested cards holding metrics, charts, and text. |
| 16 | `16_modal_dialog.py` | Modal Dialog | `ww.modal()` as a context manager with a nested form and confirmation button. |

---

## Learning path

If you are new to webwrench, work through the examples in this order:

1. **Basics (01-03)** -- output elements, charts, columns, themes.
2. **Layouts (04, 10-11, 15)** -- dashboards, tabs, sidebars, grids.
3. **Interactivity (02, 05, 14, 16)** -- widgets, callbacks, live updates, modals.
4. **Data (06, 12-13)** -- tables, multi-dataset charts, DataFrame-style plots.
5. **Advanced (07-09)** -- theming, static export, multi-page apps.

---

## Key concepts covered

| Concept | Examples |
|---------|----------|
| Script mode (`ww.title`, `ww.serve`) | 01-08, 10-16 |
| App mode (`ww.App`, `@app.page`) | 09 |
| Charts (bar, line, pie, multi-dataset) | 02, 03, 06, 07, 12, 13, 15 |
| Layout (columns, grid, tabs, sidebar) | 03-06, 10, 11, 15 |
| Widgets & callbacks | 02, 05, 14, 16 |
| Cards & metrics | 03-07, 15 |
| Tables (sortable, searchable, paginated) | 04, 06 |
| Theming & CSS | 03, 05-07 |
| Static HTML export | 08 |
| Modal dialogs | 16 |
