# webwrench

[![CI](https://github.com/deftio/webwrench/actions/workflows/ci.yml/badge.svg)](https://github.com/deftio/webwrench/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/webwrench.svg)](https://pypi.org/project/webwrench/)
[![Python](https://img.shields.io/pypi/pyversions/webwrench.svg)](https://pypi.org/project/webwrench/)
[![License](https://img.shields.io/badge/license-BSD--2--Clause-blue.svg)](LICENSE.txt)

A Python library for building interactive web dashboards and self-contained HTML reports. It uses [bitwrench.js](https://github.com/deftio/bitwrench) for rendering and the bwserve protocol (SSE down, POST back) for live updates. No JavaScript required on your end, no build tools, no runtime dependencies.

- **Script mode** for quick dashboards, **app mode** with decorator-based routing for multi-page apps
- **Static HTML export** -- same API produces a single self-contained file you can open offline or email
- **Chart.js included** -- bar, line, pie, scatter, radar, and more without extra installs
- **Callback-driven updates** -- define the UI once, update individual elements via `on_change`/`on_click`
- **Zero runtime dependencies** -- `pip install webwrench` pulls nothing else in

## Installation

```bash
pip install webwrench
```

Requires Python 3.10+.

## Quick Start

### Script Mode

```python
import webwrench as ww

ww.title("Hello World")
ww.text("My first webwrench app")
ww.serve()
```

### Interactive Dashboard

```python
import webwrench as ww

data = [12, 19, 3, 5, 2, 3]

ww.title("Sales Dashboard")
chart = ww.chart(data, type='bar', labels=['Jan','Feb','Mar','Apr','May','Jun'])
slider = ww.slider("Multiplier", min=1, max=10, value=1)

@slider.on_change
def update(value):
    chart.update([d * value for d in data])

ww.serve()
```

### Static HTML Report

```python
import webwrench as ww

ww.title("Quarterly Report")
ww.chart([45, 67, 89, 34], type='line', labels=['Q1','Q2','Q3','Q4'])
ww.text("Revenue grew 48% year-over-year.")
ww.export('quarterly-report.html')
```

The exported file is self-contained -- open it in any browser, no server needed. Charts stay interactive (tooltips, hover, legend toggling).

### Multi-Page App

```python
import webwrench as ww

app = ww.App()

@app.page('/')
def home(ctx):
    ctx.title("Dashboard")
    ctx.chart([10, 20, 30], type='bar', labels=['A', 'B', 'C'])

@app.page('/settings')
def settings(ctx):
    ctx.title("Settings")
    theme = ctx.select("Theme", ['light', 'dark', 'ocean'])

    @theme.on_change
    def switch(value):
        ctx.set_theme(value)

app.serve(port=6502)
```

## API Reference

### Display Elements

```python
ww.title(text)                          # <h1>
ww.heading(text, level=2)               # <h2>..<h6>
ww.text(text)                           # <p>
ww.markdown(md_string)                  # Rendered markdown
ww.code(code_string, lang='python')     # Syntax-highlighted code block
ww.html(raw_html, raw=False)            # HTML content (escaped by default)
ww.image(src, alt='', width=None)       # Image
ww.divider()                            # <hr>
ww.table(data, sortable=False, searchable=False, paginate=None)
ww.metric(label, value, delta=None, delta_color=None)
ww.json(data, collapsed=1)              # Collapsible JSON viewer
ww.progress(value=0, max_val=100)       # Progress bar
ww.toast(message, type='info', duration=3000)
```

### Input Widgets

All widgets return a handle with `.value` and `.on_change(callback)`.

```python
ww.button(label, on_click=None)
ww.input(label, placeholder='', value='')
ww.textarea(label, rows=4)
ww.slider(label, min=0, max=100, value=50, step=1)
ww.select(label, options=['a','b','c'], value='a')
ww.checkbox(label, value=False)
ww.radio(label, options=['x','y','z'])
ww.file_upload(label, accept='.csv,.json')
ww.date_picker(label)
ww.color_picker(label, value='#3366cc')
ww.number(label, min=0, max=100, step=1, value=0)
```

### Charts

```python
# Simple chart
ww.chart([12, 19, 3], type='bar', labels=['A','B','C'])

# Multi-dataset
ww.chart(datasets=[
    {'label': 'Sales', 'data': [12, 19, 3], 'color': '#3366cc'},
    {'label': 'Returns', 'data': [2, 3, 1], 'color': '#cc3333'}
], type='line', labels=['Jan','Feb','Mar'])

# From pandas DataFrame
ww.plot(df, x='date', y='revenue', type='line')

# Supported types: bar, line, pie, doughnut, radar, polarArea, scatter, bubble
```

### Layout

```python
with ww.columns(3) as cols:
    with cols[0]: ww.text("Left")
    with cols[1]: ww.chart(data1)
    with cols[2]: ww.chart(data2)

with ww.tabs(['Overview', 'Details']) as t:
    with t[0]: ww.title("Overview")
    with t[1]: ww.table(detail_data)

with ww.accordion("Advanced Options", open=False):
    ww.slider("Threshold", min=0, max=100, value=50)

with ww.card(title="Revenue"):
    ww.chart(revenue_data, type='line')

with ww.sidebar():
    ww.nav([{'text': 'Home', 'href': '/'}])
```

### Theming

```python
ww.theme('dark')                        # Built-in: light, dark, ocean, forest
ww.theme(primary='#006666')             # Custom palette
ww.toggle_theme()                       # Toggle light/dark
ww.css({'.my-card': {'border-radius': '12px'}})  # Custom CSS
```

### Export

```python
ww.export('report.html')                # Self-contained HTML file
ww.export('report.html', minify=True)   # Minified output
ww.screenshot('dashboard.png')          # Screenshot via html2canvas
ww.download('data.csv', content=csv_string)  # Trigger browser download
```

## How It Works

```
 Python (webwrench)                    Browser
+------------------------+           +-------------------------+
| Your Python script     |           | bitwrench.js (bundled)  |
|   |                    |           |   +-- Chart.js           |
|   v                    |  SSE -->  |   +-- bwclient.js        |
| webwrench server       | -------> |                          |
|  (asyncio, built-in)   | <------- |                          |
|                        |  POST <-- |                          |
+------------------------+           +-------------------------+
```

- **Frontend**: bitwrench.js handles DOM operations. webwrench generates TACO (Tag, Attributes, Content, Options) dicts that bitwrench renders.
- **Backend**: Pure Python asyncio HTTP server. No Flask, no FastAPI, no external dependencies.
- **Protocol**: bwserve -- SSE for server-to-client updates, POST for client-to-server actions.
- **Updates**: Only the changed element is patched, not the whole page.

## Development

```bash
git clone https://github.com/deftio/webwrench.git
cd webwrench
uv sync --dev

# Preflight — lint, security, tests (100% coverage), build, install verify
./scripts/prerelease.sh
```

### Releasing

**Direct from main** (quick):

```bash
./scripts/release.sh 0.2.0
```

**Two-phase** (for bigger releases):

```bash
./scripts/start-release.sh 0.2.0   # bump version + create release branch
# ... develop, commit, iterate ...
./scripts/prerelease.sh             # validate everything (safe, no side effects)
./scripts/release.sh                # ship it: merge, tag, push, GH release
```

`release.sh` runs all prerelease checks, then tags, pushes, and creates a GitHub Release. The CI publish pipeline handles PyPI automatically.

## License

BSD-2-Clause. See [LICENSE.txt](LICENSE.txt).
