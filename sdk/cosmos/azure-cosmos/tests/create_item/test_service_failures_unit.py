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
@pytest.mark.parametrize("legacy_exclude_visible", [False, True])
def test_indexing_report_preserves_create_transport_before_observer_read_rust(
    monkeypatch, capsys, asynchronous, diagnostics, exclude_visible, legacy_exclude_visible
):
    headers = {}
    stored = {}
    legacy_markers = set()
    native = Mock()

    class Response(dict):
        def get_response_headers(self):
            return headers

    def create(body, *, legacy=False, **options):
        headers.clear()
        if diagnostics is not None:
            headers["x-ms-cosmos-sdk-diagnostics"] = diagnostics
        stored[body["pk"], body["id"]] = dict(body)
        prepared = SimpleNamespace(
            settings=SimpleNamespace(item=SimpleNamespace(indexing_directive=options.get("indexing_directive")))
        )
        if legacy:
            legacy_markers.add(body["pk"])
        else:
            native(None, prepared)
        return Response(body)

    async def create_async(body, **options):
        return create(body, **options)

    def read(item, **kwargs):
        headers["x-ms-cosmos-sdk-diagnostics"] = "observer read, not create"
        return stored[kwargs["partition_key"], item]

    def query(*args, **kwargs):
        visible = legacy_exclude_visible if kwargs["partition_key"] in legacy_markers else exclude_visible
        ids = ["default", "include", "exclude"] if visible else ["default", "include"]
        return [{"id": item} for item in ids]

    async def fault_client(rules):
        assert rules == []
        return object()

    container = SimpleNamespace(create_item=create_async if asynchronous else create)
    legacy_container = SimpleNamespace(create_item=lambda body, **kwargs: create(body, legacy=True, **kwargs))
    legacy_client = Mock()
    legacy_client.__enter__ = Mock(return_value=legacy_client)
    legacy_client.__exit__ = Mock(return_value=False)
    observer = SimpleNamespace(read_item=read, query_items=query)
    monkeypatch.setenv("ACCOUNT_HOST", "https://localhost:8081/")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    monkeypatch.setattr(service_tests, "CosmosClient", Mock(return_value=legacy_client))
    monkeypatch.setattr(
        service_tests, "target", lambda client, *args: legacy_container if client is legacy_client else container
    )
    monkeypatch.setattr(service_tests, "observe_native_create", lambda *args, **kwargs: native)

    async def run():
        await service_tests.test_create_indexing_directive_matches_legacy_rust(
            asynchronous, fault_client, object(), observer, monkeypatch
        )

    expected = diagnostics if diagnostics is not None else "<missing create diagnostics; transport unconfirmed>"
    if exclude_visible != legacy_exclude_visible:
        with pytest.raises(AssertionError) as caught:
            asyncio.run(run())
        message = str(caught.value)
        assert "Rust indexing-directive query results differ from legacy" in message
        for mode in ("exclude", "include", "default"):
            assert f"{mode}: {expected}" in message
        assert message.index("exclude:") < message.index("include:") < message.index("default:")
        assert "observer read" not in message
    else:
        asyncio.run(run())
    output = capsys.readouterr().out
    assert f"exclude: {expected}" in output
    assert "observer read" not in output
