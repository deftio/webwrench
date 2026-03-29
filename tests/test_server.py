"""Tests for webwrench.server -- async HTTP server."""

import asyncio
import json

import pytest

from webwrench._context import Element, Page, WidgetHandle, get_default_page
from webwrench.options import options
from webwrench.server import (
    WebwrenchServer,
    _MIME_TYPES,
    _read_http_request,
    _send_response,
)


class MockStreamReader:
    """Mock asyncio.StreamReader for testing."""

    def __init__(self, data: bytes):
        self._data = data
        self._pos = 0

    async def readline(self):
        end = self._data.find(b"\n", self._pos)
        if end == -1:
            line = self._data[self._pos:]
            self._pos = len(self._data)
        else:
            line = self._data[self._pos : end + 1]
            self._pos = end + 1
        return line

    async def readexactly(self, n):
        chunk = self._data[self._pos : self._pos + n]
        self._pos += n
        if len(chunk) < n:
            raise asyncio.IncompleteReadError(chunk, n)
        return chunk


class MockStreamWriter:
    """Mock asyncio.StreamWriter for testing."""

    def __init__(self):
        self.data = b""
        self.closed = False

    def write(self, data):
        self.data += data

    async def drain(self):
        pass

    def close(self):
        self.closed = True

    async def wait_closed(self):
        pass


class TestReadHttpRequest:
    @pytest.mark.asyncio
    async def test_get_request(self):
        data = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
        reader = MockStreamReader(data)
        request_line, headers, body = await _read_http_request(reader)
        assert request_line == "GET / HTTP/1.1"
        assert headers["host"] == "localhost"
        assert body == b""

    @pytest.mark.asyncio
    async def test_post_with_body(self):
        body_content = b'{"key":"value"}'
        data = (
            b"POST /action HTTP/1.1\r\n"
            b"Content-Length: " + str(len(body_content)).encode() + b"\r\n"
            b"\r\n" + body_content
        )
        reader = MockStreamReader(data)
        request_line, headers, body = await _read_http_request(reader)
        assert request_line == "POST /action HTTP/1.1"
        assert body == body_content

    @pytest.mark.asyncio
    async def test_empty_request(self):
        reader = MockStreamReader(b"")
        request_line, headers, body = await _read_http_request(reader)
        assert request_line is None

    @pytest.mark.asyncio
    async def test_blank_line_request(self):
        reader = MockStreamReader(b"\r\n")
        request_line, headers, body = await _read_http_request(reader)
        assert request_line is None


class TestSendResponse:
    @pytest.mark.asyncio
    async def test_200(self):
        writer = MockStreamWriter()
        await _send_response(writer, 200, "text/plain", b"OK")
        assert b"HTTP/1.1 200 OK" in writer.data
        assert b"Content-Type: text/plain" in writer.data
        assert b"OK" in writer.data

    @pytest.mark.asyncio
    async def test_404(self):
        writer = MockStreamWriter()
        await _send_response(writer, 404, "text/plain", b"Not Found")
        assert b"404 Not Found" in writer.data

    @pytest.mark.asyncio
    async def test_400(self):
        writer = MockStreamWriter()
        await _send_response(writer, 400, "text/plain", b"Bad")
        assert b"400 Bad Request" in writer.data

    @pytest.mark.asyncio
    async def test_unknown_status(self):
        writer = MockStreamWriter()
        await _send_response(writer, 500, "text/plain", b"Error")
        assert b"500 Unknown" in writer.data


