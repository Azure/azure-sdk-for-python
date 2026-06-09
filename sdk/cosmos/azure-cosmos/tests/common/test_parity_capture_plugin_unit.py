# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests for parity-capture plugin registration safety."""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest


_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
_PLUGIN_PATH = _REPO_ROOT / "tests" / "common" / "parity_capture_plugin.py"


def _load_plugin():
    mod_name = "_parity_capture_plugin_under_test"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, str(_PLUGIN_PATH))
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


class PluginRegistryTests(unittest.TestCase):
    """The plugin must stay reusable across migrated CRUD operations."""

    def setUp(self):
        self.plugin = _load_plugin()

    def test_registry_contains_migrated_crud_ops(self):
        """create/delete/read must all be registered for sync + aio capture."""
        registry = self.plugin._OP_REGISTRY  # noqa: SLF001
        for op in ("create_item", "delete_item", "read_item"):
            self.assertIn(op, registry)
            self.assertIn("sync", registry[op])
            self.assertIn("aio", registry[op])
            self.assertTrue(callable(registry[op]["sync"]))
            self.assertTrue(callable(registry[op]["aio"]))


if __name__ == "__main__":
    unittest.main()

