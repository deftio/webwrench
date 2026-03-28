# webwrench -- Python UI Framework Specification

**Version**: 0.1.0-draft
**Author**: Manu Chatterjee (deftio)
**Date**: March 2026
**Status**: Design specification -- no code yet

---

## 1. Executive Summary

webwrench is a Python library for building interactive web UIs, dashboards,
and self-contained HTML reports. It is powered by bitwrench.js on the
frontend and speaks the bwserve protocol (SSE down, POST back) for live
server-driven updates.

**One-sentence pitch**: The visualization power of D3 and Chart.js, the
simplicity of Streamlit, the update precision of a native app, and the
ability to export everything as a single HTML file.

### 1.1 What webwrench is NOT

- Not a general web framework (use Flask/FastAPI for REST APIs)
- Not a React/Vue replacement (no virtual DOM, no JSX)
- Not ML-only (works for dashboards, reports, admin panels, IoT displays)

### 1.2 Cardinal Rule: bitwrench IS the Frontend

webwrench does not have a frontend of its own. bitwrench IS the frontend.
Every DOM element, every style, every layout, every component is expressed
as TACO and rendered by bitwrench.js. This is non-negotiable.

**What this means in practice:**

1. **No vanilla JS in webwrench**: If you need client-side behavior, use
   bwserve `register`/`call` to send named functions, or use bitwrench's
   existing BCCL components (makeTabs, makeAccordion, makeTable, etc.).
   Never write inline `<script>` blocks with raw DOM manipulation.

2. **No CSS variables or ad-hoc styling**: All styling flows through
   `bw.loadStyles()`, `bw.makeStyles()`, and bitwrench's palette system.
   Webwrench emits TACO with bitwrench CSS classes (`bw_card`, `bw_table`,
   `bw_btn`). It does NOT emit `style="color: var(--ww-primary)"` or
   invent its own design token system. bitwrench's design tokens are the
   design tokens.

3. **No vDOM, no diffing, no reactivity engine**: bitwrench's model is
   TACO -> DOM -> patch/replace. The server tells the client exactly what
   changed. There is no client-side state diffing, no reactive stores,
   no computed properties, no dependency graphs. If you catch yourself
   building any of these, stop -- you are reimplementing React inside
   webwrench, and that defeats the entire purpose.

4. **If bitwrench can't do it, fix bitwrench**: If a webwrench feature
   requires something bitwrench doesn't support (e.g., a new BCCL
   component, a new CSS structural rule, SVG namespace support), the
   correct action is to file a PR against bitwrench -- not to work
   around it with vanilla JS in webwrench. webwrench should contain
   zero lines of DOM-manipulating JavaScript. All JS lives in bitwrench.

5. **TACO is the wire format**: Python dicts go over SSE as JSON. The
   browser calls `bw.createDOM(taco)` or `bw.apply(msg)`. There is no
   intermediate representation, no template compilation, no HTML string
   building on the Python side. Python emits TACO, bitwrench renders it.

6. **Theming = bitwrench theming**: `ww.theme('ocean')` calls
   `bw.loadStyles({...ocean palette...})`. `ww.toggle_theme()` calls
   `bw.toggleStyles()`. webwrench does not have its own theme engine.
   If the bitwrench palette needs a new color key, add it to bitwrench.

**Anti-patterns to reject during code review:**

```python
# WRONG: vanilla JS in webwrench
ctx.exec("document.querySelector('#chart').style.display = 'none'")

# RIGHT: bitwrench protocol
ctx.remove('#chart')  # bwserve remove message
# OR
ctx.patch('chart', attr={'class': 'bw_hidden'})  # bitwrench CSS class

# WRONG: custom CSS variables
ww.css({':root': {'--ww-primary': '#006666'}})

# RIGHT: bitwrench palette
ww.theme(primary='#006666')  # bw.loadStyles({primary: '#006666'})

# WRONG: building a component registry in webwrench
class WebwrenchTabComponent:
    def __init__(self): ...
    def render(self): ...

# RIGHT: use bitwrench BCCL
ctx.render('#tabs', bw.makeTabs([...]))  # BCCL does the work
```

**The test**: If you delete all of webwrench's Python code, the browser
should still have a fully functional bitwrench runtime. webwrench is a
Python convenience layer that generates TACO and speaks bwserve protocol.
It adds zero client-side capabilities that bitwrench doesn't already have.

### 1.3 Key Differentiators vs. Streamlit and Gradio

| Capability | Streamlit | Gradio | webwrench |
|---|---|---|---|
| Update model | Full script re-run | Event handlers | Surgical DOM patches (bwserve) |
| Static HTML export | No | No | Yes -- self-contained single file |
| Built-in charts | Wrappers around Altair | None (uses Plotly/Matplotlib) | Chart.js + D3 + Leaflet + three.js bundled |
| Custom components | Requires React + npm (V1) or JS (V2) | Requires Svelte + npm | TACO dicts -- pure Python, no toolchain |
| Layout control | Rigid (columns, sidebar) | Rigid (Row/Column) | Full CSS via bitwrench themes + bw.css() |
| Transport | WebSocket (Tornado) | SSE + HTTP (FastAPI) | SSE + POST default, WebSocket opt-in |
| Embedded/IoT | No | No | Yes -- bitwrench runs on ESP32/Pico W |
| Multi-page apps | st.navigation (fragile state) | No native support | @ww.page() decorator with shared state |
| Production state mgmt | st.session_state (flat dict, string keys) | gr.State (memory leaks, 60-min cleanup) | Server-side state with deterministic cleanup |
| Instant sharing | Streamlit Cloud | share=True tunnel | Future: webwrench.dev (not v1) |

---

## 2. Architecture

### 2.1 System Overview

```
 Python (webwrench)                    Browser
+------------------------+           +-------------------------+
| User's Python script   |           | bitwrench.js (bundled)  |
|   |                    |           |   +-- Chart.js           |
|   v                    |  SSE -->  |   +-- D3.js              |
| webwrench server       | -------> |   +-- Leaflet            |
|  (asyncio / uvicorn)   | <------- |   +-- three.js            |
|                        |  POST <-- |   +-- bwclient.js        |
+------------------------+           +-------------------------+
```

**Frontend**: bitwrench.js + bundled visualization libraries. No React, no
Svelte, no build step. The browser receives a shell HTML page with all JS
inlined or served from the webwrench package.

**Backend**: Pure Python. asyncio-based HTTP server. Serves shell HTML,
handles SSE streams, processes POST callbacks.

**Protocol**: bwserve -- 9 message types over SSE (server-to-client) with
POST callbacks (client-to-server). See Section 6 for details.

### 2.2 Bundled Frontend Libraries

webwrench ships these JS libraries inside the pip package. All libraries
are served from webwrench's built-in HTTP server. No CDN calls, no npm
installs, no internet required. Your app runs sandboxed.

