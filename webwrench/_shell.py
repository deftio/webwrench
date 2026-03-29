"""Shell HTML template generator.

Produces the initial HTML page that loads bitwrench.js and the bwclient.
"""

from __future__ import annotations

import json
import os
from typing import Any

from webwrench.theme import css_dict_to_string, get_theme_palette, theme_to_css

_ASSETS_DIR = os.path.join(os.path.dirname(__file__), "_assets")

# CDN URLs for opt-in CDN mode.
CDN_URLS: dict[str, str] = {
    "bitwrench": "https://cdn.jsdelivr.net/npm/bitwrench@latest/dist/bitwrench.umd.min.js",
    "quikdown": "https://cdn.jsdelivr.net/npm/quikdown@latest/dist/quikdown.umd.min.js",
    "chartjs": "https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js",
    "d3": "https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js",
    "leaflet": "https://cdn.jsdelivr.net/npm/leaflet@1.9/dist/leaflet.min.js",
    "threejs": "https://cdn.jsdelivr.net/npm/three@0.160/build/three.min.js",
    "html2canvas": "https://cdn.jsdelivr.net/npm/html2canvas@1.4/dist/html2canvas.min.js",
}


def _read_asset(filename: str) -> str:
    """Read a bundled asset file, returning empty string if not found."""
    path = os.path.join(_ASSETS_DIR, filename)
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return f"/* {filename} not found - placeholder */"


def _is_stub_asset(filename: str) -> bool:
    """Check if an asset file is a stub placeholder (< 1024 bytes)."""
    path = os.path.join(_ASSETS_DIR, filename)
    try:
        return os.path.getsize(path) < 1024
    except OSError:
        return True


def generate_shell_html(
    page: Any,
    client_id: str = "default",
    assets_mode: str = "local",
    title: str = "webwrench",
) -> str:
    """Generate the initial shell HTML page.

    Args:
        page: The Page object to render.
        client_id: Unique ID for this client/session.
        assets_mode: 'local' to inline JS, 'cdn' to use CDN URLs.
        title: HTML <title> content.

    Returns:
        Complete HTML string.
    """
    taco_list = page.to_taco_list()
    libs_used = page._libs_used

    # Build script tags
    scripts = _build_scripts(libs_used, assets_mode)
    # Build theme CSS
    theme_css = _build_theme_css(page)
    # Build custom CSS
    custom_css = _build_custom_css(page)

    # Initial TACO data for client bootstrap
    init_data = json.dumps(taco_list)

    # Theme palette for bw.loadStyles() (JS-based styling)
    palette = get_theme_palette(page) or {}
    palette_json = json.dumps(palette)

    override_css = _override_css()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{_base_css()}
{theme_css}
{custom_css}
</style>
</head>
<body>
<div id="ww-root"></div>
{scripts}
<script>
(function() {{
  var clientId = "{client_id}";
  var initData = {init_data};
  var palette = {palette_json};
  if (typeof wwBoot === 'function') {{
    wwBoot(clientId, initData, palette);
  }} else {{
    // Fallback: render TACO directly
    var root = document.getElementById('ww-root');
    if (typeof bw !== 'undefined' && bw.loadStyles) {{
      bw.loadStyles(palette);
    }}
    if (typeof bw !== 'undefined' && bw.createDOM) {{
      initData.forEach(function(taco) {{
        root.appendChild(bw.createDOM(taco));
      }});
    }} else {{
      // Minimal fallback: render as JSON
      root.innerHTML = '<pre>' + JSON.stringify(initData, null, 2) + '</pre>';
    }}
  }}
}})();
</script>
<style id="ww-overrides">
{override_css}
</style>
</body>
</html>"""


def generate_export_html(
    page: Any,
    title: str = "webwrench report",
    minify: bool = False,
) -> str:
    """Generate a self-contained static HTML file.

    All JS libraries used by the page are inlined.
    Charts remain interactive (tooltips, hover, legend toggling).
    No server connection needed.
    """
    taco_list = page.to_taco_list()
    libs_used = page._libs_used

    # Inline all needed JS
    inline_scripts = _build_inline_scripts(libs_used)
    theme_css = _build_theme_css(page)
    custom_css = _build_custom_css(page)

    init_data = json.dumps(taco_list)

    # Theme palette for bw.loadStyles()
    palette = get_theme_palette(page) or {}
    palette_json = json.dumps(palette)

    override_css = _override_css()
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{_base_css()}
{theme_css}
{custom_css}
</style>
</head>
<body>
<div id="ww-root"></div>
{inline_scripts}
<script>
(function() {{
  var initData = {init_data};
  var palette = {palette_json};
  var root = document.getElementById('ww-root');
  // Inject bitwrench structural CSS + themed styles
  if (typeof bw !== 'undefined' && bw.loadStyles) {{
    bw.loadStyles(palette);
  }}
  if (typeof bw !== 'undefined' && bw.createDOM) {{
    initData.forEach(function(taco) {{
      root.appendChild(bw.createDOM(taco));
    }});
  }} else {{
    // Fallback: render as static HTML from TACO
    initData.forEach(function(taco) {{
      root.appendChild(wwRenderStatic(taco));
    }});
  }}
  // Render markdown via quikdown
  if (typeof quikdown !== 'undefined') {{
    root.querySelectorAll('.ww-markdown[data-md]').forEach(function(el) {{
      el.innerHTML = quikdown(el.getAttribute('data-md'), {{inline_styles: true}});
    }});
  }}
  // Initialize charts
  document.querySelectorAll('[data-chart-config]').forEach(function(canvas) {{
    var config = JSON.parse(canvas.getAttribute('data-chart-config'));
    if (typeof Chart !== 'undefined') {{
      new Chart(canvas.getContext('2d'), config);
    }}
  }});
  // Initialize sortable/paginated tables via bw.makeTable()
  if (typeof bw !== 'undefined' && bw.makeTable) {{
    document.querySelectorAll('.ww-table[data-config]').forEach(function(container) {{
      try {{
        var config = JSON.parse(container.getAttribute('data-config'));
        if (!config.sortable && !config.searchable && !config.paginate) return;
        var data = config.rows.map(function(row) {{
          var obj = {{}};
          config.headers.forEach(function(h, i) {{ obj[h] = row[i]; }});
          return obj;
        }});
        var tc = {{ data: data, sortable: !!config.sortable, hover: true, striped: true }};
        if (config.paginate) tc.pageSize = config.paginate;
        var taco = bw.makeTable(tc);
        var newEl = bw.createDOM(taco);
        container.innerHTML = '';
        container.appendChild(newEl);
      }} catch (e) {{}}
    }});
  }}
}})();
function wwRenderStatic(taco) {{
  if (typeof taco === 'string') return document.createTextNode(taco);
  var el = document.createElement(taco.t || 'div');
  if (taco.a) Object.keys(taco.a).forEach(function(k) {{ el.setAttribute(k, taco.a[k]); }});
  if (taco.c) {{
    if (Array.isArray(taco.c)) taco.c.forEach(function(child) {{ el.appendChild(wwRenderStatic(child)); }});
    else if (typeof taco.c === 'object') el.appendChild(wwRenderStatic(taco.c));
    else el.textContent = String(taco.c);
  }}
  return el;
}}
</script>
<style id="ww-overrides">
{override_css}
</style>
</body>
</html>"""

    if minify:
        # Basic minification: collapse whitespace between tags
        import re
        html = re.sub(r">\s+<", "><", html)

    return html