class TestWebwrenchServer:
    @pytest.mark.asyncio
    async def test_serve_shell(self):
        page = Page()
        page.add(Element("h1", content="Test", element_id="h1"))
        server = WebwrenchServer(page=page)
        writer = MockStreamWriter()
        await server._serve_shell(writer)
        assert b"<!DOCTYPE html>" in writer.data
        assert b"Test" in writer.data

    @pytest.mark.asyncio
    async def test_serve_asset_existing(self):
        server = WebwrenchServer()
        writer = MockStreamWriter()
        await server._serve_asset("bitwrench.min.js", writer)
        assert b"200 OK" in writer.data
        assert b"application/javascript" in writer.data

    @pytest.mark.asyncio
    async def test_serve_asset_missing(self):
        server = WebwrenchServer()
        writer = MockStreamWriter()
        await server._serve_asset("nonexistent.js", writer)
        assert b"404" in writer.data

    @pytest.mark.asyncio
    async def test_serve_asset_path_traversal(self):
        server = WebwrenchServer()
        writer = MockStreamWriter()
        await server._serve_asset("../../etc/passwd", writer)
        assert b"404" in writer.data

    @pytest.mark.asyncio
    async def test_handle_action_auto_creates_session(self):
        """Missing session is auto-created; request continues to widget lookup."""
        server = WebwrenchServer()
        writer = MockStreamWriter()
        await server._handle_action("nonexistent", b'{}', writer)
        # Session was auto-created (widget_id="" not found -> 200 ok:false)
        assert b'{"ok":false}' in writer.data
        assert server.sessions.get("nonexistent") is not None

    @pytest.mark.asyncio
    async def test_handle_action_invalid_json(self):
        server = WebwrenchServer()
        server.sessions.create("c1")
        writer = MockStreamWriter()
        await server._handle_action("c1", b"not json!", writer)
        assert b"400" in writer.data

    @pytest.mark.asyncio
    async def test_handle_action_missing_widget(self):
        page = Page()
        server = WebwrenchServer(page=page)
        server.sessions.create("c1", page)
        writer = MockStreamWriter()
        body = json.dumps({"widget_id": "no-such-widget", "action": "click"}).encode()
        await server._handle_action("c1", body, writer)
        assert b'{"ok":false}' in writer.data

    @pytest.mark.asyncio
    async def test_handle_action_click(self):
        page = Page()
        clicked = []
        widget = WidgetHandle("button", element_id="btn1", widget_type="button")
        widget.on_click(lambda: clicked.append(True))
        page.add(widget)

        server = WebwrenchServer(page=page)
        server.sessions.create("c1", page)
        writer = MockStreamWriter()
        body = json.dumps({"widget_id": "btn1", "action": "click"}).encode()
        await server._handle_action("c1", body, writer)
        assert b"200" in writer.data
        assert clicked == [True]

    @pytest.mark.asyncio
    async def test_handle_action_change(self):
        page = Page()
        changes = []
        widget = WidgetHandle("div", element_id="s1", widget_type="slider")
        widget.on_change(lambda v: changes.append(v))
        page.add(widget)

        server = WebwrenchServer(page=page)
        session = server.sessions.create("c1", page)
        writer = MockStreamWriter()
        body = json.dumps({"widget_id": "s1", "action": "change", "value": 42}).encode()
        await server._handle_action("c1", body, writer)
        assert b"200" in writer.data
        assert changes == [42]
        assert session.get_widget_value("s1") == 42

    @pytest.mark.asyncio
    async def test_handle_action_empty_body(self):
        page = Page()
        server = WebwrenchServer(page=page)
        server.sessions.create("c1", page)
        writer = MockStreamWriter()
        await server._handle_action("c1", b"", writer)
        # Empty body = empty payload, widget_id will be "", so widget not found
        assert b'{"ok":false}' in writer.data

    @pytest.mark.asyncio
    async def test_route_get_root(self):
        page = Page()
        page.add(Element("p", content="hi", element_id="p1"))
        server = WebwrenchServer(page=page)
        writer = MockStreamWriter()
        await server._route("GET", "/", {}, b"", writer)
        assert b"<!DOCTYPE html>" in writer.data

    @pytest.mark.asyncio
    async def test_route_get_asset(self):
        server = WebwrenchServer()
        writer = MockStreamWriter()
        await server._route("GET", "/ww/lib/bwclient.js", {}, b"", writer)
        assert b"200 OK" in writer.data

    @pytest.mark.asyncio
    async def test_route_post_action(self):
        page = Page()
        widget = WidgetHandle("button", element_id="b1", widget_type="button")
        page.add(widget)
        server = WebwrenchServer(page=page)
        server.sessions.create("c1", page)
        writer = MockStreamWriter()
        body = json.dumps({"widget_id": "b1", "action": "click"}).encode()
        await server._route("POST", "/bw/return/action/c1", {}, body, writer)
        assert b"200" in writer.data

    @pytest.mark.asyncio
    async def test_route_favicon(self):
        server = WebwrenchServer()
        writer = MockStreamWriter()
        await server._route("GET", "/favicon.ico", {}, b"", writer)
        assert b"204 No Content" in writer.data

    @pytest.mark.asyncio
    async def test_route_404(self):
        server = WebwrenchServer()
        writer = MockStreamWriter()
        await server._route("GET", "/unknown", {}, b"", writer)
        assert b"404" in writer.data

    @pytest.mark.asyncio
    async def test_start_and_stop(self):
        server = WebwrenchServer(port=0)  # Port 0 = OS assigns random port
        await server.start()
        assert server._running is True
        await server.stop()
        assert server._running is False

    @pytest.mark.asyncio
    async def test_sse_stream(self):
        """Test the SSE stream sends initial render and handles disconnect."""
        page = Page()
        page.add(Element("p", content="sse-test", element_id="p1"))
        server = WebwrenchServer(page=page)
        server._running = True

        writer = MockStreamWriter()

        # Start SSE in a task, then cancel after a moment
        async def run_sse():
            await server._serve_sse("sse-client", writer)

        task = asyncio.create_task(run_sse())
        await asyncio.sleep(0.05)

        # Verify SSE headers were sent
        assert b"text/event-stream" in writer.data
        assert b"data:" in writer.data  # Initial render sent

        # Stop server to end the loop
        server._running = False
        # Send a message to unblock the queue.get()
        session = server.sessions.get("sse-client")
        if session and session._async_queue:
            await session._async_queue.put({"type": "patch", "target": "p1", "content": "updated"})

        try:
            await asyncio.wait_for(task, timeout=2)
        except asyncio.TimeoutError:
            task.cancel()


