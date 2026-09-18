# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

_SAMPLES_UTIL_PATH = Path(__file__).resolve().parents[1] / "util.py"

_PKG_ROOT = Path(__file__).resolve().parents[2]
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))
from samples.util import create_version_with_endpoint as _create_version_with_endpoint
from samples.util import create_version_with_endpoint_async as _create_version_with_endpoint_async

if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

_SPEC = spec_from_file_location("samples_shared_util", _SAMPLES_UTIL_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Unable to load shared samples util from {_SAMPLES_UTIL_PATH}")

_MODULE = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

create_version_with_endpoint = _create_version_with_endpoint
create_version_with_endpoint_async = _create_version_with_endpoint_async
