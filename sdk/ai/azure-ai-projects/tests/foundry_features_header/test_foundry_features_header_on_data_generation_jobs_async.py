# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests the Foundry-Features header on the data generation job methods of the async `.datasets` sub-client.

The data generation job methods always send `Foundry-Features: DataGenerationJobs=V1Preview`
(regardless of `allow_preview`), merged with any caller-supplied Foundry-Features value.
Other `.datasets` methods must not send the header.
"""

import inspect
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.pipeline.transport import AsyncHttpTransport
from azure.core.polling import AsyncNoPolling
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
from azure.ai.projects.aio.operations import _patch_datasets_async
from azure.ai.projects.aio.operations._patch_datasets_async import DatasetsOperations

from foundry_features_header_test_base import (
    FAKE_ENDPOINT,
    FOUNDRY_FEATURES_HEADER,
    AsyncFakeCredential,
    FoundryFeaturesHeaderTestBase,
    _RequestCaptured,
)

DATA_GENERATION_JOBS_HEADER_VALUE = "DataGenerationJobs=V1Preview"

DATA_GENERATION_JOB_METHODS = [
    "begin_create_generation_job",
    "get_generation_job",
    "list_generation_jobs",
    "cancel_generation_job",
    "delete_generation_job",
]

OTHER_DATASETS_METHODS = ["list", "get", "list_versions", "delete", "create_or_update", "pending_upload"]


class CapturingAsyncTransport(AsyncHttpTransport):
    """Async transport that captures the outgoing request and raises _RequestCaptured."""

    async def send(self, request: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        raise _RequestCaptured(request)

    async def open(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def __aenter__(self) -> "CapturingAsyncTransport":
        return self

    async def __aexit__(self, *args: Any) -> None:
        pass


def _make_client() -> AsyncAIProjectClient:
    return AsyncAIProjectClient(
        endpoint=FAKE_ENDPOINT,
        credential=AsyncFakeCredential(),  # type: ignore[arg-type]
        transport=CapturingAsyncTransport(),
    )


async def _capture_async(call: Any) -> Any:
    result = call()
    if inspect.isawaitable(result):
        try:
            await result
        except _RequestCaptured as exc:
            return exc.request
        raise AssertionError("Transport was never called (awaitable completed without raising)")
    ai = result.__aiter__()
    try:
        await ai.__anext__()
    except _RequestCaptured as exc:
        return exc.request
    except StopAsyncIteration:
        raise AssertionError("Iterator exhausted without the transport being called") from None
    raise AssertionError("Transport was never called")


class TestFoundryFeaturesHeaderOnDataGenerationJobsAsync(FoundryFeaturesHeaderTestBase):

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name", DATA_GENERATION_JOB_METHODS)
    async def test_header_sent_on_data_generation_job_methods_async(self, method_name: str) -> None:
        async with _make_client() as client:
            method = getattr(client.datasets, method_name)
            request = await _capture_async(self._make_fake_call(method))
        assert request.headers.get(FOUNDRY_FEATURES_HEADER) == DATA_GENERATION_JOBS_HEADER_VALUE

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name", OTHER_DATASETS_METHODS)
    async def test_header_not_sent_on_other_datasets_methods_async(self, method_name: str) -> None:
        async with _make_client() as client:
            method = getattr(client.datasets, method_name)
            request = await _capture_async(self._make_fake_call(method))
        assert FOUNDRY_FEATURES_HEADER not in request.headers

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name", DATA_GENERATION_JOB_METHODS)
    async def test_header_merged_with_caller_supplied_value_async(self, method_name: str) -> None:
        headers = {FOUNDRY_FEATURES_HEADER: "Custom=V1Preview", "SomeOtherHeaderName": "SomeOtherHeaderValue"}
        async with _make_client() as client:
            method = getattr(client.datasets, method_name)
            request = await _capture_async(self._make_fake_call(method, extra_kwargs={"headers": headers}))
        assert request.headers.get(FOUNDRY_FEATURES_HEADER) == f"Custom=V1Preview,{DATA_GENERATION_JOBS_HEADER_VALUE}"
        assert request.headers.get("SomeOtherHeaderName") == "SomeOtherHeaderValue"
        assert headers[FOUNDRY_FEATURES_HEADER] == "Custom=V1Preview"

    @pytest.mark.asyncio
    async def test_header_sent_on_lro_polling_requests_async(self, monkeypatch: pytest.MonkeyPatch) -> None:
        polling_kwargs: dict = {}

        class _RecordingPolling(AsyncNoPolling):
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                super().__init__()
                polling_kwargs.update(kwargs)

        monkeypatch.setattr(_patch_datasets_async, "AsyncLROBasePolling", _RecordingPolling)

        operation = DatasetsOperations.__new__(DatasetsOperations)
        operation._client = MagicMock()  # pylint: disable=protected-access
        operation._config = MagicMock(polling_interval=0)  # pylint: disable=protected-access
        operation._serialize = MagicMock()  # pylint: disable=protected-access
        operation._serialize.url.return_value = "https://example.test"  # pylint: disable=protected-access
        operation._deserialize = MagicMock()  # pylint: disable=protected-access
        initial_response = MagicMock()
        initial_response.http_response.read = AsyncMock()
        initial_response.http_response.json.return_value = {"id": "job-async"}
        operation._create_generation_job_initial = AsyncMock(  # pylint: disable=protected-access
            return_value=initial_response
        )

        await operation.begin_create_generation_job(job={})

        initial_headers = operation._create_generation_job_initial.call_args.kwargs[  # pylint: disable=protected-access
            "headers"
        ]
        assert initial_headers[FOUNDRY_FEATURES_HEADER] == DATA_GENERATION_JOBS_HEADER_VALUE
        assert polling_kwargs["headers"] == {FOUNDRY_FEATURES_HEADER: DATA_GENERATION_JOBS_HEADER_VALUE}
