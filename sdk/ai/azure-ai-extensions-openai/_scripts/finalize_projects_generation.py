#!/usr/bin/env python
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Finalize extension-owned Azure AI Projects TypedDict generation."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


COPYRIGHT = "# Copyright (c) Microsoft Corporation.\n# Licensed under the MIT license.\n"

MODEL_BASE = (
    COPYRIGHT
    + '"""Minimal model_base compatibility for TypedDict generation."""\n\n'
    + "from datetime import date, datetime\n"
    + "from json import JSONEncoder\n"
    + "from typing import Any\n\n\n"
    + "class Model(dict[str, Any]):\n"
    + '    """Dictionary-backed model marker used by generated multipart helpers."""\n\n\n'
    + "class SdkJSONEncoder(JSONEncoder):\n"
    + '    """JSON encoder compatible with generated multipart helpers."""\n\n'
    + "    def __init__(self, *args: Any, exclude_readonly: bool = False, **kwargs: Any) -> None:\n"
    + "        super().__init__(*args, **kwargs)\n"
    + "        self.exclude_readonly = exclude_readonly\n\n"
    + "    def default(self, o: Any) -> Any:\n"
    + "        if isinstance(o, (datetime, date)):\n"
    + "            return o.isoformat()\n"
    + '        enum_value = getattr(o, "value", None)\n'
    + "        if enum_value is not None:\n"
    + "            return enum_value\n"
    + "        if isinstance(o, set):\n"
    + "            return list(o)\n"
    + "        return super().default(o)\n"
)

SERIALIZATION = COPYRIGHT + '"""Compatibility serialization module for generated imports."""\n'


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _remove_pycache(root: Path) -> None:
    for pycache in root.rglob("__pycache__"):
        shutil.rmtree(pycache)


def finalize(generated_root: Path) -> None:
    if not generated_root.exists():
        raise FileNotFoundError(f"Generated root not found: {generated_root}")

    _remove_pycache(generated_root)
    _write(generated_root / "_utils" / "__init__.py", "")
    _write(generated_root / "_utils" / "model_base.py", MODEL_BASE)
    _write(generated_root / "_utils" / "serialization.py", SERIALIZATION)
    _write(generated_root / "py.typed", "")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generated-root", type=Path, required=True)
    args = parser.parse_args()
    finalize(args.generated_root)


if __name__ == "__main__":
    main()
