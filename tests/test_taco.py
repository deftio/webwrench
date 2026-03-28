"""Tests for webwrench.taco -- TACO builders and bwserve message helpers."""

import json

from webwrench.taco import (
    add_class,
    container,
    make_append_msg,
    make_batch_msg,
    make_call_msg,
    make_message_msg,
    make_patch_msg,
    make_remove_msg,
    make_replace_msg,
    node,
    serialize,
    text_node,
    with_id,
)


class TestNode:
    def test_basic(self):
        t = node("div")
        assert t == {"t": "div"}

    def test_with_attrs(self):
        t = node("span", attrs={"class": "foo"})
        assert t == {"t": "span", "a": {"class": "foo"}}

    def test_with_content_string(self):
        t = node("p", content="hello")
        assert t == {"t": "p", "c": "hello"}

    def test_with_content_list(self):
        t = node("ul", content=[{"t": "li", "c": "a"}])
        assert t["c"] == [{"t": "li", "c": "a"}]

    def test_with_options(self):
        t = node("div", options={"mounted": "init()"})
        assert t["o"] == {"mounted": "init()"}

    def test_all_params(self):
        t = node("div", attrs={"id": "x"}, content="hi", options={"k": "v"})
        assert t == {"t": "div", "a": {"id": "x"}, "c": "hi", "o": {"k": "v"}}

    def test_empty_attrs_omitted(self):
        t = node("br", attrs=None)
        assert "a" not in t

    def test_none_content_omitted(self):
        t = node("br", content=None)
        assert "c" not in t

    def test_none_options_omitted(self):
        t = node("br", options=None)
        assert "o" not in t


class TestTextNode:
    def test_returns_string(self):
        assert text_node("hello") == "hello"


class TestContainer:
    def test_default(self):
        c = container()
        assert c == {"t": "div", "c": []}

    def test_with_children(self):
        c = container("ul", children=[{"t": "li"}])
        assert c == {"t": "ul", "c": [{"t": "li"}]}

    def test_with_attrs(self):
        c = container(attrs={"class": "box"})
        assert c["a"] == {"class": "box"}

    def test_default_children_empty_list(self):
        c = container("div")
        assert c["c"] == []


class TestWithId:
    def test_adds_id(self):
        t = node("div")
        result = with_id(t, "my-id")
        assert result["a"]["id"] == "my-id"
        # Original should not be mutated
        assert "a" not in t

    def test_preserves_existing_attrs(self):
        t = node("div", attrs={"class": "foo"})
        result = with_id(t, "bar")
        assert result["a"]["class"] == "foo"
        assert result["a"]["id"] == "bar"


class TestAddClass:
    def test_new_class(self):
        t = node("div")
        result = add_class(t, "active")
        assert result["a"]["class"] == "active"

    def test_append_class(self):
        t = node("div", attrs={"class": "foo"})
        result = add_class(t, "bar")
        assert result["a"]["class"] == "foo bar"

    def test_does_not_mutate_original(self):
        t = node("div", attrs={"class": "foo"})
        add_class(t, "bar")
        assert t["a"]["class"] == "foo"


class TestSerialize:
    def test_simple(self):
        t = node("p", content="hi")
        s = serialize(t)
        assert json.loads(s) == {"t": "p", "c": "hi"}

    def test_compact(self):
        s = serialize({"t": "br"})
        assert " " not in s


class TestMessages:
    def test_replace(self):
        msg = make_replace_msg("app", {"t": "div"})
        assert msg == {"type": "replace", "target": "app", "node": {"t": "div"}}

    def test_patch_content_only(self):
        msg = make_patch_msg("el", content="new")
        assert msg == {"type": "patch", "target": "el", "content": "new"}

    def test_patch_attr_only(self):
        msg = make_patch_msg("el", attr={"class": "x"})
        assert msg == {"type": "patch", "target": "el", "attr": {"class": "x"}}

    def test_patch_both(self):
        msg = make_patch_msg("el", content="txt", attr={"a": "b"})
        assert msg["content"] == "txt"
        assert msg["attr"] == {"a": "b"}

    def test_patch_neither(self):
        msg = make_patch_msg("el")
        assert msg == {"type": "patch", "target": "el"}

    def test_append(self):
        msg = make_append_msg("list", {"t": "li"})
        assert msg == {"type": "append", "target": "list", "node": {"t": "li"}}

    def test_remove(self):
        msg = make_remove_msg("item")
        assert msg == {"type": "remove", "target": "item"}

    def test_batch(self):
        ops = [make_remove_msg("a"), make_remove_msg("b")]
        msg = make_batch_msg(ops)
        assert msg["type"] == "batch"
        assert len(msg["ops"]) == 2

    def test_call_no_args(self):
        msg = make_call_msg("focus")
        assert msg == {"type": "call", "name": "focus"}

    def test_call_with_args(self):
        msg = make_call_msg("scrollTo", ["#target"])
        assert msg["args"] == ["#target"]

    def test_message(self):
        msg = make_message_msg("chart1", "update", {"data": [1, 2]})
        assert msg == {
            "type": "message",
            "target": "chart1",
            "action": "update",
            "data": {"data": [1, 2]},
        }

    def test_message_no_data(self):
        msg = make_message_msg("x", "reset")
        assert "data" not in msg