def _build_scripts(libs_used: set[str], mode: str) -> str:
    """Build <script> tags for the shell page."""
    tags: list[str] = []
    if mode == "cdn":
        tags.append(f'<script src="{CDN_URLS["bitwrench"]}"></script>')
        tags.append(f'<script src="{CDN_URLS["quikdown"]}"></script>')
        for lib in sorted(libs_used):
            if lib in CDN_URLS and lib not in ("bitwrench", "quikdown"):
                tags.append(f'<script src="{CDN_URLS[lib]}"></script>')
        tags.append(f'<script src="/ww/lib/bwclient.js"></script>')
    else:
        tags.append(f'<script src="/ww/lib/bitwrench.min.js"></script>')
        tags.append(f'<script src="/ww/lib/quikdown.min.js"></script>')
        for lib in sorted(libs_used):
            filename = _lib_filename(lib)
            if filename:
                if _is_stub_asset(filename) and lib in CDN_URLS:
                    tags.append(f'<script src="{CDN_URLS[lib]}"></script>')
                else:
                    tags.append(f'<script src="/ww/lib/{filename}"></script>')
        tags.append(f'<script src="/ww/lib/bwclient.js"></script>')
    return "\n".join(tags)


def _build_inline_scripts(libs_used: set[str]) -> str:
    """Build inline <script> blocks for export (self-contained)."""
    parts: list[str] = []
    parts.append(f"<script>{_read_asset('bitwrench.min.js')}</script>")
    parts.append(f"<script>{_read_asset('quikdown.min.js')}</script>")
    for lib in sorted(libs_used):
        filename = _lib_filename(lib)
        if filename:
            if _is_stub_asset(filename) and lib in CDN_URLS:
                parts.append(f'<script src="{CDN_URLS[lib]}"></script>')
            else:
                parts.append(f"<script>{_read_asset(filename)}</script>")
    return "\n".join(parts)


