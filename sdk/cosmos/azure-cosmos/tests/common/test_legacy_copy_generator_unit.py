# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Unit tests for the legacy-copy generator (no network).

Fidelity: the generator reproduces the cleanest existing example file for each
structural variation byte-for-byte (apart from line-ending / trailing-newline
normalisation) -- sync instance ``test_none_options.py``, sync class fixture
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
from unittest.mock import Mock


_THIS = pathlib.Path(__file__).resolve()
_TESTS_DIR = _THIS.parents[1]
_REPO_ROOT = _TESTS_DIR.parent
_GENERATOR_PATH = _REPO_ROOT / "scripts" / "v5" / "legacy_copy_generator.py"
_ENFORCER_PATH = _TESTS_DIR / "common" / "test_legacy_migration_enforcer_unit.py"


def _load_module_by_path(path, name):
    """Load a test support script from its repository path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_gen = _load_module_by_path(_GENERATOR_PATH, "_legacy_copy_generator_under_test")


def _norm(text):
    """Normalize line endings and the final newline for text comparison."""
    return text.replace("\r\n", "\n").rstrip("\n") + "\n"


class TestGeneratorReproducesCanonicalExemplars(unittest.TestCase):
    """The generator output matches the committed example file for each variation."""

    _GOLDEN = {
        "CREATE_ITEM_SYNC_NONE_OPTIONS": "create_item/sync/test_none_options.py",
        "CREATE_ITEM_SYNC_HEADERS": "create_item/sync/test_headers.py",
        "CREATE_ITEM_AIO_HEADERS": "create_item/aio/test_headers.py",
    }

    def test_exemplars_reproduced_byte_for_byte_rust(self):
        """Prove generated tests match the committed examples."""
        for spec_attr, rel in self._GOLDEN.items():
            with self.subTest(exemplar=rel):
                committed = (_TESTS_DIR / rel).read_text(encoding="utf-8")
                generated = _gen.render_legacy_file(getattr(_gen, spec_attr))
                self.assertEqual(
                    _norm(generated), _norm(committed),
                    "generator output no longer matches tests/" + rel,
                )

    def test_init_py_reproduced_rust(self):
        """Prove generated package files match the committed package marker."""
        with tempfile.TemporaryDirectory() as tmp:
            path = _gen.write_legacy_family(_gen.CREATE_ITEM_SYNC_NONE_OPTIONS, tmp)
            for package in (path.parent, path.parent.parent):
                marker = package / "__init__.py"
                self.assertEqual(_norm(_gen.render_init_py()), _norm(marker.read_text(encoding="utf-8")))
            self.assertEqual(path.parent, pathlib.Path(tmp) / "create_item" / "sync")

    def test_existing_package_marker_is_preserved_rust(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = pathlib.Path(tmp) / "create_item" / "sync"
            directory.mkdir(parents=True)
            marker = directory / "__init__.py"
            marker.write_text("# Existing package setup\n", encoding="utf-8")
            _gen.write_legacy_family(_gen.CREATE_ITEM_SYNC_NONE_OPTIONS, tmp)
            self.assertEqual(marker.read_text(encoding="utf-8"), "# Existing package setup\n")


class TestGeneratedOutputPassesEnforcer(unittest.TestCase):
    """Generated copies pass all of the enforcer's checks."""

    _ENFORCER_CHECKS = (
        "test_legacy_folders_discovered_rust",
        "test_every_legacy_folder_is_a_package_rust",
        "test_every_test_method_has_a_source_comment_rust",
        "test_every_source_reference_resolves_rust",
        "test_every_legacy_file_pins_rust_backend_rust",
        "test_no_unstructured_skips_rust",
        "test_every_copy_keeps_original_lane_markers_rust",
    )

    def test_bundled_specs_generate_enforcer_clean_tree_rust(self):
        """Prove every bundled test description passes structural checks."""
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

    def test_async_none_options_is_well_formed_rust(self):
        """Prove an async generated test opens, uses, and closes a Rust client."""
        text = _gen.render_legacy_file(_gen.CREATE_ITEM_AIO_NONE_OPTIONS)
        for needle in (
            "from azure.cosmos.aio import CosmosClient",
            "unittest.IsolatedAsyncioTestCase",
            "async def asyncSetUp(self):",
            "await self.client.__aenter__()",
            "async def asyncTearDown(self):",
            "await self.client.close()",
            "async def test_container_create_item_none_options_async_rust(self):",
            "created = await self.container.create_item(",
            '_backend="rust"',
        ):
            self.assertIn(needle, text, needle)

    def test_sync_read_item_family_is_well_formed_rust(self):
        """Prove a sync generated read test keeps its source and Rust selection."""
        text = _gen.render_legacy_file(_gen.READ_ITEM_SYNC_NONE_OPTIONS)
        self.assertIn('_backend="rust"', text)
        self.assertIn("def setUp(self) -> None:", text)
        self.assertIn(
            "# Source: tests/test_none_options.py::TestNoneOptions."
            "test_container_read_item_none_options",
            text,
        )

    def test_create_specs_do_not_emit_retired_trigger_options_rust(self):
        for spec in (_gen.CREATE_ITEM_SYNC_NONE_OPTIONS, _gen.CREATE_ITEM_AIO_NONE_OPTIONS):
            with self.subTest(surface=spec.surface):
                text = _gen.render_legacy_file(spec)
                self.assertNotIn("pre_trigger_include", text)
                self.assertNotIn("post_trigger_include", text)


