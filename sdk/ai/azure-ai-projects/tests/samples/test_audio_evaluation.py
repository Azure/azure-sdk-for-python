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
from unittest.mock import MagicMock, Mock

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
        assert_audio_evaluation_results(
            output.call_args_list, ("task_completion", "coherence")
        )
    else:
        with pytest.raises(AssertionError):
            assert_audio_evaluation_results(
                output.call_args_list, ("task_completion", "coherence")
            )


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
        "error": (
            {"code": "invalid_audio", "message": "Recording unavailable"}
            if status == "failed"
            else None
        ),
    }


@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("simulation", [False, True])
@pytest.mark.parametrize(
    "outcome", ["completed", "failed", "errored", "empty", "timeout", "cancel_error"]
)
def test_audio_sample_workflow(monkeypatch, capsys, is_async, simulation, outcome):
    """Cover routing, real SDK serialization, paginated results and cleanup."""
    suffix = "_async" if is_async else ""
    name = "voice_agent_simulation" if simulation else "audio_conversation"
    path = (
        Path(__file__).resolve().parents[2]
        / "samples"
        / "evaluations"
        / f"sample_{name}_evaluation{suffix}.py"
    )
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
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(sample, "load_dotenv", lambda: None)
    requests = []
    output_pages = []

    def handle(request):
        requests.append(request)
        if request.method == "DELETE":
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
                    "name": "store-assistant",
                    "version": "1",
                }
                assert source["model_configuration"] == {
                    "model": "user-simulator",
                    "voice_model": {
                        "type": "azure-standard",
                        "name": "en-US-AvaNeural",
                    },
                }
                assert source["source"]["type"] == "inline_user_conversation_simulation"
                assert source["source"]["test_cases"][0]["test_case_description"]
                assert source["default_simulation_configuration"]["max_num_turns"] == 3
                assert source["default_simulation_configuration"][
                    "enable_conversation_dataset_generation"
                ]
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
        body = json.loads(request.content)
        if not simulation:
            assert (
                "messages" not in body["data_source_config"]["item_schema"]["required"]
            )
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
            assert criterion["initialization_parameters"] == {
                "deployment_name": "audio-judge"
            }
            assert "data_mapping" not in criterion
        assert "audio_path" not in json.dumps(body)
        return httpx2.Response(
            200, json={"id": "eval_audio", "object": "eval", "created_at": 0}
        )

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
        assert "Task not completed" in capsys.readouterr().out
    elif outcome == "timeout":
        with pytest.raises(TimeoutError, match="600 seconds"):
            invoke()
    elif outcome == "cancel_error":
        from openai import BadRequestError

        with pytest.raises(BadRequestError, match="Cannot cancel"):
            invoke()
    else:
        with pytest.raises(RuntimeError, match="failed|errored|no items"):
            invoke()
    assert requests[-1].method == "DELETE"
    assert requests[-1].url.path.endswith("/evals/eval_audio")
    assert any(request.url.path.endswith("/cancel") for request in requests) == (
        outcome in ("timeout", "cancel_error")
    )
    if outcome not in ("timeout", "cancel_error"):
        assert output_pages == [None, "item_1"]
