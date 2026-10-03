# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline wire and response tests for Command and Pipeline jobs."""

import json
from typing import Any, Union
from urllib.parse import parse_qs, urlparse

import pytest
from azure.core.credentials import AccessToken
from azure.core.pipeline.transport import (
    AsyncHttpResponse,
    AsyncHttpTransport,
    HttpRequest,
    HttpResponse,
    HttpTransport,
)

from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
from azure.ai.projects.models import CommandJob, JobType, PipelineJob

_ENDPOINT = "https://fake-account.services.ai.azure.com/api/projects/fake-project"
_COMPUTE = "/subscriptions/test/resourceGroups/test/providers/Microsoft.CognitiveServices/accounts/test/computes/cpu"
_PIPELINE_PROPERTIES = {
    "jobType": "Pipeline",
    "displayName": "example pipeline",
    "computeId": _COMPUTE,
    "settings": {"continueOnStepFailure": False},
    "jobs": {
        "train": {
            "jobType": "Command",
            "command": "python train.py --data ${{parent.inputs.training_data}}",
            "environmentImageReference": "example.azurecr.io/train:latest",
            "inputs": {"training_data": {"path": "${{parent.inputs.training_data}}", "mode": "ro_mount"}},
        }
    },
    "inputs": {"training_data": {"type": "uri_folder", "path": "azureml://datastores/test/paths/training/"}},
    "outputs": {"model": {"type": "uri_folder", "mode": "rw_mount"}},
}
_COMMAND_PROPERTIES = {
    "jobType": "Command",
    "command": "echo hello",
    "environmentImageReference": "example.azurecr.io/train:latest",
    "computeId": _COMPUTE,
}


class _Credential:
    def get_token(self, *args: Any, **kwargs: Any) -> AccessToken:
        return AccessToken("fake-token", 9_999_999_999)


class _AsyncCredential:
    async def get_token(self, *args: Any, **kwargs: Any) -> AccessToken:
        return AccessToken("fake-token", 9_999_999_999)


class _JsonResponse(HttpResponse):
    def __init__(self, request: HttpRequest, payload: dict[str, Any]) -> None:
        super().__init__(request, None)
        self.status_code = 200
        self.headers["Content-Type"] = "application/json"
        self._content = json.dumps(payload).encode()

    def body(self) -> bytes:
        return self._content

    def json(self) -> Any:
        return json.loads(self._content)


class _AsyncJsonResponse(AsyncHttpResponse):
    def __init__(self, request: HttpRequest, payload: dict[str, Any]) -> None:
        super().__init__(request, None)
        self.status_code = 200
        self.headers["Content-Type"] = "application/json"
        self._content = json.dumps(payload).encode()

    def body(self) -> bytes:
        return self._content

    async def read(self) -> bytes:
        return self._content

    def json(self) -> Any:
        return json.loads(self._content)


class _Transport(HttpTransport):
    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self._responses = iter(responses)
        self.requests: list[HttpRequest] = []

    def send(self, request: HttpRequest, **kwargs: Any) -> HttpResponse:
        self.requests.append(request)
        return _JsonResponse(request, next(self._responses))

    def open(self) -> None:
        pass

    def close(self) -> None:
        pass

    def __exit__(self, *args: Any) -> None:
        pass


class _AsyncTransport(AsyncHttpTransport):
    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self._responses = iter(responses)
        self.requests: list[HttpRequest] = []

    async def send(self, request: HttpRequest, **kwargs: Any) -> AsyncHttpResponse:
        self.requests.append(request)
        return _AsyncJsonResponse(request, next(self._responses))

    async def open(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def __aexit__(self, *args: Any) -> None:
        pass


def _job(kind: str) -> tuple[Union[CommandJob, PipelineJob], dict[str, Any]]:
    if kind == "Pipeline":
        return (
            PipelineJob(
                display_name="example pipeline",
                compute_id=_COMPUTE,
                settings=_PIPELINE_PROPERTIES["settings"],
                jobs=_PIPELINE_PROPERTIES["jobs"],
                inputs=_PIPELINE_PROPERTIES["inputs"],
                outputs=_PIPELINE_PROPERTIES["outputs"],
            ),
            _PIPELINE_PROPERTIES,
        )
    return (
        CommandJob(
            command="echo hello",
            environment_image_reference="example.azurecr.io/train:latest",
            compute=_COMPUTE,
        ),
        _COMMAND_PROPERTIES,
    )


def _response(kind: str) -> dict[str, Any]:
    return {
        "name": kind.lower(),
        "id": f"/jobs/{kind.lower()}",
        "properties": _PIPELINE_PROPERTIES if kind == "Pipeline" else _COMMAND_PROPERTIES,
    }


def _assert_job(result: Union[CommandJob, PipelineJob], kind: str) -> None:
    if kind == "Pipeline":
        assert isinstance(result, PipelineJob)
        assert result.jobs == _PIPELINE_PROPERTIES["jobs"]
        assert result.inputs == _PIPELINE_PROPERTIES["inputs"]
        assert result.outputs == _PIPELINE_PROPERTIES["outputs"]
        assert result.settings == _PIPELINE_PROPERTIES["settings"]
    else:
        assert isinstance(result, CommandJob)
    assert result.job_type == kind
    assert result.name == kind.lower()
    assert result.id == f"/jobs/{kind.lower()}"


def _assert_requests(requests: list[HttpRequest], kind: str, expected: dict[str, Any]) -> None:
    assert len(requests) == 3
    assert [request.method for request in requests] == ["PUT", "GET", "GET"]
    for request in requests:
        assert request.headers["Foundry-Features"] == "Jobs=V1Preview"
        assert parse_qs(urlparse(request.url).query)["api-version"] == ["2026-01-15-preview"]
    assert urlparse(requests[0].url).path.endswith(f"/jobs/{kind.lower()}")
    assert json.loads(requests[0].body) == {"properties": expected}
    assert JobType.PIPELINE == "Pipeline"


@pytest.mark.parametrize("kind", ["Command", "Pipeline"])
def test_jobs_sync_create_get_and_list(kind: str) -> None:
    job, expected = _job(kind)
    transport = _Transport([_response(kind), _response(kind), {"value": [_response("Command"), _response("Pipeline")]}])

    with AIProjectClient(endpoint=_ENDPOINT, credential=_Credential(), transport=transport) as client:  # type: ignore[arg-type]
        _assert_job(client.beta.jobs.create_or_update(kind.lower(), job), kind)
        _assert_job(client.beta.jobs.get(kind.lower()), kind)
        listed = list(client.beta.jobs.list())
        assert len(listed) == 2
        _assert_job(listed[0], "Command")
        _assert_job(listed[1], "Pipeline")

    _assert_requests(transport.requests, kind, expected)


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["Command", "Pipeline"])
async def test_jobs_async_create_get_and_list(kind: str) -> None:
    job, expected = _job(kind)
    transport = _AsyncTransport(
        [_response(kind), _response(kind), {"value": [_response("Command"), _response("Pipeline")]}]
    )

    async with AsyncAIProjectClient(
        endpoint=_ENDPOINT, credential=_AsyncCredential(), transport=transport  # type: ignore[arg-type]
    ) as client:
        _assert_job(await client.beta.jobs.create_or_update(kind.lower(), job), kind)
        _assert_job(await client.beta.jobs.get(kind.lower()), kind)
        listed = [item async for item in client.beta.jobs.list()]
        assert len(listed) == 2
        _assert_job(listed[0], "Command")
        _assert_job(listed[1], "Pipeline")

    _assert_requests(transport.requests, kind, expected)
