# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline wire and response tests for Command and Pipeline jobs."""

import json
import runpy
from pathlib import Path
from typing import Any, Union
from urllib.parse import parse_qs, urlparse

import pytest
from azure.core.credentials import AccessToken
from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline.transport import (
    AsyncHttpResponse,
    AsyncHttpTransport,
    HttpRequest,
    HttpResponse,
    HttpTransport,
)

from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
from azure.ai.projects.models import (
    AssetTypes,
    CommandJob,
    DatasetVersion,
    Input,
    JobResourceConfiguration,
    JobType,
    PipelineJob,
)

_ENDPOINT = "https://fake-account.services.ai.azure.com/api/projects/fake-project"
_COMPUTE = "/subscriptions/test/resourceGroups/test/providers/Microsoft.CognitiveServices/accounts/test/computes/cpu"
_TWO_CODE_BUILDER = runpy.run_path(
    str(Path(__file__).resolve().parents[2] / "samples" / "jobs" / "sample_pipeline_two_code.py")
)["build_job"]
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
_INLINE_PIPELINE_PROPERTIES = {
    "jobType": "Pipeline",
    "computeId": _COMPUTE,
    "settings": {"default_compute": _COMPUTE, "force_rerun": True},
    "inputs": {"name": {"jobInputType": "literal", "value": "world"}},
    "outputs": {},
    "jobs": {
        "hello": {
            "type": "command",
            "identity": {"type": "managed", "msi_resource_id": "/subscriptions/test/identities/hello"},
            "component": {
                "name": "hello",
                "version": "1",
                "type": "command",
                "command": "echo hello ${{inputs.name}}",
                "environment": {"image": "example.azurecr.io/train:latest"},
                "inputs": {"name": {"type": "string"}},
                "outputs": {},
            },
            "resources": {
                "instance_count": 1,
                "instance_type": "Standard_D4_v3",
                "properties": {"AISuperComputer": {"SLATier": "Premium"}},
            },
            "inputs": {"name": {"job_input_type": "literal", "value": "${{parent.inputs.name}}"}},
            "outputs": {},
        }
    },
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


def _inline_pipeline() -> tuple[PipelineJob, CommandJob]:
    command = CommandJob(
        command="echo hello ${{inputs.name}}",
        environment_image_reference="example.azurecr.io/train:latest",
        compute=_COMPUTE,
        inputs={"name": Input(type=AssetTypes.LITERAL, value="${{parent.inputs.name}}")},
        user_assigned_identity_id="/subscriptions/test/identities/hello",
        resources=JobResourceConfiguration(
            {
                "instanceCount": 1,
                "instanceType": "Standard_D4_v3",
                "properties": {"AISuperComputer": {"SLATier": "Premium"}},
            }
        ),
    )
    pipeline = PipelineJob(
        compute_id=_COMPUTE,
        settings={"default_compute": _COMPUTE, "force_rerun": True},
        inputs={"name": Input(type=AssetTypes.LITERAL, value="world")},
        outputs={},
        jobs={"hello": command},
    )
    return pipeline, command


def _assert_inline_request(request: HttpRequest) -> None:
    assert request.method == "PUT"
    assert request.headers["Foundry-Features"] == "Jobs=V1Preview"
    assert json.loads(request.body) == {"properties": _INLINE_PIPELINE_PROPERTIES}


def _two_code_job(tmp_path: Path) -> tuple[PipelineJob, dict[str, Path]]:
    code_dirs = {node: tmp_path / node for node in ("produce", "consume")}
    for node, code_dir in code_dirs.items():
        code_dir.mkdir()
        (code_dir / f"{node}.py").write_text(f"print({node!r})", encoding="utf-8")
    job = _TWO_CODE_BUILDER(
        compute_id=_COMPUTE,
        image="example.azurecr.io/train:latest",
        node_uai_id="/subscriptions/test/identities/hello",
        instance_type="Singularity.D4_v3",
        producer_code_dir=str(code_dirs["produce"]),
        consumer_code_dir=str(code_dirs["consume"]),
    )
    return job, code_dirs


def _code_uri(name: str, version: str) -> str:
    return f"azureai://accounts/fake-account/projects/fake-project/data/{name}/versions/{version}"


def _uploaded_code(name: str, version: str) -> DatasetVersion:
    return DatasetVersion(
        {
            "id": _code_uri(name, version),
            "name": name,
            "version": version,
            "type": "uri_folder",
            "dataUri": "azureml://datastores/test/paths/code/",
        }
    )


def _assert_two_code_request(request: HttpRequest, code_uris: dict[str, str]) -> None:
    assert request.method == "PUT"
    assert request.headers["Foundry-Features"] == "Jobs=V1Preview"
    assert request.headers["x-ms-foundry-job-route"] == "execution"
    assert parse_qs(urlparse(request.url).query)["api-version"] == ["2026-01-15-preview"]
    resources = {
        "instance_count": 1,
        "instance_type": "Singularity.D4_v3",
        "properties": {"AISuperComputer": {"SLATier": "Premium"}},
    }
    identity = {"type": "managed", "msi_resource_id": "/subscriptions/test/identities/hello"}
    expected = {
        "properties": {
            "jobType": "Pipeline",
            "displayName": "Two-step code SDK test",
            "computeId": _COMPUTE,
            "settings": {"default_compute": _COMPUTE, "force_rerun": True},
            "inputs": {},
            "outputs": {},
            "jobs": {
                "produce": {
                    "type": "command",
                    "component": {
                        "name": "produce",
                        "version": "1",
                        "type": "command",
                        "command": "python produce.py ${{outputs.message}}",
                        "environment": {"image": "example.azurecr.io/train:latest"},
                        "inputs": {},
                        "outputs": {"message": {"type": "uri_file"}},
                        "code": code_uris["produce"],
                    },
                    "identity": identity,
                    "resources": resources,
                    "inputs": {},
                    "outputs": {"message": {"job_output_type": "uri_file", "mode": "ReadWriteMount"}},
                },
                "consume": {
                    "type": "command",
                    "component": {
                        "name": "consume",
                        "version": "1",
                        "type": "command",
                        "command": "python consume.py ${{inputs.message}}",
                        "environment": {"image": "example.azurecr.io/train:latest"},
                        "inputs": {"message": {"type": "uri_file"}},
                        "outputs": {},
                        "code": code_uris["consume"],
                    },
                    "inputs": {
                        "message": {
                            "job_input_type": "literal",
                            "value": "${{parent.jobs.produce.outputs.message}}",
                        }
                    },
                    "outputs": {},
                    "identity": identity,
                    "resources": resources,
                },
            },
        }
    }
    assert json.loads(request.body) == expected


def test_jobs_sync_create_from_command_node() -> None:
    pipeline, command = _inline_pipeline()
    transport = _Transport([_response("Pipeline")])

    with AIProjectClient(endpoint=_ENDPOINT, credential=_Credential(), transport=transport) as client:  # type: ignore[arg-type]
        _assert_job(client.beta.jobs.create_or_update("pipeline", pipeline), "Pipeline")

    assert len(transport.requests) == 1
    _assert_inline_request(transport.requests[0])
    assert command.inputs is not None
    assert command.inputs["name"].value == "${{parent.inputs.name}}"
    assert command.resources is not None
    assert command.resources.instance_type == "Standard_D4_v3"


@pytest.mark.asyncio
async def test_jobs_async_create_from_command_node() -> None:
    pipeline, _ = _inline_pipeline()
    transport = _AsyncTransport([_response("Pipeline")])

    async with AsyncAIProjectClient(
        endpoint=_ENDPOINT, credential=_AsyncCredential(), transport=transport  # type: ignore[arg-type]
    ) as client:
        _assert_job(await client.beta.jobs.create_or_update("pipeline", pipeline), "Pipeline")

    assert len(transport.requests) == 1
    _assert_inline_request(transport.requests[0])


def test_jobs_sync_create_from_mapping_with_command_node() -> None:
    _, command = _inline_pipeline()
    pipeline = PipelineJob(
        {
            "computeId": _COMPUTE,
            "settings": {"default_compute": _COMPUTE, "force_rerun": True},
            "inputs": {"name": Input(type=AssetTypes.LITERAL, value="world")},
            "outputs": {},
            "jobs": {"hello": command},
        }
    )

    transport = _Transport([_response("Pipeline")])
    with AIProjectClient(endpoint=_ENDPOINT, credential=_Credential(), transport=transport) as client:  # type: ignore[arg-type]
        _assert_job(client.beta.jobs.create_or_update("pipeline", pipeline), "Pipeline")

    assert len(transport.requests) == 1
    _assert_inline_request(transport.requests[0])


def test_pipeline_composes_commands_and_preserves_raw_graph_nodes() -> None:
    first, _ = _inline_pipeline()
    raw_node = {"type": "command", "component": {"name": "raw", "version": "1"}}
    pipeline = PipelineJob(
        compute_id=_COMPUTE,
        jobs={
            "hello": CommandJob(
                command="echo hello", environment_image_reference="example.azurecr.io/train:latest", compute=_COMPUTE
            ),
            "second": CommandJob(
                command="echo again", environment_image_reference="example.azurecr.io/train:latest", compute=_COMPUTE
            ),
            "raw": raw_node,
        },
    )

    assert pipeline.jobs is not None
    assert pipeline.jobs["hello"]["component"]["command"] == "echo hello"
    assert pipeline.jobs["second"]["component"]["command"] == "echo again"
    assert pipeline.jobs["raw"] == raw_node
    assert first.jobs is not None
    assert first.jobs["hello"] == _INLINE_PIPELINE_PROPERTIES["jobs"]["hello"]


def test_pipeline_uploads_both_local_code_folders(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline, code_dirs = _two_code_job(tmp_path)
    transport = _Transport([_response("Pipeline")])
    uploads: list[tuple[str, str, str]] = []

    def missing_asset(*, name: str, version: str) -> DatasetVersion:
        raise ResourceNotFoundError(f"Dataset {name}:{version} not found")

    def upload_folder(*, name: str, version: str, folder: str, **kwargs: Any) -> DatasetVersion:
        uploads.append((name, version, folder))
        return _uploaded_code(name, version)

    with AIProjectClient(endpoint=_ENDPOINT, credential=_Credential(), transport=transport) as client:  # type: ignore[arg-type]
        monkeypatch.setattr(client.beta.jobs._datasets, "get", missing_asset)
        monkeypatch.setattr(client.beta.jobs._datasets, "upload_folder", upload_folder)
        _assert_job(
            client.beta.jobs.create_or_update(
                "two-code",
                pipeline,
                headers={"x-ms-foundry-job-route": "execution"},
            ),
            "Pipeline",
        )

    assert [(name, folder) for name, _, folder in uploads] == [
        ("two-code-produce-code", str(code_dirs["produce"])),
        ("two-code-consume-code", str(code_dirs["consume"])),
    ]
    assert uploads[0][1] != uploads[1][1]
    assert len(transport.requests) == 1
    _assert_two_code_request(
        transport.requests[0],
        {
            name.removeprefix("two-code-").removesuffix("-code"): _code_uri(name, version)
            for name, version, _ in uploads
        },
    )


@pytest.mark.asyncio
async def test_pipeline_uploads_both_local_code_folders_async(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline, code_dirs = _two_code_job(tmp_path)
    transport = _AsyncTransport([_response("Pipeline")])
    uploads: list[tuple[str, str, str]] = []

    async def missing_asset(*, name: str, version: str) -> DatasetVersion:
        raise ResourceNotFoundError(f"Dataset {name}:{version} not found")

    async def upload_folder(*, name: str, version: str, folder: str, **kwargs: Any) -> DatasetVersion:
        uploads.append((name, version, folder))
        return _uploaded_code(name, version)

    async with AsyncAIProjectClient(
        endpoint=_ENDPOINT, credential=_AsyncCredential(), transport=transport  # type: ignore[arg-type]
    ) as client:
        monkeypatch.setattr(client.beta.jobs._datasets, "get", missing_asset)
        monkeypatch.setattr(client.beta.jobs._datasets, "upload_folder", upload_folder)
        _assert_job(
            await client.beta.jobs.create_or_update(
                "two-code",
                pipeline,
                headers={"x-ms-foundry-job-route": "execution"},
            ),
            "Pipeline",
        )

    assert [(name, folder) for name, _, folder in uploads] == [
        ("two-code-produce-code", str(code_dirs["produce"])),
        ("two-code-consume-code", str(code_dirs["consume"])),
    ]
    assert len(transport.requests) == 1
    _assert_two_code_request(
        transport.requests[0],
        {
            name.removeprefix("two-code-").removesuffix("-code"): _code_uri(name, version)
            for name, version, _ in uploads
        },
    )


def test_pipeline_does_not_submit_when_code_upload_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline, _ = _two_code_job(tmp_path)
    transport = _Transport([])

    def missing_asset(*, name: str, version: str) -> DatasetVersion:
        raise ResourceNotFoundError(f"Dataset {name}:{version} not found")

    def upload_folder(*, name: str, version: str, folder: str, **kwargs: Any) -> DatasetVersion:
        raise RuntimeError("upload failed")

    with AIProjectClient(endpoint=_ENDPOINT, credential=_Credential(), transport=transport) as client:  # type: ignore[arg-type]
        monkeypatch.setattr(client.beta.jobs._datasets, "get", missing_asset)
        monkeypatch.setattr(client.beta.jobs._datasets, "upload_folder", upload_folder)
        with pytest.raises(RuntimeError, match="upload failed"):
            client.beta.jobs.create_or_update("two-code", pipeline)

    assert transport.requests == []


@pytest.mark.parametrize(
    ("extra", "message"),
    [
        ({"priority": "High"}, "priority"),
        ({"inputs": {"data": Input(type=AssetTypes.URI_FILE, path="azureai:data:1")}}, "input 'data'"),
        (
            {"outputs": {"message": {"job_output_type": "uri_file", "mode": "ReadWriteMount"}}},
            "output 'message'",
        ),
        ({"compute": "/subscriptions/test/computes/other"}, "default compute"),
        ({"resources": JobResourceConfiguration({"shmSize": "1g"})}, "shmSize"),
    ],
)
def test_pipeline_rejects_unmapped_command_fields(extra: dict[str, Any], message: str) -> None:
    fields: dict[str, Any] = {
        "command": "echo hello",
        "environment_image_reference": "example.azurecr.io/train:latest",
        "compute": _COMPUTE,
    }
    fields.update(extra)
    with pytest.raises(ValueError, match=message):
        PipelineJob(compute_id=_COMPUTE, jobs={"hello": CommandJob(**fields)})


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
