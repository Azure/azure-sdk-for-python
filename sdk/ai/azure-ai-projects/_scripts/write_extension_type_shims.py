#!/usr/bin/env python
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Write local compatibility shims for extension-owned Projects types."""

from __future__ import annotations

import argparse
from pathlib import Path


COPYRIGHT = "# Copyright (c) Microsoft Corporation.\n# Licensed under the MIT license.\n"

TYPES_SHIM = (
    COPYRIGHT
    + '"""Compatibility re-export for extension-owned Azure AI Projects generated types."""\n\n'
    + "from azure.ai.extensions.openai.projects._generated import types as _extension_types\n"
    + "from azure.ai.extensions.openai.projects._generated.types import *  # type: ignore # noqa: F401,F403\n\n"
    + "for _name in dir(_extension_types):\n"
    + '    if not _name.startswith("__"):\n'
    + "        globals()[_name] = getattr(_extension_types, _name)\n"
)

UNIONS_SHIM = (
    COPYRIGHT
    + '"""Compatibility re-export for extension-owned Azure AI Projects generated types."""\n\n'
    + "from azure.ai.extensions.openai.projects._generated._unions import *  # type: ignore # noqa: F401,F403\n"
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_shims(package_root: Path) -> None:
    _write(package_root / "azure" / "ai" / "projects" / "types.py", TYPES_SHIM)
    _write(package_root / "azure" / "ai" / "projects" / "_unions.py", UNIONS_SHIM)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, default=Path("."))
    args = parser.parse_args()
    write_shims(args.package_root)


if __name__ == "__main__":
    main()
