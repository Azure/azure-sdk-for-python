# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Run the per-operation rust smoke scripts as one pytest.

Each smoke_test_rust_<op>.py is a standalone script with a main() that returns
0 (round trip OK), 1 (wrong outcome), or 2 (binding not built). This wraps all
of them: exit 2 becomes a skip, 1 becomes a failure. Run with -m cosmosRustSmoke,
or it rides the emulator lane. Skips without the rust binding or an account.
"""
from __future__ import annotations

import importlib.util
import os
import pathlib

import pytest

pytestmark = [pytest.mark.cosmosEmulator, pytest.mark.cosmosRustSmoke]

_TESTS_ROOT = pathlib.Path(__file__).resolve().parent.parent
_SMOKE = sorted(_TESTS_ROOT.glob("*_item/smoke_test_rust_*.py"))


def _have_binding() -> bool:
    try:
        from azure.cosmos import _rust  # noqa: F401
        return True
    except ImportError:
        return False


def _have_account() -> bool:
    return bool(os.environ.get("ACCOUNT_HOST"))


@pytest.mark.skipif(not _SMOKE, reason="no smoke scripts found")
@pytest.mark.parametrize("script", _SMOKE, ids=lambda p: p.parent.name)
def test_smoke_round_trip(script):
    """Run one operation's smoke script; 0 = pass, 2 = skip (not built), 1 = fail."""
    if not _have_binding():
        pytest.skip("rust binding not built (maturin develop)")
    if not _have_account():
        pytest.skip("no account set (ACCOUNT_HOST)")
    spec = importlib.util.spec_from_file_location(script.stem, script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    code = mod.main()
    if code == 2:
        pytest.skip("binding/op missing — script reported not built")
    assert code == 0, "{} smoke round trip failed (exit {})".format(script.parent.name, code)

