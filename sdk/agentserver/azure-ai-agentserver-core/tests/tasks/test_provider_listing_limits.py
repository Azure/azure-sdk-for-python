# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Parity for total task-list limits and complete ownership enumeration."""

from __future__ import annotations

import json
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse

import pytest
import pytest_asyncio

from azure.ai.agentserver.core.tasks._exceptions_internal import _HostedConflict
from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.tasks._manager import TaskManager
from azure.ai.agentserver.core.tasks._models import TaskCreateRequest, TaskInfo

from .conftest import FakeAsyncHttpTransport, FakeResponse
from .test_hosted_provider_transport import _make_provider


@pytest_asyncio.fixture(params=["local", "hosted"])
async def listing(request, tmp_path, monkeypatch):
    filters = {"agent_name": "agent", "session_id": "session", "tag": {"kind": "matching"}, "order": "asc"}
    records = []
    if request.param == "local":
        provider = LocalFileTaskProvider(base_dir=tmp_path)
        for index in range(126):
            records.append(
                await provider.create(
                    TaskCreateRequest(
                        id=f"task-{index:03}",
                        agent_name="agent",
                        session_id="session",
                        title="Listing regression",
                        tags={"kind": "matching"},
                    )
                )
            )
        records.sort(key=lambda info: info.created_at or "")
        await provider.create(
            TaskCreateRequest(agent_name="agent", session_id="session", title="Filtered out", tags={"kind": "other"})
        )
        yield SimpleNamespace(provider=provider, records=records, filters=filters, requests=[], kind="local")
        return

    records = [
        TaskInfo.from_dict(
            {"id": f"task-{index:03}", "agent_name": "agent", "session_id": "session", "status": "pending"}
        )
        for index in range(126)
    ]
    provider = _make_provider(FakeAsyncHttpTransport())
    queries = []
    offsets = {"opaque-start": 6}

    async def send(http_request):
        query = parse_qs(urlparse(http_request.url).query)
        queries.append(query)
        assert query["agent_name"] == ["agent"]
        assert query["session_id"] == ["session"]
        assert query["tag.kind"] == ["matching"]
        assert query["order"] == ["asc"]
        cursor = query.get("after", [None])[0]
        offset = offsets[cursor] if cursor is not None else 0
        end = min(offset + min(7, int(query["limit"][0])), len(records))
        body = {"data": [record.to_dict() for record in records[offset:end]], "has_more": end < len(records)}
        if body["has_more"]:
            token = f"opaque-page-{end}"
            offsets[token] = end
            body["last_id"] = token
        return SimpleNamespace(status_code=200, headers={}, body=lambda: json.dumps(body).encode())

    monkeypatch.setattr(provider, "_send", send)
    try:
        yield SimpleNamespace(provider=provider, records=records, filters=filters, requests=queries, kind="hosted")
    finally:
        await provider.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("limit", ["omitted", None, 20, 25, 100, 101, 1000])
@pytest.mark.parametrize("continued", [False, True])
async def test_listing_total_limit_and_unbounded_result_shape(listing, limit, continued):
    kwargs = {} if limit == "omitted" else {"limit": limit}
    if continued:
        kwargs["after"] = listing.records[5].id if listing.kind == "local" else "opaque-start"
    expected = listing.records[6:] if continued else listing.records
    bounded = limit not in ("omitted", None)
    if bounded:
        expected = expected[: min(limit, 100)]
    result = await listing.provider.list(**listing.filters, **kwargs)
    assert isinstance(result, list)
    assert all(isinstance(info, TaskInfo) for info in result)
    assert len(result) == (min(limit, 100) if bounded else 120 if continued else 126)
    assert [info.id for info in result] == [info.id for info in expected]
    if listing.kind == "hosted":
        assert len(listing.requests) == (len(expected) + 6) // 7
        assert listing.requests[0]["limit"] == [str(min(limit, 100) if bounded else 100)]
        for index, query in enumerate(listing.requests):
            assert query["limit"] == [str(min(limit, 100) - index * 7 if bounded else 100)]
            if index:
                assert query["after"][0].startswith("opaque-page-")


