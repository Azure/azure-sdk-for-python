# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for ID generation behavior."""

from __future__ import annotations

import re

import pytest

from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses.models import _generated as generated_models


def test_id_generator__new_id_uses_new_format_shape() -> None:
    created_id = IdGenerator.new_id("msg")

    assert created_id.startswith("msg_")
    body = created_id[len("msg_") :]
    assert len(body) == 50

    partition_key = body[:18]
    entropy = body[18:]

    assert len(partition_key) == 18
    assert partition_key.endswith("00")
    assert re.fullmatch(r"[0-9a-f]{16}00", partition_key) is not None
    assert len(entropy) == 32
    assert re.fullmatch(r"[A-Za-z0-9]{32}", entropy) is not None


def test_id_generator__new_id_reuses_new_format_partition_key_from_hint() -> None:
    hint = "caresp_1234567890abcdef00ABCDEFGHIJKLMNOPQRSTUVWXYZ012345"

    created_id = IdGenerator.new_id("fc", hint)

    assert created_id.startswith("fc_1234567890abcdef00")


def test_id_generator__new_id_upgrades_legacy_partition_key_from_hint() -> None:
    legacy_partition_key = "1234567890abcdef"
    legacy_entropy = "A" * 32
    legacy_hint = f"msg_{legacy_entropy}{legacy_partition_key}"

    created_id = IdGenerator.new_id("rs", legacy_hint)

    assert created_id.startswith("rs_1234567890abcdef00")


def test_id_generator__extract_partition_key_supports_new_and_legacy_formats() -> None:
    new_format_id = "caresp_1234567890abcdef00ABCDEFGHIJKLMNOPQRSTUVWXYZ012345"
    legacy_format_id = "msg_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1234567890abcdef"

    assert IdGenerator.extract_partition_key(new_format_id) == "1234567890abcdef00"
    assert IdGenerator.extract_partition_key(legacy_format_id) == "1234567890abcdef"


def test_id_generator__extract_partition_key_raises_for_bad_input() -> None:
    with pytest.raises(ValueError, match="ID must not be null or empty"):
        IdGenerator.extract_partition_key("")

    with pytest.raises(ValueError, match="has no '_' delimiter"):
        IdGenerator.extract_partition_key("badid")

    with pytest.raises(ValueError, match="unexpected body length"):
        IdGenerator.extract_partition_key("msg_short")


def test_id_generator__is_valid_reports_compatible_errors() -> None:
    assert IdGenerator.is_valid("") == (False, "ID must not be null or empty.")
    assert IdGenerator.is_valid("badid") == (False, "ID 'badid' has no '_' delimiter.")
    assert IdGenerator.is_valid("_short") == (
        False,
        "ID has an empty prefix.",
    )
    assert IdGenerator.is_valid("msg_short") == (
        False,
        "ID 'msg_short' has unexpected body length 5 (expected 50 or 48).",
    )


def test_id_generator__is_valid_checks_allowed_prefixes() -> None:
    valid_id = "msg_1234567890abcdef00ABCDEFGHIJKLMNOPQRSTUVWXYZ012345"

    ok, error = IdGenerator.is_valid(valid_id, allowed_prefixes=["msg", "fc"])
    assert ok is True
    assert error is None

    ok, error = IdGenerator.is_valid(valid_id, allowed_prefixes=["fc"])
    assert ok is False
    assert error == "ID prefix 'msg' is not in the allowed set [fc]."


def test_id_generator__convenience_method_uses_caresp_prefix() -> None:
    created_id = IdGenerator.new_response_id()

    assert created_id.startswith("caresp_")
    assert len(created_id.split("_", maxsplit=1)[1]) == 50


def test_id_generator__new_item_id_dispatches_by_generated_model_type() -> None:
    item_message = object.__new__(generated_models.ItemMessage)
    item_reference = object.__new__(generated_models.ItemReferenceParam)

    generated_id = IdGenerator.new_item_id(item_message)

    assert generated_id is not None
    assert generated_id.startswith("msg_")
    assert IdGenerator.new_item_id(item_reference) is None
    assert IdGenerator.new_item_id(object()) is None
