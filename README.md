# webwrench

Python UI framework for building interactive web dashboards and self-contained HTML reports.

webwrench is powered by [bitwrench.js](https://github.com/deftio/bitwrench) on the frontend and uses the bwserve protocol (SSE down, POST back) for live server-driven updates. Build dashboards with pure Python -- no JavaScript, no build tools, no npm.

## Features

- **Script mode**: Top-to-bottom, sequential -- write a dashboard in 5 lines
- **App mode**: Decorator-based routing for multi-page applications
- **Static HTML export**: Same API, same charts, self-contained file you can email to anyone
- **Chart.js built in**: Bar, line, pie, scatter, radar, and more -- no extra installs
- **Zero runtime dependencies**: `pip install webwrench` is all you need
- **Surgical updates**: Only the changed element updates, not the whole page

## Installation

```bash
pip install webwrench
```

## Quick Start

### Hello World

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

The exported file is fully self-contained -- open it in any browser, no server needed. Charts remain interactive (tooltips, hover, legend toggling).

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

app.serve(port=8080)
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

## Coming from Streamlit?

webwrench will feel familiar. Here are the key differences:

| | Streamlit | webwrench |
|---|---|---|
| **Script runs** | Re-runs on every interaction | Runs once to build initial UI |
| **Updates** | Full page re-render | Only the changed element updates |
| **Static export** | Not available | `ww.export('report.html')` |
| **Dependencies** | 30+ pip packages | Zero runtime deps |

**Typical migration pattern:**

```python
# Streamlit
import streamlit as st
st.title("Dashboard")
val = st.slider("Multiplier", 1, 10, 1)
st.bar_chart({"data": [d * val for d in data]})

# webwrench
import webwrench as ww
ww.title("Dashboard")
chart = ww.chart(data, type='bar', labels=labels)
slider = ww.slider("Multiplier", min=1, max=10, value=1)

@slider.on_change
def update(value):
    chart.update([d * value for d in data])

ww.serve()
```

The main difference: in webwrench, you define the UI once and use callbacks to update specific elements. No re-running, no `@st.cache_data`, no `session_state` initialization guards.

## Coming from Gradio?

If you've used Gradio's event handler model, webwrench's callback pattern will feel natural:

```python
# Gradio
import gradio as gr
def update(multiplier):
    return create_plot(multiplier)
demo = gr.Interface(fn=update, inputs=gr.Slider(1, 10), outputs=gr.Plot())
demo.launch()

# webwrench
import webwrench as ww
chart = ww.chart(data, type='bar')
slider = ww.slider("Multiplier", min=1, max=10, value=1)

@slider.on_change
def update(value):
    chart.update([d * value for d in data])

ww.serve()
```

webwrench bundles Chart.js directly, so you don't need matplotlib or plotly for common chart types.

## Architecture

```
 Python (webwrench)                    Browser
+------------------------+           +-------------------------+
| Your Python script     |           | bitwrench.js (bundled)  |
|   |                    |           |   +-- Chart.js           |
|   v                    |  SSE -->  |   +-- (D3, Leaflet,     |
| webwrench server       | -------> |       three.js planned)  |
|  (asyncio, built-in)   | <------- |   +-- bwclient.js        |
|                        |  POST <-- |                         |
+------------------------+           +-------------------------+
```

- **Frontend**: bitwrench.js handles all DOM operations. webwrench generates [TACO](https://github.com/nicklausw/bitwrench) (Tag, Attributes, Content, Options) dicts that bitwrench renders.
- **Backend**: Pure Python asyncio HTTP server. No Flask, no FastAPI, no external deps.
- **Protocol**: bwserve -- SSE for server-to-client updates, POST for client-to-server callbacks.

## Development

```bash
# Clone and install dev dependencies
git clone https://github.com/deftio/webwrench.git
cd webwrench
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=webwrench --cov-report=term-missing

# Lint
ruff check webwrench/
```

## Roadmap

- **v0.1.0** (current): Core display elements, widgets, Chart.js, themes, serve/export
- **v0.2.0**: Layout primitives, multi-page apps, pandas integration, more widgets
- **v0.3.0**: D3, Leaflet maps, three.js 3D, advanced visualization
- **v0.4.0**: WebSocket transport, authentication, production features
- **v0.5.0+**: Plugin system, CLI, hot reload, Jupyter integration

## License

BSD2
