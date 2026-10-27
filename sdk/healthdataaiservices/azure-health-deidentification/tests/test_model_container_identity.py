# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for the _patch.py shim that keeps model container fields bound to one object.

No service calls or recordings are involved.
"""
import pytest

import azure.health.deidentification.aio  # pylint: disable=unused-import
from azure.health.deidentification import _patch
from azure.health.deidentification._utils import model_base
from azure.health.deidentification.models import (
    SimplePhiEntity,
    SourceStorageLocation,
    TaggedPhiEntities,
)

# Each pattern lists how references are obtained, in order; the first reference is then mutated.
PATTERNS = {
    "A_dict_property_mutate_dict_ref": ["dict", "property"],
    "B_property_dict_mutate_property_ref": ["property", "dict"],
    "C_property_mutate": ["property"],
    "D_dict_mutate": ["dict"],
    "E_property_property_mutate_first_ref": ["property", "property"],
}


def _access(model, attr, key, how):
    return model[key] if how == "dict" else getattr(model, attr)


def _make_source():
    return SourceStorageLocation(location="https://example.blob.core.windows.net/c", prefix="p", extensions=[".txt"])


def _make_tagged_from_kwargs():
    return TaggedPhiEntities(
        encoding="CodePoint",
        entities=[SimplePhiEntity(category="Patient", offset=0, length=4, text="John")],
    )


def _make_tagged_from_mapping():
    return TaggedPhiEntities(
        {"encoding": "CodePoint", "entities": [{"category": "Patient", "offset": 0, "length": 4, "text": "John"}]}
    )


def _mutate_extensions(source, accesses):
    refs = [_access(source, "extensions", "extensions", how) for how in accesses]
    refs[0].append(".csv")
    return source.as_dict()["extensions"]


@pytest.mark.parametrize("accesses", PATTERNS.values(), ids=PATTERNS.keys())
def test_list_of_str_mutation_is_serialized(accesses):
    assert _mutate_extensions(_make_source(), accesses) == [".txt", ".csv"]


@pytest.mark.parametrize(
    "make_tagged", [_make_tagged_from_kwargs, _make_tagged_from_mapping], ids=["kwargs", "mapping"]
)
@pytest.mark.parametrize("accesses", PATTERNS.values(), ids=PATTERNS.keys())
def test_list_of_models_mutation_is_serialized(accesses, make_tagged):
    tagged = make_tagged()
    refs = [_access(tagged, "entities", "entities", how) for how in accesses]
    refs[0].append(SimplePhiEntity(category="Date", offset=9, length=10))
    refs[0][0]["text"] = "Jane"

    assert tagged.as_dict() == {
        "encoding": "CodePoint",
        "entities": [
            {"category": "Patient", "offset": 0, "length": 4, "text": "Jane"},
            {"category": "Date", "offset": 9, "length": 10},
        ],
    }
    assert [type(e) for e in tagged.entities] == [SimplePhiEntity, SimplePhiEntity]
    assert tagged.entities[0].text == "Jane"


def test_property_and_dict_access_share_one_list():
    source = _make_source()
    via_dict = source["extensions"]
    via_property = source.extensions
    assert via_property is via_dict
    assert source["extensions"] is via_dict


def test_setting_field_replaces_container():
    source = _make_source()
    old = source.extensions
    source.extensions = [".json"]
    assert source.extensions == [".json"]
    assert old == [".txt"]
    assert source.as_dict()["extensions"] == [".json"]


def test_shim_is_applied_once_for_sync_and_aio():
    _patch.patch_sdk()
    _patch.patch_sdk()
    get = model_base._RestField.__get__  # pylint: disable=protected-access
    assert getattr(get, _patch._IDENTITY_SHIM_MARKER, False)  # pylint: disable=protected-access
    assert not getattr(get.__wrapped__, _patch._IDENTITY_SHIM_MARKER, False)  # pylint: disable=protected-access


def test_generated_get_still_needs_shim(monkeypatch):
    """Fails once the emitter preserves container identity itself; then remove the _patch.py shim."""
    rest_field = model_base._RestField  # pylint: disable=protected-access
    monkeypatch.setattr(rest_field, "__get__", rest_field.__get__.__wrapped__)
    assert _mutate_extensions(_make_source(), PATTERNS["A_dict_property_mutate_dict_ref"]) == [".txt"], (
        "Generated _RestField.__get__ now preserves container identity; "
        "remove _preserve_container_identity from azure/health/deidentification/_patch.py."
    )
