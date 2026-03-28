"""Theme management for webwrench.

All theming delegates to bitwrench's bw.loadStyles() and bw.toggleStyles().
webwrench does NOT have its own theme engine.
"""

from __future__ import annotations

from typing import Any

from webwrench._context import get_default_page
from webwrench.taco import make_call_msg


# Built-in bitwrench palette presets.
PRESETS: dict[str, dict[str, str]] = {
    "light": {
        "primary": "#3366cc",
        "secondary": "#666666",
        "background": "#ffffff",
        "surface": "#f5f5f5",
        "text": "#333333",
        "border": "#dddddd",
    },
    "dark": {
        "primary": "#66aaff",
        "secondary": "#aaaaaa",
        "background": "#1e1e1e",
        "surface": "#2d2d2d",
        "text": "#eeeeee",
        "border": "#444444",
    },
    "ocean": {
        "primary": "#006666",
        "secondary": "#336699",
        "background": "#f0f8ff",
        "surface": "#e0f0f8",
        "text": "#1a3344",
        "border": "#b0cce0",
    },
    "forest": {
        "primary": "#2d6a2e",
        "secondary": "#5a8a3c",
        "background": "#f5f9f5",
        "surface": "#e8f0e8",
        "text": "#1a331a",
        "border": "#a0c0a0",
    },
}


def resolve_theme(name_or_kwargs: str | None = None, **kwargs: str) -> dict[str, str]:
    """Resolve a theme name or keyword palette to a palette dict.

    Examples:
        resolve_theme('dark')                -> dark preset
        resolve_theme(primary='#006666')     -> custom palette merged onto light
        resolve_theme('ocean')               -> ocean preset
    """
    if isinstance(name_or_kwargs, str):
        if name_or_kwargs in PRESETS:
            palette = dict(PRESETS[name_or_kwargs])
            palette.update(kwargs)
            return palette
        raise ValueError(
            f"Unknown theme '{name_or_kwargs}'. "
            f"Available: {', '.join(sorted(PRESETS))}"
        )
    # Custom palette: start from light and override
    palette = dict(PRESETS["light"])
    palette.update(kwargs)
    return palette


def theme_to_css(palette: dict[str, str]) -> str:
    """Convert a palette dict to a CSS :root variable block."""
    lines = [":root {"]
    for key, value in sorted(palette.items()):
        lines.append(f"  --bw-{key}: {value};")
    lines.append("}")
    return "\n".join(lines)


def set_theme(
    page: Any | None = None,
    name: str | None = None,
    **kwargs: str,
) -> dict[str, str]:
    """Set the theme on a page.

    Returns the resolved palette dict.
    """
    if page is None:
        page = get_default_page()
    palette = resolve_theme(name, **kwargs)
    page._theme = palette
    return palette


def get_theme_palette(page: Any | None = None) -> dict[str, str] | None:
    """Return the current theme palette, or None if not set."""
    if page is None:
        page = get_default_page()
    theme = page._theme
    if isinstance(theme, dict):
        return theme
    return None


def make_load_styles_call(palette: dict[str, str]) -> dict[str, Any]:
    """Create a bwserve 'call' message that invokes bw.loadStyles."""
    return make_call_msg("loadStyles", [palette])


def make_toggle_styles_call() -> dict[str, Any]:
    """Create a bwserve 'call' message that invokes bw.toggleStyles."""
    return make_call_msg("toggleStyles")


def set_custom_css(css_dict: dict[str, Any], page: Any | None = None) -> None:
    """Store custom CSS rules on the page."""
    if page is None:
        page = get_default_page()
    if page._custom_css is None:
        page._custom_css = {}
    page._custom_css.update(css_dict)


def css_dict_to_string(css_dict: dict[str, Any]) -> str:
    """Convert a Python dict of CSS rules to a CSS string.

    Example:
        {'.my-card': {'border-radius': '12px'}}
        ->
        .my-card { border-radius: 12px; }
    """
    parts: list[str] = []
    for selector, props in css_dict.items():
        prop_strs = [f"  {k}: {v};" for k, v in props.items()]
        parts.append(f"{selector} {{\n" + "\n".join(prop_strs) + "\n}")
    return "\n".join(parts)
