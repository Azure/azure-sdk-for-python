# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""The Rust binding rejects the typed partitionless-key sentinel on create.

This does not establish the external driver's routing behavior or replace a
test against a partitionless container.
"""
import json
import os
import uuid

import pytest

from azure.cosmos._backend.binding_adapter import BindingAdapter
from azure.cosmos._backend.contracts import PreparedRequest
from azure.cosmos._backend.operations import OP_CREATE_ITEM
from azure.cosmos._backend.partition_key_input import BindingPartitionKey


def test_partitionless_container_rejected_by_rust_binding_rust():
    """Check rejection of the explicit typed partitionless-key sentinel.

    Accept ValueError or RuntimeError and require 'partitionless' in its message.
    A cross-partition query scope is not this sentinel. This test does not
    independently detect whether initialization performed network I/O.
    """

    # Real configuration is required by this test's lazy driver initialization.
    # No network recorder or prohibition is installed here.
    endpoint = os.environ.get("ACCOUNT_HOST")
    master_key = os.environ.get("ACCOUNT_KEY")
    if not endpoint or not master_key:
        pytest.skip(
            "ACCOUNT_HOST / ACCOUNT_KEY not set; this test needs a real "
            "endpoint to bootstrap the Rust driver before the binding "
            "ever inspects the typed partition key."
        )

    backend = BindingAdapter(endpoint=endpoint, master_key=master_key)
    body = {"id": uuid.uuid4().hex, "pk": "a"}
    prepared = PreparedRequest(
        op=OP_CREATE_ITEM,
        container_link="dbs/does_not_matter/colls/does_not_matter",
        body_bytes=json.dumps(body).encode("utf-8"),
        partition_key=BindingPartitionKey("empty_sentinel"),
        headers={},
    )

    # Accept either exception type, then check the message substring separately.
    try:
        with pytest.raises((ValueError, RuntimeError)) as excinfo:
            backend.execute(prepared)
    finally:
        backend.close()

    message = str(excinfo.value)
    assert "partitionless" in message.lower(), (
        "Rust binding must reject the empty_sentinel partition key with a message "
        "naming the partitionless-container limitation; got: {!r}".format(message)
    )