| Library | Version | Size (min+gz) | Purpose |
|---|---|---|---|
| bitwrench.js | latest | ~38 KB | DOM, TACO, themes, BCCL components |
| Chart.js | 4.x | ~70 KB | Bar, line, pie, scatter, radar, polar, bubble |
| D3.js | 7.x | ~100 KB | Custom SVG viz, force graphs, geo projections |
| Leaflet | 1.9.x | ~42 KB | Interactive maps, tile layers, markers |
| three.js | r16x | ~180 KB | 3D rendering, WebGL scenes |
| html2canvas | 1.4.x | ~40 KB | Screenshot/export support |
| **Total** | | **~470 KB** | All gzipped, served once, browser-cached |

**Batteries included**: bitwrench.js is always loaded (it is the
runtime). The visualization libraries (Chart.js, D3, Leaflet, three.js)
are loaded on demand -- when you call `ww.chart()`, the shell page
includes a `<script>` tag for Chart.js served from webwrench's own
`/ww/lib/` route. When you call `ww.map()`, Leaflet gets included.
This is not "tree-shaking" (a build-time concept from the React world).
It is simply: include what you use, serve it yourself.

**Why self-hosted by default**: Stability. A webwrench app that works
today should work identically in 3 years. CDN URLs break, CDN versions
get yanked, CDN providers go down, corporate firewalls block CDNs.
Vendoring the libraries inside the pip package means the app is a
self-contained unit. `pip install webwrench==1.0.0` in 2029 produces
the same app as it does today.

**CDN opt-in** (runtime config, not build config):

```python
# Default: libraries served from webwrench's bundled assets
ww.serve()  # Everything comes from localhost

# Opt-in: use CDN for all libraries (e.g., for smaller Docker images)
ww.serve(assets='cdn')

# Or set globally before serve
ww.options.assets = 'cdn'
ww.serve()
```

This is a runtime decision, not a build decision. It does not affect the
API or the app's behavior -- only where `<script src="...">` points to.
Pythonic: keyword arg on `serve()`, or a module-level option. No config
files, no YAML, no JSON.

### 2.3 No Full Re-Run Model

This is the fundamental architectural difference from Streamlit.

**Streamlit**: User moves slider -> entire Python script re-executes ->
entire UI re-renders. Requires caching decorators to avoid re-computing
expensive operations.

**webwrench**: User moves slider -> POST sends slider value to server ->
Python handler runs -> handler calls `ww.patch('chart', new_data)` ->
SSE sends a single patch message -> only the chart updates. The rest of
the page is untouched.

This means:
- No `@st.cache_data` equivalent needed for basic use
- No re-initialization guards (`if "key" not in st.session_state`)
- No script execution ordering surprises
- O(1) update cost per interaction, not O(n) where n = script complexity

### 2.4 Two Distinct Features: Live Apps and Report Generation

webwrench enables two separate things. They share the same Python API
for building UI, but they are different products with different outputs.

**Feature 1: Live Apps** (`ww.serve()`)

A running Python server with live SSE updates, interactive widgets, and
server-side callbacks. This is the Streamlit/Gradio replacement. The
server stays running, users connect via browser, interactions POST back
to Python handlers.

```python
import webwrench as ww

ww.title("Live Dashboard")
chart = ww.chart(get_data(), type='bar')
btn = ww.button("Refresh")

@btn.on_click
def refresh():
    chart.update(get_data())  # Server fetches new data, patches chart

ww.serve(port=8080)  # Server runs until stopped
```

**Feature 2: Report Generation** (`ww.export()`)

Produces a self-contained HTML file. No server involved. The Python
script runs, builds the UI with the same `ww.*` calls, then writes it
to a file instead of serving it. Same API, different output.

```python
import webwrench as ww

ww.title("Q1 Results")
ww.chart(q1_data, type='bar', labels=quarters)
ww.table(summary_df)
ww.text("Revenue grew 48% year-over-year.")
ww.export('q1-report.html')  # Write file, done. No server.
```

Note: the developer uses the exact same `ww.title()`, `ww.chart()`,
`ww.table()` calls. The only difference is the last line: `ww.export()`
instead of `ww.serve()`. No separate Report class, no second API to
learn. A Streamlit user can read this immediately.

The report file contains:
- bitwrench.js (minified, inlined)
- Chart.js / D3 / Leaflet / three.js (whichever the script used)
- All data serialized as JSON
- All TACO structures pre-rendered as HTML
- Interactive charts (hover tooltips, legend toggling, zoom/pan)
- No server required -- open in any browser, email to anyone

Reports can also be generated from within a live app:

```python
@export_btn.on_click
def do_export():
    # Capture current state as report
    ww.export('snapshot.html')
    ww.download('snapshot.html')  # Send to user's browser
```

These are complementary features. A data team might run a live dashboard
(`ww.serve()`) during the day and generate nightly HTML reports
(`ww.export()`) via cron. Same API, different last line.

---

## 3. API Design

### 3.1 Philosophy: Hybrid API

webwrench supports two modes that compose seamlessly:

**Script mode** (Streamlit-like): Top-to-bottom, sequential. Best for
quick dashboards and reports. But unlike Streamlit, the script runs
ONCE to build the initial UI, not on every interaction.

**App mode** (Flask-like): Decorator-based routes and explicit event
handlers. Best for multi-page apps and complex interactions.

Both modes share the same underlying primitives.

### 3.2 Script Mode Examples

**Hello World**:
```python
import webwrench as ww

ww.title("Hello World")
ww.text("This is my first webwrench app")
ww.serve()
```

**Slider + Chart**:
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

**DataFrame display**:
```python
import webwrench as ww
import pandas as pd

df = pd.DataFrame({'name': ['Alice','Bob','Carol'], 'score': [95, 87, 92]})
ww.title("Scores")
ww.table(df, sortable=True, searchable=True)
ww.serve()
```

**Static export**:
```python
import webwrench as ww

ww.title("Quarterly Report")
ww.chart([45, 67, 89, 34], type='line', labels=['Q1','Q2','Q3','Q4'])
ww.text("Revenue grew 48% year-over-year.")
ww.export('quarterly-report.html')
```

### 3.3 App Mode Examples

**Multi-page app**:
```python
import webwrench as ww

app = ww.App()

@app.page('/')
def home(ctx):
    ctx.title("Dashboard")
    ctx.chart(get_data(), type='bar')

@app.page('/settings')
def settings(ctx):
    ctx.title("Settings")
    theme = ctx.select("Theme", ['light', 'dark', 'ocean'])

    @theme.on_change
    def switch(value):
        ctx.set_theme(value)

@app.page('/report')
def report(ctx):
    ctx.title("Monthly Report")
    ctx.chart(get_monthly_data(), type='line')
    ctx.button("Export PDF", on_click=lambda: ctx.screenshot('report.pdf'))

app.serve(port=8080)
```