def _lib_filename(lib: str) -> str | None:
    """Map a library name to its asset filename."""
    mapping: dict[str, str] = {
        "chartjs": "chart.min.js",
        "d3": "d3.min.js",
        "leaflet": "leaflet.min.js",
        "threejs": "three.min.js",
        "html2canvas": "html2canvas.min.js",
    }
    return mapping.get(lib)


def _build_theme_css(page: Any) -> str:
    """Build theme CSS from the page's theme settings."""
    palette = get_theme_palette(page)
    if palette:
        return theme_to_css(palette)
    return ""


def _build_custom_css(page: Any) -> str:
    """Build custom CSS from the page's css() calls."""
    if page._custom_css:
        return css_dict_to_string(page._custom_css)
    return ""


def _base_css() -> str:
    """Pre-JS fallback CSS.

    These styles render a usable page while bitwrench.js loads.
    bw.loadStyles() overwrites all .bw_* rules with themed versions.
    The ww-overrides <style> block (placed after scripts) provides the
    final visual polish that survives loadStyles.
    """
    return """
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; font-family: system-ui, -apple-system, BlinkMacSystemFont,
    'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6; color: #1e293b; background: #f8fafc;
    -webkit-font-smoothing: antialiased; }
#ww-root { max-width: 1100px; margin: 0 auto; padding: 2.5rem 2rem; }
h1, h2, h3, h4, h5, h6 { margin: 0.75em 0 0.35em; }
p { margin: 0.5em 0; }
hr { border: none; border-top: 1px solid #e2e8f0; margin: 1.5rem 0; }
.bw_btn { display: inline-block; padding: 0.5em 1.2em; border: none;
    border-radius: 6px; cursor: pointer; color: #fff; font-weight: 600;
    font-size: 0.9rem; background: #006666; margin: 0.25rem 0.3rem 0.25rem 0; }
.bw_card { border: 1px solid #e2e8f0; border-radius: 10px; margin: 0.75rem 0;
    background: #fff; }
.bw_card_header { padding: 0.8rem 1.25rem; font-weight: 600; font-size: 0.92rem;
    border-bottom: 1px solid #f1f5f9; }
.bw_card_body { padding: 1.25rem; }
.bw_form_group { margin: 0.75rem 0; }
.bw_form_label { display: block; font-weight: 600; font-size: 0.85rem;
    margin-bottom: 0.3rem; color: #475569; }
.bw_form_control { display: block; width: 100%; padding: 0.5rem 0.75rem;
    border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.92rem; }
.bw_range { width: 100%; }
.bw_table { width: 100%; border-collapse: collapse; }
.bw_table th, .bw_table td { padding: 0.5em 0.75em; text-align: left;
    border-bottom: 1px solid #e2e8f0; }
.bw_table th { font-weight: 600; }
.bw_nav { display: flex; gap: 0.25rem; padding: 0.35rem; }
.bw_nav_link { text-decoration: none; padding: 0.4rem 1rem; border-radius: 6px;
    font-weight: 500; color: #475569; }
"""


