"""
Prompty adapter selector.

This SDK provides two prompty engines:
- SDK prompty (preferred): the built-in implementation in this package.
- Promptflow prompty (legacy-compat): external implementation for backward compatibility.

Selection rules:
- For reasoning runs (is_reasoning_model=True), prefer the SDK prompty even if Promptflow is installed.
- Otherwise, if Promptflow is available, it is used by default unless explicitly overridden.
- Kwarg overrides on `AsyncPrompty.load(...)` (mirrors `evaluate(...)`):
  - `_use_pf_client=True` forces Promptflow; raises if Promptflow is not installed.
  - `_use_run_submitter_client=True` forces the SDK prompty.
  - If both flags are `True`, an error is raised.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict
from typing_extensions import TypeAlias
from azure.ai.evaluation._legacy.prompty._yaml_utils import load_yaml_string
from azure.ai.evaluation._constants import DEFAULT_MAX_COMPLETION_TOKENS_REASONING_MODELS


def _sanitize_reasoning_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    # Remove unsupported params and swap token field
    if "max_tokens" in params:
        params.pop("max_tokens", None)
        params["max_completion_tokens"] = DEFAULT_MAX_COMPLETION_TOKENS_REASONING_MODELS
    for key in ["temperature", "top_p", "presence_penalty", "frequency_penalty"]:
        params.pop(key, None)
    return params


def _extract_prompty_parameters(source: str) -> Dict[str, Any]:
    # Read prompty file and parse the YAML front matter; return model.parameters dict if present
    path = Path(source)
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return {}
    pattern = r"-{3,}\n(.*)-{3,}\n(.*)"
    m = re.search(pattern, content, re.DOTALL)
    if not m:
        return {}
    yaml_str, _ = m.groups()
    cfg = load_yaml_string(yaml_str) or {}
    model_cfg = cfg.get("model", {})
    return dict(model_cfg.get("parameters", {}) or {})


try:
    from promptflow.core._flow import AsyncPrompty as _PFAsyncPrompty  # type: ignore
    from promptflow._sdk.entities._flows import FlexFlow as _FlexFlow  # type: ignore
    from promptflow._sdk.entities._flows.dag import Flow as _Flow  # type: ignore

    class _AsyncPrompty:  # wrapper that applies reasoning param fixes and client selection before PF loads
        @classmethod
        def load(cls, source: str, **kwargs):
            is_reasoning_model = kwargs.pop("is_reasoning_model", False)
            use_run_submitter_client = kwargs.pop("_use_run_submitter_client", None)
            use_pf_client = kwargs.pop("_use_pf_client", None)
            # Prefer legacy implementation entirely when reasoning is requested,
            # until Promptflow supports reasoning parameter sanitization natively.
            if is_reasoning_model:
                from azure.ai.evaluation._legacy.prompty import AsyncPrompty as _LegacyAsync

                return _LegacyAsync.load(source=source, is_reasoning_model=True, **kwargs)
            # Client selection mirrors evaluate(...)
            if use_run_submitter_client and use_pf_client:
                raise ValueError("Only one of _use_pf_client and _use_run_submitter_client should be set to True.")
            # Default when both unset: Promptflow
            choose_pf = False
            if use_run_submitter_client is None and use_pf_client is None:
                choose_pf = True
            elif use_run_submitter_client is False and use_pf_client is False:
                choose_pf = False
            elif use_run_submitter_client:
                choose_pf = False
            elif use_pf_client:
                choose_pf = True
            elif use_run_submitter_client is None and use_pf_client is False:
                choose_pf = False
            elif use_run_submitter_client is False and use_pf_client is None:
                choose_pf = True
            # Route based on selection
            model = kwargs.get("model", {})
            if is_reasoning_model:
                # Merge sanitized parameters into the override model dict so PF uses them
                base_params = _extract_prompty_parameters(source)
                sanitized = _sanitize_reasoning_parameters(base_params)
                override_params = dict(model.get("parameters", {}) or {})
                override_params.update(sanitized)
                model["parameters"] = override_params
                kwargs["model"] = model
            if choose_pf:
                return _PFAsyncPrompty.load(source=source, **kwargs)
            else:
                from azure.ai.evaluation._legacy.prompty import AsyncPrompty as _LegacyAsync

                return _LegacyAsync.load(source=source, **kwargs)

except ImportError:
    from azure.ai.evaluation._legacy.prompty import AsyncPrompty as _AsyncPrompty

    class _FlexFlow:
        pass

    _FlexFlow.__name__ = "FlexFlow"

    class _Flow:
        name: str

    _Flow.__name__ = "Flow"


AsyncPrompty: TypeAlias = _AsyncPrompty
FlexFlow: TypeAlias = _FlexFlow
Flow: TypeAlias = _Flow
