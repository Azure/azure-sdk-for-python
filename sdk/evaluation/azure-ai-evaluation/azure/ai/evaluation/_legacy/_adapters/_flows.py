"""
Prompty adapter selector.

This SDK provides two prompty engines:
- SDK prompty (preferred): the built-in implementation in this package.
- Promptflow prompty (legacy-compat): external implementation for backward compatibility.

Selection rules:
- For reasoning runs (is_reasoning_model=True), prefer the SDK prompty even if Promptflow is installed.
- Otherwise, if Promptflow is available, it is used by default unless explicitly overridden.
- Env overrides:
  - Set AZEVAL_USE_LEGACY_PROMPTY=1 to force the SDK prompty (kept for backward compatibility).
  - Set AZEVAL_USE_PROMPTFLOW=1 to force the Promptflow prompty.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict
from typing_extensions import TypeAlias
from azure.ai.evaluation._legacy.prompty._yaml_utils import load_yaml_string
from azure.ai.evaluation._constants import DEFAULT_MAX_COMPLETION_TOKENS_REASONING_MODELS


_use_legacy = os.environ.get("AZEVAL_USE_LEGACY_PROMPTY", "0") == "1"
# Allow explicitly forcing Promptflow as the legacy-compat engine
_force_promptflow = os.environ.get("AZEVAL_USE_PROMPTFLOW", "0") == "1"


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


if not _use_legacy and not _force_promptflow:
    try:
        from promptflow.core._flow import AsyncPrompty as _PFAsyncPrompty  # type: ignore
        from promptflow._sdk.entities._flows import FlexFlow as _FlexFlow  # type: ignore
        from promptflow._sdk.entities._flows.dag import Flow as _Flow  # type: ignore

        class _AsyncPrompty:  # wrapper that applies reasoning param fixes before PF loads
            @classmethod
            def load(cls, source: str, **kwargs):
                is_reasoning_model = kwargs.pop("is_reasoning_model", False)
                # Prefer legacy implementation entirely when reasoning is requested,
                # until Promptflow supports reasoning parameter sanitization natively.
                if is_reasoning_model:
                    from azure.ai.evaluation._legacy.prompty import AsyncPrompty as _LegacyAsync

                    return _LegacyAsync.load(source=source, is_reasoning_model=True, **kwargs)
                model = kwargs.get("model", {})
                if is_reasoning_model:
                    # Merge sanitized parameters into the override model dict so PF uses them
                    base_params = _extract_prompty_parameters(source)
                    sanitized = _sanitize_reasoning_parameters(base_params)
                    override_params = dict(model.get("parameters", {}) or {})
                    override_params.update(sanitized)
                    model["parameters"] = override_params
                    kwargs["model"] = model
                return _PFAsyncPrompty.load(source=source, **kwargs)

    except ImportError:
        _use_legacy = True

if _use_legacy or _force_promptflow:
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
