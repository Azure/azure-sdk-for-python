# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline coverage for audio run extensions and the recorded-audio samples."""

import asyncio
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

import httpx2
import pytest
from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient

ENDPOINT = "https://example.services.ai.azure.com/api/projects/example"
RECORDING = {
    "conversation_artifacts": {
        "audio": {
            "asset_id": "azureai://accounts/example/projects/example/datasets/recordings/versions/1",
            "asset_file_path": "recordings/conversation.wav",
        }
    },
    "messages": [{"role": "user", "content": "Transcript context"}],
}


def _run_response(modality, status="completed", errored=0):
    response = {
        "id": "evalrun_audio",
        "object": "eval.run",
        "eval_id": "eval_audio",
        "created_at": 0,
        "status": status,
        "result_counts": {"total": 1, "passed": 1, "failed": 0, "errored": errored},
        "error": ({"code": "invalid_audio", "message": "Recording unavailable"} if status == "failed" else None),
    }
    if modality is not None:
        response["input_modality"] = modality
    return response


@pytest.mark.parametrize("modality", [None, "text", "audio"])
@pytest.mark.parametrize("source_type", ["file_content", "file_id"])
@pytest.mark.parametrize("is_async", [False, True])
def test_input_modality_passthrough(modality, source_type, is_async):
    """The public project client needs no new argument to send audio run options."""
    captured = []

    def handle(request):
        assert request.method == "POST"
        assert request.url.path.endswith("/openai/v1/evals/eval_audio/runs")
        captured.append(json.loads(request.content))
        return httpx2.Response(200, json=_run_response(modality))

    source = (
        {"type": "file_content", "content": [{"item": RECORDING}]}
        if source_type == "file_content"
        else {
            "type": "file_id",
            "id": "azureai://accounts/example/projects/example/datasets/input/versions/1",
        }
    )
    extra_body = {"evaluation_level": "conversation"}
    if modality is not None:
        extra_body["input_modality"] = modality

    async def invoke_async():
        async with (
            AsyncAIProjectClient(endpoint=ENDPOINT, credential=Mock()) as project_client,
            project_client.get_openai_client(
                api_key="test-key",
                http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handle)),
            ) as client,
        ):
            return await client.evals.runs.create(
                eval_id="eval_audio",
                data_source={"type": "jsonl", "source": source},
                extra_body=extra_body,
            )

    if is_async:
        run = asyncio.run(invoke_async())
    else:
        with (
            AIProjectClient(endpoint=ENDPOINT, credential=Mock()) as project_client,
            project_client.get_openai_client(
                api_key="test-key",
                http_client=httpx2.Client(transport=httpx2.MockTransport(handle)),
            ) as client,
        ):
            run = client.evals.runs.create(
                eval_id="eval_audio",
                data_source={"type": "jsonl", "source": source},
                extra_body=extra_body,
            )

    assert len(captured) == 1
    assert captured[0]["data_source"] == {"type": "jsonl", "source": source}
    assert captured[0]["evaluation_level"] == "conversation"
    if modality is None:
        assert "input_modality" not in captured[0]
        assert "input_modality" not in (run.model_extra or {})
    else:
        assert captured[0]["input_modality"] == modality
        assert run.model_extra["input_modality"] == modality


@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("outcome", ["completed", "failed", "errored", "timeout"])
def test_audio_sample_workflow(monkeypatch, is_async, outcome):
    """Execute both samples against mock HTTP, including failure and cleanup paths."""
    suffix = "_async" if is_async else ""
    path = (
        Path(__file__).resolve().parents[2]
        / "samples"
        / "evaluations"
        / f"sample_audio_conversation_evaluation{suffix}.py"
    )
    spec = importlib.util.spec_from_file_location(f"audio_sample{suffix}", path)
    sample = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sample)
    values = {
        "FOUNDRY_PROJECT_ENDPOINT": ENDPOINT,
        "FOUNDRY_MODEL_NAME": "audio-judge",
        "FOUNDRY_AUDIO_EVALUATOR_NAME": "example.audio",
        "FOUNDRY_AUDIO_EVALUATOR_VERSION": "1",
        "FOUNDRY_AUDIO_ASSET_ID": RECORDING["conversation_artifacts"]["audio"]["asset_id"],
        "FOUNDRY_AUDIO_ASSET_FILE_PATH": RECORDING["conversation_artifacts"]["audio"]["asset_file_path"],
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)
    monkeypatch.setattr(sample, "load_dotenv", lambda: None)
    requests = []

    def handle(request):
        requests.append(request)
        if request.method == "DELETE":
            return httpx2.Response(
                200,
                json={"id": "eval_audio", "object": "eval.deleted", "deleted": True},
            )
        if request.url.path.endswith("/cancel"):
            return httpx2.Response(200, json=_run_response("audio", status="canceled"))
        if request.url.path.endswith("/runs"):
            body = json.loads(request.content)
            assert body["input_modality"] == "audio"
            assert body["evaluation_level"] == "conversation"
            assert body["data_source"]["source"]["content"][0]["item"] == {
                "conversation_artifacts": RECORDING["conversation_artifacts"]
            }
            status = {"failed": "failed", "timeout": "queued"}.get(outcome, "completed")
            return httpx2.Response(
                200,
                json=_run_response("audio", status, errored=int(outcome == "errored")),
            )
        if request.url.path.endswith("/output_items"):
            return httpx2.Response(200, json={"object": "list", "data": [], "has_more": False})
        assert request.url.path.endswith("/evals")
        body = json.loads(request.content)
        assert body["data_source_config"]["item_schema"]["required"] == ["conversation_artifacts"]
        criterion = body["testing_criteria"][0]
        assert criterion["evaluator_name"] == "example.audio"
        assert criterion["evaluator_version"] == "1"
        assert criterion["initialization_parameters"] == {"deployment_name": "audio-judge"}
        assert "data_mapping" not in criterion
        return httpx2.Response(200, json={"id": "eval_audio", "object": "eval", "created_at": 0})

    project_type = sample.AIProjectClient

    def project_factory(**kwargs):
        kwargs["credential"] = Mock()
        project = project_type(**kwargs)
        get_client = project.get_openai_client
        http_client = (
            httpx2.AsyncClient(transport=httpx2.MockTransport(handle))
            if is_async
            else httpx2.Client(transport=httpx2.MockTransport(handle))
        )
        monkeypatch.setattr(
            project,
            "get_openai_client",
            lambda: get_client(api_key="test-key", http_client=http_client),
        )
        return project

    monkeypatch.setattr(sample, "DefaultAzureCredential", MagicMock)
    monkeypatch.setattr(sample, "AIProjectClient", project_factory)
    clock = iter([0, 601])
    monkeypatch.setattr(
        sample,
        "time",
        SimpleNamespace(monotonic=lambda: next(clock), sleep=sample.time.sleep),
    )

    def invoke():
        if is_async:
            asyncio.run(sample.main())
        else:
            sample.main()

    if outcome == "completed":
        invoke()
    elif outcome == "timeout":
        with pytest.raises(TimeoutError, match="600 seconds"):
            invoke()
    else:
        with pytest.raises(RuntimeError, match="failed|errored"):
            invoke()
    assert requests[-1].method == "DELETE"
    assert requests[-1].url.path.endswith("/evals/eval_audio")
    assert any(request.url.path.endswith("/cancel") for request in requests) == (outcome == "timeout")