class TestGeneratedLaneMarkers(unittest.TestCase):
    """Lane markers come from the originals, not a hard-coded default."""

    @staticmethod
    def _spec(*sources, class_markers=None):
        methods = tuple(
            _gen.LegacyMethod(name="test_m{}".format(i), source=src, body="        pass")
            for i, src in enumerate(sources)
        )
        return _gen.LegacyFileSpec(
            op="op", surface="sync", filename="test_x.py", class_name="TestX",
            db_id_prefix="x", docstring="x", methods=methods, class_markers=class_markers,
        )

    def _write(self, root, rel, text):
        path = pathlib.Path(root) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_live_only_original_keeps_live_markers_rust(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, "tests/test_a.py", (
                "import pytest\n"
                "@pytest.mark.cosmosCircuitBreaker\n@pytest.mark.cosmosLong\n"
                "class TestA:\n    def test_one(self):\n        pass\n"
            ))
            text = _gen.render_legacy_file(self._spec("tests/test_a.py::TestA.test_one"), source_root=tmp)
        self.assertIn("@pytest.mark.cosmosCircuitBreaker\n@pytest.mark.cosmosLong\nclass TestX", text)
        self.assertNotIn("cosmosEmulator", text)

    def test_disagreeing_originals_get_method_markers_rust(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, "tests/test_a.py", (
                "import pytest\npytestmark = [pytest.mark.cosmosEmulator]\n"
                "class TestA:\n    def test_one(self):\n        pass\n"
                "    @pytest.mark.cosmosQuery\n    def test_two(self):\n        pass\n"
            ))
            text = _gen.render_legacy_file(self._spec(
                "tests/test_a.py::TestA.test_one", "tests/test_a.py::TestA.test_two"), source_root=tmp)
        self.assertIn("class TestX(unittest.TestCase):", text)
        self.assertNotIn("@pytest.mark.cosmosEmulator\nclass", text)
        self.assertIn("    @pytest.mark.cosmosEmulator\n    def test_m0_rust", text)
        self.assertIn("    @pytest.mark.cosmosEmulator\n    @pytest.mark.cosmosQuery\n    def test_m1_rust", text)

    def test_unresolvable_source_fails_instead_of_defaulting_rust(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "cannot derive markers"):
                _gen.render_legacy_file(self._spec("tests/missing.py::TestA.test_one"), source_root=tmp)


class TestGeneratedSyncFixtureCleanup(unittest.TestCase):
    """Exercise the rendered scaffold without making service requests."""

    def test_cleanup_covers_setup_and_cleanup_failures_rust(self):
        for failure in (None, "database", "container", "delete"):
            with self.subTest(failure=failure):
                namespace = {"__name__": "generated_none_options"}
                exec(_gen.render_legacy_file(_gen.CREATE_ITEM_SYNC_NONE_OPTIONS), namespace)
                cleanup = Mock()
                client = Mock(close=cleanup.close, delete_database=cleanup.delete)
                container = client.create_database.return_value.create_container.return_value
                container.create_item.side_effect = lambda body, **kwargs: dict(body)
                if failure == "database":
                    client.create_database.side_effect = RuntimeError("database setup failed")
                elif failure == "container":
                    client.create_database.return_value.create_container.side_effect = RuntimeError(
                        "container setup failed"
                    )
                elif failure == "delete":
                    cleanup.delete.side_effect = RuntimeError("database cleanup failed")
                namespace["CosmosClient"] = Mock(return_value=client)
                case = namespace["TestNoneOptions"]("test_container_create_item_none_options_rust")
                result = unittest.TestResult()
                case.run(result)
                self.assertEqual(result.testsRun, 1)
                self.assertEqual(result.failures, [])
                self.assertEqual(len(result.errors), int(failure is not None))
                self.assertEqual(
                    [call[0] for call in cleanup.mock_calls],
                    ["close"] if failure == "database" else ["delete", "close"],
                )
                if failure != "database":
                    cleanup.delete.assert_called_once_with(case._db_id)
                self.assertEqual(namespace["CosmosClient"].call_args.kwargs["_backend"], "rust")


if __name__ == "__main__":
    unittest.main()
