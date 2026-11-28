# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline execution of voice samples through the public project/OpenAI bridge."""

import asyncio
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, Mock

import httpx2
import pytest

from test_samples_helpers import assert_audio_evaluation_results

ENDPOINT = "https://example.services.ai.azure.com/api/projects/example"
DATASET_ID = "azureai://accounts/example/projects/example/data/conversations/versions/1"


@pytest.mark.parametrize(
    "outcome",
    ["low_score", "missing", "duplicate", "skipped", "error", "nan", "empty"],
)
def test_audio_result_validation(outcome):
    results = [
        {"name": "task_completion", "score": 0, "passed": False, "status": "completed"},
        {"name": "coherence", "score": 1, "passed": False, "status": "completed"},
    ]
    if outcome == "missing":
        results.pop()
    elif outcome == "duplicate":
        results[1]["name"] = "task_completion"
    elif outcome == "skipped":
        results[1]["status"] = "skipped"
    elif outcome == "error":
        results[1]["error"] = {"code": "invalid_audio"}
    elif outcome == "nan":
        results[1]["score"] = float("nan")
    item = Mock()
    item.model_dump.return_value = {"results": results}
    output = Mock()
    if outcome != "empty":
        output(item)
    if outcome == "low_score":
        assert_audio_evaluation_results(output.call_args_list, ("task_completion", "coherence"))
    else:
        with pytest.raises(AssertionError):
            assert_audio_evaluation_results(output.call_args_list, ("task_completion", "coherence"))


def _run_response(status="completed", errored=0, total=1):
    return {
        "id": "evalrun_audio",
        "object": "eval.run",
        "eval_id": "eval_audio",
        "created_at": 0,
        "status": status,
        # A low score must not be mistaken for an execution failure.
        "result_counts": {
            "total": total,
            "passed": 0,
            "failed": total,
            "errored": errored,
        },
        "error": ({"code": "invalid_audio", "message": "Recording unavailable"} if status == "failed" else None),
    }


