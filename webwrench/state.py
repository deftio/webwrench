"""Session state and shared state management."""

from __future__ import annotations

import asyncio
from typing import Any


class SessionState:
    """Per-session state container.

    Supports attribute-style access (not string-keyed dict).
    """

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            return super().__getattribute__(name)
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(f"State has no attribute '{name}'") from None

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            self._data[name] = value

    def __contains__(self, name: str) -> bool:
        return name in self._data

    def __delattr__(self, name: str) -> None:
        if name.startswith("_"):
            super().__delattr__(name)
        else:
            try:
                del self._data[name]
            except KeyError:
                raise AttributeError(f"State has no attribute '{name}'") from None


class SharedState:
    """State shared across pages within a session (app-level)."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)


class Session:
    """A connected client session.

    Each browser tab gets one Session. It holds per-session widget values,
    state, and the SSE message queue.
    """

    def __init__(self, client_id: str, page: Any = None) -> None:
        self.client_id = client_id
        self.page = page
        self.state = SessionState()
        self._widget_values: dict[str, Any] = {}
        self._message_queue: list[dict[str, Any]] = []
        self._async_queue: asyncio.Queue[dict[str, Any]] | None = None
        self._computed: dict[str, Any] = {}

    def get_widget_value(self, widget_id: str, default: Any = None) -> Any:
        return self._widget_values.get(widget_id, default)

    def set_widget_value(self, widget_id: str, value: Any) -> None:
        self._widget_values[widget_id] = value

    def send_message(self, message: dict[str, Any]) -> None:
        """Queue a message to be sent via SSE."""
        self._message_queue.append(message)
        if self._async_queue is not None:
            self._async_queue.put_nowait(message)

    def send_patch(self, element_id: str, content: Any) -> None:
        """Send a patch message for an element."""
        self.send_message(
            {"type": "patch", "target": element_id, "content": content}
        )

    def drain_messages(self) -> list[dict[str, Any]]:
        """Return and clear all pending messages."""
        messages = list(self._message_queue)
        self._message_queue.clear()
        return messages

    def compute(self, key: str, func: Any) -> Any:
        """Compute and cache a value."""
        if key not in self._computed:
            self._computed[key] = func()
        return self._computed[key]

    def recompute(self, key: str, func: Any) -> Any:
        """Invalidate cache and recompute."""
        self._computed[key] = func()
        return self._computed[key]

    def init_async_queue(self) -> asyncio.Queue[dict[str, Any]]:
        """Initialize async queue for SSE streaming."""
        self._async_queue = asyncio.Queue()
        return self._async_queue


class SessionManager:
    """Manages active sessions."""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create(self, client_id: str, page: Any = None) -> Session:
        """Create a new session."""
        session = Session(client_id, page)
        self._sessions[client_id] = session
        return session

    def get(self, client_id: str) -> Session | None:
        """Get a session by client ID."""
        return self._sessions.get(client_id)

    def remove(self, client_id: str) -> None:
        """Remove a session (cleanup on disconnect)."""
        self._sessions.pop(client_id, None)

    @property
    def active_count(self) -> int:
        return len(self._sessions)

    def clear(self) -> None:
        """Remove all sessions."""
        self._sessions.clear()
