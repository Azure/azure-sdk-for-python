# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Cross-language parity guard for the header/option mapping -- no network.

The options -> wire-header mapping is split across two languages: the Python
prep (``_request_prep.flatten_options_to_headers``) owns truthy-gating and a few
translations, while the Rust fast path (``extract_op_modifiers`` in
``azure_cosmos_rust/src/wire/request.rs``) owns the camelCase -> ``x-ms-*`` table plus
typed-field lifting. Adding a knob is therefore a DUAL edit.

The landmine: the Rust match ends in ``_ => continue`` -- any option-key Python
emits that Rust does not recognise is SILENTLY DROPPED (no error, wrong wire
bytes, green tests). A knob added on the Python side alone quietly no-ops on the
fast path.

These tests make that drift impossible to MISS instead of impossible to HAPPEN:
they parse the recognised keys straight out of ``wire/request.rs`` and assert they stay
in lockstep with ``_request_prep.RUST_HANDLED_OPTION_KEYS``. They need no built
extension and no network -- just the two source files. If you add (or rename) an
option-key on either side without the other, exactly one of these fails with a
message naming the offending key and both files to edit.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from azure.cosmos._helpers._request_prep import RUST_HANDLED_OPTION_KEYS

# wire/request.rs lives at <pkg-root>/azure_cosmos_rust/src/wire/request.rs; this test file is at
# <pkg-root>/tests/common/, so two parents up from the test dir is the pkg root.
_WIRE_RS = (
    Path(__file__).resolve().parents[2] / "azure_cosmos_rust" / "src" / "wire" / "request.rs"
)


def _extract_op_modifiers_body() -> str:
    """Return just the body of ``fn extract_op_modifiers`` from wire/request.rs.

    Scoping the parse to that one function keeps unrelated string literals
    elsewhere in the file from polluting the recognised-key set.
    """
    src = _WIRE_RS.read_text(encoding="utf-8")
    start = src.find("fn extract_op_modifiers")
    assert start != -1, f"could not find extract_op_modifiers in {_WIRE_RS}"
    # The next top-level ``\nfn `` after the start ends this function.
    end = src.find("\nfn ", start + 1)
    return src[start:end if end != -1 else len(src)]


def _rust_recognised_keys() -> set:
    """All keys ``extract_op_modifiers`` matches explicitly, lower-cased.

    Two shapes are recognised in the function:
      * typed-field guards   ``lower == "<key>"``
      * wire-name match arms ``"<key>" => ...``
    Rust lower-cases the incoming key first, so every captured key is already
    the lower-cased form we compare against.
    """
    body = _extract_op_modifiers_body()
    typed = set(re.findall(r'lower\s*==\s*"([^"]+)"', body))
    arms = set(re.findall(r'"([^"]+)"\s*=>', body))
    return typed | arms


# The camelCase option-keys (no hyphen / underscore) that the Rust side
# translates. Wire-name-style keys it also recognises -- ``if-match``,
# ``if-none-match`` (produced by Python's accessCondition translation),
# ``x-ms-activity-id``, ``x-ms-session-token``, ``__overall_timeout_seconds``
# (sentinels / already-wire-name forms) -- are intentionally NOT part of the
# camelCase option-key contract and are excluded by the ``isalpha`` filter.
# ``prefer`` is the one alpha-only exception: it is a real HTTP header name
# forwarded verbatim (the ``other == "prefer" => None`` passthrough arm), not a
# camelCase option-key, so it is excluded explicitly.
_WIRE_NAME_PASSTHROUGH = frozenset({"prefer"})


def _rust_camelcase_option_keys() -> set:
    return {
        k for k in _rust_recognised_keys()
        if k.isalpha() and k not in _WIRE_NAME_PASSTHROUGH
    }


def test_every_python_option_key_is_handled_by_rust():
    """Forward parity: no Python knob silently dropped by ``_ => continue``.

    Every key the Python prep hands to the binding as raw camelCase
    (``RUST_HANDLED_OPTION_KEYS``) must have a matching arm in
    ``extract_op_modifiers``; otherwise it hits ``_ => continue`` and vanishes on
    the wire.
    """
    recognised = _rust_recognised_keys()
    missing = sorted(
        key for key in RUST_HANDLED_OPTION_KEYS if key.lower() not in recognised
    )
    assert not missing, (
        "These option-keys are emitted by the Python prep "
        "(_request_prep.RUST_HANDLED_OPTION_KEYS) but have NO matching arm in "
        "extract_op_modifiers (azure_cosmos_rust/src/wire/request.rs). On the Rust fast "
        "path they would hit `_ => continue` and be SILENTLY DROPPED -- wrong "
        f"wire bytes with green tests: {missing}. Add the wire-name arm in "
        "wire/request.rs (and rebuild the extension)."
    )


def test_no_rust_only_option_key():
    """Reverse parity: the Rust table has no camelCase key Python never declares.

    A camelCase arm in ``extract_op_modifiers`` with no entry in
    ``RUST_HANDLED_OPTION_KEYS`` means the contract / docs drifted (or a knob was
    added Rust-first); flag it so the shared vocabulary stays documented in one
    place.
    """
    contract = {k.lower() for k in RUST_HANDLED_OPTION_KEYS}
    extra = sorted(_rust_camelcase_option_keys() - contract)
    assert not extra, (
        "These camelCase keys are translated by extract_op_modifiers "
        "(azure_cosmos_rust/src/wire/request.rs) but are missing from "
        "_request_prep.RUST_HANDLED_OPTION_KEYS: "
        f"{extra}. Add them to the Python contract so the split mapping stays "
        "documented and the forward parity test covers them."
    )


def test_contract_is_nonempty_and_parse_found_keys():
    """Guard the guard: a silent parse failure must not make parity vacuous.

    If the regexes ever stop matching (wire/request.rs refactor), the two tests above
    could pass trivially against an empty set. Assert we actually parsed the
    known-present keys so the guard cannot rot into a no-op.
    """
    recognised = _rust_recognised_keys()
    assert RUST_HANDLED_OPTION_KEYS, "the Python contract set is unexpectedly empty"
    # A few keys that must always be present unless the design changes wholesale.
    for anchor in ("pretriggerinclude", "indexingdirective", "if-match"):
        assert anchor in recognised, (
            f"expected '{anchor}' among the keys parsed from extract_op_modifiers; "
            "the wire/request.rs parse may be broken -- fix the regexes in this test."
        )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
