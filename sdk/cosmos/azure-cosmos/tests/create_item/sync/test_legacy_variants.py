# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Public Rust copies of quoted-path, suppressed-response and encoding creates."""

from copy import deepcopy
from functools import partial

import pytest

from config import clients
from create_item._legacy_contracts import INCOMPLETE_KEYS, assert_bad_hierarchical_key
from create_item._legacy_variants import (
    CASES,
    ENCODING_CASES,
    RESPONSE_MODES,
    assert_created,
    assert_fields,
    observe_native_create,
)
from create_item._legacy_variants import (  # pylint: disable=unused-import
    _make_variant_container_fixture,
    _variant_database_fixture,
)

from azure.cosmos import PartitionKey, exceptions

SCALAR_CASES = ("hash-null", "hash-missing", "hash-boolean", "hash-string", "hash-integer", "hash-float")


def _case_params(*names, client_suppressed=(False, True)):
    return [
        pytest.param(case, *mode.values, id=f"{case['name']}-{mode.id}")
        for case in CASES if case["name"] in names
        for mode in RESPONSE_MODES if mode.values[0] in client_suppressed
    ]


def _create_partition_key_case(
    variant_database, make_variant_container, monkeypatch, backend, case, client_suppressed, options, suppressed
):
    target = make_variant_container(case["definition"])
    with clients.create_data_client(
        _backend="rust" if backend == "rust" else "core-python",
        no_response_on_write=client_suppressed,
        timeout=30,
    ) as client:
        container = client.get_database_client(variant_database.id).get_container_client(target.id)
        native = observe_native_create(monkeypatch, client, backend)
        body = deepcopy(case["body"])
        created = container.create_item(body, **options)
        assert body == case["body"]
        assert_created(created, body, suppressed, native)
        assert_fields(container.read_item(body["id"], partition_key=case["key"]), body)


def _reject_incomplete_partition_key(
    variant_database, make_variant_container, monkeypatch, backend, definition, body, no_response
):
    target = make_variant_container(definition)
    with clients.create_data_client(_backend="rust" if backend == "rust" else "core-python", timeout=30) as client:
        container = client.get_database_client(variant_database.id).get_container_client(target.id)
        native = observe_native_create(monkeypatch, client, backend)
        original = deepcopy(body)
        with pytest.raises(exceptions.CosmosHttpResponseError) as caught:
            container.create_item(body, no_response=no_response)
        assert_bad_hierarchical_key(caught.value, native)
        assert body == original


def _hierarchical_scenarios(case_name, incomplete_id):
    created = [
        pytest.param(partial(_create_partition_key_case, case=case, client_suppressed=client_suppressed,
                             options=options, suppressed=suppressed), id=param.id)
        for param in _case_params(case_name)
        for case, client_suppressed, options, suppressed in [param.values]
    ]
    incomplete = next(param for param in INCOMPLETE_KEYS if param.id == incomplete_id)
    rejected = [
        pytest.param(partial(_reject_incomplete_partition_key, definition=incomplete.values[0],
                             body=incomplete.values[1], no_response=no_response),
                     id=f"{incomplete_id}-no_response-{no_response}")
        for no_response in (False, True)
    ]
    return created + rejected


def _round_trip_unicode(variant_database, make_variant_container, monkeypatch, backend, body):
    target = make_variant_container(PartitionKey(path="/pk"))
    with clients.create_data_client(_backend=backend, timeout=30) as client:
        container = client.get_database_client(variant_database.id).get_container_client(target.id)
        native = observe_native_create(monkeypatch, client, backend)
        original = deepcopy(body)
        created = container.create_item(body)
        assert body == original
        assert_created(created, original, False, native)
        read = container.read_item(created["id"], partition_key=body["pk"])
        assert_fields(read, original)
        for key in ("pk", "unicode_content"):
            if key in original:
                assert read[key].encode("utf-8") == original[key].encode("utf-8")


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("case,client_suppressed,options,suppressed",
                         _case_params("hash-double-quoted", "hash-single-quoted", client_suppressed=(False,)))
def test_partitioned_collection_partition_key_extraction_special_chars_rust(
    variant_database, make_variant_container, monkeypatch, backend, case, client_suppressed, options, suppressed
):
    # Source: tests/test_crud_container.py::TestCRUDContainerOperations.test_partitioned_collection_partition_key_extraction_special_chars
    _create_partition_key_case(
        variant_database, make_variant_container, monkeypatch, backend, case, client_suppressed, options, suppressed
    )


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("case,client_suppressed,options,suppressed",
                         _case_params("hash-double-quoted", "hash-single-quoted", client_suppressed=(True,)))