**Shared state across pages**:
```python
app = ww.App()
app.state['user'] = None  # Shared across all pages for this session

@app.page('/')
def home(ctx):
    if ctx.state['user']:
        ctx.text(f"Welcome back, {ctx.state['user']}")
    else:
        ctx.redirect('/login')

@app.page('/login')
def login(ctx):
    name = ctx.input("Username")
    btn = ctx.button("Login")

    @btn.on_click
    def do_login():
        ctx.state['user'] = name.value
        ctx.redirect('/')
```

### 3.4 Core API Surface

#### Display Elements

```python
ww.title(text)                    # <h1>
ww.heading(text, level=2)         # <h2>..<h6>
ww.text(text)                     # <p>
ww.markdown(md_string)            # Rendered markdown
ww.code(code_string, lang='python')  # Syntax-highlighted code block
ww.html(raw_html)                 # Raw HTML (escaped by default, raw=True to bypass)
ww.image(src, alt='', width=None) # Image from URL, path, or bytes
ww.divider()                      # <hr>
```

#### Input Widgets

All widgets return a handle object with `.value` and `.on_change(callback)`.

```python
ww.button(label, on_click=None)          # Click handler
ww.input(label, placeholder='', value='')  # Text input
ww.textarea(label, rows=4)              # Multi-line text
ww.slider(label, min=0, max=100, value=50, step=1)
ww.select(label, options=['a','b','c'], value='a')
ww.checkbox(label, value=False)
ww.radio(label, options=['x','y','z'])
ww.file_upload(label, accept='.csv,.json')
ww.date_picker(label)
ww.color_picker(label, value='#3366cc')
ww.number(label, min=0, max=100, step=1, value=0)
```

#### Visualization

```python
# Chart.js (simple, declarative)
ww.chart(data, type='bar', labels=None, title=None, options=None)
ww.chart(datasets=[
    {'label': 'Sales', 'data': [12,19,3], 'color': '#3366cc'},
    {'label': 'Returns', 'data': [2,3,1], 'color': '#cc3333'}
], type='line', labels=['Jan','Feb','Mar'])

# Supported Chart.js types:
# 'bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea',
# 'scatter', 'bubble', 'mixed'

# D3 (advanced, custom)
ww.d3(render_func, data, width=600, height=400)
# render_func is a Python callable that returns D3 SVG specification
# OR a string of D3 JavaScript code

# Leaflet (maps)
ww.map(center=[37.7749, -122.4194], zoom=12)
ww.map(markers=[
    {'lat': 37.77, 'lng': -122.41, 'label': 'Office'},
    {'lat': 37.78, 'lng': -122.42, 'label': 'Warehouse'}
])

# three.js (3D)
ww.scene3d(objects=[...], camera={...}, controls='orbit')

# Pandas integration
ww.plot(df, x='date', y='revenue', type='line')  # DataFrame shorthand
ww.plot(df, x='category', y='count', type='bar', color='region')
```

#### Layout

```python
# Columns
with ww.columns(3) as cols:
    with cols[0]:
        ww.text("Left")
    with cols[1]:
        ww.chart(data1)
    with cols[2]:
        ww.chart(data2)

# Columns with custom widths
with ww.columns([2, 1]) as cols:  # 2:1 ratio
    with cols[0]:
        ww.chart(main_chart_data)
    with cols[1]:
        ww.text("Sidebar content")

# Tabs
with ww.tabs(['Overview', 'Details', 'Settings']) as tabs:
    with tabs[0]:
        ww.title("Overview")
    with tabs[1]:
        ww.table(detail_data)
    with tabs[2]:
        ww.text("Settings here")

# Accordion / collapsible
with ww.accordion("Advanced Options", open=False):
    ww.slider("Threshold", 0, 100, 50)

# Sidebar
with ww.sidebar():
    ww.title("Navigation")
    ww.nav([
        {'text': 'Home', 'href': '/'},
        {'text': 'Reports', 'href': '/reports'}
    ])

# Grid (CSS Grid -- full control)
with ww.grid(template='1fr 2fr / auto auto auto'):
    ww.text("Cell 1")
    ww.chart(data)
    ww.table(df)

# Card
with ww.card(title="Monthly Revenue"):
    ww.chart(revenue_data, type='line')
    ww.text("Up 12% from last month")

# Modal
modal = ww.modal("Confirm Delete")
with modal:
    ww.text("Are you sure?")
    ww.button("Yes", on_click=do_delete)
    ww.button("Cancel", on_click=modal.close)
```

#### Data Display

```python
# Tables (bitwrench makeTable under the hood)
ww.table(data, sortable=True, searchable=True, paginate=20)
ww.table(df)  # pandas DataFrame
ww.table(records)  # list of dicts

# Metrics / KPI cards
ww.metric("Revenue", "$1.2M", delta="+12%", delta_color="green")

# JSON viewer
ww.json(data_dict, collapsed=2)

# Progress
bar = ww.progress(0, max=100)
bar.update(50)

# Toast notifications
ww.toast("File saved successfully", type='success', duration=3000)
```

#### Theming

```python
# Use built-in bitwrench themes
ww.theme('ocean')  # Calls bw.loadStyles() with ocean palette
ww.theme('dark')
ww.theme('forest')

# Custom theme from seed colors
ww.theme(primary='#006666', secondary='#333333')

# Toggle light/dark at runtime
ww.toggle_theme()  # Calls bw.toggleStyles()

# Inject custom CSS
ww.css({
    '.my-card': {
        'border-radius': '12px',
        'box-shadow': '0 4px 8px rgba(0,0,0,0.1)'
    }
})
```

#### Export and Screenshot

```python
# Export entire page as self-contained HTML
ww.export('report.html')

# Export with specific options
ww.export('report.html', include_3d=False, minify=True)

# Screenshot (uses html2canvas)
ww.screenshot('dashboard.png')           # Full page
ww.screenshot('chart.png', selector='#revenue-chart')  # Specific element

# PDF export (via browser print or puppeteer if available)
ww.export_pdf('report.pdf')
```

---

## 4. State Management

### 4.1 Design Principles

1. **Server owns state, client owns DOM**: Python holds the authoritative
   data. The browser's DOM reflects it. No client-side state to sync.

2. **Explicit updates, not reactive re-runs**: When state changes, the
   developer decides what to update via `.update()`, `.patch()`, or
   re-render calls. No implicit dependency tracking.

3. **Deterministic cleanup**: When a session disconnects (browser tab
   closed, network timeout), state is cleaned up immediately -- not after
   60 minutes (Gradio) or "when GC runs" (Streamlit).

4. **No string-keyed global dict**: State is structured Python objects,
   not `session_state["my_key_42"]`.

### 4.2 Session State

```python
@app.page('/')
def dashboard(ctx):
    # ctx.state is a typed namespace, not a flat dict
    ctx.state.counter = 0
    ctx.state.user = None
    ctx.state.filters = {'date_range': 'last_30', 'category': 'all'}

    btn = ctx.button("Increment")

    @btn.on_click
    def increment():
        ctx.state.counter += 1
        counter_display.update(str(ctx.state.counter))
```

### 4.3 Shared State (Cross-Page)

