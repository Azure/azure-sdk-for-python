# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests for the legacy-copy generator (no network).

Fidelity: the generator reproduces the cleanest existing example file for each
structural variation byte-for-byte (apart from line-ending / trailing-newline
normalisation) -- sync instance ``test_none_options.py``, sync class-fixtured
``test_headers.py``, and async ``test_headers.py``.

Enforcement: output generated from the bundled specs passes the existing
enforcer (``test_legacy_migration_enforcer_unit.py``), pointed at a throwaway
generated tree with ``# Source:`` lines resolved against the real repo.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile
import unittest


_THIS = pathlib.Path(__file__).resolve()
_TESTS_DIR = _THIS.parents[1]
_REPO_ROOT = _TESTS_DIR.parent
_GENERATOR_PATH = _REPO_ROOT / "scripts" / "v5" / "legacy_copy_generator.py"
_ENFORCER_PATH = _TESTS_DIR / "common" / "test_legacy_migration_enforcer_unit.py"


def _load_module_by_path(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_gen = _load_module_by_path(_GENERATOR_PATH, "_legacy_copy_generator_under_test")


def _norm(text):
    return text.replace("\r\n", "\n").rstrip("\n") + "\n"


class TestGeneratorReproducesCanonicalExemplars(unittest.TestCase):
    """The generator output matches the committed example file for each variation."""

    _GOLDEN = {
        "CREATE_ITEM_SYNC_NONE_OPTIONS": "create_item/sync/legacy/test_none_options.py",
        "CREATE_ITEM_SYNC_HEADERS": "create_item/sync/legacy/test_headers.py",
        "CREATE_ITEM_AIO_HEADERS": "create_item/aio/legacy/test_headers.py",
    }

    def test_exemplars_reproduced_byte_for_byte(self):
        for spec_attr, rel in self._GOLDEN.items():
            with self.subTest(exemplar=rel):
                committed = (_TESTS_DIR / rel).read_text(encoding="utf-8")
                generated = _gen.render_legacy_file(getattr(_gen, spec_attr))
                self.assertEqual(
                    _norm(generated), _norm(committed),
                    "generator output no longer matches tests/" + rel,
                )

    def test_init_py_reproduced(self):
        committed = (
            _TESTS_DIR / "create_item" / "sync" / "legacy" / "__init__.py"
        ).read_text(encoding="utf-8")
        self.assertEqual(_norm(_gen.render_init_py()), _norm(committed))


class TestGeneratedOutputPassesEnforcer(unittest.TestCase):
    """Generated copies pass all of the enforcer's checks."""

    _ENFORCER_CHECKS = (
        "test_legacy_folders_discovered",
        "test_every_legacy_folder_is_a_package",
        "test_every_test_method_has_a_source_comment",
        "test_every_source_reference_resolves",
        "test_every_legacy_file_pins_rust_backend",
        "test_no_unstructured_skips",
    )

    def test_bundled_specs_generate_enforcer_clean_tree(self):
        enforcer = _load_module_by_path(_ENFORCER_PATH, "_legacy_enforcer_under_test")
        original_tests_dir = enforcer._TESTS_DIR
        original_pkg_root = enforcer._PKG_ROOT
        with tempfile.TemporaryDirectory() as tmp:
            tests_root = pathlib.Path(tmp)
            for spec in _gen.BUNDLED_SPECS:
                _gen.write_legacy_family(spec, tests_root)
            enforcer._TESTS_DIR = tests_root
            enforcer._PKG_ROOT = _REPO_ROOT
            try:
                for check in self._ENFORCER_CHECKS:
                    case = enforcer.LegacyMigrationEnforcerTests(check)
                    getattr(case, check)()
            finally:
                enforcer._TESTS_DIR = original_tests_dir
                enforcer._PKG_ROOT = original_pkg_root


class TestGeneratedShapesAreWellFormed(unittest.TestCase):
    """The async and instance-fixture surfaces render the right scaffold."""

    def test_async_none_options_is_well_formed(self):
        text = _gen.render_legacy_file(_gen.CREATE_ITEM_AIO_NONE_OPTIONS)
        for needle in (
            "from azure.cosmos.aio import CosmosClient",
            "unittest.IsolatedAsyncioTestCase",
            "async def asyncSetUp(self):",
            "await self.client.__aenter__()",
            "async def asyncTearDown(self):",
            "await self.client.close()",
            "async def test_container_create_item_none_options_async(self):",
            "created = await self.container.create_item(",
            '_backend="rust"',
        ):
            self.assertIn(needle, text, needle)

    def test_sync_read_item_family_is_well_formed(self):
        text = _gen.render_legacy_file(_gen.READ_ITEM_SYNC_NONE_OPTIONS)
        self.assertIn('_backend="rust"', text)
        self.assertIn("def setUp(self) -> None:", text)
        self.assertIn(
            "# Source: tests/test_none_options.py::TestNoneOptions."
            "test_container_read_item_none_options",
            text,
        )


if __name__ == "__main__":
    unittest.main()