def _override_css() -> str:
    """Post-loadStyles CSS overrides.

    This block is placed AFTER bitwrench.js runs bw.loadStyles(), so it wins
    on cascade order.  Uses #ww-root for specificity where needed.
    Styles webwrench-specific .ww-* components that bitwrench doesn't know about.
    """
    return """
/* ── Layout root ── */
#ww-root { max-width: 1100px; margin: 0 auto; padding: 2.5rem 2rem; }

/* ── Typography polish ── */
#ww-root h1 { font-size: 2rem; font-weight: 800; letter-spacing: -0.02em;
    margin: 1.5rem 0 0.75rem; }
#ww-root h2 { font-size: 1.4rem; font-weight: 700; letter-spacing: -0.01em;
    margin: 2rem 0 0.6rem; padding-bottom: 0.3rem; }
#ww-root h3 { font-size: 1.15rem; font-weight: 600; margin: 1.2rem 0 0.4rem; }
#ww-root p { line-height: 1.7; }
#ww-root hr { margin: 1.5rem 0; }

/* ── Button spacing ── */
#ww-root .bw_btn { margin: 0.3rem 0.4rem 0.3rem 0; }

/* ── Card tuning ── */
#ww-root .bw_card { margin-bottom: 1.25rem; overflow: visible; }
#ww-root .bw_card_body > .bw_form_group:first-child { margin-top: 0.25rem; }
#ww-root .bw_card_body > .bw_form_group:last-child { margin-bottom: 0.25rem; }

/* ── ww-specific components ── */
.ww-chart { margin: 1rem 0; }
.ww-table { margin: 1rem 0; overflow-x: auto; }
.ww-textarea-field { resize: vertical; min-height: 2.5rem; }
.ww-columns { gap: 1.25rem; }

/* ── Slider value badge ── */
#ww-root .ww-slider-value { display: inline-block; min-width: 3em;
    text-align: center; font-weight: 700; font-variant-numeric: tabular-nums;
    font-size: 0.88rem; border-radius: 6px; padding: 0.15em 0.5em;
    margin-left: 0.5em; }

/* ── Metrics ── */
.ww-metric { text-align: center; padding: 1.25rem 1rem; }
.ww-metric-value { font-size: 2.5rem; font-weight: 800; line-height: 1.15;
    letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }
.ww-metric-label { font-size: 0.78rem; text-transform: uppercase;
    letter-spacing: 0.08em; font-weight: 600; opacity: 0.55;
    margin-bottom: 0.4rem; }
.ww-metric-delta { font-size: 0.88rem; font-weight: 700; margin-top: 0.35rem;
    display: inline-block; padding: 0.15em 0.6em; border-radius: 20px; }
.ww-metric-delta-positive { color: #16a34a; background: rgba(22,163,74,0.1); }
.ww-metric-delta-negative { color: #dc2626; background: rgba(220,38,38,0.1); }

/* ── Progress ── */
.ww-progress { border-radius: 10px; overflow: hidden; height: 0.7rem;
    margin: 0.75rem 0; }
.ww-progress-bar { height: 100%; border-radius: 10px;
    transition: width 0.5s cubic-bezier(.4,0,.2,1); }

/* ── Sidebar ── */
.ww-sidebar { width: 260px; padding: 1.5rem 1.25rem; flex-shrink: 0; }

/* ── Modal ── */
.ww-modal { position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%);
    background: #fff; border-radius: 16px; padding: 0;
    box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); z-index: 1001;
    min-width: 400px; max-width: 90vw; overflow: hidden; }
.ww-modal-header { padding: 0; }
.ww-modal-overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.5);
    z-index: 1000; backdrop-filter: blur(4px); }

/* ── Accordion ── */
.ww-accordion { margin: 0.6rem 0; border-radius: 10px; overflow: hidden; }
.ww-accordion-title { cursor: pointer; padding: 0.85rem 1.1rem; font-weight: 600;
    font-size: 0.92rem; transition: background 0.15s ease; list-style: none; }
.ww-accordion-title::-webkit-details-marker { display: none; }
.ww-accordion-title::before { content: '\\25B8'; display: inline-block;
    margin-right: 0.65rem; transition: transform 0.2s ease; font-size: 0.8em; }
details[open] > .ww-accordion-title::before { transform: rotate(90deg); }
details[open] > .ww-accordion-title { border-bottom: 1px solid #f1f5f9; }
.ww-accordion > :not(summary) { padding: 1rem 1.1rem; }

/* ── Nav ── */
.ww-nav { display: flex; gap: 0.3rem; padding: 0.35rem;
    border-bottom: none; margin: 1rem 0; }

/* ── Code / JSON ── */
.ww-json, .ww-code { border-radius: 10px; overflow-x: auto; line-height: 1.6;
    font-family: 'SF Mono', 'Fira Code', Menlo, Consolas, monospace;
    font-size: 0.85rem; }
.ww-json { padding: 1.1rem 1.25rem; }
.ww-code { padding: 1rem 1.25rem; margin: 0.75rem 0; }

/* ── Toast ── */
@keyframes ww-toast-in { from { transform: translateX(120%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; } }
@keyframes ww-toast-out { from { opacity: 1; } to { opacity: 0; } }
.ww-toast { position: fixed; top: 1.5rem; right: 1.5rem; padding: 0.85rem 1.5rem;
    border-radius: 10px; z-index: 9999; font-weight: 600; font-size: 0.9rem;
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    animation: ww-toast-in 0.35s cubic-bezier(.4,0,.2,1); color: #fff; }
.ww-toast-fading { animation: ww-toast-out 0.3s ease-in forwards; }
.ww-toast-success { background: #16a34a; }
.ww-toast-error, .ww-toast-danger { background: #dc2626; }
.ww-toast-warning { background: #ca8a04; }
.ww-toast-info { background: #0891b2; }

/* ── Markdown (rendered by quikdown with inline_styles) ── */
.ww-markdown { margin: 0.5rem 0; }
"""