```python
app = ww.App()

# App-level state persists across page navigations within a session
app.state.user = None
app.state.preferences = {}

@app.page('/')
def home(ctx):
    # Access shared state
    if ctx.app.state.user:
        ctx.text(f"Hello, {ctx.app.state.user}")
```

### 4.4 Server-Side Computed Values

```python
@app.page('/dashboard')
def dashboard(ctx):
    # Expensive computation runs once, result cached per session
    data = ctx.compute('sales_data', fetch_sales_from_db)

    chart = ctx.chart(data, type='bar')
    refresh = ctx.button("Refresh")

    @refresh.on_click
    def do_refresh():
        # Invalidate + recompute
        data = ctx.recompute('sales_data', fetch_sales_from_db)
        chart.update(data)
```

---

## 5. Transport Layer

### 5.1 Default: SSE + POST (bwserve Protocol)

The developer never manages transport directly. Under the hood:

**Server -> Client (SSE)**:
- DOM patches (`replace`, `patch`, `append`, `remove`)
- Batched updates (`batch`)
- Function registration and invocation (`register`, `call`)
- Component messages (`message`)
- Keep-alive pings every 15 seconds

**Client -> Server (POST)**:
- Widget value changes (slider moved, button clicked, text entered)
- Query responses (screenshot data, DOM inspection results)
- Custom action dispatches

```
Browser                              Python
  |                                    |
  |--- GET / -----------------------> | (serve shell HTML)
  |<-- HTML + bitwrench.js ---------- |
  |                                    |
  |--- GET /bw/events/:id ----------> | (open SSE stream)
  |<-- SSE: {type:'replace',...} ----- | (initial render)
  |<-- SSE: {type:'patch',...} ------- | (live updates)
  |                                    |
  |--- POST /bw/return/action/:id --> | (user clicked button)
  |<-- SSE: {type:'patch',...} ------- | (update response)
  |                                    |
  |--- POST /bw/return/query/:id ---> | (screenshot data)
```

### 5.2 WebSocket Upgrade (Opt-In)

For apps that need high-frequency bidirectional communication:

```python
app = ww.App(transport='websocket')

# Or per-page
@app.page('/chat', transport='websocket')
def chat(ctx):
    # Full-duplex communication
    pass
```

WebSocket mode uses the same message format as SSE mode -- the protocol
is transport-agnostic. The developer's code does not change.

### 5.3 When to Use Which

| Use Case | Transport | Why |
|---|---|---|
| Dashboard with charts | SSE + POST | One-way updates, occasional clicks |
| Form-based app | SSE + POST | Submit-driven, low frequency |
| Chat application | WebSocket | Bidirectional, high frequency |
| Real-time collaboration | WebSocket | Multi-user, low latency |
| IoT sensor display | SSE + POST | Server pushes readings |
| Gaming | WebSocket | Frame-rate-sensitive input |

---

## 6. bwserve Protocol (Reference)

webwrench speaks the existing bitwrench bwserve protocol. This ensures
compatibility with the Node.js bwserve implementation and allows mixed
Python/Node backends in the future.

### 6.1 Message Types (Server -> Client)

| Type | Fields | Effect |
|---|---|---|
| `replace` | `target`, `node` | Replace element content with TACO |
| `patch` | `target`, `content`, `attr` | Update text and/or attributes only |
| `append` | `target`, `node` | Add child element |
| `remove` | `target` | Delete element (with lifecycle cleanup) |
| `batch` | `ops` (array) | Execute multiple operations atomically |
| `register` | `name`, `body` | Send named JS function to client |
| `call` | `name`, `args` | Invoke registered or built-in function |
| `exec` | `code` | Execute arbitrary JS (opt-in, security risk) |
| `message` | `target`, `action`, `data` | Dispatch to component handle method |

### 6.2 Client -> Server (POST Routes)

| Route | Purpose |
|---|---|
| `/bw/return/action/:clientId` | Widget interaction (button click, etc.) |
| `/bw/return/query/:clientId` | Response to server query (DOM inspection) |
| `/bw/return/screenshot/:clientId` | Screenshot data (base64 PNG) |
| `/bw/return/event/:clientId` | DOM event forwarded to server |

### 6.3 Built-In Client Functions

Pre-registered by bwclient.js, callable from Python via `ctx.call()`:

| Function | Purpose |
|---|---|
| `scrollTo(selector)` | Scroll element into view |
| `focus(selector)` | Focus an input element |
| `download(filename, content, mime)` | Trigger file download |
| `clipboard(text)` | Copy to clipboard |
| `redirect(url)` | Navigate to URL |
| `log(...args)` | Console.log |

---

## 7. Visualization Deep Dive

### 7.1 Chart.js Integration

Chart.js handles 90% of dashboard chart needs with zero configuration:

```python
# Simple -- data + type
ww.chart([12, 19, 3, 5, 2, 3], type='bar')

# With labels and title
ww.chart(
    data=[12, 19, 3, 5, 2, 3],
    labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    type='line',
    title='Monthly Sales'
)

# Multi-dataset
ww.chart(
    datasets=[
        {'label': '2024', 'data': [12, 19, 3], 'color': '#3366cc'},
        {'label': '2025', 'data': [15, 22, 7], 'color': '#cc6633'}
    ],
    labels=['Q1', 'Q2', 'Q3'],
    type='bar'
)

# From pandas DataFrame
ww.chart(df, x='month', y='revenue', type='line')
ww.chart(df, x='category', y=['sales', 'returns'], type='bar')

# Full Chart.js options pass-through
ww.chart(data, type='radar', options={
    'scales': {'r': {'beginAtZero': True}},
    'plugins': {'legend': {'position': 'bottom'}}
})
```

**Supported types**: bar, line, pie, doughnut, radar, polarArea, scatter,
bubble, mixed.

**Interactive in both live and static export**: Tooltips, hover effects,
legend toggling, and animation all work without a server.

### 7.2 D3 Integration

For custom, publication-quality visualizations:

```python
# Option 1: D3 specification as Python dict
ww.d3({
    'type': 'force',
    'nodes': [{'id': 'A'}, {'id': 'B'}, {'id': 'C'}],
    'links': [{'source': 'A', 'target': 'B'}, {'source': 'B', 'target': 'C'}]
}, width=600, height=400)

# Option 2: D3 JavaScript code (full power)
ww.d3_raw("""
    const svg = d3.select(container);
    const data = DATA;  // Injected by webwrench
    // ... full D3 code ...
""", data=my_python_data)

# Option 3: Pre-built D3 visualizations
ww.treemap(data, value_key='size', label_key='name')
ww.sunburst(hierarchical_data)
ww.chord(matrix_data, labels=['A','B','C','D'])
ww.sankey(flows_data)
ww.heatmap(matrix, x_labels=cols, y_labels=rows)
ww.force_graph(nodes, edges)
```

### 7.3 Leaflet Integration

