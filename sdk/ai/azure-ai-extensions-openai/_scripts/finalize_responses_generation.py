#!/usr/bin/env python
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Finalize extension-owned OpenAI Responses model generation.

The TypeSpec emitter owns the generated TypedDict contract files. This script
only keeps extension-local overlays that are still needed for generated import
shape, enum references, and documentation hooks.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
COPYRIGHT = "# Copyright (c) Microsoft Corporation.\n# Licensed under the MIT license.\n"

TYPES_SHIM = (
    COPYRIGHT
    + '"""Compatibility union aliases for TypedDict generation."""\n\n'
    + "from ._unions import *  # type: ignore # noqa: F401,F403\n"
    + "from .types import *  # type: ignore # noqa: F401,F403\n"
)

MODEL_BASE = (
    COPYRIGHT
    + '"""Minimal model_base compatibility for TypedDict generation."""\n\n'
    + "from typing import Any\n\n"
    + "Model = dict[str, Any]\n\n\n"
    + "def rest_field(*args: Any, **kwargs: Any) -> None:  # pylint: disable=unused-argument\n"
    + '    """Return a placeholder field marker for generated patch classes."""\n'
    + "    return None\n\n\n"
)

SERIALIZATION = COPYRIGHT + '"""Compatibility serialization module for generated imports."""\n'

ENUM_FALLBACK = (
    COPYRIGHT
    + '"""Compatibility enum module for TypedDict generation.\n\n'
    + "TypedDict mode emits enum-like aliases in ``types.py`` but older emitter\n"
    + "builds can still import this module from generated type hints.\n"
    + '"""\n\n\n'
    + "class _EnumMemberFallback(str):\n"
    + "    @property\n"
    + "    def value(self) -> str:\n"
    + "        return str(self)\n\n\n"
    + "def _member_value(enum_name: str, member_name: str) -> str:\n"
    + '    if enum_name == "ResponseStreamEventType":\n'
    + '        return member_name.lower().replace("_", ".")\n'
    + "    return member_name.lower()\n\n\n"
    + "class _EnumFallbackMeta(type):\n"
    + "    def __getattr__(cls, name: str) -> _EnumMemberFallback:\n"
    + "        return _EnumMemberFallback(_member_value(cls.__name__, name))\n\n\n"
    + "class _EnumFallback(str, metaclass=_EnumFallbackMeta):\n"
    + '    """Fallback object for enum names referenced by generated code."""\n\n\n'
    + "def __getattr__(name: str) -> type[_EnumFallback]:\n"
    + "    return type(name, (_EnumFallback,), {})\n"
)

TYPEDDICT_MODELS = (
    COPYRIGHT
    + '"""TypedDict model exports for Responses contracts."""\n\n'
    + "from .. import _unions as _unions_module\n"
    + "from .. import types as _types_module\n"
    + "from .._unions import *  # type: ignore # noqa: F401,F403\n"
    + "from ..types import *  # type: ignore # noqa: F401,F403\n\n\n"
    + "_TYPE_EXPORT_EXCLUDES = {\n"
    + '    "Any",\n'
    + '    "Literal",\n'
    + '    "Optional",\n'
    + '    "Required",\n'
    + '    "TYPE_CHECKING",\n'
    + '    "TypedDict",\n'
    + '    "Union",\n'
    + "}\n"
    + "__all__: list[str] = []\n\n"
    + "for _name in dir(_types_module):\n"
    + "    if _name.startswith(\"_\") or _name in _TYPE_EXPORT_EXCLUDES:\n"
    + "        continue\n"
    + "    globals()[_name] = getattr(_types_module, _name)\n"
    + "    __all__.append(_name)\n\n"
    + "for _name in dir(_unions_module):\n"
    + "    if _name.startswith(\"_\") or _name in __all__:\n"
    + "        continue\n"
    + "    globals()[_name] = getattr(_unions_module, _name)\n"
    + "    __all__.append(_name)\n"
)

MODELS_INIT = (
    "# coding=utf-8\n"
    "# --------------------------------------------------------------------------\n"
    "# Copyright (c) Microsoft Corporation. All rights reserved.\n"
    "# Licensed under the MIT License. See License.txt in the project root for license information.\n"
    "# --------------------------------------------------------------------------\n"
    "# pylint: disable=wrong-import-position\n\n"
    + "from typing import TYPE_CHECKING\n\n"
    + "if TYPE_CHECKING:\n"
    + "    from ._patch import *  # pylint: disable=unused-wildcard-import\n\n"
    + "from ._patch import __all__ as _patch_all\n"
    + "from ._patch import *\n"
    + "from ._patch import patch_sdk as _patch_sdk\n"
    + "from .. import types as _types\n"
    + "from .._unions import *  # type: ignore # noqa: F401,F403\n"
    + "from ..types import *  # type: ignore # noqa: F401,F403\n"
    + "from ._models import __all__ as _models_all\n"
    + "from ._models import *  # type: ignore # noqa: F401,F403\n\n"
    + "_TYPE_EXPORT_EXCLUDES = {\n"
    + '    "Any",\n'
    + '    "Literal",\n'
    + '    "Optional",\n'
    + '    "Required",\n'
    + '    "TYPE_CHECKING",\n'
    + '    "TypedDict",\n'
    + '    "Union",\n'
    + "}\n"
    + "__all__ = [name for name in _models_all if name not in _TYPE_EXPORT_EXCLUDES]\n"
    + "__all__.extend([p for p in _patch_all if p not in __all__])  # pyright: ignore\n"
    + "_patch_sdk()\n"
)

ROOT_INIT = (
    COPYRIGHT
    + "# coding=utf-8\n"
    + "# --------------------------------------------------------------------------\n"
    + "# Copyright (c) Microsoft Corporation. All rights reserved.\n"
    + "# Licensed under the MIT License. See License.txt in the project root for license information.\n"
    + "# --------------------------------------------------------------------------\n\n"
    + '"""Model-only generated package surface."""\n\n'
    + "from .models import *  # type: ignore # noqa: F401,F403\n"
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _remove_pycache(root: Path) -> None:
    for pycache in root.rglob("__pycache__"):
        shutil.rmtree(pycache)


def finalize(generated_root: Path) -> None:
    if not generated_root.exists():
        raise FileNotFoundError(f"Generated root not found: {generated_root}")

    custom_patch = PACKAGE_ROOT / "customizations" / "responses" / "models" / "_patch.py"
    if not custom_patch.exists():
        raise FileNotFoundError(f"Response customization not found: {custom_patch}")

    _remove_pycache(generated_root)
    _write(generated_root / "__init__.py", ROOT_INIT)
    _write(generated_root / "_types.py", TYPES_SHIM)
    _write(generated_root / "_utils" / "__init__.py", "")
    _write(generated_root / "_utils" / "model_base.py", MODEL_BASE)
    _write(generated_root / "_utils" / "serialization.py", SERIALIZATION)
    _write(generated_root / "models" / "_enums.py", ENUM_FALLBACK)
    _write(generated_root / "models" / "_models.py", TYPEDDICT_MODELS)
    _write(generated_root / "models" / "__init__.py", MODELS_INIT)
    shutil.copyfile(custom_patch, generated_root / "models" / "_patch.py")
    _write(generated_root / "py.typed", "")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generated-root", type=Path, required=True)
    args = parser.parse_args()
    finalize(args.generated_root)


if __name__ == "__main__":
    main()
