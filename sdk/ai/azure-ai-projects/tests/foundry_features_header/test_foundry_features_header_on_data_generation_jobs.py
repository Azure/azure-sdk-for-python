# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests the Foundry-Features header on the data generation job methods of the sync `.datasets` sub-client.

The data generation job methods always send `Foundry-Features: DataGenerationJobs=V1Preview`
(regardless of `allow_preview`), merged with any caller-supplied Foundry-Features value.
Other `.datasets` methods must not send the header.
"""

from typing import Any, Iterator
from unittest.mock import MagicMock

import pytest
from azure.core.pipeline.transport import HttpTransport
from azure.core.polling import NoPolling
from azure.ai.projects import AIProjectClient
from azure.ai.projects.operations import _patch_datasets
from azure.ai.projects.operations._patch_datasets import DatasetsOperations

from foundry_features_header_test_base import (
    FAKE_ENDPOINT,
    FOUNDRY_FEATURES_HEADER,
    FakeCredential,
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


class CapturingTransport(HttpTransport):
    """Sync transport that captures the outgoing request and raises _RequestCaptured."""

    def send(self, request: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        raise _RequestCaptured(request)

    def open(self) -> None:
        pass

    def close(self) -> None:
        pass

    def __enter__(self) -> "CapturingTransport":
        return self

    def __exit__(self, *args: Any) -> None:
        pass


@pytest.fixture(scope="module")
def client() -> Iterator[AIProjectClient]:
    with AIProjectClient(
        endpoint=FAKE_ENDPOINT,
        credential=FakeCredential(),  # type: ignore[arg-type]
        transport=CapturingTransport(),
    ) as c:
        yield c


def _capture(call: Any) -> Any:
    try:
        result = call()
    except _RequestCaptured as exc:
        return exc.request
    try:
        next(iter(result))
    except _RequestCaptured as exc:
        return exc.request
    except StopIteration:
        raise AssertionError("Iterator exhausted without the transport being called") from None
    raise AssertionError("Transport was never called")


class TestFoundryFeaturesHeaderOnDataGenerationJobs(FoundryFeaturesHeaderTestBase):

    @pytest.mark.parametrize("method_name", DATA_GENERATION_JOB_METHODS)
    def test_header_sent_on_data_generation_job_methods(self, client: AIProjectClient, method_name: str) -> None:
        method = getattr(client.datasets, method_name)
        request = _capture(self._make_fake_call(method))
        assert request.headers.get(FOUNDRY_FEATURES_HEADER) == DATA_GENERATION_JOBS_HEADER_VALUE

    @pytest.mark.parametrize("method_name", OTHER_DATASETS_METHODS)
    def test_header_not_sent_on_other_datasets_methods(self, client: AIProjectClient, method_name: str) -> None:
        method = getattr(client.datasets, method_name)
        request = _capture(self._make_fake_call(method))
        assert FOUNDRY_FEATURES_HEADER not in request.headers

    @pytest.mark.parametrize("method_name", DATA_GENERATION_JOB_METHODS)
    def test_header_merged_with_caller_supplied_value(self, client: AIProjectClient, method_name: str) -> None:
        method = getattr(client.datasets, method_name)
        headers = {FOUNDRY_FEATURES_HEADER: "Custom=V1Preview", "SomeOtherHeaderName": "SomeOtherHeaderValue"}
        request = _capture(self._make_fake_call(method, extra_kwargs={"headers": headers}))
        assert request.headers.get(FOUNDRY_FEATURES_HEADER) == f"Custom=V1Preview,{DATA_GENERATION_JOBS_HEADER_VALUE}"
        assert request.headers.get("SomeOtherHeaderName") == "SomeOtherHeaderValue"
        # The caller's dictionary is not mutated.
        assert headers[FOUNDRY_FEATURES_HEADER] == "Custom=V1Preview"

    @pytest.mark.parametrize("method_name", DATA_GENERATION_JOB_METHODS)
    def test_header_not_duplicated_when_caller_already_supplies_it(
        self, client: AIProjectClient, method_name: str
    ) -> None:
        method = getattr(client.datasets, method_name)
        headers = {"foundry-features": f"{DATA_GENERATION_JOBS_HEADER_VALUE.lower()}, Custom=V1Preview"}
        request = _capture(self._make_fake_call(method, extra_kwargs={"headers": headers}))
        assert (
            request.headers.get(FOUNDRY_FEATURES_HEADER)
            == f"{DATA_GENERATION_JOBS_HEADER_VALUE.lower()},Custom=V1Preview"
        )

    def test_header_sent_on_lro_polling_requests(self, monkeypatch: pytest.MonkeyPatch) -> None:
        polling_kwargs: dict = {}

        class _RecordingPolling(NoPolling):
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                super().__init__()
                polling_kwargs.update(kwargs)

        monkeypatch.setattr(_patch_datasets, "LROBasePolling", _RecordingPolling)

        operation = DatasetsOperations.__new__(DatasetsOperations)
        operation._client = MagicMock()  # pylint: disable=protected-access
        operation._config = MagicMock(polling_interval=0)  # pylint: disable=protected-access
        operation._serialize = MagicMock()  # pylint: disable=protected-access
        operation._serialize.url.return_value = "https://example.test"  # pylint: disable=protected-access
        operation._deserialize = MagicMock()  # pylint: disable=protected-access
        initial_response = MagicMock()
        initial_response.http_response.json.return_value = {"id": "job-sync"}
        operation._create_generation_job_initial = MagicMock(  # pylint: disable=protected-access
            return_value=initial_response
        )

        operation.begin_create_generation_job(job={}, headers={FOUNDRY_FEATURES_HEADER: "Custom=V1Preview"})

        initial_headers = operation._create_generation_job_initial.call_args.kwargs[  # pylint: disable=protected-access
            "headers"
        ]
        expected = f"Custom=V1Preview,{DATA_GENERATION_JOBS_HEADER_VALUE}"
        assert initial_headers[FOUNDRY_FEATURES_HEADER] == expected
        assert polling_kwargs["headers"] == {FOUNDRY_FEATURES_HEADER: expected}