```python
# Basic map
ww.map(center=[37.7749, -122.4194], zoom=12)

# With markers
ww.map(
    center=[40.7128, -74.0060],
    zoom=10,
    markers=[
        {'lat': 40.71, 'lng': -74.00, 'label': 'NYC Office', 'color': 'red'},
        {'lat': 40.75, 'lng': -73.98, 'label': 'Midtown', 'color': 'blue'}
    ]
)

# Choropleth from GeoJSON
ww.map(
    geojson=us_states_geojson,
    color_by='population',
    colorscale='viridis'
)

# Heatmap layer
ww.map(
    center=[34.05, -118.25],
    heatmap=earthquake_coords  # [[lat, lng, magnitude], ...]
)
```

### 7.4 three.js Integration

```python
# Basic 3D scene
ww.scene3d(
    objects=[
        {'type': 'box', 'size': [1,1,1], 'color': '#3366cc', 'position': [0,0,0]},
        {'type': 'sphere', 'radius': 0.5, 'color': '#cc3333', 'position': [2,0,0]}
    ],
    controls='orbit',  # Mouse orbit controls
    width=600, height=400
)

# Point cloud (scientific data)
ww.point_cloud(points_xyz, colors=colors_rgb, size=0.02)

# Surface plot (alternative to matplotlib 3D)
ww.surface(z_matrix, x_range=[-5,5], y_range=[-5,5], colorscale='jet')

# STL/OBJ model viewer
ww.model3d('model.stl', controls='orbit', auto_rotate=True)
```

### 7.5 Pandas Integration

webwrench detects pandas DataFrames and provides smart defaults:

```python
import pandas as pd

df = pd.read_csv('sales.csv')

# Auto-detect best chart type from data shape
ww.plot(df)  # Heuristic: numeric cols -> line chart, categorical -> bar

# Explicit
ww.plot(df, x='date', y='revenue', type='line', title='Revenue Over Time')
ww.plot(df, x='region', y='sales', type='bar', color='product')
ww.plot(df, x='price', y='quantity', type='scatter', size='revenue')
```

### 7.6 Report Behavior

| Library | Live App | Report (.html) |
|---|---|---|
| Chart.js | Full interactivity | Full interactivity (tooltips, legend, animation) |
| D3 | Full interactivity | SVG preserved, hover/transitions preserved |
| Leaflet | Full interactivity | Map renders, tiles cached or linked |
| three.js | Full interactivity | WebGL scene preserved, orbit controls work |

Reports inline only the libraries the report actually uses. If you only
called `ww.chart()`, only bitwrench + Chart.js are inlined. This is not
tree-shaking (a build step) -- it is simply not including libraries you
did not use.

---

## 8. Competitive Analysis

### 8.1 Streamlit Weaknesses (Exploitable)

**Architecture**:
- Full script re-run on every interaction. A slider change re-executes
  the entire Python script. Mitigated by @st.cache_data and @st.fragment,
  but these are band-aids on a fundamentally wasteful execution model.
- Each browser tab spawns a dedicated ScriptRunner thread with its own
  memory. Linear memory growth per concurrent user.
- WebSocket transport (Tornado) requires sticky sessions for load balancing.

**State management**:
- `st.session_state` is a flat dict with string keys. No typing, no
  structure, no IDE autocomplete.
- Every stateful value needs initialization guards:
  `if "key" not in st.session_state: st.session_state.key = default`
- Callbacks execute before the main script re-run, creating non-obvious
  execution ordering.
- URL navigation destroys state (creates new session).

**Layout**:
- Rigid: columns, sidebar, tabs, expanders. No CSS Grid, no flexbox
  control, no custom spacing.
- 120px wasted blank space at top of every page (GitHub issue #6336).
- Nested columns beyond one level explicitly warned against.
- Custom layouts require injecting raw CSS via `st.markdown()` with
  `unsafe_allow_html=True`, targeting internal `data-testid` attributes
  that break between releases.

**Custom components**:
- V1: iframe-based. Each component sandboxed. Cannot share CSS, cannot
  communicate with each other, height calculation bugs.
- V2 (2025+): No iframe, but still requires JavaScript/TypeScript
  knowledge and npm toolchain.

**No static export**: GitHub issue #611 (opened 2019, still unresolved).
Requires a running Python server for any interactivity.

**Scale**: Practical ceiling of 10-50 concurrent users on 4GB server.
No built-in horizontal scaling. Cache invalidation storms on deployment.

**Corporate risk**: Acquired by Snowflake for $800M (2022). Incentive is
to drive Snowflake adoption, not open-source innovation. "Streamlit in
Snowflake" has significant restrictions (32MB message limit, CSP blocks
external scripts, many features unsupported).

### 8.2 Gradio Weaknesses (Exploitable)

**ML-only focus**: "Specifically designed for ML applications." General
dashboards, admin panels, and CRUD apps are underserved. Layout is
Row/Column only -- no CSS Grid, no responsive breakpoints.

**Performance regressions**: Svelte 4 -> 5 rewrite (Gradio 5 -> 6)
caused widespread breakage. Users report 10x slowdowns for visibility
changes. "Every single release of Gradio 6 has broken working features."

**Memory leaks**: gr.State grows unbounded. Documented case: 100MB ->
7GB after single button click. 60-minute cleanup delay after tab close.
Issue remains open.