class TestMultiPageRouting:
    @pytest.mark.asyncio
    async def test_app_page_routing(self):
        """App with two pages serves correct HTML for each path."""
        from webwrench.app import App

        app = App()

        @app.page("/")
        def home(ctx):
            ctx.title("Home Page")

        @app.page("/about")
        def about(ctx):
            ctx.title("About Page")

        server = WebwrenchServer(app=app)
        # Request /
        writer = MockStreamWriter()
        await server._route("GET", "/", {}, b"", writer)
        assert b"<!DOCTYPE html>" in writer.data
        assert b"Home Page" in writer.data

        # Request /about
        writer2 = MockStreamWriter()
        await server._route("GET", "/about", {}, b"", writer2)
        assert b"<!DOCTYPE html>" in writer2.data
        assert b"About Page" in writer2.data

    @pytest.mark.asyncio
    async def test_app_page_unknown_path_404(self):
        """Unregistered paths still 404."""
        from webwrench.app import App

        app = App()

        @app.page("/")
        def home(ctx):
            ctx.title("Home")

        server = WebwrenchServer(app=app)
        writer = MockStreamWriter()
        await server._route("GET", "/nonexistent", {}, b"", writer)
        assert b"404" in writer.data

    @pytest.mark.asyncio
    async def test_session_page_widget_lookup(self):
        """_handle_action uses session.page for widget lookup."""
        from webwrench.app import App

        app = App()

        clicked = []

        @app.page("/")
        def home(ctx):
            btn = ctx.button("Click Me")
            btn.on_click(lambda: clicked.append(True))

        server = WebwrenchServer(app=app)
        # Build the page as the server would
        from webwrench.state import Session
        session = server.sessions.create("c1", None)
        page = app.build_page("/", session)
        session.page = page

        # Find the button widget id
        widget_id = list(page._widgets.keys())[0]

        writer = MockStreamWriter()
        body = json.dumps({"widget_id": widget_id, "action": "click"}).encode()
        await server._handle_action("c1", body, writer)
        assert b'{"ok":true}' in writer.data
        assert clicked == [True]

    @pytest.mark.asyncio
    async def test_sse_uses_session_page(self):
        """SSE initial render uses session.page when set."""
        page1 = Page()
        page1.add(Element("p", content="session-page", element_id="sp1"))

        server = WebwrenchServer()
        server._running = True
        session = server.sessions.create("sse-sp", None)
        session.page = page1

        writer = MockStreamWriter()

        async def run_sse():
            await server._serve_sse("sse-sp", writer)

        task = asyncio.create_task(run_sse())
        await asyncio.sleep(0.05)

        assert b"session-page" in writer.data

        server._running = False
        if session._async_queue:
            await session._async_queue.put({"type": "noop"})
        try:
            await asyncio.wait_for(task, timeout=2)
        except asyncio.TimeoutError:
            task.cancel()


class TestHandleConnection:
    @pytest.mark.asyncio
    async def test_handles_empty_connection(self):
        server = WebwrenchServer()
        reader = MockStreamReader(b"")
        writer = MockStreamWriter()
        await server._handle_connection(reader, writer)
        assert writer.closed


class TestMimeTypes:
    def test_js(self):
        assert _MIME_TYPES[".js"] == "application/javascript"

    def test_css(self):
        assert _MIME_TYPES[".css"] == "text/css"

    def test_html(self):
        assert _MIME_TYPES[".html"] == "text/html"
