import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).parents[1] / "scripts" / "prepare_emitter_package_update.py"
SPEC = importlib.util.spec_from_file_location("prepare_emitter_package_update", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PrepareEmitterPackageUpdateTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.repository = Path(self.directory.name) / "repository"
        self.eng = self.repository / "eng"
        self.eng.mkdir(parents=True)
        self.artifact = Path(self.directory.name) / "artifact"
        self.artifact.mkdir()
        self.original = {
            "name": "emitter",
            "dependencies": {"@azure-tools/typespec-python": "0.1.0"},
            "devDependencies": {"@typespec/compiler": "^1.0.0"},
        }
        self.original_lock = {
            "name": "emitter",
            "lockfileVersion": 3,
            "requires": True,
            "packages": {
                "": copy.deepcopy(self.original),
                "node_modules/@azure-tools/typespec-python": {
                    "version": "0.1.0",
                    "resolved": MODULE.CFS_REGISTRY + "python/-/python-0.1.0.tgz",
                },
                "node_modules/@typespec/compiler": {
                    "version": "1.0.0",
                    "resolved": MODULE.CFS_REGISTRY + "compiler/-/compiler-1.0.0.tgz",
                },
            },
        }
        self.manifest = copy.deepcopy(self.original)
        self.manifest["dependencies"]["@azure-tools/typespec-python"] = "0.2.0"
        self.lock = copy.deepcopy(self.original_lock)
        self.lock["packages"][""] = copy.deepcopy(self.manifest)
        self.lock["packages"]["node_modules/@azure-tools/typespec-python"].update(
            version="0.2.0", resolved=MODULE.CFS_REGISTRY + "python/-/python-0.2.0.tgz"
        )
        self.write(self.eng, self.original, self.original_lock)
        self.write(self.artifact, self.manifest, self.lock)
        self.original_bytes = {
            name: (self.eng / name).read_bytes() for name in MODULE.FILES
        }

    def write(self, directory, manifest, lock):
        for name, value in zip(MODULE.FILES, (manifest, lock)):
            (directory / name).write_text(json.dumps(value), encoding="utf-8")

    def prepare(self):
        return MODULE.prepare_update(self.artifact, self.repository)

    def assert_rejected(self):
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertEqual(
            self.original_bytes,
            {name: (self.eng / name).read_bytes() for name in MODULE.FILES},
        )

    def test_prepares_version_update_without_executing_package_content(self):
        self.lock["packages"]["node_modules/@azure-tools/typespec-python"][
            "hasInstallScript"
        ] = True
        self.write(self.artifact, self.manifest, self.lock)
        with mock.patch(
            "subprocess.run",
            side_effect=AssertionError("Must not execute package code"),
        ):
            self.assertTrue(self.prepare())
        self.assertEqual(
            json.loads((self.eng / MODULE.FILES[0]).read_text()), self.manifest
        )
        self.assertEqual(
            json.loads((self.eng / MODULE.FILES[1]).read_text()), self.lock
        )

    def test_no_version_change_ignores_lockfile_only_changes(self):
        lock = copy.deepcopy(self.original_lock)
        lock["packages"]["node_modules/@typespec/compiler"]["license"] = "MIT"
        self.write(self.artifact, self.original, lock)
        self.assertFalse(self.prepare())
        self.assertEqual(
            self.original_bytes,
            {name: (self.eng / name).read_bytes() for name in MODULE.FILES},
        )

    def test_rejects_manifest_scripts_new_dependencies_and_dependency_protocols(self):
        candidates = []
        scripts = copy.deepcopy(self.manifest)
        scripts["scripts"] = {"prepare": "echo malicious"}
        candidates.append(scripts)
        added = copy.deepcopy(self.manifest)
        added["dependencies"]["unexpected-package"] = "1.0.0"
        candidates.append(added)
        moved = copy.deepcopy(self.manifest)
        moved["devDependencies"]["@azure-tools/typespec-python"] = moved[
            "dependencies"
        ].pop("@azure-tools/typespec-python")
        candidates.append(moved)
        for version in (
            "file:../payload",
            "https://example.invalid/a.tgz",
            "git+https://example.invalid/a",
            "npm:x@1.0.0",
            "1.0.0\n::warning::payload",
        ):
            manifest = copy.deepcopy(self.manifest)
            manifest["dependencies"]["@azure-tools/typespec-python"] = version
            candidates.append(manifest)
        for manifest in candidates:
            with self.subTest(manifest=manifest):
                self.write(self.artifact, manifest, self.lock)
                self.assert_rejected()

    def test_rejects_extra_artifact_files(self):
        (self.artifact / "payload.sh").write_text("exit 99")
        self.assert_rejected()

    def test_rejects_symlink_and_directory_inputs(self):
        target = self.artifact / MODULE.FILES[0]
        with mock.patch.object(
            Path, "is_symlink", autospec=True, side_effect=lambda path: path == target
        ):
            self.assert_rejected()
        target.unlink()
        target.mkdir()
        self.assert_rejected()

    def test_rejects_invalid_json_and_large_inputs(self):
        for content in ("not json", "[]"):
            with self.subTest(content=content):
                (self.artifact / MODULE.FILES[0]).write_text(content)
                self.assert_rejected()
        self.write(self.artifact, self.manifest, self.lock)
        with mock.patch.object(MODULE, "MAX_JSON_BYTES", 1):
            self.assert_rejected()

    def test_rejects_lockfile_metadata_and_root_dependency_changes(self):
        candidates = []
        scripts = copy.deepcopy(self.lock)
        scripts["packages"][""]["scripts"] = {"prepare": "echo malicious"}
        candidates.append(scripts)
        mismatch = copy.deepcopy(self.lock)
        mismatch["packages"][""]["dependencies"] = self.original["dependencies"]
        candidates.append(mismatch)
        wrong_version = copy.deepcopy(self.lock)
        wrong_version["lockfileVersion"] = 2
        candidates.append(wrong_version)
        for lock in candidates:
            with self.subTest(lock=lock):
                self.write(self.artifact, self.manifest, lock)
                self.assert_rejected()

    def test_rejects_lockfile_path_and_registry_escapes(self):
        package = "node_modules/@azure-tools/typespec-python"
        for resolved in (
            "https://example.invalid/payload.tgz",
            "file:../payload",
            MODULE.CFS_REGISTRY + "%2e%2e/payload.tgz",
            MODULE.CFS_REGISTRY + "payload.tgz?query=1",
        ):
            with self.subTest(resolved=resolved):
                lock = copy.deepcopy(self.lock)
                lock["packages"][package]["resolved"] = resolved
                self.write(self.artifact, self.manifest, lock)
                self.assert_rejected()
        for path in (
            "node_modules/../.git/hooks/pre-commit",
            "node_modules\\payload",
            "/tmp/payload",
        ):
            with self.subTest(path=path):
                lock = copy.deepcopy(self.lock)
                lock["packages"][path] = lock["packages"].pop(package)
                self.write(self.artifact, self.manifest, lock)
                self.assert_rejected()
        for key, value in (("link", True), ("version", "file:../payload")):
            with self.subTest(key=key):
                lock = copy.deepcopy(self.lock)
                lock["packages"][package][key] = value
                self.write(self.artifact, self.manifest, lock)
                self.assert_rejected()

    def test_cli_signals_only_validated_changes(self):
        output = Path(self.directory.name) / "output"
        for manifest, lock, expected in (
            (self.original, self.original_lock, "false"),
            (self.manifest, self.lock, "true"),
        ):
            with self.subTest(expected=expected):
                self.write(self.artifact, manifest, lock)
                output.write_text("")
                self.write(self.eng, self.original, self.original_lock)
                with mock.patch.object(
                    Path, "cwd", return_value=self.repository
                ), mock.patch.object(
                    sys, "argv", [str(SCRIPT), str(self.artifact)]
                ), mock.patch.dict(
                    os.environ, {"GITHUB_OUTPUT": str(output)}
                ):
                    MODULE.main()
                self.assertEqual(output.read_text(), f"available={expected}\n")
        output.write_text("")
        (self.artifact / "payload.sh").write_text("exit 99")
        with mock.patch.object(
            Path, "cwd", return_value=self.repository
        ), mock.patch.object(
            sys, "argv", [str(SCRIPT), str(self.artifact)]
        ), mock.patch.dict(
            os.environ, {"GITHUB_OUTPUT": str(output)}
        ):
            with self.assertRaises(ValueError):
                MODULE.main()
        self.assertEqual(output.read_text(), "")


if __name__ == "__main__":
    unittest.main()
