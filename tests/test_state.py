"""Tests for webwrench.state -- SessionState, SharedState, Session, SessionManager."""

import asyncio

import pytest

from webwrench.state import Session, SessionManager, SessionState, SharedState


class TestSessionState:
    def test_set_and_get(self):
        s = SessionState()
        s.counter = 0
        assert s.counter == 0

    def test_attribute_error(self):
        s = SessionState()
        with pytest.raises(AttributeError, match="no attribute 'missing'"):
            _ = s.missing

    def test_contains(self):
        s = SessionState()
        assert "x" not in s
        s.x = 1
        assert "x" in s

    def test_delattr(self):
        s = SessionState()
        s.foo = 42
        del s.foo
        assert "foo" not in s

    def test_delattr_missing(self):
        s = SessionState()
        with pytest.raises(AttributeError, match="no attribute 'nope'"):
            del s.nope

    def test_private_attrs_bypass_data(self):
        s = SessionState()
        # _data is stored normally via super().__setattr__
        assert isinstance(s._data, dict)


class TestSharedState:
    def test_set_and_get(self):
        s = SharedState()
        s["user"] = "alice"
        assert s["user"] == "alice"

    def test_contains(self):
        s = SharedState()
        assert "key" not in s
        s["key"] = 1
        assert "key" in s

    def test_delitem(self):
        s = SharedState()
        s["x"] = 10
        del s["x"]
        assert "x" not in s

    def test_delitem_missing(self):
        s = SharedState()
        with pytest.raises(KeyError):
            del s["missing"]

    def test_get_default(self):
        s = SharedState()
        assert s.get("missing") is None
        assert s.get("missing", 42) == 42

    def test_get_existing(self):
        s = SharedState()
        s["key"] = "val"
        assert s.get("key") == "val"


class TestSession:
    def test_init(self):
        s = Session("client1")
        assert s.client_id == "client1"
        assert s.page is None

    def test_widget_values(self):
        s = Session("c1")
        assert s.get_widget_value("w1") is None
        assert s.get_widget_value("w1", 42) == 42
        s.set_widget_value("w1", 100)
        assert s.get_widget_value("w1") == 100

    def test_send_message(self):
        s = Session("c1")
        s.send_message({"type": "patch", "target": "x"})
        assert len(s._message_queue) == 1

    def test_send_patch(self):
        s = Session("c1")
        s.send_patch("el1", "new content")
        msgs = s.drain_messages()
        assert len(msgs) == 1
        assert msgs[0]["type"] == "patch"
        assert msgs[0]["target"] == "el1"
        assert msgs[0]["content"] == "new content"

    def test_drain_messages_clears(self):
        s = Session("c1")
        s.send_message({"type": "test"})
        msgs = s.drain_messages()
        assert len(msgs) == 1
        assert s.drain_messages() == []

    def test_compute_caches(self):
        s = Session("c1")
        call_count = 0

        def expensive():
            nonlocal call_count
            call_count += 1
            return 42

        assert s.compute("key", expensive) == 42
        assert s.compute("key", expensive) == 42
        assert call_count == 1

    def test_recompute_invalidates(self):
        s = Session("c1")
        counter = [0]

        def compute():
            counter[0] += 1
            return counter[0]

        assert s.compute("k", compute) == 1
        assert s.recompute("k", compute) == 2
        assert s.compute("k", compute) == 2  # cached at 2 now

    def test_init_async_queue(self):
        s = Session("c1")
        q = s.init_async_queue()
        assert isinstance(q, asyncio.Queue)
        assert s._async_queue is q

    def test_send_message_to_async_queue(self):
        s = Session("c1")
        s.init_async_queue()
        s.send_message({"type": "test"})
        assert s._async_queue.qsize() == 1

    def test_state_is_session_state(self):
        s = Session("c1")
        s.state.x = 10
        assert s.state.x == 10


class TestSessionManager:
    def test_create_and_get(self):
        mgr = SessionManager()
        s = mgr.create("c1")
        assert mgr.get("c1") is s

    def test_get_missing(self):
        mgr = SessionManager()
        assert mgr.get("nope") is None

    def test_remove(self):
        mgr = SessionManager()
        mgr.create("c1")
        mgr.remove("c1")
        assert mgr.get("c1") is None

    def test_remove_missing_no_error(self):
        mgr = SessionManager()
        mgr.remove("nonexistent")  # Should not raise

    def test_active_count(self):
        mgr = SessionManager()
        assert mgr.active_count == 0
        mgr.create("a")
        mgr.create("b")
        assert mgr.active_count == 2

    def test_clear(self):
        mgr = SessionManager()
        mgr.create("a")
        mgr.create("b")
        mgr.clear()
        assert mgr.active_count == 0
