# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import json

def _to_json_primitive(obj):
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [_to_json_primitive(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _to_json_primitive(v) for k, v in obj.items()}
    for method in ("to_dict", "as_dict", "dict", "serialize"):
        if hasattr(obj, method):
            try:
                return _to_json_primitive(getattr(obj, method)())
            except Exception:
                pass
    if hasattr(obj, "__dict__"):
        return _to_json_primitive({k: v for k, v in vars(obj).items() if not k.startswith("_")})
    return str(obj)

def pprint(str) -> None:
    print(json.dumps(_to_json_primitive(str), indent=2))