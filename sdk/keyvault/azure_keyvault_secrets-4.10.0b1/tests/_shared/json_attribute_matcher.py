# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json

_has_json_body = lambda req: req.body and "json" in req.headers.get("Content-Type", "")


def json_attribute_matcher(r1, r2):
    """Tests whether two vcr.py requests have JSON content with identical attributes (ignoring values)."""

    if _has_json_body(r1) and _has_json_body(r2):
        c1 = json.loads(str(r1.body))
        c2 = json.loads(str(r2.body))
        assert sorted(c1.keys()) == sorted(c2.keys())