**Custom components require Svelte + npm**: The Gradio team acknowledges
this conflicts with their user base ("folks who want to touch as little
frontend code as possible"). A plain HTML/CSS/JS proposal exists but has
not shipped.

**No static export**: Architecture requires running Python server. The
browser-only Gradio-Lite (Pyodide/WASM) project is reportedly archived.

**Version churn**: Three major versions (4, 5, 6) with breaking changes.
Developers pin old versions to avoid regressions.

**No built-in charting**: All visualization depends on external Python
libraries (Matplotlib, Plotly, Bokeh). No interactive chart components
beyond what those libraries provide.

### 8.3 Other Competitors

**Panel (HoloViz)**: More flexible than Streamlit, supports Bokeh/Plotly/
Matplotlib. But complex API, heavy dependencies, no static export for
interactive content.

**Dash (Plotly)**: Closest to webwrench in architecture (callback-based,
no re-run). But tied to Plotly ecosystem, verbose callback syntax,
requires understanding of React component model for custom elements.

**Shiny for Python**: True reactive model (like R Shiny). Minimal
re-renders. But small ecosystem, limited community adoption.

**NiceGUI**: Python UI framework with Vue.js frontend. Similar goals to
webwrench. But tied to Vue ecosystem, no static export, limited
visualization compared to bundled Chart.js+D3.

### 8.4 webwrench Positioning Matrix

```
                    Easy to start
                         |
              Streamlit  |  webwrench
                         |
  Limited ---------------+--------------- Powerful
  visualization          |           visualization
                         |
               Gradio    |  Dash/Panel
                         |
                    Hard to start
```

webwrench aims for the top-right quadrant: easy to start (Streamlit-like
script mode) with powerful visualization (Chart.js + D3 + Leaflet +
three.js bundled, no pip installs needed).

---

## 9. Implementation Phases

### Phase 1: Foundation (v0.1.0)

**Goal**: "Hello World" to working dashboard in pure Python, with
screenshot and static export from day one.

- [ ] Python HTTP server (asyncio-based, zero external deps)
- [ ] Shell HTML generator (inlines bitwrench.js)
- [ ] SSE streaming with keep-alive
- [ ] POST callback handling
- [ ] Core display elements: title, text, heading, markdown, divider, image
- [ ] Core widgets: button, input, slider, select, checkbox
- [ ] Chart.js integration: bar, line, pie, scatter
- [ ] ww.table() with sortable columns (uses bw.makeTable())
- [ ] ww.theme() with bitwrench preset themes (calls bw.loadStyles())
- [ ] ww.serve() and ww.export() entry points
- [ ] **Static HTML export** (bitwrench + Chart.js inlined, self-contained)
- [ ] **ww.screenshot()** via html2canvas (already vendored in bitwrench)
- [ ] **ww.download()** -- trigger browser file download from Python
- [ ] Session management (per-tab state, cleanup on disconnect)
- [ ] `pip install webwrench` with bundled JS assets
- [ ] Zero vanilla JS in webwrench -- all client behavior via TACO + bwserve

**Deliverable**: A pip-installable package that can produce a live
dashboard, export it as static HTML, and screenshot any element.
Scientists can `ww.export('report.html')` and email the file.

### Phase 2: Layout and Interaction (v0.2.0)

- [ ] Layout primitives: columns, tabs, accordion, sidebar, card, grid
- [ ] Modal dialogs
- [ ] Toast notifications
- [ ] Multi-dataset charts
- [ ] Pandas DataFrame integration (ww.plot, ww.table from df)
- [ ] ww.metric() KPI cards
- [ ] ww.progress() bar
- [ ] File upload widget
- [ ] Color picker, date picker, number input
- [ ] @app.page() decorator for multi-page apps
- [ ] Shared state across pages
- [ ] Widget handle .on_change() callbacks
- [ ] ctx.compute() / ctx.recompute() for cached computations

### Phase 3: Advanced Visualization (v0.3.0)

- [ ] D3 integration (pre-built: treemap, sunburst, heatmap, force graph, sankey, chord)
- [ ] D3 raw mode (custom JS code injection with data)
- [ ] Leaflet maps (markers, choropleth, heatmap layer)
- [ ] three.js scenes (basic shapes, point clouds, surface plots, model viewer)
- [ ] ww.export_pdf() via print dialog
- [ ] Screenshot of specific elements with annotation overlay
- [ ] Report generation for all viz types (D3, Leaflet, three.js)

### Phase 4: Production Features (v0.4.0)

- [ ] WebSocket transport (opt-in per-page)
- [ ] Authentication middleware (basic auth, token auth, OAuth hooks)
- [ ] Rate limiting
- [ ] CORS configuration
- [ ] Multi-worker support (uvicorn workers)
- [ ] CDN override for JS assets
- [ ] Custom CSS injection (ww.css())
- [ ] ww.nav() navigation component
- [ ] Breadcrumbs
- [ ] Search widget with server-side filtering
- [ ] Background tasks (long-running computations with progress)

### Phase 5: Ecosystem (v0.5.0+)

- [ ] Plugin system for third-party widgets
- [ ] CLI: `webwrench serve app.py`, `webwrench export app.py report.html`
- [ ] Hot reload in development mode
- [ ] webwrench.dev free hosting (like Streamlit Cloud)
- [ ] Jupyter notebook integration (inline webwrench in cells)
- [ ] REST API auto-generation (like Gradio)
- [ ] Docker base image
- [ ] VS Code extension (live preview)

---

## 10. Technical Decisions

### 10.1 Python Server Stack

**Option A (chosen for v1): asyncio + built-in http**

Zero external dependencies. Works with Python 3.9+. Handles SSE streams
natively via chunked transfer encoding. Single-threaded event loop
with async handlers.

```python
pip install webwrench  # No other deps needed
```

**Future**: Add optional uvicorn/FastAPI adapter for production deployment
with multi-worker support. But the core library works with zero pip deps
beyond webwrench itself.

### 10.2 TACO in Python

bitwrench's TACO format maps directly to Python dicts:

```python
# JavaScript TACO
{'t': 'div', 'a': {'class': 'card'}, 'c': 'Hello'}

# Python TACO (identical)
{'t': 'div', 'a': {'class': 'card'}, 'c': 'Hello'}
```

No translation layer needed. Python dicts serialize to JSON, which
bitwrench.js consumes directly. This is a major advantage over
Streamlit (protobuf) and Gradio (custom serialization).

### 10.3 Dependency Policy: Longevity Above All

**The 3-year rule**: `pip install webwrench==X.Y.Z` must produce an
identical, working app in 2029 as it does in 2026. This means:

- **Zero runtime Python deps**. No Flask, no FastAPI, no Jinja2, no
  aiohttp. The HTTP server uses Python's built-in `asyncio`. Zero
  third-party imports means zero transitive dependency breakage.

- **Vendored JS libraries**. bitwrench, Chart.js, D3, Leaflet, three.js,
  and html2canvas are pinned, minified files inside the pip package.
  They do not fetch from CDNs at runtime (unless the developer opts in).
  They do not change between webwrench releases unless deliberately
  upgraded.

- **No build toolchain**. No webpack, no rollup, no esbuild in the
  webwrench package. The JS files are pre-built. `pip install` is the
  only step.

**Optional deps**: pandas (for DataFrame integration), numpy (for
array handling). Detected at import time, not required. If pandas is
not installed, `ww.table(df)` raises a clear error. Everything else
works.

**Dev deps**: pytest, playwright (for integration tests).

**Why this matters**: Streamlit has 30+ transitive Python deps. Gradio
has 50+. Both break regularly when dependencies release incompatible
versions. A Streamlit app from 2022 often cannot `pip install` cleanly
in 2026. webwrench avoids this entirely.

### 10.4 Python Version Support

Python 3.9+ (matches bitwrench's browser support philosophy of
"reasonably current, not bleeding edge").

### 10.5 Licensing

MIT license (matches bitwrench). All bundled JS libraries are MIT
or BSD compatible:
- bitwrench: BSD-2-Clause
- Chart.js: MIT
- D3: ISC
- Leaflet: BSD-2-Clause
- three.js: MIT
- html2canvas: MIT

---

## 11. Package Structure

```
webwrench/
  __init__.py           # Public API: ww.title, ww.chart, ww.serve, etc.
  app.py                # App class, page routing, session management
  server.py             # HTTP server, SSE streaming, POST handling
  state.py              # Session state, shared state, compute cache
  widgets.py            # Widget definitions (button, slider, etc.)
  charts.py             # Chart.js, D3, Leaflet, three.js wrappers
  layout.py             # Columns, tabs, grid, sidebar, card, modal
  display.py            # Title, text, markdown, code, image, table
  export.py             # Static HTML export, screenshot, PDF
  theme.py              # bitwrench theme integration
  taco.py               # TACO dict builders and utilities
  _assets/              # Bundled JS/CSS files
    bitwrench.umd.min.js
    bitwrench.css
    chart.min.js
    d3.min.js
    leaflet.min.js
    leaflet.css
    three.min.js
    html2canvas.min.js
    bwclient.js         # SSE client (inlined into shell HTML)
  _shell.py             # Shell HTML template generator
```

---

## 12. Success Criteria

### v0.1.0 (Foundation)

- [ ] 4-line hello world works: title, text, serve
- [ ] Chart with 6 data points renders in browser
- [ ] Button click triggers Python callback, updates chart
- [ ] `ww.export('out.html')` produces a self-contained HTML file <200KB
- [ ] Static export chart has working tooltips (no server)
- [ ] Slider widget works with on_change callback
- [ ] Theme switching works (light/dark/custom)
- [ ] `pip install webwrench` from PyPI, zero other deps needed
- [ ] Works on Python 3.9, 3.10, 3.11, 3.12
- [ ] 80%+ test coverage

### v0.3.0 (Visualization Parity)

- [ ] Can recreate any Streamlit demo in fewer lines of code
- [ ] D3 force graph renders from Python data
- [ ] Leaflet map with 1000 markers renders smoothly
- [ ] three.js point cloud with 10K points renders
- [ ] Static export with all 4 viz libs is <600KB
- [ ] Multi-page app with shared state works

### v1.0.0 (Production Ready)

- [ ] 100+ concurrent users on single server (benchmark)
- [ ] WebSocket transport for chat/collab apps
- [ ] Authentication middleware
- [ ] Hot reload in dev mode
- [ ] CLI entry point: `webwrench serve app.py`
- [ ] Published documentation site
- [ ] 5+ community-contributed examples

---

## 13. What Streamlit and Gradio Users Actually Want

Sourced from GitHub issues, forum threads, and community discussions.
Each item cites real user complaints, not speculation.

### 13.1 Static/Offline Export

**Streamlit GitHub #611** (opened Oct 2019, still open 2026): "Export to
standalone HTML file." One of the most upvoted feature requests in
Streamlit's history. Architecturally impossible because the re-run model
requires a live Python server. Community workaround `st-static-export`
(PyPI) is limited to text + basic Altair charts, max 5000 rows.

**Gradio GitHub #9146, #4466**: Similar requests. Gradio-Lite (Pyodide/
WASM) was attempted but is reportedly archived. 5-15s cold start, no
C-extension packages, each instance consumes significant browser memory.

