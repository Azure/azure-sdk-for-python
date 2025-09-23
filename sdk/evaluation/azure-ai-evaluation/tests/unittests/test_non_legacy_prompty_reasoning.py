import sys
import types
import importlib
from pathlib import Path

import pytest


def _make_fake_promptflow_modules(monkeypatch):
    core_flow = types.ModuleType("promptflow.core._flow")

    class FakePFAsyncPrompty:
        last_kwargs = None

        @classmethod
        def load(cls, source: str, **kwargs):
            cls.last_kwargs = kwargs
            return object()

    core_flow.AsyncPrompty = FakePFAsyncPrompty

    flows_entities = types.ModuleType("promptflow._sdk.entities._flows")

    class FlexFlow:
        pass

    flows_entities.FlexFlow = FlexFlow

    class Prompty:  # provide Prompty symbol to avoid ImportError in code paths
        pass

    flows_entities.Prompty = Prompty

    flows_dag = types.ModuleType("promptflow._sdk.entities._flows.dag")

    class Flow:
        name = "dummy"

    flows_dag.Flow = Flow

    # Inject into sys.modules for the duration of the test only
    monkeypatch.setitem(sys.modules, "promptflow.core._flow", core_flow)
    monkeypatch.setitem(sys.modules, "promptflow._sdk.entities._flows", flows_entities)
    monkeypatch.setitem(sys.modules, "promptflow._sdk.entities._flows.dag", flows_dag)

    return FakePFAsyncPrompty


def _write_temp_prompty(tmp_path: Path, params: str) -> Path:
    # Build prompty content with correct indentation
    indented = "\n".join(["    " + line if line.strip() else line for line in params.strip().splitlines()])
    content = (
        "---\n"
        "name: Test Prompty\n"
        "model:\n"
        "  api: chat\n"
        "  configuration:\n"
        "    type: azure_openai\n"
        "    azure_deployment: dummy\n"
        "    api_key: ${env:AZURE_OPENAI_API_KEY}\n"
        "    api_version: ${env:AZURE_OPENAI_API_VERSION}\n"
        "    azure_endpoint: ${env:AZURE_OPENAI_ENDPOINT}\n"
        "  parameters:\n"
        f"{indented}\n"
        "inputs:\n"
        "  query:\n"
        "    type: string\n"
        "  response:\n"
        "    type: string\n"
        "---\n"
        "user:\n"
        "{{query}}\n"
        "assistant:\n"
        "{{response}}\n"
    )
    p = tmp_path / "test.prompty"
    p.write_text(content, encoding="utf-8")
    return p


def test_sanitize_reasoning_parameters_removes_and_adds():
    from azure.ai.evaluation._legacy._adapters import _flows as flows

    params = {
        "max_tokens": 100,
        "temperature": 0.2,
        "top_p": 0.9,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0,
        "stream": False,
    }
    sanitized = flows._sanitize_reasoning_parameters(dict(params))
    assert "max_tokens" not in sanitized
    assert "temperature" not in sanitized
    assert "top_p" not in sanitized
    assert "presence_penalty" not in sanitized
    assert "frequency_penalty" not in sanitized
    assert "max_completion_tokens" in sanitized
    # Preserve unrelated params
    assert sanitized["stream"] is False


def test_extract_prompty_parameters_parses_yaml(tmp_path):
    from azure.ai.evaluation._legacy._adapters import _flows as flows

    prompty = _write_temp_prompty(tmp_path, "max_tokens: 128\ntemperature: 0.1\n")
    parsed = flows._extract_prompty_parameters(str(prompty))
    assert parsed.get("max_tokens") == 128
    assert parsed.get("temperature") == 0.1


def test_pf_wrapper_prefers_legacy_when_reasoning(tmp_path, monkeypatch):
    # Install fake promptflow modules and reload adapter to take non-legacy path
    FakePFAsyncPrompty = _make_fake_promptflow_modules(monkeypatch)
    import azure.ai.evaluation._legacy._adapters._flows as flows

    importlib.reload(flows)

    # Create a prompty with legacy params
    prompty = _write_temp_prompty(tmp_path, "max_tokens: 128\ntemperature: 0.1\n")

    # Call wrapper with is_reasoning_model=True and a model override
    result = flows.AsyncPrompty.load(
        source=str(prompty),
        is_reasoning_model=True,
        model={"parameters": {"stream": True}},
    )
    assert result is not None

    # Ensure PF AsyncPrompty.load was NOT invoked (legacy preferred for reasoning)
    assert FakePFAsyncPrompty.last_kwargs is None


def test_pf_wrapper_no_change_when_not_reasoning(tmp_path, monkeypatch):
    FakePFAsyncPrompty = _make_fake_promptflow_modules(monkeypatch)
    import azure.ai.evaluation._legacy._adapters._flows as flows

    importlib.reload(flows)

    prompty = _write_temp_prompty(tmp_path, "max_tokens: 128\ntemperature: 0.1\n")
    flows.AsyncPrompty.load(
        source=str(prompty),
        is_reasoning_model=False,
        model={"parameters": {"stream": True}},
    )
    # PF path used; our wrapper doesn't copy prompty params when not reasoning.
    # Only the override should be present.
    assert FakePFAsyncPrompty.last_kwargs is not None
    model_kwargs = FakePFAsyncPrompty.last_kwargs.get("model", {})
    params = model_kwargs.get("parameters", {})
    assert params.get("stream") is True
