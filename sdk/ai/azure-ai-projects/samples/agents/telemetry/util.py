# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

_AGENTS_UTIL_PATH = Path(__file__).resolve().parents[1] / "util.py"
_PKG_ROOT = Path(__file__).resolve().parents[3]
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

_SPEC = spec_from_file_location("samples_agents_util", _AGENTS_UTIL_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Unable to load agent samples util from {_AGENTS_UTIL_PATH}")

_MODULE = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

create_version_with_endpoint = _MODULE.create_version_with_endpoint
create_version_with_endpoint_async = _MODULE.create_version_with_endpoint_async