**webwrench answer**: Same API, different last line. Build your UI with
`ww.title()`, `ww.chart()`, `ww.table()`, then call `ww.export()` instead
of `ww.serve()`. Self-contained HTML with bitwrench + Chart.js inlined,
interactive charts (zoom, tooltips), opens in any browser. Can also be
called from within a live app as an export button.

### 13.2 Screenshot / Image Export

**Streamlit**: No built-in screenshot. Users resort to browser extensions,
Selenium scripts, or third-party packages. Forum threads document the
pain of capturing dashboard state for slide decks and emails.

**Gradio**: No screenshot capability. Users manually screenshot or use
Playwright/Puppeteer externally.

**webwrench answer**: `ww.screenshot('dashboard.png')` using bitwrench's
existing html2canvas integration (bwserve screenshot protocol, proven
since v2.0.20). Can target specific elements via selector.

### 13.3 Layout Control

**Streamlit GitHub #6336** (highly upvoted): "Too much blank space at
top of page." 120px wasted on every page. No fix without CSS hacks.
**Streamlit forum "CSS hacks"**: Hundreds of posts sharing fragile
workarounds like `st.markdown('<style>[data-testid="stSidebar"]
{width:400px}</style>', unsafe_allow_html=True)` -- targeting internal
attributes that break between releases.
**Streamlit docs** explicitly warn against nested columns beyond one
level. No CSS Grid. No custom spacing. No responsive breakpoints.

**Gradio GitHub #11708**: Alignment across rows broken. #12891, #12831:
Performance collapse with nested layouts (10s freeze vs 0.5s in v5).
No CSS Grid, no absolute positioning, no z-index control.

**webwrench answer**: Full CSS through bitwrench -- `bw.css()` for
custom rules, `bw.loadStyles()` for theming, CSS Grid via `ww.grid()`.
bitwrench's structural CSS handles spacing, padding, responsive behavior.

### 13.4 State Management

**Streamlit forum** "Beyond Dashboards: Building Complex, State-Persistent
Applications": Developer documents spending "2-3 months" mastering
`st.session_state`. Every variable needs `if "key" not in` guards.
**Streamlit GitHub #11679**: Concurrency bugs -- `on_change` callbacks
that take longer than the next interaction cause data loss.
**Streamlit forum** "Preserving Page State in Streamlit App with Multiple
Pages": URL navigation creates new sessions, destroying all state.

**Gradio GitHub #11602**: Memory jumps from 100MB to 7GB after a single
button click. Official docs warn: "gr.State increases in an unbounded
manner." **Gradio #7227**: Session state cleanup "does not occur until
the server is closed." **Gradio #9502**: gr.State objects must be inside
`gr.Blocks()` context -- centralized state patterns throw KeyError.

**webwrench answer**: Server-side Python objects, not string-keyed dicts.
No re-run ordering. Deterministic cleanup on disconnect. State persists
across page navigations within a session.

### 13.5 Charting Without Extra Dependencies

**Streamlit**: Native charts (`st.line_chart`, `st.bar_chart`) are thin
Altair wrappers -- minimal customization. Anything beyond basic requires
`pip install plotly` or `pip install matplotlib`, learning their APIs,
and dealing with theme conflicts between Streamlit and the chart library.
No chart click/selection callbacks without custom components.

**Gradio**: No built-in charting engine. All visualization through
external libraries. No heatmaps, treemaps, gauges, or dashboard-specific
charts. 3D plotting limited, discussed in forums as workarounds only.

**webwrench answer**: Chart.js bundled (bar, line, pie, radar, scatter,
bubble, polar, doughnut). D3 for advanced viz. Leaflet for maps.
three.js for 3D. Zero pip installs. Charts work in both live and
exported HTML.

### 13.6 Performance at Scale

**Streamlit forum** "Scalability concerns with large user base":
Community reports 10-50 concurrent user ceiling on 4GB server. Each tab
spawns a ScriptRunner thread with independent memory. WebSocket requires
sticky session load balancing. **Streamlit forum** "Troubleshooting
performance issues with multiple concurrent users": No built-in
horizontal scaling.

**Gradio GitHub #12831**: WanGP project reports 10x performance
regression from v5.29 to v6. Visibility changes went from <0.5s to 10s.
**Gradio #12921**: "Every single release of Gradio 6 has broken working
features and caused incredible performance regression."

