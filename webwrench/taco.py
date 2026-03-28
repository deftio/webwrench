"""TACO (Tag, Attributes, Content, Options) dict builders.

TACO is bitwrench's DOM representation format:
  {'t': tag, 'a': {attributes}, 'c': content, 'o': {options}}

These are pure functions with no side effects.
"""

from __future__ import annotations

import json
from typing import Any


def node(
    tag: str,
    attrs: dict[str, Any] | None = None,
    content: Any = None,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a TACO node dict."""
    taco: dict[str, Any] = {"t": tag}
    if attrs:
        taco["a"] = attrs
    if content is not None:
        taco["c"] = content
    if options:
        taco["o"] = options
    return taco


def text_node(text: str) -> str:
    """Text nodes in TACO are just strings."""
    return text


def container(
    tag: str = "div",
    children: list[Any] | None = None,
    attrs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a TACO container node with children."""
    return node(tag, attrs=attrs, content=children or [])


def with_id(taco: dict[str, Any], element_id: str) -> dict[str, Any]:
    """Add or set the id attribute on a TACO node."""
    result = dict(taco)
    attrs = dict(result.get("a", {}))
    attrs["id"] = element_id
    result["a"] = attrs
    return result


def add_class(taco: dict[str, Any], css_class: str) -> dict[str, Any]:
    """Add a CSS class to a TACO node."""
    result = dict(taco)
    attrs = dict(result.get("a", {}))
    existing = attrs.get("class", "")
    if existing:
        attrs["class"] = f"{existing} {css_class}"
    else:
        attrs["class"] = css_class
    result["a"] = attrs
    return result


def serialize(taco: Any) -> str:
    """Serialize a TACO structure to JSON string."""
    return json.dumps(taco, separators=(",", ":"))


def make_replace_msg(target: str, taco_node: dict[str, Any]) -> dict[str, Any]:
    """Create a bwserve 'replace' message."""
    return {"type": "replace", "target": target, "node": taco_node}


def make_patch_msg(
    target: str,
    content: Any | None = None,
    attr: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a bwserve 'patch' message."""
    msg: dict[str, Any] = {"type": "patch", "target": target}
    if content is not None:
        msg["content"] = content
    if attr is not None:
        msg["attr"] = attr
    return msg


def make_append_msg(target: str, taco_node: dict[str, Any]) -> dict[str, Any]:
    """Create a bwserve 'append' message."""
    return {"type": "append", "target": target, "node": taco_node}


def make_remove_msg(target: str) -> dict[str, Any]:
    """Create a bwserve 'remove' message."""
    return {"type": "remove", "target": target}


def make_batch_msg(ops: list[dict[str, Any]]) -> dict[str, Any]:
    """Create a bwserve 'batch' message."""
    return {"type": "batch", "ops": ops}


def make_call_msg(name: str, args: list[Any] | None = None) -> dict[str, Any]:
    """Create a bwserve 'call' message."""
    msg: dict[str, Any] = {"type": "call", "name": name}
    if args is not None:
        msg["args"] = args
    return msg


def make_message_msg(
    target: str, action: str, data: Any = None
) -> dict[str, Any]:
    """Create a bwserve 'message' message."""
    msg: dict[str, Any] = {"type": "message", "target": target, "action": action}
    if data is not None:
        msg["data"] = data
    return msg
