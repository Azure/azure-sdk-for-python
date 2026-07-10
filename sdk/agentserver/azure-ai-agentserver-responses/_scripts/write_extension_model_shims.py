#!/usr/bin/env python
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Write local compatibility shims for extension-owned Responses models."""

from __future__ import annotations

import argparse
from pathlib import Path


COPYRIGHT = "# Copyright (c) Microsoft Corporation.\n# Licensed under the MIT license.\n"
EXTENSION_ROOT = "azure.ai.extensions.openai.responses._generated.sdk.models"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _shim(module: str, description: str = "Compatibility re-export for extension-owned OpenAI Responses models.") -> str:
    return (
        COPYRIGHT
        + f'"""{description}"""\n\n'
        + f"from {EXTENSION_ROOT}{module} import *  # type: ignore # noqa: F401,F403\n"
    )


def write_shims(local_generated_root: Path) -> None:
    _write(local_generated_root / "__init__.py", _shim("", "Compatibility package for extension-owned OpenAI Responses models."))
    _write(local_generated_root / "types.py", _shim(".types"))
    _write(local_generated_root / "_unions.py", _shim("._unions"))
    _write(local_generated_root / "_types.py", _shim("._types"))
    _write(local_generated_root / "_patch.py", _shim("._patch"))
    _write(local_generated_root / "_utils" / "__init__.py", _shim("._utils"))
    _write(local_generated_root / "_utils" / "model_base.py", _shim("._utils.model_base"))
    _write(local_generated_root / "_utils" / "serialization.py", _shim("._utils.serialization"))
    _write(local_generated_root / "models" / "_patch.py", _shim(".models._patch"))
    _write(local_generated_root / "models" / "_enums.py", _shim(".models._enums"))
    _write(local_generated_root / "models" / "_models.py", _shim(".models._models"))
    _write(
        local_generated_root / "models" / "__init__.py",
        COPYRIGHT
        + '"""Compatibility re-export for extension-owned OpenAI Responses model classes."""\n\n'
        + f"from {EXTENSION_ROOT}.models import *  # type: ignore # noqa: F401,F403\n\n"
        + "try:\n"
        + f"    from {EXTENSION_ROOT}.models import __all__  # type: ignore # noqa: F401\n"
        + "except ImportError:\n"
        + "    __all__: list[str] = []\n",
    )
    _write(local_generated_root / "py.typed", "")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-generated-root", type=Path, required=True)
    args = parser.parse_args()
    write_shims(args.local_generated_root)


if __name__ == "__main__":
    main()