**webwrench answer**: SSE+POST is standard HTTP. No sticky sessions.
Works behind any reverse proxy, CDN, or load balancer. Surgical DOM
patches (not full re-render). Server does not re-execute scripts.

### 13.7 Custom Components Without JavaScript Toolchains

**Streamlit**: V1 custom components require React + npm + iframe. V2
(2025+) removes iframe but still requires JavaScript/TypeScript.
Building a custom component is a multi-day project.

**Gradio GitHub #12074** (Gradio team): "Gradio users are folks who want
to touch as little frontend code as possible, and forcing them to
navigate different files for a single UI element and understand all the
existing component code conflicts with the core reason users use Gradio."
Custom components require Svelte + npm toolchain. Proposed plain
HTML/CSS/JS alternative has not shipped.

**webwrench answer**: Components are TACO dicts -- pure Python. No npm,
no Svelte, no React. If bitwrench's BCCL doesn't have a component you
need, contribute it to bitwrench (it's a PR, not a separate build
system). Custom visuals use the D3 or Chart.js integration.

### 13.8 Cookie and Auth Support

**Streamlit forum** "RANT: Feeling very disillusioned building on
Streamlit with lack of cookie support for cloud deployment": Developer
details frustration with inability to implement proper auth flows.
No built-in authentication. Streamlit Community Cloud has only basic
auth. No cookie support on cloud deployment.

**Gradio**: No built-in auth. Public share links expire after ~1 week.

**webwrench answer**: Standard HTTP server -- cookies work naturally.
Auth middleware can be added in Phase 4 (basic auth, token auth, OAuth
hooks). No architectural barrier like Streamlit's WebSocket-only
transport.

---

## 14. bitwrench PRs Required

Features that webwrench will need but bitwrench may not yet support.
Each becomes a PR against bitwrench, NOT a workaround in webwrench.

1. **Chart.js TACO wrapper**: A BCCL helper `bw.makeChart(config)` that
   returns TACO wrapping a `<canvas>` with Chart.js initialization in
   `o.mounted`. Needed so charts are TACO objects, not raw JS.

2. **Leaflet TACO wrapper**: Similar to Chart.js -- `bw.makeMap(config)`
   that returns TACO with Leaflet initialization in lifecycle hooks.

3. **three.js TACO wrapper**: `bw.makeScene3D(config)` for 3D scenes.

4. **D3 TACO wrapper**: `bw.makeD3(config)` for D3 visualizations using
   the `bw.raw()` SVG workaround pattern (since createDOM lacks SVG
   namespace support).

5. **Progress bar component**: `bw.makeProgress(value, max)` BCCL helper
   if not already present.

6. **Metric/KPI card component**: `bw.makeMetric(label, value, delta)`
   BCCL helper for dashboard KPI displays.

7. **Grid layout helper**: May need structural CSS additions for CSS Grid
   support beyond the existing flexbox-based layout.

8. **Export-friendly lifecycle**: Ensure `bw.createDOM()` can produce a
   complete DOM tree suitable for serialization to HTML string (for
   `ww.export()`), including Chart.js canvas rendering to static image
   fallback.

These PRs improve bitwrench for ALL users (not just webwrench), which
is the correct design direction.

---

## 15. Open Questions

1. **Async vs sync API**: Should widget callbacks be async by default?
   Streamlit is sync (thread-per-session). Gradio is async (FastAPI).
   webwrench could support both, but which is the default?

2. **DataFrame rendering**: For large DataFrames (100K+ rows), should
   webwrench virtualize the table (only render visible rows) or paginate?
   Streamlit virtualizes. Pagination is simpler and works in static export.

3. **D3 safety**: Allowing raw D3 JavaScript code (`ww.d3_raw()`) is
   powerful but introduces XSS risk. Should this be opt-in like
   bwserve's `exec` message type?

4. **Map tile caching in static export**: Leaflet maps need tile images
   from a tile server. Static export could: (a) link to tile CDN (requires
   internet), (b) cache visible tiles as base64 (large file), or
   (c) render as static image (loses interactivity). Which default?

5. **bitwrench-chart (P6)**: Once bitwrench's native SVG charting library
   ships, should webwrench migrate from Chart.js to bitwrench-chart for
   basic charts? Or keep both?

6. **Notebook integration**: Should `ww.chart()` work inline in Jupyter
   notebooks? This would require an IFrame or HTML display approach.
   Worth the complexity for v1?

---

## Appendix A: Why Not Just Use bwserve Directly?

bwserve is a Node.js library. Python developers should not need to install
Node.js, write JavaScript, or understand TACO format to build a dashboard.

webwrench wraps the bwserve protocol in a Pythonic API:

| bwserve (Node.js) | webwrench (Python) |
|---|---|
| `client.render('#app', {t:'div', c:'Hello'})` | `ww.text("Hello")` |
| `client.patch('counter', '42')` | `counter.update('42')` |
| `client.call('download', 'f.csv', data, 'text/csv')` | `ww.download('f.csv', data)` |
| Manual SSE/POST wiring | Automatic |
| Manual shell HTML | Automatic |
| Requires Node.js | `pip install webwrench` |

The protocol is identical. A webwrench app can even communicate with a
Node.js bwserve instance if needed (shared protocol = interop for free).

---

## Appendix B: Comparison Code -- Same App in Three Frameworks

### The app: Interactive bar chart with slider multiplier

**Streamlit (13 lines)**:
```python
import streamlit as st

data = [12, 19, 3, 5, 2, 3]
labels = ['Jan','Feb','Mar','Apr','May','Jun']

st.title("Sales Dashboard")
multiplier = st.slider("Multiplier", 1, 10, 1)
# Script re-runs here on every slider change
scaled = [d * multiplier for d in data]
st.bar_chart(dict(zip(labels, scaled)))
# Cannot export as HTML
```

**Gradio (16 lines)**:
```python
import gradio as gr

data = [12, 19, 3, 5, 2, 3]

def update(multiplier):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.bar(['Jan','Feb','Mar','Apr','May','Jun'],
           [d * multiplier for d in data])
    return fig

demo = gr.Interface(
    fn=update, inputs=gr.Slider(1, 10, value=1, label="Multiplier"),
    outputs=gr.Plot(), title="Sales Dashboard"
)
demo.launch()
# Cannot export as HTML
```

**webwrench (11 lines)**:
```python
import webwrench as ww

data = [12, 19, 3, 5, 2, 3]

ww.title("Sales Dashboard")
chart = ww.chart(data, type='bar', labels=['Jan','Feb','Mar','Apr','May','Jun'])
slider = ww.slider("Multiplier", min=1, max=10, value=1)

@slider.on_change
def update(value):
    chart.update([d * value for d in data])

ww.serve()  # OR: ww.export('dashboard.html') for static
```

Key differences:
- webwrench: 11 lines, no imports beyond webwrench, can export as HTML
- Only the chart updates on slider change (not the whole page)
- Chart.js renders natively in the browser (no matplotlib server-side)
