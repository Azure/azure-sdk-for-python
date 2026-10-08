# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Guard: no responses module may import generated model types eagerly.

Enforces the lazy module-alias pattern applied once by
``_scripts/qualify_model_references.py`` so new changes cannot reintroduce
import-time TypedDict construction (cold-start cost). An eager
``from ..models._generated import ResponseObject`` triggers the models package
``__getattr__`` and builds that TypedDict at import; the allowed form binds only
the module (``from ..models import _generated as _generated_models``) and
references types as attributes, constructing nothing at import.

Runs the codemod's ``--check`` mode as a subprocess so this rides the existing
unit-test CI with no pipeline changes and no runtime/import cost.
"""
import subprocess
import sys
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[2] / "_scripts" / "qualify_model_references.py"


def test_no_eager_generated_model_imports():
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        "Eager generated-model imports detected. Use the lazy module alias, e.g. "
        "`from ..models import _generated as _generated_models`, and reference types as "
        f"`_generated_models.<Name>`.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
