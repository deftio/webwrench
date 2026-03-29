"""Tests targeting specific coverage gaps."""

import asyncio
import io
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from webwrench._context import Element, Page, WidgetHandle, get_default_page
from webwrench.layout import LayoutContainer
from webwrench.server import WebwrenchServer, _print_banner, _read_http_request, serve
from webwrench.state import SessionState


# ---- state.py lines 20, 37 ---- #


class TestSessionStatePrivateAttrs:
    def test_getattr_private_via_super(self):
        """Line 20: `return super().__getattribute__(name)` for _ names."""
        s = SessionState()
        # Accessing _data should go through super().__getattribute__
        assert isinstance(s._data, dict)

    def test_delattr_private(self):
        """Line 37: `super().__delattr__(name)` for _ names."""
        s = SessionState()
        # Add a private attribute then delete it
        s._temp = "test"
        assert s._temp == "test"
        del s._temp
        with pytest.raises(AttributeError):
            _ = s._temp


# ---- layout.py line 41 ---- #


class TestLayoutContainerWidgetCapture:
    def test_captures_widget_in_container(self):
        """Line 41: Widget is already registered on the page during context manager."""
        page = Page()
        container = LayoutContainer("div", page=page)
        page.add(container)
        with container:
            widget = WidgetHandle("button", element_id="btn-in-container", widget_type="button")
            page.add(widget)
        # The widget should be a child of the container
        assert any(
            getattr(el, "id", None) == "btn-in-container"
            for el in container.content
        )


# ---- server.py _handle_connection lines 79-82, 87-88 ---- #


class MockStreamReader:
    def __init__(self, data: bytes):
        self._data = data
        self._pos = 0

    async def readline(self):
        end = self._data.find(b"\n", self._pos)
        if end == -1:
            line = self._data[self._pos:]
            self._pos = len(self._data)
        else:
            line = self._data[self._pos: end + 1]
            self._pos = end + 1
        return line

    async def readexactly(self, n):
        chunk = self._data[self._pos: self._pos + n]
        self._pos += n
        if len(chunk) < n:
            raise asyncio.IncompleteReadError(chunk, n)
        return chunk


class MockStreamWriter:
    def __init__(self, raise_on_close=False):
        self.data = b""
        self.closed = False
        self._raise_on_close = raise_on_close

    def write(self, data):
        self.data += data

    async def drain(self):
        pass

    def close(self):
        self.closed = True
        if self._raise_on_close:
            raise ConnectionError("connection reset")

    async def wait_closed(self):
        if self._raise_on_close:
            raise ConnectionError("connection reset")


class TestHandleConnectionFullParsing:
    @pytest.mark.asyncio
    async def test_parses_and_routes_get(self):
        """Lines 79-80: Parsing request line and routing."""
        page = Page()
        page.add(Element("p", content="test", element_id="p1"))
        server = WebwrenchServer(page=page)
        data = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
        reader = MockStreamReader(data)
        writer = MockStreamWriter()
        await server._handle_connection(reader, writer)
        assert b"<!DOCTYPE html>" in writer.data

    @pytest.mark.asyncio
    async def test_connection_error_during_route(self):
        """Lines 81-82: ConnectionError caught during routing."""
        server = WebwrenchServer()

        # Craft a request that parses OK, but route() raises ConnectionError
        with patch.object(server, "_route", side_effect=ConnectionError("reset")):
            data = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
            reader = MockStreamReader(data)
            writer = MockStreamWriter()
            await server._handle_connection(reader, writer)
            # Should not raise, error is caught

    @pytest.mark.asyncio
    async def test_incomplete_read_error_during_handle(self):
        """Lines 81-82: IncompleteReadError caught."""
        server = WebwrenchServer()

        with patch.object(server, "_route", side_effect=asyncio.IncompleteReadError(b"", 100)):
            data = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
            reader = MockStreamReader(data)
            writer = MockStreamWriter()
            await server._handle_connection(reader, writer)
            # Should not raise

    @pytest.mark.asyncio
    async def test_close_error_in_finally(self):
        """Lines 87-88: ConnectionError during writer.close()."""
        page = Page()
        server = WebwrenchServer(page=page)
        data = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
        reader = MockStreamReader(data)
        writer = MockStreamWriter(raise_on_close=True)
        # Should not raise even though close() raises
        await server._handle_connection(reader, writer)


# ---- server.py SSE route match (lines 107-109) ---- #

class TestSSERouteMatch:
    @pytest.mark.asyncio
    async def test_route_sse_events(self):
        """Lines 107-109: Route GET /bw/events/:id to SSE handler."""
        page = Page()
        page.add(Element("p", content="hi", element_id="p1"))
        server = WebwrenchServer(page=page)
        server._running = True

        writer = MockStreamWriter()

        async def run_sse():
            await server._route("GET", "/bw/events/test-client", {}, b"", writer)

        task = asyncio.create_task(run_sse())
        await asyncio.sleep(0.05)

        # Should have sent SSE headers and initial data
        assert b"text/event-stream" in writer.data

        # Stop to end the loop
        server._running = False
        session = server.sessions.get("test-client")
        if session and session._async_queue:
            await session._async_queue.put({"type": "noop"})

        try:
            await asyncio.wait_for(task, timeout=2)
        except asyncio.TimeoutError:
            task.cancel()


# ---- server.py SSE keep-alive (lines 175-178) ---- #

