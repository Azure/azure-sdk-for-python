# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Verify create transport reporting without a service or native binding call."""

import asyncio
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from create_item import test_service_failures as service_tests


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "diagnostics",
    [
        "transports=[metadata/gateway,data_plane/gateway_v2]",
        "transports=[data_plane/gateway]",
        "transports=[data_plane/gateway,data_plane/gateway_v2]",
        None,
    ],
)
@pytest.mark.parametrize("exclude_visible", [False, True])
def test_indexing_report_preserves_create_transport_before_observer_read_rust(
    monkeypatch, capsys, asynchronous, diagnostics, exclude_visible
):
    headers = {}
    stored = {}
    native = Mock()

    class Response(dict):
        def get_response_headers(self):
            return headers

    def create(body, **options):
        headers.clear()
        if diagnostics is not None:
            headers["x-ms-cosmos-sdk-diagnostics"] = diagnostics
        stored[body["id"]] = dict(body)
        prepared = SimpleNamespace(
            settings=SimpleNamespace(item=SimpleNamespace(indexing_directive=options.get("indexing_directive")))
        )
        native(None, prepared)
        return Response(body)

    async def create_async(body, **options):
        return create(body, **options)

    def read(item, **kwargs):
        headers["x-ms-cosmos-sdk-diagnostics"] = "observer read, not create"
        return stored[item]

    def query(*args, **kwargs):
        ids = ["default", "include", "exclude"] if exclude_visible else ["default", "include"]
        return [{"id": item} for item in ids]

    async def fault_client(rules):
        assert rules == []
        return object()

    container = SimpleNamespace(create_item=create_async if asynchronous else create)
    observer = SimpleNamespace(read_item=read, query_items=query)
    monkeypatch.setattr(service_tests, "target", lambda *args: container)
    monkeypatch.setattr(service_tests, "observe_native_create", lambda *args, **kwargs: native)

    async def run():
        await service_tests.test_service_applies_create_indexing_directive_rust(
            asynchronous, fault_client, object(), observer, monkeypatch
        )

    expected = diagnostics if diagnostics is not None else "<missing create diagnostics; transport unconfirmed>"
    if exclude_visible:
        with pytest.raises(AssertionError) as caught:
            asyncio.run(run())
        message = str(caught.value)
        assert "Exclude reached native create but the service query still returns the item" in message
        for mode in ("exclude", "include", "default"):
            assert f"{mode}: {expected}" in message
        assert message.index("exclude:") < message.index("include:") < message.index("default:")
        assert "observer read" not in message
    else:
        asyncio.run(run())
    output = capsys.readouterr().out
    assert f"exclude: {expected}" in output
    assert "observer read" not in output
