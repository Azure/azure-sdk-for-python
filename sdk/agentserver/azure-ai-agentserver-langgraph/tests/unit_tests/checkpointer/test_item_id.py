# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for item ID utilities."""

import pytest

from azure.ai.agentserver.langgraph.checkpointer._item_id import (
    ParsedItemId,
    make_item_id,
    parse_item_id,
)


@pytest.mark.unit
def test_make_item_id_formats_correctly() -> None:
    """Test that make_item_id creates correct composite IDs."""
    item_id = make_item_id("ns1", "cp-001", "checkpoint")
    assert item_id == "ns1:cp-001:checkpoint:"


@pytest.mark.unit
def test_make_item_id_with_sub_key() -> None:
    """Test that make_item_id includes sub_key correctly."""
    item_id = make_item_id("ns1", "cp-001", "writes", "task1:0")
    assert item_id == "ns1:cp-001:writes:task1%3A0"


@pytest.mark.unit
def test_make_item_id_with_blob() -> None:
    """Test blob item ID format."""
    item_id = make_item_id("", "cp-001", "blob", "messages:v2")
    assert item_id == ":cp-001:blob:messages%3Av2"


@pytest.mark.unit
def test_parse_item_id_extracts_components() -> None:
    """Test that parse_item_id extracts all components correctly."""
    item_id = "ns1:cp-001:checkpoint:"
    parsed = parse_item_id(item_id)

    assert parsed.checkpoint_ns == "ns1"
    assert parsed.checkpoint_id == "cp-001"
    assert parsed.item_type == "checkpoint"
    assert parsed.sub_key == ""


@pytest.mark.unit
def test_parse_item_id_extracts_sub_key() -> None:
    """Test that parse_item_id extracts sub_key correctly."""
    item_id = "ns1:cp-001:writes:task1%3A0"
    parsed = parse_item_id(item_id)

    assert parsed.checkpoint_ns == "ns1"
    assert parsed.checkpoint_id == "cp-001"
    assert parsed.item_type == "writes"
    assert parsed.sub_key == "task1:0"


@pytest.mark.unit
def test_roundtrip_simple() -> None:
    """Test roundtrip encoding/decoding of simple IDs."""
    original_ns = "namespace"
    original_id = "checkpoint-123"
    original_type = "checkpoint"
    original_key = ""

    item_id = make_item_id(original_ns, original_id, original_type, original_key)
    parsed = parse_item_id(item_id)

    assert parsed.checkpoint_ns == original_ns
    assert parsed.checkpoint_id == original_id
    assert parsed.item_type == original_type
    assert parsed.sub_key == original_key


@pytest.mark.unit
def test_roundtrip_with_special_characters() -> None:
    """Test roundtrip encoding/decoding with special characters (colons)."""
    original_ns = "ns:with:colons"
    original_id = "cp:123:abc"
    original_type = "blob"
    original_key = "channel:v1:extra"

    item_id = make_item_id(original_ns, original_id, original_type, original_key)
    parsed = parse_item_id(item_id)

    assert parsed.checkpoint_ns == original_ns
    assert parsed.checkpoint_id == original_id
    assert parsed.item_type == original_type
    assert parsed.sub_key == original_key


@pytest.mark.unit
def test_roundtrip_with_percent_signs() -> None:
    """Test roundtrip encoding/decoding with percent signs."""
    original_ns = "ns%test"
    original_id = "cp%123"
    original_type = "checkpoint"
    original_key = "key%value"

    item_id = make_item_id(original_ns, original_id, original_type, original_key)
    parsed = parse_item_id(item_id)

    assert parsed.checkpoint_ns == original_ns
    assert parsed.checkpoint_id == original_id
    assert parsed.item_type == original_type
    assert parsed.sub_key == original_key


@pytest.mark.unit
def test_parse_item_id_raises_on_invalid_format() -> None:
    """Test that parse_item_id raises ValueError for invalid format."""
    with pytest.raises(ValueError, match="Invalid item_id format"):
        parse_item_id("invalid:format")

    with pytest.raises(ValueError, match="Invalid item_id format"):
        parse_item_id("only:two:parts")


@pytest.mark.unit
def test_parse_item_id_raises_on_invalid_type() -> None:
    """Test that parse_item_id raises ValueError for invalid item type."""
    with pytest.raises(ValueError, match="Invalid item_type"):
        parse_item_id("ns:cp:invalid:key")