class TestSSEKeepalive:
    @pytest.mark.asyncio
    async def test_keepalive_sent_on_timeout(self):
        """Lines 175-178: Keep-alive comment sent when queue times out."""
        from webwrench.options import options
        old_interval = options.keep_alive_interval
        options.keep_alive_interval = 0  # Instant timeout

        page = Page()
        server = WebwrenchServer(page=page)
        server._running = True

        writer = MockStreamWriter()

        async def run_sse():
            await server._serve_sse("ka-client", writer)

        task = asyncio.create_task(run_sse())
        # Wait enough for at least one timeout cycle
        await asyncio.sleep(0.1)

        server._running = False
        session = server.sessions.get("ka-client")
        if session and session._async_queue:
            await session._async_queue.put({"type": "noop"})

        try:
            await asyncio.wait_for(task, timeout=2)
        except asyncio.TimeoutError:
            task.cancel()

        options.keep_alive_interval = old_interval

        assert b": keepalive" in writer.data


# ---- server.py SSE BrokenPipeError (lines 179-180) ---- #

class TestSSEBrokenPipe:
    @pytest.mark.asyncio
    async def test_broken_pipe_during_sse(self):
        """Lines 179-180: BrokenPipeError during SSE is caught."""
        page = Page()
        server = WebwrenchServer(page=page)
        server._running = True

        class BreakingWriter:
            data = b""
            closed = False
            call_count = 0

            def write(self, d):
                self.call_count += 1
                if self.call_count > 3:
                    raise BrokenPipeError("broken pipe")
                self.data += d

            async def drain(self):
                if self.call_count > 3:
                    raise BrokenPipeError("broken pipe")

            def close(self):
                self.closed = True

            async def wait_closed(self):
                pass

        writer = BreakingWriter()
        # Should not raise - BrokenPipeError is caught
        await server._serve_sse("bp-client", writer)


# ---- server.py _read_http_request timeout (lines 248-249) ---- #

class TestReadHttpRequestTimeout:
    @pytest.mark.asyncio
    async def test_timeout_on_readline(self):
        """Lines 248-249: TimeoutError on initial readline."""
        class SlowReader:
            async def readline(self):
                await asyncio.sleep(100)  # Never returns in time

        with patch("webwrench.server.asyncio.wait_for", side_effect=asyncio.TimeoutError):
            reader = SlowReader()
            result = await _read_http_request(reader)
            assert result[0] is None


# ---- server.py _read_http_request body read error (lines 275-276) ---- #

class TestReadHttpRequestBodyError:
    @pytest.mark.asyncio
    async def test_bad_content_length(self):
        """Lines 275-276: ValueError on invalid Content-Length."""
        data = b"POST /x HTTP/1.1\r\nContent-Length: not-a-number\r\n\r\n"
        reader = MockStreamReader(data)
        _, headers, body = await _read_http_request(reader)
        assert body == b""

    @pytest.mark.asyncio
    async def test_incomplete_body(self):
        """IncompleteReadError when body is shorter than Content-Length."""
        data = b"POST /x HTTP/1.1\r\nContent-Length: 100\r\n\r\nshort"
        reader = MockStreamReader(data)
        _, headers, body = await _read_http_request(reader)
        assert body == b""  # falls through to empty on error


# ---- server.py serve() blocking function (lines 313-327) ---- #

class TestServeFunction:
    def test_serve_with_assets_kwarg(self):
        """Line 313-314: assets kwarg sets options."""
        from webwrench.options import options

        with patch("webwrench.server.asyncio.new_event_loop") as mock_loop_fn, \
             patch("webwrench.server.asyncio.set_event_loop"):
            mock_loop = MagicMock()
            mock_loop_fn.return_value = mock_loop
            mock_loop.run_until_complete = MagicMock()
            mock_loop.run_forever = MagicMock(side_effect=KeyboardInterrupt)
            mock_loop.close = MagicMock()

            serve(port=9999, assets="cdn")
            assert options.assets == "cdn"
            options.assets = "local"  # reset

    def test_serve_keyboard_interrupt(self):
        """Lines 316-327: Server starts, receives KeyboardInterrupt, stops."""
        with patch("webwrench.server.asyncio.new_event_loop") as mock_loop_fn, \
             patch("webwrench.server.asyncio.set_event_loop"):
            mock_loop = MagicMock()
            mock_loop_fn.return_value = mock_loop
            mock_loop.run_until_complete = MagicMock()
            mock_loop.run_forever = MagicMock(side_effect=KeyboardInterrupt)
            mock_loop.close = MagicMock()

            serve(port=9999)  # Should not raise
            assert mock_loop.run_forever.called
            assert mock_loop.close.called


# ---- server.py _print_banner (lines 332-333) ---- #

class TestPrintBanner:
    @pytest.mark.asyncio
    async def test_print_banner_default(self, capsys):
        """Lines 332-333: Banner prints correct host."""
        await _print_banner("0.0.0.0", 6502)
        captured = capsys.readouterr()
        assert "localhost:6502" in captured.out

    @pytest.mark.asyncio
    async def test_print_banner_custom_host(self, capsys):
        """Lines 332-333: Custom host in banner."""
        await _print_banner("192.168.1.1", 3000)
        captured = capsys.readouterr()
        assert "192.168.1.1:3000" in captured.out


# ---- app.py serve() method (lines 197-214) ---- #

class TestAppServe:
    def test_app_serve_with_root_page(self):
        """Lines 197-212: App.serve() with '/' page registered."""
        from webwrench.app import App

        app = App()

        @app.page("/")
        def home(ctx):
            ctx.title("Home")

        with patch("webwrench.server.serve") as mock_serve:
            app.serve(port=9999)
            assert mock_serve.called
            kwargs = mock_serve.call_args
            assert kwargs[1]["port"] == 9999

    def test_app_serve_without_root_page(self):
        """Lines 213-214: App.serve() without '/' falls through."""
        from webwrench.app import App

        app = App()

        @app.page("/about")
        def about(ctx):
            ctx.title("About")

        with patch("webwrench.server.serve") as mock_serve:
            app.serve(port=9999)
            assert mock_serve.called
