# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Import/registration smoke test for every ``samples/sample_*.py`` module.

Spec 040 F6 — the sample e2e tests define their handlers *inline* and never
import the sample files, so a broken registration decorator (e.g. the
non-existent ``@app.create`` that left samples 12–16 raising ``AttributeError``
at import) went unnoticed. This test imports each sample module so any
import-time / registration-time error fails CI.

Samples that require an optional third-party dependency (``openai``,
``langgraph``/``langchain-core``) are skipped when that dependency is not
installed — a missing optional dep is not a sample bug. Any *other* import
error (a real breakage) fails the test.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_SAMPLES_DIR = Path(__file__).resolve().parents[2] / "samples"

# Optional third-party imports some samples need. A ModuleNotFoundError naming
# one of these → skip (environment gap); anything else → real failure.
_OPTIONAL_DEPS = {"openai", "langgraph", "langchain_core", "langgraph.checkpoint.sqlite"}

_SAMPLE_FILES = sorted(p.name for p in _SAMPLES_DIR.glob("sample_*.py"))


@pytest.mark.parametrize("sample_file", _SAMPLE_FILES)
def test_sample_module_imports_and_registers(sample_file: str) -> None:
    """Importing the sample must not raise (this is where ``@app.<decorator>``
    registration runs)."""
    path = _SAMPLES_DIR / sample_file
    spec = importlib.util.spec_from_file_location(f"_sample_{path.stem}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except ModuleNotFoundError as exc:
        missing = (exc.name or "").split(".")[0]
        if missing in {d.split(".")[0] for d in _OPTIONAL_DEPS}:
            pytest.skip(f"optional dependency '{missing}' not installed")
        raise


def test_at_least_the_expected_samples_are_present() -> None:
    """Guard against an accidental mass-deletion of samples."""
    assert len(_SAMPLE_FILES) >= 15, _SAMPLE_FILES
