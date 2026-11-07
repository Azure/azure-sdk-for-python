# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Deprecated sync ``delete_item`` kwargs warn and never reach the wire.

``populate_query_metrics`` is sync-only and deprecated on ``delete_item``; the
async sibling does not expose it at all.
"""

import os
import uuid
import warnings
from typing import Any, Dict

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos import _cosmos_client_connection as _ccc_module
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from azure.cosmos.http_constants import HttpHeaders


@pytest.fixture
def container_ids():
    """Own a database with one ``/pk`` container and delete it afterwards."""
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database = client.create_database("delete_deprecated_" + uuid.uuid4().hex)
        try:
            database.create_container("orders", partition_key=PartitionKey(path="/pk"))
            yield database.id, "orders"
        finally:
            try:
                client.delete_database(database.id)
            except CosmosResourceNotFoundError:
                pass


def _assert_deprecation_warning_fired(recorded, kwarg_name: str) -> None:
    """Confirm customers receive the documented deprecation warning."""
    matches = [w for w in recorded
               if issubclass(w.category, DeprecationWarning)
               and kwarg_name in str(w.message)]
    assert matches, (
        "expected a DeprecationWarning mentioning {!r}, got: {}".format(
            kwarg_name, [str(w.message) for w in recorded]
        )
    )


def test_populate_query_metrics_deprecated_and_not_on_wire_rust(container_ids):
    """``populate_query_metrics=True`` is deprecated AND not forwarded.

    1. The public sync ``delete_item`` emits a ``DeprecationWarning``
       mentioning ``populate_query_metrics``.
    2. The ``x-ms-documentdb-populatequerymetrics`` request header is NOT on
       the outgoing DELETE. ``CosmosClientConnection.__Delete`` receives the
       fully built ``req_headers``, so it is wrapped to capture them; that
       requires the core-python backend. The public method drops the value
       before either backend's helper layer sees it.
    """
    database_id, container_id = container_ids
    captured_delete_headers: Dict[str, Any] = {}

    original_delete = _ccc_module.CosmosClientConnection._CosmosClientConnection__Delete  # type: ignore[attr-defined]

    def _capturing_delete(self, path, request_params, req_headers, **kwargs):  # type: ignore[no-redef]
        if "/docs/" in path:
            captured_delete_headers.clear()
            captured_delete_headers.update(dict(req_headers))
        return original_delete(self, path, request_params, req_headers, **kwargs)

    _ccc_module.CosmosClientConnection._CosmosClientConnection__Delete = _capturing_delete  # type: ignore[attr-defined]
    try:
        with CosmosClient(
            os.environ["ACCOUNT_HOST"],
            os.environ["ACCOUNT_KEY"],
            _backend="core-python",  # type: ignore[arg-type]
        ) as client:
            cont = client.get_database_client(database_id).get_container_client(container_id)
            item_id = uuid.uuid4().hex
            cont.create_item({"id": item_id, "pk": "a"})
            with warnings.catch_warnings(record=True) as recorded:
                warnings.simplefilter("always")
                cont.delete_item(
                    item_id,
                    partition_key="a",
                    populate_query_metrics=True,
                )
    finally:
        _ccc_module.CosmosClientConnection._CosmosClientConnection__Delete = original_delete  # type: ignore[attr-defined]

    _assert_deprecation_warning_fired(recorded, "populate_query_metrics")
    pqm_header = HttpHeaders.PopulateQueryMetrics
    assert captured_delete_headers, "the DELETE request headers were not captured"
    assert pqm_header not in captured_delete_headers, (
        "``populate_query_metrics`` must be DROPPED before the helper "
        "layer on delete_item -- the wire header {!r} must NOT be on "
        "the outgoing DELETE. Captured headers: {!r}".format(
            pqm_header, sorted(captured_delete_headers)
        )
    )