@pytest.mark.asyncio
@pytest.mark.parametrize("limit", [0, -1])
async def test_nonpositive_total_limit_has_matching_error_classification(listing, limit):
    with pytest.raises(_HostedConflict) as raised:
        await listing.provider.list(**listing.filters, limit=limit)
    assert raised.value._code == "invalid_request"
    assert raised.value.status_code == 400
    assert listing.requests == []


@pytest.mark.asyncio
async def test_hosted_budget_stops_without_fetching_or_exposing_a_continuation():
    records = [{"id": f"task-{index}", "agent_name": "agent", "session_id": "session"} for index in range(30)]
    transport = FakeAsyncHttpTransport([FakeResponse.json_response({"data": records, "has_more": True})])
    provider = _make_provider(transport)
    try:
        result = await provider.list(limit=20)
        assert isinstance(result, list)
        assert all(isinstance(info, TaskInfo) for info in result)
        assert [info.id for info in result] == [f"task-{index}" for index in range(20)]
        assert len(transport.requests) == 1
    finally:
        await provider.close()


@pytest.mark.asyncio
async def test_manager_ownership_and_recovery_scans_explicitly_override_a_bounded_provider_default(tmp_path):
    provider = LocalFileTaskProvider(base_dir=tmp_path)
    for index in range(126):
        await provider.create(
            TaskCreateRequest(
                id=f"task-{index:03}",
                agent_name="agent",
                session_id="session",
                title="Ownership listing",
                tags={"task_name": "response"},
                source=TaskManager._build_source("response"),
            )
        )
    limits = []

    async def legacy_list(*, limit=20, **kwargs):
        limits.append(limit)
        return await provider.list(limit=limit, **kwargs)

    config = SimpleNamespace(agent_name="agent", session_id="session", agent_version="1.0.0", is_hosted=False)
    manager = TaskManager(config=config, provider=SimpleNamespace(list=legacy_list))
    result = await manager.list_tasks(fn_name="response")
    assert isinstance(result, list)
    assert all(isinstance(info, TaskInfo) for info in result)
    assert len(result) == 126
    assert {info.id for info in result} == {f"task-{index:03}" for index in range(126)}
    assert limits == [None]
    await manager._recover_stale_tasks()
    assert limits == [None, None]


@pytest.mark.asyncio
@pytest.mark.parametrize("limit,expected", [(None, 35), (25, 25)])
async def test_hosted_empty_page_continues_without_consuming_result_budget(limit, expected):
    records = [{"id": f"task-{index}", "agent_name": "agent", "session_id": "session"} for index in range(35)]
    transport = FakeAsyncHttpTransport(
        [
            FakeResponse.json_response({"data": [], "has_more": True, "last_id": "opaque-empty"}),
            FakeResponse.json_response({"data": records, "has_more": False}),
        ]
    )
    provider = _make_provider(transport)
    try:
        result = await provider.list(limit=limit)
        assert len(result) == expected
        assert [info.id for info in result] == [f"task-{index}" for index in range(expected)]
        assert len(transport.requests) == 2
        assert parse_qs(urlparse(transport.requests[1].url).query)["after"] == ["opaque-empty"]
    finally:
        await provider.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("limit", [None, 25])
async def test_hosted_later_page_error_never_returns_partial_success(limit):
    transport = FakeAsyncHttpTransport(
        [
            FakeResponse.json_response(
                {
                    "data": [{"id": "first", "agent_name": "agent", "session_id": "session"}],
                    "has_more": True,
                    "last_id": "opaque-next",
                }
            ),
            FakeResponse.json_response(
                {"error": {"code": "invalid_request", "message": "listing unavailable"}}, status_code=400
            ),
        ]
    )
    provider = _make_provider(transport)
    try:
        with pytest.raises(_HostedConflict) as raised:
            await provider.list(limit=limit)
        assert raised.value._code == "invalid_request"
        assert len(transport.requests) == 2
    finally:
        await provider.close()
