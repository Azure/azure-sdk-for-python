# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Read-many dispatch is retained Rust execution, never the compatibility query gate."""

from dataclasses import FrozenInstanceError

import pytest

from azure.cosmos._backend._binding_conversions import build_binding_request_from_page
from azure.cosmos._backend.contracts import PreparedPageRequest, ReadManyItem
from azure.cosmos._backend.operations import get_page_binding_function_name
from azure.cosmos._backend.partition_key_input import BindingPartitionKey
from ._helpers import make_proxy


def test_read_items_has_only_retained_native_dispatch_rust():
    assert get_page_binding_function_name("read_items", uses_cursor=True) == "fetch_page_with_cursor"
    assert get_page_binding_function_name("read_items", uses_cursor=False) is None


def test_typed_selection_is_immutable_and_not_a_sql_query_rust():
    item = ReadManyItem("a", BindingPartitionKey("components", ("tenant", None, Ellipsis)))
    page = PreparedPageRequest("read_items", "dbs/d/colls/c", read_many_items=(item,))
    request = build_binding_request_from_page(page)
    assert request.read_many_items == (item,)
    assert request.body_bytes == b"" and request.query_scope is None
    with pytest.raises(FrozenInstanceError):
        item.item_id = "other"
    with pytest.raises(TypeError):
        PreparedPageRequest("read_items", "dbs/d/colls/c", read_many_items=[item])


@pytest.mark.parametrize("backend", ["missing-context", "core-python"])
def test_read_items_never_falls_back_to_core_python_rust(backend):
    proxy, adapter = make_proxy()
    if backend == "missing-context":
        proxy._item_context = None
    else:
        adapter.name = "core-python"
    with pytest.raises(NotImplementedError, match="Rust"):
        proxy.read_items([("a", "p")])
