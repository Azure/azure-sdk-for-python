# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Offline tests for the cloud workflow, using disposable Git repositories."""

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "regenerate.py"
SPEC = importlib.util.spec_from_file_location("cloud_regeneration", SCRIPT)
assert SPEC and SPEC.loader
workflow = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workflow)

SOURCE_COMMIT = "a" * 40
NEW_SOURCE_COMMIT = "b" * 40
ORIGINAL_CODE = "value = 1\n"


class CloudRegenerationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        self.package = self.repo.joinpath(*workflow.PACKAGE_PATH.split("/"))
        self.package.mkdir(parents=True)
        self.source = self.package / "example.py"
        self.source.write_text(ORIGINAL_CODE, encoding="utf-8")
        self.location = self.package / "tsp-location.yaml"
        self.location.write_text(
            f"directory: specification/example\ncommit: {SOURCE_COMMIT}\nrepo: Azure/azure-rest-api-specs\n",
            encoding="utf-8",
        )
        self.cli_dir = self.repo / "eng" / "common" / "tsp-client"
        self.cli_dir.mkdir(parents=True)
        (self.cli_dir / "package.json").write_text(
            json.dumps({"dependencies": {"@azure-tools/typespec-client-generator-cli": "1.2.3"}}),
            encoding="utf-8",
        )
        (self.repo / "eng" / "emitter-package.json").write_text(
            json.dumps({"dependencies": {"@azure-tools/typespec-python": "4.5.6"}}),
            encoding="utf-8",
        )
        (self.repo / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
        (self.repo / ".gitattributes").write_text("* text=auto eol=lf\n", encoding="utf-8")
        self.git("init", "--quiet")
        self.git("add", ".")
        self.git(
            "-c",
            "user.name=Workflow Test",
            "-c",
            "user.email=workflow-test@example.invalid",
            "commit",
            "--quiet",
            "-m",
            "Initial test fixture",
        )
        self.sdk_commit = self.git("rev-parse", "HEAD").decode().strip()
        self.artifact = self.root / "artifact"
        self.addCleanup(patch.stopall)
        patch.object(workflow, "PACKAGE_ROOT", self.package).start()
        self.commands = []

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.repo, stderr=subprocess.PIPE)

    def result(self, patch_bytes, source_commit=SOURCE_COMMIT):
        return {
            "package": workflow.PACKAGE_PATH,
            "sdk_commit": self.sdk_commit,
            "typespec_commit": source_commit,
            "checks": [{"command": workflow.shlex.join(command), "result": "passed"} for command in workflow.CHECKS],
            "changed_files": [f"{workflow.PACKAGE_PATH}/example.py"],
            "patch_sha256": hashlib.sha256(patch_bytes).hexdigest(),
        }

    def write_artifact(self, patch_bytes, result=None):
        self.artifact.mkdir()
        (self.artifact / "regeneration.patch").write_bytes(patch_bytes)
        (self.artifact / "result.json").write_text(json.dumps(result or self.result(patch_bytes)), encoding="utf-8")

    def source_patch(self):
        self.source.write_text("value = 2\n", encoding="utf-8")
        patch_bytes = self.git("diff", "--binary")
        self.source.write_text(ORIGINAL_CODE, encoding="utf-8")
        return patch_bytes

    def apply(self, typespec_commit=""):
        workflow.apply(argparse.Namespace(artifact_dir=self.artifact, typespec_commit=typespec_commit))

    def fake_runner(self, command, cwd):
        command = [str(arg) for arg in command]
        self.commands.append((command, cwd))
        if command[0] == "npm":
            installed = self.cli_dir / "node_modules" / "@azure-tools" / "typespec-client-generator-cli"
            installed.mkdir(parents=True)
            (installed / "package.json").write_text(json.dumps({"version": "1.2.3"}), encoding="utf-8")
        elif command[0] == "node":
            self.source.write_text("value = 2\n", encoding="utf-8")
            (self.package / "new_model.py").write_text("created = True\n", encoding="utf-8")
        elif command[0] == "git":
            subprocess.run(
                command,
                cwd=cwd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

    def generate(self, typespec_commit=""):
        with patch.object(workflow.shutil, "which", return_value="npm"), patch.object(
            workflow, "run", side_effect=self.fake_runner
        ), contextlib.redirect_stdout(io.StringIO()):
            workflow.generate(argparse.Namespace(output_dir=self.artifact, typespec_commit=typespec_commit))

    def test_generate_uses_pinned_cli_and_package_requirements(self):
        self.generate(NEW_SOURCE_COMMIT)
        result = json.loads((self.artifact / "result.json").read_text())
        self.assertEqual(result["sdk_commit"], self.sdk_commit)
        self.assertEqual(result["typespec_commit"], NEW_SOURCE_COMMIT)
        self.assertEqual(result["tsp_client_version"], "1.2.3")
        self.assertEqual(result["emitter_version"], "4.5.6")
        self.assertEqual(
            result["checks"],
            [{"command": workflow.shlex.join(command), "result": "passed"} for command in workflow.CHECKS],
        )
        self.assertIn(f"{workflow.PACKAGE_PATH}/new_model.py", result["changed_files"])
        self.assertEqual(self.commands[0], (["npm", "ci", "--prefix", str(self.cli_dir)], self.repo))
        self.assertIn(
            (
                [
                    workflow.sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    "dev_requirements.txt",
                    "-e",
                    ".",
                ],
                self.package,
            ),
            self.commands,
        )
        cli_command = next(command for command, _ in self.commands if command[0] == "node")
        self.assertEqual(cli_command[-3:], ["update", "--debug", "--no-prompt"])
        patch_bytes = (self.artifact / "regeneration.patch").read_bytes()
        self.assertEqual(hashlib.sha256(patch_bytes).hexdigest(), result["patch_sha256"])
        workflow.check_paths(
            workflow.patch_paths(
                self.git(
                    "apply",
                    "--numstat",
                    "-z",
                    str(self.artifact / "regeneration.patch"),
                )
            )
        )

    def test_generate_preserves_existing_typespec_pin(self):
        self.generate()
        result = json.loads((self.artifact / "result.json").read_text())
        self.assertEqual(result["typespec_commit"], SOURCE_COMMIT)

    def test_install_failure_stops_before_generation_without_success_artifact(self):
        with patch.object(workflow.shutil, "which", return_value="npm"), patch.object(
            workflow, "run", side_effect=subprocess.CalledProcessError(1, ["npm", "ci"])
        ) as runner:
            with self.assertRaises(subprocess.CalledProcessError):
                workflow.generate(argparse.Namespace(output_dir=self.artifact, typespec_commit=NEW_SOURCE_COMMIT))
        runner.assert_called_once()
        self.assertIn(SOURCE_COMMIT, self.location.read_text())
        self.assertFalse((self.artifact / "result.json").exists())
        self.assertFalse((self.artifact / "regeneration.patch").exists())

    def test_validation_failure_does_not_publish_patch(self):
        original_runner = self.fake_runner

        def fail_mypy(command, cwd):
            if list(command) == ["azpysdk", "mypy", "."]:
                raise subprocess.CalledProcessError(1, command)
            original_runner(command, cwd)

        self.fake_runner = fail_mypy
        with self.assertRaises(subprocess.CalledProcessError):
            self.generate()
        self.assertFalse((self.artifact / "result.json").exists())
        self.assertFalse((self.artifact / "regeneration.patch").exists())
        self.assertFalse(any(command == ["azpysdk", "devtest", "."] for command, _ in self.commands))

    def test_validation_optout_stops_before_generation(self):
        original_runner = self.fake_runner

        def reject_optout(command, cwd):
            if "-c" in command and "is_check_enabled" in command[-1]:
                raise subprocess.CalledProcessError(1, command)
            original_runner(command, cwd)

        self.fake_runner = reject_optout
        with self.assertRaises(subprocess.CalledProcessError):
            self.generate(NEW_SOURCE_COMMIT)
        self.assertIn(SOURCE_COMMIT, self.location.read_text())
        self.assertFalse(any(command[0] == "node" for command, _ in self.commands))
        self.assertFalse((self.artifact / "result.json").exists())
        self.assertIn("check_only=True", workflow.CHECKS[1][-1])

    def test_generate_rejects_dirty_checkout_before_install(self):
        self.source.write_text("existing_edit = True\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "clean Actions checkout"):
            self.generate()
        self.assertEqual(self.commands, [])
        self.assertEqual(self.source.read_text(), "existing_edit = True\n")

    def test_generate_rejects_outside_package_edits(self):
        original_runner = self.fake_runner

        def edit_outside_package(command, cwd):
            original_runner(command, cwd)
            if command[0] == "node":
                (self.repo / "unrelated.py").write_text("unrelated = True\n", encoding="utf-8")

        self.fake_runner = edit_outside_package
        with self.assertRaisesRegex(ValueError, "out-of-package"):
            self.generate()
        self.assertFalse((self.artifact / "result.json").exists())

    def test_apply_validated_patch_preserves_unrelated_edits(self):
        self.write_artifact(self.source_patch())
        unrelated = self.repo / "notes.txt"
        unrelated.write_text("existing unrelated work\n", encoding="utf-8")
        self.apply()
        self.assertEqual(self.source.read_text(), "value = 2\n")
        self.assertEqual(unrelated.read_text(), "existing unrelated work\n")

    def test_generated_patch_transfers_new_files_and_typespec_pin(self):
        receiver = self.root / "receiver"
        shutil.copytree(self.repo, receiver)
        self.generate(NEW_SOURCE_COMMIT)
        package = receiver.joinpath(*workflow.PACKAGE_PATH.split("/"))
        with patch.object(workflow, "PACKAGE_ROOT", package):
            self.apply(NEW_SOURCE_COMMIT)
        self.assertEqual((package / "new_model.py").read_text(), "created = True\n")
        self.assertIn(NEW_SOURCE_COMMIT, (package / "tsp-location.yaml").read_text())

    def test_generated_patch_transfers_binary_files(self):
        receiver = self.root / "receiver"
        shutil.copytree(self.repo, receiver)
        original_runner = self.fake_runner
        content = b"\x00\xffbinary content\n"

        def generate_binary(command, cwd):
            original_runner(command, cwd)
            if command[0] == "node":
                (self.package / "generated.bin").write_bytes(content)

        self.fake_runner = generate_binary
        self.generate()
        package = receiver.joinpath(*workflow.PACKAGE_PATH.split("/"))
        with patch.object(workflow, "PACKAGE_ROOT", package):
            self.apply()
        self.assertEqual((package / "generated.bin").read_bytes(), content)

    def test_orchestration_script_can_run_outside_the_sdk_checkout(self):
        self.write_artifact(self.source_patch())
        relocated = self.root / "orchestration.py"
        shutil.copyfile(SCRIPT, relocated)
        subprocess.run(
            [
                workflow.sys.executable,
                str(relocated),
                "apply",
                "--artifact-dir",
                str(self.artifact),
            ],
            cwd=self.package,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(self.source.read_text(), "value = 2\n")

    def test_apply_rejects_wrong_sdk_baseline(self):
        patch_bytes = self.source_patch()
        result = self.result(patch_bytes)
        result["sdk_commit"] = "c" * 40
        self.write_artifact(patch_bytes, result)
        with self.assertRaisesRegex(ValueError, "SDK baseline"):
            self.apply()
        self.assertEqual(self.source.read_text(), ORIGINAL_CODE)

    def test_apply_rejects_wrong_typespec_commit(self):
        patch_bytes = self.source_patch()
        self.write_artifact(patch_bytes, self.result(patch_bytes, NEW_SOURCE_COMMIT))
        with self.assertRaisesRegex(ValueError, "TypeSpec commit"):
            self.apply()
        self.assertEqual(self.source.read_text(), ORIGINAL_CODE)

    def test_apply_accepts_selected_typespec_commit(self):
        patch_bytes = self.source_patch()
        self.write_artifact(patch_bytes, self.result(patch_bytes, NEW_SOURCE_COMMIT))
        self.apply(NEW_SOURCE_COMMIT)
        self.assertEqual(self.source.read_text(), "value = 2\n")

    def test_apply_rejects_missing_validation_results(self):
        patch_bytes = self.source_patch()
        result = self.result(patch_bytes)
        result["checks"] = result["checks"][:-1]
        self.write_artifact(patch_bytes, result)
        with self.assertRaisesRegex(ValueError, "validation results"):
            self.apply()
        self.assertEqual(self.source.read_text(), ORIGINAL_CODE)

    def test_apply_rejects_modified_patch(self):
        patch_bytes = self.source_patch()
        self.write_artifact(patch_bytes)
        (self.artifact / "regeneration.patch").write_bytes(patch_bytes + b"\n")
        with self.assertRaisesRegex(ValueError, "digest"):
            self.apply()
        self.assertEqual(self.source.read_text(), ORIGINAL_CODE)

    def test_apply_rejects_outside_package_patch_even_with_valid_metadata(self):
        outside = self.repo / ".gitignore"
        original = outside.read_text()
        outside.write_text(original + "extra/\n", encoding="utf-8")
        patch_bytes = self.git("diff", "--binary")
        outside.write_text(original, encoding="utf-8")
        self.write_artifact(patch_bytes)
        with self.assertRaisesRegex(ValueError, "out-of-package"):
            self.apply()
        self.assertEqual(outside.read_text(), original)

    def test_apply_rejects_rename_from_outside_the_package(self):
        outside = self.repo / ".gitignore"
        inside = self.package / "moved.txt"
        self.git("mv", str(outside), str(inside))
        patch_bytes = self.git("diff", "--binary", "HEAD")
        self.git("mv", str(inside), str(outside))
        self.write_artifact(patch_bytes)
        with self.assertRaisesRegex(ValueError, "out-of-package"):
            self.apply()
        self.assertTrue(outside.exists())
        self.assertFalse(inside.exists())

    def test_apply_checks_conflicts_before_modifying_files(self):
        self.write_artifact(self.source_patch())
        self.source.write_text("value = 3\n", encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(subprocess.CalledProcessError):
            self.apply()
        self.assertEqual(self.source.read_text(), "value = 3\n")

    def test_apply_rejects_invalid_patch_whitespace_before_modifying_files(self):
        self.source.write_text("value = 2 \n", encoding="utf-8")
        patch_bytes = self.git("diff", "--binary")
        self.source.write_text(ORIGINAL_CODE, encoding="utf-8")
        self.write_artifact(patch_bytes)
        with self.assertRaises(subprocess.CalledProcessError):
            self.apply()
        self.assertEqual(self.source.read_text(), ORIGINAL_CODE)

    def test_empty_patch_is_a_valid_no_change_result(self):
        self.write_artifact(b"")
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.apply()
        self.assertIn("no package changes", output.getvalue())
        self.assertEqual(self.source.read_text(), ORIGINAL_CODE)

    def test_git_status_and_patch_parsing_support_renames(self):
        renamed = self.package / "renamed.py"
        self.git("mv", str(self.source), str(renamed))
        paths = workflow.status_paths(self.git("status", "--porcelain=v1", "--untracked-files=all", "-z"))
        self.assertCountEqual(
            paths,
            [
                f"{workflow.PACKAGE_PATH}/example.py",
                f"{workflow.PACKAGE_PATH}/renamed.py",
            ],
        )
        patch_file = self.root / "rename.patch"
        patch_file.write_bytes(self.git("diff", "--binary", "HEAD"))
        paths = workflow.patch_paths(self.git("apply", "--numstat", "-z", str(patch_file)))
        workflow.check_paths(paths)
        self.assertIn(f"{workflow.PACKAGE_PATH}/renamed.py", paths)

    def test_rejects_unsafe_paths(self):
        for path in (
            "sdk/ai/another-package/model.py",
            "sdk/ai/azure-ai-projects-other/model.py",
            f"{workflow.PACKAGE_PATH}/../outside.py",
            f"{workflow.PACKAGE_PATH}/nested\\outside.py",
            f"{workflow.PACKAGE_PATH}/.env",
        ):
            with self.subTest(path=path), self.assertRaises(ValueError):
                workflow.check_paths([path])

    def test_commit_input_requires_a_full_sha(self):
        self.assertEqual(workflow.commit_sha("A" * 40), SOURCE_COMMIT)
        self.assertEqual(workflow.commit_sha(""), "")
        for value in (
            "main",
            "abc123",
            "a" * 41,
            "https://github.com/Azure/azure-rest-api-specs/pull/1",
        ):
            with self.subTest(value=value), self.assertRaises(argparse.ArgumentTypeError):
                workflow.commit_sha(value)


if __name__ == "__main__":
    unittest.main()
