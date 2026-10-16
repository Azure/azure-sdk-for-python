# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Guard the actual typed Python/native contract, not a removed dictionary reader."""
from dataclasses import fields
from types import SimpleNamespace

import pytest

from azure.cosmos._backend.request_settings import (
    RequestSettings, ItemSettings, QuerySettings, ResourceSettings,
    binding_settings_contract_error, _request_settings_schema,
)
from azure.cosmos._helpers._request_settings import OPTION_FIELDS


def test_every_normalized_option_targets_a_declared_field():
    groups = {
        "": RequestSettings, "item": ItemSettings,
        "query": QuerySettings, "resource": ResourceSettings,
    }
    for option, (group, name) in OPTION_FIELDS.items():
        assert name in {field.name for field in fields(groups[group])}, option


def test_native_inventory_matches_both_directions():
    native = pytest.importorskip("azure.cosmos._rust")
    assert binding_settings_contract_error(native) is None
    schema = _request_settings_schema()
    assert {"priority", "no_response", "timeout_seconds"} <= set(schema["RequestSettings"])
    assert set(schema) == set(native._request_settings_schema())


@pytest.mark.parametrize("extra", [False, True])
def test_a_one_sided_field_change_requires_a_rebuild(extra):
    schema = _request_settings_schema()
    schema["RequestSettings"] = (
        schema["RequestSettings"] + ("unknown_future_field",)
        if extra else tuple(name for name in schema["RequestSettings"] if name != "no_response")
    )
    assert "rebuild" in binding_settings_contract_error(SimpleNamespace(_request_settings_schema=lambda: schema))


def test_old_extensions_fail_explicitly_when_checked():
    assert "rebuild" in binding_settings_contract_error(SimpleNamespace())