def test_partitioned_collection_partition_key_extraction_special_chars_response_payload_on_write_disabled_rust(
    variant_database, make_variant_container, monkeypatch, backend, case, client_suppressed, options, suppressed
):
    # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_partitioned_collection_partition_key_extraction_special_chars
    _create_partition_key_case(
        variant_database, make_variant_container, monkeypatch, backend, case, client_suppressed, options, suppressed
    )


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("case,client_suppressed,options,suppressed",
                         _case_params("hash-nested", "hash-object-leaf", "hash-missing-descendant",
                                      client_suppressed=(False,)))
def test_partitioned_collection_partition_key_extraction_rust(
    variant_database, make_variant_container, monkeypatch, backend, case, client_suppressed, options, suppressed
):
    # Source: tests/test_crud_container.py::TestCRUDContainerOperations.test_partitioned_collection_partition_key_extraction
    _create_partition_key_case(
        variant_database, make_variant_container, monkeypatch, backend, case, client_suppressed, options, suppressed
    )


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("case,client_suppressed,options,suppressed",
                         _case_params("hash-nested", "hash-object-leaf", "hash-missing-descendant",
                                      client_suppressed=(True,)))
def test_partitioned_collection_partition_key_extraction_response_payload_on_write_disabled_rust(
    variant_database, make_variant_container, monkeypatch, backend, case, client_suppressed, options, suppressed
):
    # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_partitioned_collection_partition_key_extraction
    _create_partition_key_case(
        variant_database, make_variant_container, monkeypatch, backend, case, client_suppressed, options, suppressed
    )


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADCircuitBreaker
@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("case,client_suppressed,options,suppressed",
                         _case_params(*SCALAR_CASES, client_suppressed=(False,)))
def test_partitioned_collection_partition_key_value_types_rust(
    variant_database, make_variant_container, monkeypatch, backend, case, client_suppressed, options, suppressed
):
    # Source: tests/test_crud.py::TestCRUDOperations.test_partitioned_collection_partition_key_value_types
    _create_partition_key_case(
        variant_database, make_variant_container, monkeypatch, backend, case, client_suppressed, options, suppressed
    )


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("case,client_suppressed,options,suppressed",
                         _case_params(*SCALAR_CASES, client_suppressed=(True,)))
def test_partitioned_collection_partition_key_value_types_response_payload_on_write_disabled_rust(
    variant_database, make_variant_container, monkeypatch, backend, case, client_suppressed, options, suppressed
):
    # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_partitioned_collection_partition_key_value_types
    _create_partition_key_case(
        variant_database, make_variant_container, monkeypatch, backend, case, client_suppressed, options, suppressed
    )


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("case,client_suppressed,options,suppressed",
                         _case_params("hierarchical-double-quoted", "hierarchical-single-quoted"))
def test_partitioned_collection_partition_key_extraction_special_chars_subpartition_rust(
    variant_database, make_variant_container, monkeypatch, backend, case, client_suppressed, options, suppressed
):
    # Source: tests/test_crud_subpartition.py::TestSubpartitionCrud.test_partitioned_collection_partition_key_extraction_special_chars_subpartition
    _create_partition_key_case(
        variant_database, make_variant_container, monkeypatch, backend, case, client_suppressed, options, suppressed
    )


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("scenario", _hierarchical_scenarios("hierarchical-nested", "missing-nested-components"))
def test_partitioned_collection_partition_key_extraction_subpartition_rust(
    variant_database, make_variant_container, monkeypatch, backend, scenario
):
    # Source: tests/test_crud_subpartition.py::TestSubpartitionCrud.test_partitioned_collection_partition_key_extraction_subpartition
    scenario(variant_database, make_variant_container, monkeypatch, backend)


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("scenario", _hierarchical_scenarios("hierarchical-mixed-types", "missing-second-component"))
def test_partitioned_collection_document_crud_and_query_subpartition_rust(
    variant_database, make_variant_container, monkeypatch, backend, scenario
):
    # Source: tests/test_crud_subpartition.py::TestSubpartitionCrud.test_partitioned_collection_document_crud_and_query_subpartition
    scenario(variant_database, make_variant_container, monkeypatch, backend)


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("body", [param for param in ENCODING_CASES if param.id == "unicode-separators"])
def test_create_document_with_line_separator_para_seperator_next_line_unicodes_rust(
    variant_database, make_variant_container, monkeypatch, backend, body
):
    # Source: tests/test_encoding.py::TestEncoding.test_create_document_with_line_separator_para_seperator_next_line_unicodes
    _round_trip_unicode(variant_database, make_variant_container, monkeypatch, backend, body)


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
@pytest.mark.parametrize("backend", ["rust", "core-python"])
@pytest.mark.parametrize("body", [param for param in ENCODING_CASES if param.id == "unicode-partition-key"])
def test_unicode_characters_in_partition_key_rust(variant_database, make_variant_container, monkeypatch, backend, body):
    # Source: tests/test_encoding.py::TestEncoding.test_unicode_characters_in_partition_key
    _round_trip_unicode(variant_database, make_variant_container, monkeypatch, backend, body)
