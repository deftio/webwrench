"""Async HTTP server for webwrench live apps.

Provides:
  - GET /           -> Shell HTML page
  - GET /bw/events/:id -> SSE stream
  - POST /bw/return/action/:id -> Widget callbacks
  - GET /ww/lib/:filename -> Bundled JS assets
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import uuid
from typing import Any

from webwrench._context import (
    Page,
    get_default_page,
    restore_active_session,
    set_active_session,
)
from webwrench._shell import generate_shell_html
from webwrench.options import options
from webwrench.state import Session, SessionManager

_ASSETS_DIR = os.path.join(os.path.dirname(__file__), "_assets")

# MIME types for served assets.
_MIME_TYPES: dict[str, str] = {
    ".js": "application/javascript",
    ".css": "text/css",
    ".html": "text/html",
    ".json": "application/json",
    ".png": "image/png",
    ".svg": "image/svg+xml",
}


class WebwrenchServer:
    """Asyncio-based HTTP server implementing the bwserve protocol."""

    def __init__(self, page: Page | None = None, host: str = "0.0.0.0", port: int = 6502, app: Any = None) -> None:
        self.page = page or get_default_page()
        self.host = host
        self.port = port
        self.app = app
        self.sessions = SessionManager()
        self._server: asyncio.Server | None = None
        self._running = False

    async def start(self) -> None:
        """Start the HTTP server."""
        self._server = await asyncio.start_server(
            self._handle_connection, self.host, self.port
        )
        self._running = True

    async def stop(self) -> None:
        """Stop the HTTP server."""
        self._running = False
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
        self.sessions.clear()

    async def _handle_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """Handle a single TCP connection."""
        try:
            request_line, headers, body = await _read_http_request(reader)
            if request_line is None:
                writer.close()
                return

            method, path, _ = request_line.split(" ", 2)
            await self._route(method, path, headers, body, writer)
        except (ConnectionError, asyncio.IncompleteReadError):
            pass
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except (ConnectionError, BrokenPipeError):
                pass

    async def _route(
        self,
        method: str,
        path: str,
        headers: dict[str, str],
        body: bytes,
        writer: asyncio.StreamWriter,
    ) -> None:
        """Route a request to the appropriate handler."""
        # GET / -> shell HTML (or app page if app is set)
        if method == "GET" and path == "/":
            if self.app is not None and "/" in self.app.registered_paths:
                await self._serve_app_page("/", writer)
            else:
                await self._serve_shell(writer)
            return

        # GET /favicon.ico -> 204 (suppress browser 404 noise)
        if method == "GET" and path == "/favicon.ico":
            await _send_response(writer, 204, "image/x-icon", b"")
            return

        # GET /bw/events/:id -> SSE stream
        sse_match = re.match(r"^/bw/events/(.+)$", path)
        if method == "GET" and sse_match:
            client_id = sse_match.group(1)
            await self._serve_sse(client_id, writer)
            return

        # POST /bw/return/action/:id -> widget callback
        action_match = re.match(r"^/bw/return/action/(.+)$", path)
        if method == "POST" and action_match:
            client_id = action_match.group(1)
            await self._handle_action(client_id, body, writer)
            return

        # GET /ww/lib/:filename -> serve JS asset
        lib_match = re.match(r"^/ww/lib/(.+)$", path)
        if method == "GET" and lib_match:
            filename = lib_match.group(1)
            await self._serve_asset(filename, writer)
            return

        # App page routing
        if method == "GET" and self.app is not None and path in self.app.registered_paths:
            await self._serve_app_page(path, writer)
            return

        # 404
        await _send_response(writer, 404, "text/plain", b"Not Found")

    async def _serve_shell(self, writer: asyncio.StreamWriter) -> None:
        """Serve the initial shell HTML page."""
        client_id = str(uuid.uuid4())
        # Create session eagerly so POST actions don't 404 before SSE connects
        self.sessions.create(client_id, self.page)
        html = generate_shell_html(
            self.page,
            client_id=client_id,
            assets_mode=options.assets,
        )
        await _send_response(writer, 200, "text/html", html.encode("utf-8"))

    async def _serve_app_page(self, path: str, writer: asyncio.StreamWriter) -> None:
        """Serve an app page by path."""
        client_id = str(uuid.uuid4())
        session = self.sessions.create(client_id, None)
        page = self.app.build_page(path, session)
        session.page = page
        html = generate_shell_html(page, client_id=client_id, assets_mode=options.assets)
        await _send_response(writer, 200, "text/html", html.encode("utf-8"))

    async def _serve_sse(
        self, client_id: str, writer: asyncio.StreamWriter
    ) -> None:
        """Open an SSE stream for a client."""
        session = self.sessions.get(client_id)
        if session is None:
            # Fallback: create if shell didn't (e.g. direct SSE reconnect)
            session = self.sessions.create(client_id, self.page)
        queue = session.init_async_queue()

        # Send SSE headers
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/event-stream\r\n"
            "Cache-Control: no-cache\r\n"
            "Connection: keep-alive\r\n"
            "Access-Control-Allow-Origin: *\r\n"
            "\r\n"
        )
        writer.write(response.encode())
        await writer.drain()

        # Send initial render
        page = session.page or self.page
        taco_list = page.to_taco_list()
        for taco in taco_list:
            msg = {"type": "replace", "target": "ww-root", "node": taco}
            event_data = f"data: {json.dumps(msg)}\n\n"
            writer.write(event_data.encode())
        await writer.drain()

        # Stream loop
        try:
            while self._running:
                try:
                    msg = await asyncio.wait_for(
                        queue.get(), timeout=options.keep_alive_interval
                    )
                    event_data = f"data: {json.dumps(msg)}\n\n"
                    writer.write(event_data.encode())
                    await writer.drain()
                except asyncio.TimeoutError:
                    # Send keep-alive comment
                    writer.write(b": keepalive\n\n")
                    await writer.drain()
        except (ConnectionError, BrokenPipeError):
            pass
        finally:
            self.sessions.remove(client_id)

    async def _handle_action(
        self, client_id: str, body: bytes, writer: asyncio.StreamWriter
    ) -> None:
        """Handle a widget action POST."""
        session = self.sessions.get(client_id)
        if session is None:
            # Auto-create if session was lost (e.g. SSE reconnect race)
            session = self.sessions.create(client_id, self.page)

        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            await _send_response(writer, 400, "text/plain", b"Invalid JSON")
            return

        widget_id = payload.get("widget_id", "")
        action = payload.get("action", "click")
        value = payload.get("value")

        page = session.page or self.page
        widget = page.get_widget(widget_id)
        if widget is None:
            await _send_response(writer, 200, "application/json", b'{"ok":false}')
            return

        # Set session context for the callback
        token = set_active_session(session)
        try:
            if action == "change" and value is not None:
                session.set_widget_value(widget_id, value)
                widget._fire_change(value)
            elif action == "click":
                widget._fire_click()
        finally:
            restore_active_session(token)

        await _send_response(writer, 200, "application/json", b'{"ok":true}')

    async def _serve_asset(
        self, filename: str, writer: asyncio.StreamWriter
    ) -> None:
        """Serve a bundled JS/CSS asset file."""
        # Sanitize filename to prevent path traversal
        safe_name = os.path.basename(filename)
        path = os.path.join(_ASSETS_DIR, safe_name)
        if not os.path.isfile(path):
            await _send_response(writer, 404, "text/plain", b"Asset not found")
            return

        ext = os.path.splitext(safe_name)[1]
        mime = _MIME_TYPES.get(ext, "application/octet-stream")
        with open(path, "rb") as f:
            data = f.read()
        await _send_response(writer, 200, mime, data)


async def _read_http_request(
    reader: asyncio.StreamReader,
) -> tuple[str | None, dict[str, str], bytes]:
    """Parse an HTTP request from a stream.

    Returns (request_line, headers_dict, body).
    """
    try:
        request_line_bytes = await asyncio.wait_for(reader.readline(), timeout=30)
    except (asyncio.TimeoutError, ConnectionError):
        return None, {}, b""

    if not request_line_bytes:
        return None, {}, b""

    request_line = request_line_bytes.decode("utf-8", errors="replace").strip()
    if not request_line:
        return None, {}, b""

    headers: dict[str, str] = {}
    while True:
        line = await reader.readline()
        line_str = line.decode("utf-8", errors="replace").strip()
        if not line_str:
            break
        if ":" in line_str:
            key, val = line_str.split(":", 1)
            headers[key.strip().lower()] = val.strip()

    # Read body if Content-Length present
    body = b""
    content_length = headers.get("content-length")
    if content_length:
        try:
            length = int(content_length)
            body = await asyncio.wait_for(reader.readexactly(length), timeout=30)
        except (asyncio.TimeoutError, asyncio.IncompleteReadError, ValueError):
            pass

    return request_line, headers, body


async def _send_response(
    writer: asyncio.StreamWriter,
    status: int,
    content_type: str,
    body: bytes,
) -> None:
    """Send an HTTP response."""
    status_text = {200: "OK", 204: "No Content", 400: "Bad Request", 404: "Not Found"}.get(
        status, "Unknown"
    )
    header = (
        f"HTTP/1.1 {status} {status_text}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Access-Control-Allow-Origin: *\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )
    writer.write(header.encode() + body)
    await writer.drain()


def serve(
    page: Page | None = None,
    host: str = "0.0.0.0",
    port: int = 6502,
    **kwargs: Any,
) -> None:
    """Start a webwrench server (blocking).

    This is the main entry point for live apps.
    """
    app = kwargs.pop("app", None)
    if "assets" in kwargs:
        options.assets = kwargs.pop("assets")

    server = WebwrenchServer(page=page, host=host, port=port, app=app)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(server.start())
        loop.run_until_complete(_print_banner(host, port))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(server.stop())
        loop.close()


async def _print_banner(host: str, port: int) -> None:
    """Print the server startup banner."""
    display_host = "localhost" if host == "0.0.0.0" else host
    print(f"\n  webwrench running at http://{display_host}:{port}\n")
