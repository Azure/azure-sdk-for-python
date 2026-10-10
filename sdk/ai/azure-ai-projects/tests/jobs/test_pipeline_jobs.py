# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline wire and response tests for Command and Pipeline jobs."""

import importlib
import json
import os
import re
import runpy
import subprocess
import sys
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

from azure.ai.projects import AIProjectClient, dsl
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
from azure.ai.projects.models import (
    AssetTypes,
    CommandJob,
    DatasetVersion,
    Input,
    InputOutputModes,
    JobResourceConfiguration,
    JobType,
    Output,
    PipelineJob,
)
from azure.ai.projects.operations._job_helper import _content_hash
from azure.ai.projects._component_source import _RUNNER_NAME, _stage_component_source

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


def test_pipeline_converts_value_bound_uri_folder_input() -> None:
    producer = CommandJob(
        command="python produce.py ${{outputs.bundle}}",
        environment_image_reference="example.azurecr.io/train:latest",
        compute=_COMPUTE,
        outputs={
            "bundle": Output(
                type=AssetTypes.URI_FOLDER,
                asset_name="bundle",
                mode=InputOutputModes.READ_WRITE_MOUNT,
            )
        },
    )
    consumer = CommandJob(
        command="python consume.py ${{inputs.bundle}}",
        environment_image_reference="example.azurecr.io/train:latest",
        compute=_COMPUTE,
        inputs={
            "bundle": Input(
                type=AssetTypes.URI_FOLDER,
                value="${{parent.jobs.producer.outputs.bundle}}",
            )
        },
    )

    pipeline = PipelineJob(
        compute_id=_COMPUTE,
        settings={"default_compute": _COMPUTE},
        jobs={"producer": producer, "consumer": consumer},
    )
    graph = pipeline.as_dict(exclude_readonly=True)["jobs"]

    assert graph["producer"]["component"]["outputs"]["bundle"] == {
        "type": "uri_folder"
    }
    assert graph["producer"]["outputs"]["bundle"] == {
        "job_output_type": "uri_folder",
        "mode": "ReadWriteMount",
    }
    assert graph["consumer"]["component"]["inputs"]["bundle"] == {
        "type": "uri_folder"
    }
    assert graph["consumer"]["inputs"]["bundle"] == {
        "job_input_type": "literal",
        "value": "${{parent.jobs.producer.outputs.bundle}}",
    }

    transport = _Transport([_response("Pipeline")])
    with AIProjectClient(
        endpoint=_ENDPOINT,
        credential=_Credential(),
        transport=transport,  # type: ignore[arg-type]
    ) as client:
        _assert_job(
            client.beta.jobs.create_or_update("folder-handoff", pipeline),
            "Pipeline",
        )

    submitted_jobs = json.loads(transport.requests[0].body)[
        "properties"
    ]["jobs"]
    assert submitted_jobs["consumer"]["component"]["inputs"][
        "bundle"
    ] == {"type": "uri_folder"}
    assert submitted_jobs["consumer"]["inputs"]["bundle"] == {
        "job_input_type": "literal",
        "value": "${{parent.jobs.producer.outputs.bundle}}",
    }


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
        (
            {
                "inputs": {
                    "folder": Input(
                        type=AssetTypes.URI_FOLDER,
                        value="${{parent.inputs.folder}}",
                        mode=InputOutputModes.READ_ONLY_MOUNT,
                    )
                }
            },
            "input 'folder'",
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


def _dsl_job(monkeypatch: pytest.MonkeyPatch) -> PipelineJob:
    monkeypatch.setenv("JOB_COMPUTE_ID", _COMPUTE)
    monkeypatch.setenv("JOB_ENVIRONMENT_IMAGE", "example.azurecr.io/train:latest")
    monkeypatch.setenv("JOB_NODE_UAI_RESOURCE_ID", "/subscriptions/test/identities/hello")
    monkeypatch.setenv("JOB_INSTANCE_TYPE", "Singularity.D4_v3")
    sample = runpy.run_path(str(Path(__file__).resolve().parents[2] / "samples" / "jobs" / "sample_pipeline_dsl.py"))
    return sample["workflow"](text="hello")


def _source_dsl_job(monkeypatch: pytest.MonkeyPatch) -> PipelineJob:
    monkeypatch.setenv("JOB_COMPUTE_ID", _COMPUTE)
    monkeypatch.setenv("JOB_ENVIRONMENT_IMAGE", "example.azurecr.io/train:latest")
    monkeypatch.setenv("JOB_NODE_UAI_RESOURCE_ID", "/subscriptions/test/identities/hello")
    monkeypatch.setenv("JOB_INSTANCE_TYPE", "Singularity.D4_v3")
    sample = Path(__file__).resolve().parents[2] / "samples" / "jobs" / "pipeline_source"
    monkeypatch.syspath_prepend(str(sample))
    workflow = runpy.run_path(str(sample / "sample_pipeline_source.py"))["workflow"]
    return workflow(text=" world ")


def _dsl_code_paths(job: PipelineJob) -> dict[str, Path]:
    assert job.jobs is not None
    return {name: Path(node["component"]["code"]) for name, node in job.jobs.items()}


def _assert_dsl_request(request: HttpRequest, uploaded: dict[str, str]) -> None:
    assert request.method == "PUT"
    assert request.headers["Foundry-Features"] == "Jobs=V1Preview"
    assert request.headers["x-ms-foundry-job-route"] == "execution"
    assert parse_qs(urlparse(request.url).query)["api-version"] == ["2026-01-15-preview"]
    assert re.fullmatch(r"/api/projects/fake-project/jobs/pipeline-[0-9a-f]{32}", urlparse(request.url).path)
    resources = {
        "instance_count": 1,
        "instance_type": "Singularity.D4_v3",
        "properties": {"AISuperComputer": {"SLATier": "Premium"}},
    }
    identity = {"type": "managed", "msi_resource_id": "/subscriptions/test/identities/hello"}
    assert json.loads(request.body) == {
        "properties": {
            "jobType": "Pipeline",
            "displayName": "workflow",
            "experimentName": "pipeline_samples",
            "computeId": _COMPUTE,
            "settings": {"default_compute": _COMPUTE, "force_rerun": True},
            "inputs": {"text": {"jobInputType": "literal", "value": "hello"}},
            "outputs": {"receipt": {"jobOutputType": "uri_file", "mode": "ReadWriteMount"}},
            "jobs": {
                "produce": {
                    "type": "command",
                    "component": {
                        "name": "produce",
                        "version": "1",
                        "type": "command",
                        "command": 'python component.py "${{inputs.text}}" "${{outputs.message}}"',
                        "environment": {"image": "example.azurecr.io/train:latest"},
                        "inputs": {"text": {"type": "string"}},
                        "outputs": {"message": {"type": "uri_file"}},
                        "code": uploaded["produce"],
                    },
                    "identity": identity,
                    "resources": resources,
                    "inputs": {"text": {"job_input_type": "literal", "value": "${{parent.inputs.text}}"}},
                    "outputs": {"message": {"job_output_type": "uri_file", "mode": "ReadWriteMount"}},
                },
                "consume": {
                    "type": "command",
                    "component": {
                        "name": "consume",
                        "version": "1",
                        "type": "command",
                        "command": 'python component.py "${{inputs.message}}" "${{outputs.receipt}}"',
                        "environment": {"image": "example.azurecr.io/train:latest"},
                        "inputs": {"message": {"type": "uri_file"}},
                        "outputs": {"receipt": {"type": "uri_file"}},
                        "code": uploaded["consume"],
                    },
                    "identity": identity,
                    "resources": resources,
                    "inputs": {
                        "message": {
                            "job_input_type": "literal",
                            "value": "${{parent.jobs.produce.outputs.message}}",
                        }
                    },
                    "outputs": {
                        "receipt": {
                            "job_output_type": "uri_file",
                            "mode": "ReadWriteMount",
                            "path": "${{parent.outputs.receipt}}",
                        }
                    },
                },
            },
        }
    }


def test_dsl_component_bodies_execute_with_module_level_imports(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    job = _dsl_job(monkeypatch)
    code = _dsl_code_paths(job)
    try:
        assert code["produce"] != code["consume"]
        assert all(path.is_dir() for path in code.values())
        for path in code.values():
            script = (path / "component.py").read_text(encoding="utf-8")
            assert "from pathlib import Path" in script
            assert "azure.ai.projects" not in script

        message = tmp_path / "message.txt"
        receipt = tmp_path / "receipt.txt"
        subprocess.run(
            [sys.executable, str(code["produce"] / "component.py"), "hello", str(message)],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            [sys.executable, str(code["consume"] / "component.py"), str(message), str(receipt)],
            check=True,
            capture_output=True,
            text=True,
        )
        assert receipt.read_text(encoding="utf-8") == "HELLO"
    finally:
        for directory in job._component_code_dirs:
            directory.cleanup()


def test_dsl_sync_uploads_code_and_cleans_after_submission(monkeypatch: pytest.MonkeyPatch) -> None:
    job = _dsl_job(monkeypatch)
    paths = _dsl_code_paths(job)
    transport = _Transport([_response("Pipeline")])
    uploads: list[tuple[str, str]] = []

    def missing_asset(*, name: str, version: str) -> DatasetVersion:
        raise ResourceNotFoundError(f"Dataset {name}:{version} not found")

    def upload_folder(*, name: str, version: str, folder: str, **kwargs: Any) -> DatasetVersion:
        assert Path(folder).is_dir()
        uploads.append((name, folder))
        return _uploaded_code(name, version)

    with AIProjectClient(endpoint=_ENDPOINT, credential=_Credential(), transport=transport) as client:  # type: ignore[arg-type]
        monkeypatch.setattr(client.beta.jobs._datasets, "get", missing_asset)
        monkeypatch.setattr(client.beta.jobs._datasets, "upload_folder", upload_folder)
        created = client.beta.jobs.create_or_update(
            job, experiment_name="pipeline_samples", headers={"x-ms-foundry-job-route": "execution"}
        )

    assert isinstance(created, PipelineJob)
    assert job.experiment_name == "pipeline_samples"
    assert len(uploads) == 2
    assert [name.rsplit("-", 2)[-2] for name, _ in uploads] == ["produce", "consume"]
    assert [folder for _, folder in uploads] == [str(paths["produce"]), str(paths["consume"])]
    assert all(not path.exists() for path in paths.values())
    assert len(transport.requests) == 1
    code_uris = {name.rsplit("-", 2)[-2]: job.jobs[name.rsplit("-", 2)[-2]]["component"]["code"] for name, _ in uploads}
    _assert_dsl_request(transport.requests[0], code_uris)


@pytest.mark.asyncio
async def test_dsl_async_uploads_code_and_cleans_after_submission(monkeypatch: pytest.MonkeyPatch) -> None:
    job = _dsl_job(monkeypatch)
    paths = _dsl_code_paths(job)
    transport = _AsyncTransport([_response("Pipeline")])
    uploads: list[tuple[str, str]] = []

    async def missing_asset(*, name: str, version: str) -> DatasetVersion:
        raise ResourceNotFoundError(f"Dataset {name}:{version} not found")

    async def upload_folder(*, name: str, version: str, folder: str, **kwargs: Any) -> DatasetVersion:
        assert Path(folder).is_dir()
        uploads.append((name, folder))
        return _uploaded_code(name, version)

    async with AsyncAIProjectClient(
        endpoint=_ENDPOINT, credential=_AsyncCredential(), transport=transport  # type: ignore[arg-type]
    ) as client:
        monkeypatch.setattr(client.beta.jobs._datasets, "get", missing_asset)
        monkeypatch.setattr(client.beta.jobs._datasets, "upload_folder", upload_folder)
        created = await client.beta.jobs.create_or_update(
            job, experiment_name="pipeline_samples", headers={"x-ms-foundry-job-route": "execution"}
        )

    assert isinstance(created, PipelineJob)
    assert len(uploads) == 2
    assert [folder for _, folder in uploads] == [str(paths["produce"]), str(paths["consume"])]
    assert all(not path.exists() for path in paths.values())
    assert len(transport.requests) == 1
    assert json.loads(transport.requests[0].body)["properties"]["experimentName"] == "pipeline_samples"


def test_dsl_upload_failure_cleans_code_without_put(monkeypatch: pytest.MonkeyPatch) -> None:
    job = _dsl_job(monkeypatch)
    paths = _dsl_code_paths(job)
    transport = _Transport([])
    uploads: list[str] = []

    def missing_asset(*, name: str, version: str) -> DatasetVersion:
        raise ResourceNotFoundError(f"Dataset {name}:{version} not found")

    def upload_folder(*, name: str, version: str, folder: str, **kwargs: Any) -> DatasetVersion:
        uploads.append(folder)
        if len(uploads) == 2:
            raise RuntimeError("upload failed")
        return _uploaded_code(name, version)

    with AIProjectClient(endpoint=_ENDPOINT, credential=_Credential(), transport=transport) as client:  # type: ignore[arg-type]
        monkeypatch.setattr(client.beta.jobs._datasets, "get", missing_asset)
        monkeypatch.setattr(client.beta.jobs._datasets, "upload_folder", upload_folder)
        with pytest.raises(RuntimeError, match="upload failed"):
            client.beta.jobs.create_or_update(job)

    assert len(uploads) == 2
    assert transport.requests == []
    assert all(not path.exists() for path in paths.values())


@pytest.mark.asyncio
async def test_dsl_async_upload_failure_cleans_code_without_put(monkeypatch: pytest.MonkeyPatch) -> None:
    job = _dsl_job(monkeypatch)
    paths = _dsl_code_paths(job)
    transport = _AsyncTransport([])
    uploads: list[str] = []

    async def missing_asset(*, name: str, version: str) -> DatasetVersion:
        raise ResourceNotFoundError(f"Dataset {name}:{version} not found")

    async def upload_folder(*, name: str, version: str, folder: str, **kwargs: Any) -> DatasetVersion:
        uploads.append(folder)
        if len(uploads) == 2:
            raise RuntimeError("upload failed")
        return _uploaded_code(name, version)

    async with AsyncAIProjectClient(
        endpoint=_ENDPOINT, credential=_AsyncCredential(), transport=transport  # type: ignore[arg-type]
    ) as client:
        monkeypatch.setattr(client.beta.jobs._datasets, "get", missing_asset)
        monkeypatch.setattr(client.beta.jobs._datasets, "upload_folder", upload_folder)
        with pytest.raises(RuntimeError, match="upload failed"):
            await client.beta.jobs.create_or_update(job)

    assert len(uploads) == 2
    assert transport.requests == []
    assert all(not path.exists() for path in paths.values())


def test_dsl_repeated_component_calls_get_distinct_nodes() -> None:
    @dsl.component
    def write(text: str, result: dsl.Output(type="uri_file", mode="Upload")) -> None:
        from pathlib import Path

        Path(result).write_text(text, encoding="utf-8")

    @dsl.pipeline(
        compute_id=_COMPUTE,
        environment_image_reference="example.azurecr.io/train:latest",
        user_assigned_identity_id="/subscriptions/test/identities/hello",
        instance_type="Singularity.D4_v3",
    )
    def workflow(text: str):
        first = write(text=text)
        second = write(text=text)
        return {"first": first.outputs.result, "second": second.outputs.result}

    job = workflow(text="hello")
    try:
        assert list(job.jobs) == ["write", "write_2"]
        assert job.jobs["write"]["outputs"]["result"]["path"] == "${{parent.outputs.first}}"
        assert job.jobs["write_2"]["outputs"]["result"]["path"] == "${{parent.outputs.second}}"
        assert job.jobs["write"]["outputs"]["result"]["mode"] == "Upload"
        assert _dsl_code_paths(job)["write"] != _dsl_code_paths(job)["write_2"]
    finally:
        for directory in job._component_code_dirs:
            directory.cleanup()


def test_dsl_typed_primitives_and_remote_file_input(tmp_path: Path) -> None:
    assert dsl.command_component is dsl.component

    @dsl.component
    def transform(
        count: int,
        scale: float,
        enabled: bool,
        source: dsl.Input(type="uri_file"),
        result: dsl.Output(type="uri_file"),
    ) -> None:
        from pathlib import Path

        if enabled:
            Path(result).write_text(Path(source).read_text(encoding="utf-8") * count + str(scale), encoding="utf-8")

    @dsl.pipeline(
        compute_id=_COMPUTE,
        environment_image_reference="example.azurecr.io/train:latest",
        user_assigned_identity_id="/subscriptions/test/identities/hello",
        instance_type="Singularity.D4_v3",
    )
    def workflow(count: int, scale: float, enabled: bool, source: dsl.Input(type="uri_file")):
        node = transform(count=count, scale=scale, enabled=enabled, source=source)
        return {"result": node.outputs.result}

    job = workflow(
        count=3,
        scale=1.5,
        enabled=True,
        source=dsl.Input(type="uri_file", path="azureml://datastores/test/paths/input.txt"),
    )
    try:
        assert job.inputs["count"] == {"jobInputType": "literal", "value": "3"}
        assert job.inputs["scale"] == {"jobInputType": "literal", "value": "1.5"}
        assert job.inputs["enabled"] == {"jobInputType": "literal", "value": "True"}
        assert job.inputs["source"] == {
            "jobInputType": "uri_file",
            "uri": "azureml://datastores/test/paths/input.txt",
        }
        node = job.jobs["transform"]
        assert node["component"]["inputs"] == {
            "count": {"type": "integer"},
            "scale": {"type": "number"},
            "enabled": {"type": "boolean"},
            "source": {"type": "uri_file"},
        }
        assert node["inputs"]["source"]["value"] == "${{parent.inputs.source}}"

        source = tmp_path / "source.txt"
        output = tmp_path / "output.txt"
        source.write_text("go", encoding="utf-8")
        subprocess.run(
            [
                sys.executable,
                str(_dsl_code_paths(job)["transform"] / "component.py"),
                "3",
                "1.5",
                "True",
                str(source),
                str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        assert output.read_text(encoding="utf-8") == "gogogo1.5"
    finally:
        for directory in job._component_code_dirs:
            directory.cleanup()


def test_dsl_rejects_unsupported_module_globals_and_outside_calls() -> None:
    @dsl.component
    def write_with_global(result: dsl.Output(type="uri_file")) -> None:
        Path(result).write_text(_COMPUTE, encoding="utf-8")

    @dsl.pipeline(
        compute_id=_COMPUTE,
        environment_image_reference="example.azurecr.io/train:latest",
        user_assigned_identity_id="/subscriptions/test/identities/hello",
        instance_type="Singularity.D4_v3",
    )
    def workflow() -> None:
        write_with_global()

    with pytest.raises(RuntimeError, match="inside a @pipeline"):
        write_with_global()
    with pytest.raises(ValueError, match="unsupported module globals"):
        workflow()


def test_dsl_source_components_run_with_helpers_imports_and_resources(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    job = _source_dsl_job(monkeypatch)
    paths = _dsl_code_paths(job)
    snapshot = paths["produce"]
    try:
        assert snapshot == paths["consume"]
        assert len(job._component_code_dirs) == 1
        assert (snapshot / _RUNNER_NAME).is_file()
        assert (snapshot / "steps" / "source_pipeline_components.py").is_file()
        assert (snapshot / "steps" / "helpers.py").is_file()
        assert (snapshot / "steps" / "greeting.txt").read_text(encoding="utf-8").strip() == "hello"
        assert job.jobs["produce"]["component"]["command"] == (
            f"python {_RUNNER_NAME} steps.source_pipeline_components produce text:str,message:str "
            '"${{inputs.text}}" "${{outputs.message}}"'
        )
        assert job.jobs["consume"]["inputs"]["message"]["value"] == "${{parent.jobs.produce.outputs.message}}"

        source_root = Path(__file__).resolve().parents[2]
        environment = os.environ.copy()
        environment["PYTHONPATH"] = os.pathsep.join([str(source_root), environment.get("PYTHONPATH", "")])
        message = tmp_path / "message.txt"
        receipt = tmp_path / "receipt.txt"
        subprocess.run(
            [
                sys.executable,
                str(snapshot / _RUNNER_NAME),
                "steps.source_pipeline_components",
                "produce",
                "text:str,message:str",
                " world ",
                str(message),
            ],
            cwd=tmp_path,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            [
                sys.executable,
                str(snapshot / _RUNNER_NAME),
                "steps.source_pipeline_components",
                "consume",
                "message:str,receipt:str",
                str(message),
                str(receipt),
            ],
            cwd=tmp_path,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        assert message.read_text(encoding="utf-8") == "hello world"
        assert receipt.read_text(encoding="utf-8") == "HELLO WORLD"
    finally:
        for directory in job._component_code_dirs:
            directory.cleanup()


def test_dsl_source_sync_uploads_shared_snapshot_once(monkeypatch: pytest.MonkeyPatch) -> None:
    job = _source_dsl_job(monkeypatch)
    snapshot = _dsl_code_paths(job)["produce"]
    transport = _Transport([_response("Pipeline")])
    uploads: list[tuple[str, str]] = []

    def missing_asset(*, name: str, version: str) -> DatasetVersion:
        raise ResourceNotFoundError(f"Dataset {name}:{version} not found")

    def upload_folder(*, name: str, version: str, folder: str, **kwargs: Any) -> DatasetVersion:
        assert (Path(folder) / "steps" / "helpers.py").is_file()
        uploads.append((name, folder))
        return _uploaded_code(name, version)

    with AIProjectClient(endpoint=_ENDPOINT, credential=_Credential(), transport=transport) as client:  # type: ignore[arg-type]
        monkeypatch.setattr(client.beta.jobs._datasets, "get", missing_asset)
        monkeypatch.setattr(client.beta.jobs._datasets, "upload_folder", upload_folder)
        client.beta.jobs.create_or_update(
            job, experiment_name="pipeline_samples", headers={"x-ms-foundry-job-route": "execution"}
        )

    assert len(uploads) == 1
    assert uploads[0][1] == str(snapshot)
    assert not snapshot.exists()
    assert len(transport.requests) == 1
    properties = json.loads(transport.requests[0].body)["properties"]
    assert properties["jobs"]["produce"]["component"]["code"] == properties["jobs"]["consume"]["component"]["code"]
    assert properties["jobs"]["produce"]["component"]["code"] == job.jobs["produce"]["component"]["code"]
    assert properties["experimentName"] == "pipeline_samples"


@pytest.mark.asyncio
async def test_dsl_source_async_uploads_shared_snapshot_once(monkeypatch: pytest.MonkeyPatch) -> None:
    job = _source_dsl_job(monkeypatch)
    snapshot = _dsl_code_paths(job)["produce"]
    transport = _AsyncTransport([_response("Pipeline")])
    uploads: list[str] = []

    async def missing_asset(*, name: str, version: str) -> DatasetVersion:
        raise ResourceNotFoundError(f"Dataset {name}:{version} not found")

    async def upload_folder(*, name: str, version: str, folder: str, **kwargs: Any) -> DatasetVersion:
        uploads.append(folder)
        return _uploaded_code(name, version)

    async with AsyncAIProjectClient(
        endpoint=_ENDPOINT, credential=_AsyncCredential(), transport=transport  # type: ignore[arg-type]
    ) as client:
        monkeypatch.setattr(client.beta.jobs._datasets, "get", missing_asset)
        monkeypatch.setattr(client.beta.jobs._datasets, "upload_folder", upload_folder)
        await client.beta.jobs.create_or_update(
            job, experiment_name="pipeline_samples", headers={"x-ms-foundry-job-route": "execution"}
        )

    assert uploads == [str(snapshot)]
    assert not snapshot.exists()
    assert len(transport.requests) == 1
    properties = json.loads(transport.requests[0].body)["properties"]
    assert properties["jobs"]["produce"]["component"]["code"] == properties["jobs"]["consume"]["component"]["code"]


def test_dsl_source_snapshot_filters_files_before_hash_and_upload(tmp_path: Path) -> None:
    root = tmp_path / "code"
    nested = root / "pkg"
    nested.mkdir(parents=True)
    (root / ".gitignore").write_text("*.tmp\n!keep.tmp\n", encoding="utf-8")
    (root / ".env").write_text("not-for-upload", encoding="utf-8")
    (root / "discard.tmp").write_text("ignored", encoding="utf-8")
    (root / "keep.tmp").write_text("included", encoding="utf-8")
    (nested / ".gitignore").write_text("private.txt\n", encoding="utf-8")
    (nested / "private.txt").write_text("ignored", encoding="utf-8")
    (nested / "public.txt").write_text("included", encoding="utf-8")

    snapshots = [tmp_path / "first", tmp_path / "second"]
    snapshots[0].mkdir()
    _stage_component_source(root, snapshots[0])
    (root / "discard.tmp").write_text("changed", encoding="utf-8")
    (nested / "private.txt").write_text("changed", encoding="utf-8")
    snapshots[1].mkdir()
    _stage_component_source(root, snapshots[1])

    assert _content_hash(snapshots[0]) == _content_hash(snapshots[1])
    assert sorted(path.relative_to(snapshots[0]).as_posix() for path in snapshots[0].rglob("*") if path.is_file()) == [
        _RUNNER_NAME,
        "keep.tmp",
        "pkg/public.txt",
    ]


def test_dsl_source_snapshot_amlignore_overrides_gitignore_and_excludes_directories(tmp_path: Path) -> None:
    root = tmp_path / "code"
    root.mkdir()
    (root / ".gitignore").write_text("keep.txt\n", encoding="utf-8")
    (root / ".amlignore").write_text("private/\n", encoding="utf-8")
    (root / "keep.txt").write_text("included", encoding="utf-8")
    private = root / "private"
    private.mkdir()
    (private / "secret.txt").write_text("excluded", encoding="utf-8")
    stage = tmp_path / "stage"
    stage.mkdir()

    _stage_component_source(root, stage)

    assert (stage / "keep.txt").read_text(encoding="utf-8") == "included"
    assert not (stage / "private").exists()
    assert not (stage / ".gitignore").exists()
    assert not (stage / ".amlignore").exists()


def test_dsl_source_snapshot_rejects_included_symlinks(tmp_path: Path) -> None:
    root = tmp_path / "code"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    try:
        (root / "link.txt").symlink_to(outside)
    except OSError:
        pytest.skip("Symbolic links are unavailable on this host")
    stage = tmp_path / "stage"
    stage.mkdir()
    with pytest.raises(ValueError, match="included symbolic link"):
        _stage_component_source(root, stage)


@pytest.mark.skipif(os.name != "nt", reason="Windows junctions only")
def test_dsl_source_snapshot_rejects_included_junctions(tmp_path: Path) -> None:
    root = tmp_path / "code"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    link = str(root / "link").replace("'", "''")
    target = str(outside).replace("'", "''")
    subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            f"New-Item -ItemType Junction -Path '{link}' -Target '{target}' | Out-Null",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    stage = tmp_path / "stage"
    stage.mkdir()
    with pytest.raises(ValueError, match="included junction"):
        _stage_component_source(root, stage)


def test_dsl_source_requires_importable_function_inside_root(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="inside its code root"):

        @dsl.component(code=tmp_path)
        def outside(result: dsl.Output(type="uri_file")) -> None:
            Path(result).write_text("outside", encoding="utf-8")

    with pytest.raises(ValueError, match="module-level"):

        @dsl.component(code=Path(__file__).resolve().parent)
        def nested(result: dsl.Output(type="uri_file")) -> None:
            Path(result).write_text("nested", encoding="utf-8")


def test_dsl_source_runner_converts_primitive_ports(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    code_root = tmp_path / "code"
    code_root.mkdir()
    module_name = "source_numeric_component"
    (code_root / f"{module_name}.py").write_text(
        "from pathlib import Path\n"
        "from azure.ai.projects.dsl import Output, component\n"
        "@component(code='.')\n"
        "def write(count: int, ratio: float, enabled: bool, result: Output(type='uri_file')) -> None:\n"
        "    Path(result).write_text(f'{count}|{ratio}|{enabled}', encoding='utf-8')\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(code_root))
    writer = importlib.import_module(module_name).write

    @dsl.pipeline(
        compute_id=_COMPUTE,
        environment_image_reference="example.azurecr.io/train:latest",
        user_assigned_identity_id="/subscriptions/test/identities/hello",
        instance_type="Singularity.D4_v3",
    )
    def workflow():
        return {"result": writer(count=3, ratio=1.5, enabled=True).outputs.result}

    job = workflow()
    try:
        stage = _dsl_code_paths(job)["write"]
        assert job.jobs["write"]["component"]["command"].startswith(
            f"python {_RUNNER_NAME} {module_name} write count:int,ratio:float,enabled:bool,result:str "
        )
        environment = os.environ.copy()
        environment["PYTHONPATH"] = os.pathsep.join(
            [str(Path(__file__).resolve().parents[2]), environment.get("PYTHONPATH", "")]
        )
        result = tmp_path / "result.txt"
        subprocess.run(
            [
                sys.executable,
                str(stage / _RUNNER_NAME),
                module_name,
                "write",
                "count:int,ratio:float,enabled:bool,result:str",
                "3",
                "1.5",
                "True",
                str(result),
            ],
            cwd=tmp_path,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        assert result.read_text(encoding="utf-8") == "3|1.5|True"
    finally:
        for directory in job._component_code_dirs:
            directory.cleanup()


def test_jobs_sync_job_only_names_are_unique() -> None:
    job = PipelineJob(compute_id=_COMPUTE, jobs={})
    transport = _Transport([_response("Pipeline"), _response("Pipeline")])
    with AIProjectClient(endpoint=_ENDPOINT, credential=_Credential(), transport=transport) as client:  # type: ignore[arg-type]
        client.beta.jobs.create_or_update(job)
        client.beta.jobs.create_or_update(job)
        with pytest.raises(TypeError, match="one PipelineJob"):
            client.beta.jobs.create_or_update("missing-job")
        with pytest.raises(TypeError, match="A job cannot be supplied"):
            client.beta.jobs.create_or_update(job, job)

    paths = [urlparse(request.url).path for request in transport.requests]
    assert len(paths) == len(set(paths)) == 2
    assert all(re.fullmatch(r"/api/projects/fake-project/jobs/pipeline-[0-9a-f]{32}", path) for path in paths)


@pytest.mark.asyncio
async def test_jobs_async_job_only_names_are_unique() -> None:
    job = PipelineJob(compute_id=_COMPUTE, jobs={})
    transport = _AsyncTransport([_response("Pipeline"), _response("Pipeline")])
    async with AsyncAIProjectClient(
        endpoint=_ENDPOINT, credential=_AsyncCredential(), transport=transport  # type: ignore[arg-type]
    ) as client:
        await client.beta.jobs.create_or_update(job)
        await client.beta.jobs.create_or_update(job)

    paths = [urlparse(request.url).path for request in transport.requests]
    assert len(paths) == len(set(paths)) == 2
    assert all(re.fullmatch(r"/api/projects/fake-project/jobs/pipeline-[0-9a-f]{32}", path) for path in paths)
