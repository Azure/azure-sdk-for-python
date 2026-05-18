# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""End-to-end tests for validator generator CLI output."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


def _script_path() -> Path:
    return Path(__file__).resolve().parents[2] / "scripts" / "generate_validators.py"


def _spec() -> str:
    return """{
  "paths": {
    "/responses": {
      "post": {
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CreateResponse"
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "CreateResponse": {
        "type": "object",
        "required": ["model"],
        "properties": {
          "model": {"type": "string"},
          "metadata": {"$ref": "#/components/schemas/Metadata"}
        }
      },
      "Metadata": {
        "type": "object",
        "additionalProperties": {"type": "string"}
      }
    }
  }
}
"""


def test_generator_emits_valid_python_module(tmp_path: Path) -> None:
    spec_path = tmp_path / "spec.json"
    out_path = tmp_path / "_validators.py"
    spec_path.write_text(_spec(), encoding="utf-8")

    proc = subprocess.run(
        [
            sys.executable,
            str(_script_path()),
            "--input",
            str(spec_path),
            "--output",
            str(out_path),
            "--root-schemas",
            "CreateResponse",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr

    source = out_path.read_text(encoding="utf-8")
    compile(source, str(out_path), "exec")


def test_generated_module_exposes_expected_validate_functions(tmp_path: Path) -> None:
    spec_path = tmp_path / "spec.json"
    out_path = tmp_path / "_validators.py"
    spec_path.write_text(_spec(), encoding="utf-8")

    proc = subprocess.run(
        [
            sys.executable,
            str(_script_path()),
            "--input",
            str(spec_path),
            "--output",
            str(out_path),
            "--root-schemas",
            "CreateResponse",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr

    module_name = "generated_validator_module"
    spec = importlib.util.spec_from_file_location(module_name, out_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert hasattr(module, "validate_CreateResponse")


def test_regeneration_overwrites_previous_output_cleanly(tmp_path: Path) -> None:
    spec_path = tmp_path / "spec.json"
    out_path = tmp_path / "_validators.py"
    spec_path.write_text(_spec(), encoding="utf-8")

    out_path.write_text("stale-content", encoding="utf-8")

    proc = subprocess.run(
        [
            sys.executable,
            str(_script_path()),
            "--input",
            str(spec_path),
            "--output",
            str(out_path),
            "--root-schemas",
            "CreateResponse",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr

    content = out_path.read_text(encoding="utf-8")
    assert "stale-content" not in content
    assert content.startswith("# pylint: disable=line-too-long,useless-suppression,too-many-lines")


def test_generator_handles_inline_create_response_schema(tmp_path: Path) -> None:
    spec_path = tmp_path / "spec-inline.json"
    out_path = tmp_path / "_validators.py"
    spec_path.write_text(
        """{
  "paths": {
    "/responses": {
      "post": {
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "anyOf": [
                  {
                    "type": "object",
                    "required": ["model"],
                    "properties": {
                      "model": {"type": "string"}
                    }
                  }
                ]
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {}
  }
}
""",
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            sys.executable,
            str(_script_path()),
            "--input",
            str(spec_path),
            "--output",
            str(out_path),
            "--root-schemas",
            "CreateResponse",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    content = out_path.read_text(encoding="utf-8")
    assert "def _validate_CreateResponse(" in content
    assert "class CreateResponseValidator" in content
