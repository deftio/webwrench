"""Export functionality: static HTML export, screenshot, download, PDF.

ww.export() produces a self-contained HTML file.
ww.screenshot() and ww.download() generate bwserve protocol messages.
"""

from __future__ import annotations

from typing import Any

from webwrench._context import Page, get_active_session, get_default_page
from webwrench._shell import generate_export_html
from webwrench.taco import make_call_msg


def export(
    filename: str,
    page: Page | None = None,
    title: str = "webwrench report",
    minify: bool = False,
    include_3d: bool = True,
) -> str:
    """Export the current page as a self-contained HTML file.

    Args:
        filename: Output file path (e.g. 'report.html').
        page: Page to export (default: module-level default page).
        title: HTML <title> for the report.
        minify: Apply basic HTML minification.
        include_3d: Include three.js (set False to reduce file size).

    Returns:
        The HTML string that was written to the file.
    """
    p = page or get_default_page()

    if not include_3d:
        p._libs_used.discard("threejs")

    html = generate_export_html(p, title=title, minify=minify)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    return html


def export_string(
    page: Page | None = None,
    title: str = "webwrench report",
    minify: bool = False,
) -> str:
    """Generate export HTML as a string without writing to a file."""
    p = page or get_default_page()
    return generate_export_html(p, title=title, minify=minify)


def screenshot(
    filename: str = "screenshot.png",
    selector: str | None = None,
) -> dict[str, Any]:
    """Request a screenshot via html2canvas.

    Returns a bwserve call message. In a live app, this is sent via SSE.
    The client captures the screenshot and POSTs it back.
    """
    args: list[Any] = [filename]
    if selector:
        args.append(selector)
    return make_call_msg("wwScreenshot", args)


def download(
    filename: str,
    content: str | bytes | None = None,
    mime: str = "application/octet-stream",
) -> dict[str, Any]:
    """Trigger a file download in the user's browser.

    Returns a bwserve call message.
    """
    if content is None:
        # Download the file from the server's filesystem
        return make_call_msg("download", [filename, "", mime])
    if isinstance(content, bytes):
        import base64
        content_str = base64.b64encode(content).decode("ascii")
        return make_call_msg("download", [filename, content_str, mime])
    return make_call_msg("download", [filename, content, mime])


def export_pdf(filename: str = "report.pdf") -> dict[str, Any]:
    """Request a PDF export via the browser's print dialog.

    Returns a bwserve call message.
    """
    return make_call_msg("wwExportPDF", [filename])
