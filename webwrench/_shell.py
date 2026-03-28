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
  if (typeof wwBoot === 'function') {{
    wwBoot(clientId, initData);
  }} else {{
    // Fallback: render TACO directly
    var root = document.getElementById('ww-root');
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
  var root = document.getElementById('ww-root');
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
  // Initialize charts
  document.querySelectorAll('[data-chart-config]').forEach(function(canvas) {{
    var config = JSON.parse(canvas.getAttribute('data-chart-config'));
    if (typeof Chart !== 'undefined') {{
      new Chart(canvas.getContext('2d'), config);
    }}
  }});
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
        for lib in sorted(libs_used):
            if lib in CDN_URLS:
                tags.append(f'<script src="{CDN_URLS[lib]}"></script>')
        tags.append(f'<script src="/ww/lib/bwclient.js"></script>')
    else:
        tags.append(f'<script src="/ww/lib/bitwrench.min.js"></script>')
        for lib in sorted(libs_used):
            filename = _lib_filename(lib)
            if filename:
                tags.append(f'<script src="/ww/lib/{filename}"></script>')
        tags.append(f'<script src="/ww/lib/bwclient.js"></script>')
    return "\n".join(tags)


def _build_inline_scripts(libs_used: set[str]) -> str:
    """Build inline <script> blocks for export (self-contained)."""
    parts: list[str] = []
    parts.append(f"<script>{_read_asset('bitwrench.min.js')}</script>")
    for lib in sorted(libs_used):
        filename = _lib_filename(lib)
        if filename:
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
    """Minimal base CSS for webwrench layout."""
    return """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       line-height: 1.6; padding: 1rem; color: var(--bw-text, #333);
       background: var(--bw-background, #fff); }
#ww-root { max-width: 1200px; margin: 0 auto; }
h1, h2, h3, h4, h5, h6 { margin: 0.5em 0; }
p { margin: 0.5em 0; }
hr { margin: 1em 0; border: none; border-top: 1px solid var(--bw-border, #ddd); }
.ww-chart { margin: 1em 0; }
.ww-table { margin: 1em 0; overflow-x: auto; }
.bw_table { width: 100%; border-collapse: collapse; }
.bw_table th, .bw_table td { padding: 0.5em; text-align: left;
    border-bottom: 1px solid var(--bw-border, #ddd); }
.bw_table th { font-weight: 600; background: var(--bw-surface, #f5f5f5); }
.bw_btn { padding: 0.5em 1em; border: 1px solid var(--bw-border, #ddd);
    border-radius: 4px; cursor: pointer; background: var(--bw-primary, #3366cc);
    color: #fff; font-size: 1em; }
.bw_btn:hover { opacity: 0.9; }
.bw_card { padding: 1em; border: 1px solid var(--bw-border, #ddd);
    border-radius: 8px; margin: 0.5em 0; background: var(--bw-surface, #f5f5f5); }
.ww-label { display: block; font-weight: 500; margin-bottom: 0.25em; }
.ww-input-group, .ww-textarea-group, .ww-slider-group, .ww-select-group,
.ww-checkbox-group, .ww-radio-group, .ww-file-group, .ww-date-group,
.ww-color-group, .ww-number-group { margin: 0.5em 0; }
.ww-slider-input, .ww-select-field, .ww-input-field, .ww-textarea-field,
.ww-number-input, .ww-date-input { width: 100%; padding: 0.4em; }
.ww-columns { gap: 1rem; }
.ww-metric { text-align: center; }
.ww-metric-value { font-size: 2em; font-weight: 700; }
.ww-metric-label { font-size: 0.9em; opacity: 0.7; }
.ww-metric-delta { font-size: 0.85em; }
.ww-progress { background: var(--bw-surface, #eee); border-radius: 4px;
    overflow: hidden; height: 1.2em; margin: 0.5em 0; }
.ww-progress-bar { background: var(--bw-primary, #3366cc); height: 100%;
    transition: width 0.3s; }
.ww-sidebar { width: 260px; padding: 1em; border-right: 1px solid var(--bw-border, #ddd); }
.ww-modal { position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%);
    background: var(--bw-background, #fff); border-radius: 8px; padding: 1.5em;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2); z-index: 1000; }
.ww-accordion { margin: 0.5em 0; }
.ww-accordion-title { cursor: pointer; padding: 0.5em; font-weight: 500; }
.ww-nav { display: flex; gap: 1em; padding: 0.5em 0; }
.ww-nav-link { text-decoration: none; color: var(--bw-primary, #3366cc); }
.ww-json { background: var(--bw-surface, #f5f5f5); padding: 1em; border-radius: 4px;
    overflow-x: auto; font-size: 0.9em; }
"""