@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("simulation", [False, True])
@pytest.mark.parametrize(
    "outcome,setup",
    [(outcome, "existing") for outcome in ("completed", "failed", "errored", "empty", "timeout", "cancel_error")]
    + [(outcome, "defaults") for outcome in ("completed", "evaluation_error", "upload_error")],
)
def test_audio_sample_workflow(monkeypatch, capsys, is_async, simulation, outcome, setup):
    """Cover routing, real SDK serialization, paginated results and cleanup."""
    suffix = "_async" if is_async else ""
    name = "voice_agent_simulation" if simulation else "audio_conversation"
    path = Path(__file__).resolve().parents[2] / "samples" / "evaluations" / f"sample_{name}_evaluation{suffix}.py"
    spec = importlib.util.spec_from_file_location(f"{name}_sample{suffix}", path)
    sample = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sample)
    for key, value in {
        "FOUNDRY_PROJECT_ENDPOINT": ENDPOINT,
        "FOUNDRY_MODEL_NAME": "audio-judge",
        "FOUNDRY_DATASET_ID": DATASET_ID,
        "FOUNDRY_AGENT_NAME": "store-assistant",
        "FOUNDRY_AGENT_VERSION": "1",
        "FOUNDRY_SIMULATOR_MODEL_NAME": "user-simulator",
        "FOUNDRY_SIMULATOR_VOICE": "en-US-AvaNeural",
    }.items():
        if setup == "defaults" and key not in ("FOUNDRY_PROJECT_ENDPOINT", "FOUNDRY_MODEL_NAME"):
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)
    monkeypatch.delenv("FOUNDRY_VOICE_AGENT_MODEL", raising=False)
    if setup == "latest":
        monkeypatch.delenv("FOUNDRY_AGENT_VERSION")
    monkeypatch.setattr(sample, "load_dotenv", lambda: None)
    requests = []
    output_pages = []
    resource_events = []
    created_agent = []

    def handle(request):
        requests.append(request)
        if request.method == "DELETE":
            resource_events.append("delete_evaluation")
            return httpx2.Response(
                200,
                json={"id": "eval_audio", "object": "eval.deleted", "deleted": True},
            )
        if request.url.path.endswith("/cancel"):
            if outcome == "cancel_error":
                return httpx2.Response(
                    400,
                    json={"error": {"message": "Cannot cancel", "type": "bad_request"}},
                )
            return httpx2.Response(200, json=_run_response(status="canceled"))
        if request.url.path.endswith("/runs"):
            body = json.loads(request.content)
            assert "input_modality" not in body
            assert body["name"]
            assert body["evaluation_level"] == "conversation"
            source = body["data_source"]
            if simulation:
                assert source["type"] == "azure_ai_user_conversation_simulation"
                assert source["target"] == {
                    "type": "azure_ai_agent",
                    "name": created_agent[0] if setup == "defaults" else "store-assistant",
                    "version": "5" if setup == "latest" else "1",
                }
                assert source["model_configuration"] == {
                    "model": "gpt-4.1" if setup == "defaults" else "user-simulator",
                    "voice_model": {
                        "type": "azure-standard",
                        "name": "en-US-AvaNeural",
                    },
                }
                assert source["source"]["type"] == "inline_user_conversation_simulation"
                assert source["source"]["test_cases"][0]["test_case_description"]
                assert source["default_simulation_configuration"]["max_num_turns"] == 3
                assert source["default_simulation_configuration"]["enable_conversation_dataset_generation"]
            else:
                assert source == {
                    "type": "jsonl",
                    "source": {"type": "file_id", "id": DATASET_ID},
                }
            status = {
                "failed": "failed",
                "timeout": "queued",
                "cancel_error": "queued",
            }.get(outcome, "completed")
            return httpx2.Response(
                200,
                json=_run_response(
                    status,
                    errored=int(outcome == "errored"),
                    total=int(outcome != "empty"),
                ),
            )
        if request.url.path.endswith("/output_items"):
            after = request.url.params.get("after")
            output_pages.append(after)
            item_id = "item_2" if after else "item_1"
            return httpx2.Response(
                200,
                json={
                    "object": "list",
                    "data": [
                        {
                            "id": item_id,
                            "object": "eval.run.output_item",
                            "results": [
                                {
                                    "name": "task_completion",
                                    "score": 0,
                                    "passed": False,
                                    "reason": "Task not completed",
                                }
                            ],
                        }
                    ],
                    "has_more": not after,
                    "last_id": item_id,
                },
            )
        assert request.url.path.endswith("/evals")
        if outcome == "evaluation_error":
            return httpx2.Response(400, json={"error": {"message": "Cannot create evaluation", "type": "bad_request"}})
        body = json.loads(request.content)
        if not simulation:
            assert "messages" not in body["data_source_config"]["item_schema"]["required"]
        criteria = body["testing_criteria"]
        metrics = (
            ("task_completion",)
            if simulation
            else (
                "task_completion",
                "groundedness",
                "customer_satisfaction",
                "coherence",
            )
        )
        assert [criterion["evaluator_name"] for criterion in criteria] == [
            f"builtin.{metric}_audio" for metric in metrics
        ]
        for criterion in criteria:
            assert criterion["evaluator_version"] == "1"
            assert criterion["initialization_parameters"] == {"deployment_name": "audio-judge"}
            assert "data_mapping" not in criterion
        assert "audio_path" not in json.dumps(body)
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
        operation_mock = AsyncMock if is_async else Mock

        def upload_folder(**kwargs):
            folder = Path(kwargs["folder"])
            assert [file.name for file in folder.iterdir()] == ["conversation.wav"]
            assert (folder / "conversation.wav").read_bytes().startswith(b"RIFF")
            resource_events.append("upload_recording")
            return SimpleNamespace(id=DATASET_ID.replace("/conversations/", "/recording/"))

        def upload_file(**kwargs):
            if outcome == "upload_error":
                raise RuntimeError("Cannot upload JSONL")
            row = json.loads(Path(kwargs["file_path"]).read_text(encoding="utf-8"))
            assert row == {
                "conversation_artifacts": {
                    "audio": {
                        "asset_id": DATASET_ID.replace("/data/conversations/", "/datasets/recording/"),
                        "asset_file_path": "conversation.wav",
                    }
                }
            }
            resource_events.append("upload_jsonl")
            return SimpleNamespace(id=DATASET_ID)

        def delete_dataset(**kwargs):
            resource_events.append("delete_jsonl" if "conversations" in kwargs["name"] else "delete_recording")

        def create_agent(**kwargs):
            if outcome == "upload_error":
                raise RuntimeError("Cannot create voice agent")
            definition = kwargs["definition"]
            assert definition.kind == "voice"
            assert definition.model_type == "managed"
            assert definition.model == "gpt-realtime"
            assert definition.store
            created_agent.append(kwargs["agent_name"])
            resource_events.append("create_agent")
            return SimpleNamespace(name=kwargs["agent_name"], version="1")

        monkeypatch.setattr(project.datasets, "upload_folder", operation_mock(side_effect=upload_folder))
        monkeypatch.setattr(project.datasets, "upload_file", operation_mock(side_effect=upload_file))
        monkeypatch.setattr(project.datasets, "delete", operation_mock(side_effect=delete_dataset))
        monkeypatch.setattr(project.agents, "create_version", operation_mock(side_effect=create_agent))
        monkeypatch.setattr(
            project.agents,
            "delete_version",
            operation_mock(side_effect=lambda **kwargs: resource_events.append("delete_agent")),
        )
        monkeypatch.setattr(
            project.agents,
            "get",
            operation_mock(return_value=SimpleNamespace(versions=SimpleNamespace(latest=SimpleNamespace(version="5")))),
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
        assert "Task not completed" in capsys.readouterr().out
    elif outcome == "timeout":
        with pytest.raises(TimeoutError, match="600 seconds"):
            invoke()
    elif outcome in ("cancel_error", "evaluation_error"):
        from openai import BadRequestError

        with pytest.raises(BadRequestError, match="Cannot cancel|Cannot create evaluation"):
            invoke()
    elif outcome == "upload_error":
        with pytest.raises(RuntimeError, match="Cannot upload JSONL|Cannot create voice agent"):
            invoke()
    else:
        with pytest.raises(RuntimeError, match="failed|errored|no items"):
            invoke()
    if setup == "defaults":
        if simulation:
            assert resource_events == (
                []
                if outcome == "upload_error"
                else ["create_agent"]
                + ([] if outcome == "evaluation_error" else ["delete_evaluation"])
                + ["delete_agent"]
            )
        elif outcome == "upload_error":
            assert resource_events == ["upload_recording", "delete_recording"]
        else:
            assert resource_events == ["upload_recording", "upload_jsonl"] + (
                [] if outcome == "evaluation_error" else ["delete_evaluation"]
            ) + ["delete_jsonl", "delete_recording"]
    else:
        assert resource_events == ["delete_evaluation"]
    if outcome in ("evaluation_error", "upload_error"):
        assert not any(request.method == "DELETE" for request in requests)
        return
    assert requests[-1].method == "DELETE"
    assert requests[-1].url.path.endswith("/evals/eval_audio")
    assert any(request.url.path.endswith("/cancel") for request in requests) == (outcome in ("timeout", "cancel_error"))
    if outcome not in ("timeout", "cancel_error"):
        assert output_pages == [None, "item_1"]


@pytest.mark.parametrize("is_async", [False, True])
def test_voice_sample_uses_latest_existing_agent(monkeypatch, capsys, is_async):
    test_audio_sample_workflow(monkeypatch, capsys, is_async, True, "completed", "latest")


@pytest.mark.parametrize("is_async", [False, True])
def test_voice_sample_rejects_version_without_agent(monkeypatch, is_async):
    suffix = "_async" if is_async else ""
    path = (
        Path(__file__).resolve().parents[2]
        / "samples"
        / "evaluations"
        / f"sample_voice_agent_simulation_evaluation{suffix}.py"
    )
    spec = importlib.util.spec_from_file_location(f"voice_version_sample{suffix}", path)
    sample = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sample)
    monkeypatch.setattr(sample, "load_dotenv", lambda: None)
    monkeypatch.delenv("FOUNDRY_AGENT_NAME", raising=False)
    monkeypatch.setenv("FOUNDRY_AGENT_VERSION", "1")
    client = Mock()
    monkeypatch.setattr(sample, "AIProjectClient", client)
    with pytest.raises(ValueError, match="requires FOUNDRY_AGENT_NAME"):
        if is_async:
            asyncio.run(sample.main())
        else:
            sample.main()
    client.assert_not_called()
