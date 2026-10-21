# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Offline environment-planning and PowerShell integration regressions."""

import ast
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any
import unittest

SKILL_ROOT = Path(__file__).resolve().parents[1]
for module_name in ("sample_test_plan", "sample_environment_plan"):
    specification = importlib.util.spec_from_file_location(module_name, SKILL_ROOT / "scripts" / f"{module_name}.py")
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[module_name] = module
    specification.loader.exec_module(module)
ENVIRONMENT = sys.modules["sample_environment_plan"]
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell")


class SampleEnvironmentPlanTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="sample env plan ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        (self.root / "samples").mkdir()
        (self.root / "tests" / "samples").mkdir(parents=True)
        self.template = self.root / ".env.template"
        self.template.write_text("# Keep this comment\nexport EXISTING = keep-template-value\n", encoding="utf-8")
        self.preparer = self.root / "tests" / "test_base.py"
        self.preparer.write_text(
            'servicePreparer = functools.partial(\n    EnvironmentVariableLoader,\n    "",\n'
            '    existing="keep-playback-value",  # Keep this too\n)\n\n'
            'modelsServicePreparer = functools.partial(EnvironmentVariableLoader, "", special="preserve")\n',
            encoding="utf-8",
        )

    def sample(self, relative, code):
        path = self.root / "samples" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('raise RuntimeError("Do not execute samples during registration")\n' + code, encoding="utf-8")
        return path

    def harness(self):
        path = self.root / "tests" / "samples" / "test_samples.py"
        path.write_text(
            "class TestSamples(AzureRecordedTestCase):\n"
            "    @servicePreparer()\n"
            '    @pytest.mark.parametrize("sample_path", get_sample_paths("agents", samples_to_skip=[]))\n'
            "    def test_agents_samples(self, sample_path, **kwargs):\n        pass\n",
            encoding="utf-8",
        )
        return path

    def plan(self, names, overrides=None):
        return ENVIRONMENT.build_environment_plan(self.root, names, overrides)

    def apply_to_fixture(self, plan):
        for file in plan["files"]:
            path = Path(file["path"])
            self.assertTrue(path.is_relative_to(self.root))
            path.write_bytes(file["after"].encode("utf-8-sig" if file["bom"] else "utf-8"))

    def defaults(self, text):
        tree = ast.parse(text)
        call = next(
            node.value
            for node in tree.body
            if isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "servicePreparer"
        )
        assert isinstance(call, ast.Call)
        return {item.arg: ast.literal_eval(item.value) for item in call.keywords}

    def test_scanner_is_an_unchanged_local_copy(self):
        original = (
            SKILL_ROOT.parent
            / "azure-ai-projects-sample-validation"
            / "scripts"
            / "GetSampleRequiredEnvironmentVariables.ps1"
        )
        duplicate = SKILL_ROOT / "scripts" / original.name
        # Checkout EOL/final-newline normalization must not hide source changes.
        self.assertEqual(
            original.read_text(encoding="utf-8-sig").splitlines(),
            duplicate.read_text(encoding="utf-8-sig").splitlines(),
        )

    def test_missing_names_and_defaults_are_added_once_without_overwriting(self):
        original_template = self.template.read_bytes()
        original_preparer = self.preparer.read_bytes()
        plan = self.plan(["EXISTING", "NEW_API_KEY", "NEW_PROJECT_ENDPOINT", "NEW_API_KEY"])
        self.assertEqual(self.template.read_bytes(), original_template)
        self.assertEqual(self.preparer.read_bytes(), original_preparer)
        self.assertEqual(plan["environment"]["templateAdded"], ["NEW_API_KEY", "NEW_PROJECT_ENDPOINT"])
        self.assertEqual(len(plan["files"]), 2)
        self.apply_to_fixture(plan)
        self.assertIn("NEW_API_KEY=\nNEW_PROJECT_ENDPOINT=\n", self.template.read_text(encoding="utf-8"))
        self.assertIn("export EXISTING = keep-template-value", self.template.read_text(encoding="utf-8"))
        source = self.preparer.read_text(encoding="utf-8")
        self.assertIn("# Keep this too", source)
        self.assertIn('special="preserve"', source)
        values = self.defaults(source)
        self.assertEqual(values["existing"], "keep-playback-value")
        self.assertEqual(values["new_api_key"], "sanitized-new-api-key")
        self.assertEqual(values["new_project_endpoint"], ENVIRONMENT.PROJECT_ENDPOINT)
        self.assertEqual(self.plan(["EXISTING", "NEW_API_KEY", "NEW_PROJECT_ENDPOINT"])["files"], [])

    def test_can_add_only_the_missing_side(self):
        self.template.write_text("NEW_VALUE=\n", encoding="utf-8")
        plan = self.plan(["NEW_VALUE"])
        self.assertEqual([item["relativePath"] for item in plan["files"]], ["tests/test_base.py"])
        self.apply_to_fixture(plan)
        self.template.write_text("# NEW_VALUE= is not an active assignment\n", encoding="utf-8")
        plan = self.plan(["NEW_VALUE"])
        self.assertEqual([item["relativePath"] for item in plan["files"]], [".env.template"])

    def test_structural_defaults_and_explicit_playback_overrides(self):
        names = [
            "NEW_PROJECT_CONNECTION_ID",
            "AZURE_TENANT_ID",
            "NEW_ENDPOINT",
            "POLL_INTERVAL_SECONDS",
            "CUSTOM_PAYLOAD",
        ]
        plan = self.plan(names, {"CUSTOM_PAYLOAD": '{"fictional": true}', "POLL_INTERVAL_SECONDS": "60"})
        values = {item["name"]: item["value"] for item in plan["environment"]["servicePreparerAdded"]}
        self.assertEqual(values["AZURE_TENANT_ID"], ENVIRONMENT.ZERO_UUID)
        self.assertEqual(
            values["NEW_PROJECT_CONNECTION_ID"],
            ENVIRONMENT.PROJECT_RESOURCE_ID + "/connections/sanitized-new-connection",
        )
        self.assertEqual(values["NEW_ENDPOINT"], "https://sanitized-new-endpoint.example.com")
        self.assertEqual(values["POLL_INTERVAL_SECONDS"], "60")
        self.apply_to_fixture(plan)
        self.assertEqual(
            self.defaults(self.preparer.read_text(encoding="utf-8"))["custom_payload"], '{"fictional": true}'
        )
        self.assertNotIn('"fictional"', self.template.read_text(encoding="utf-8"))

    def test_user_input_defaults_are_readable_questions(self):
        expected = {
            "USER_INPUT": "What is user input?",
            "AI_SEARCH_USER_INPUT": "What is ai search user input?",
            "WEB_IQ_USER_INPUT": "What is web iq user input?",
        }
        plan = self.plan(list(expected))
        values = {item["name"]: item["value"] for item in plan["environment"]["servicePreparerAdded"]}
        self.assertEqual(values, expected)
        self.assertEqual(ENVIRONMENT.sanitized_default("USER_INPUT_FORMAT"), "sanitized-user-input-format")
        self.apply_to_fixture(plan)
        self.assertEqual(
            self.defaults(self.preparer.read_text(encoding="utf-8"))["ai_search_user_input"],
            expected["AI_SEARCH_USER_INPUT"],
        )
        self.assertIn("AI_SEARCH_USER_INPUT=\n", self.template.read_text(encoding="utf-8"))
        self.assertNotIn("What is", self.template.read_text(encoding="utf-8"))
        self.assertEqual(self.plan(list(expected))["files"], [])

    def test_user_input_override_and_existing_default_are_preserved(self):
        name = "BING_CUSTOM_USER_INPUT"
        value = "What is a fictional topic?"
        plan = self.plan([name], {name: value})
        self.assertEqual(plan["environment"]["servicePreparerAdded"][0]["value"], value)
        self.apply_to_fixture(plan)
        self.assertEqual(self.plan([name])["files"], [])
        self.assertEqual(self.defaults(self.preparer.read_text(encoding="utf-8"))[name.lower()], value)

    def test_overrides_never_replace_existing_defaults(self):
        plan = self.plan(["EXISTING"], {"EXISTING": "sanitized-replacement"})
        self.assertEqual(plan["files"], [])
        self.assertEqual(plan["environment"]["servicePreparerAdded"], [])

    def test_no_required_names_needs_no_configuration_files(self):
        self.template.unlink()
        self.preparer.unlink()
        self.assertEqual(self.plan([])["files"], [])

    def test_preserves_bom_crlf_and_missing_final_newline(self):
        for path in (self.template, self.preparer):
            path.write_bytes(path.read_text(encoding="utf-8").rstrip("\n").replace("\n", "\r\n").encode("utf-8-sig"))
        plan = self.plan(["ADDED_VALUE"])
        for file in plan["files"]:
            self.assertTrue(file["bom"])
            self.assertNotIn("\n", file["after"].replace("\r\n", ""))
            self.assertTrue(all(line.rstrip(" \t") == line for line in file["after"].splitlines()))
        self.apply_to_fixture(plan)
        self.assertEqual(self.plan(["ADDED_VALUE"])["files"], [])

    def test_compact_and_unterminated_last_argument_preserve_syntax(self):
        preparers = [
            'servicePreparer = functools.partial(EnvironmentVariableLoader, "")\n',
            'servicePreparer = functools.partial(EnvironmentVariableLoader, "", )\n',
            'servicePreparer = functools.partial(\n    EnvironmentVariableLoader,\n    ""  # preserve comment\n)\n',
        ]
        for source in preparers:
            with self.subTest(source=source):
                self.preparer.write_text(source, encoding="utf-8")
                updated = next(
                    file["after"]
                    for file in self.plan(["NEW_VALUE"])["files"]
                    if file["relativePath"] == "tests/test_base.py"
                )
                compile(updated, str(self.preparer), "exec")
                self.assertEqual(self.defaults(updated)["new_value"], "sanitized-new-value")

    def test_rejects_invalid_names_and_loader_option_collisions(self):
        for name in ("not_uppercase", "BAD-NAME", "CLASS", "DIRECTORY", "OPTIONS", "NAME_PREFIX"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.plan([name])

    def test_rejects_unscanned_empty_multiline_or_nonstring_overrides(self):
        for mapping in ({"TYPO": "sanitized"}, {"NEW_VALUE": ""}, {"NEW_VALUE": "a\nb"}, {"NEW_VALUE": 5}):
            with self.subTest(mapping=mapping), self.assertRaises(ValueError):
                self.plan(["NEW_VALUE"], mapping)

    def test_ambiguous_or_dynamic_preparers_fail_without_writes(self):
        sources = [
            "servicePreparer = build_preparer()\n",
            'servicePreparer = functools.partial(EnvironmentVariableLoader, "", **DYNAMIC)\n',
            'servicePreparer = functools.partial(EnvironmentVariableLoader, "", foo="a", FOO="b")\n',
            'servicePreparer = functools.partial(EnvironmentVariableLoader, "different-prefix")\n',
        ]
        original = self.template.read_bytes()
        for source in sources:
            with self.subTest(source=source):
                self.preparer.write_text(source, encoding="utf-8")
                with self.assertRaises(ValueError):
                    self.plan(["NEW_VALUE"])
                self.assertEqual(self.template.read_bytes(), original)

    def test_planning_never_imports_preparer_or_reads_local_secrets(self):
        self.preparer.write_text(
            'raise RuntimeError("Do not import")\n' + self.preparer.read_text(encoding="utf-8"), encoding="utf-8"
        )
        private = self.root / ".env"
        private.write_text("NEW_API_KEY=private-sentinel-do-not-copy\n", encoding="utf-8")
        plan = self.plan(["NEW_API_KEY"])
        self.assertNotIn("private-sentinel", json.dumps(plan))
        self.assertEqual(private.read_text(encoding="utf-8"), "NEW_API_KEY=private-sentinel-do-not-copy\n")

    def invoke_powershell(self, paths, *flags, overrides=None, success=True) -> dict[str, Any]:
        assert POWERSHELL is not None

        def quote(value):
            return "'" + str(value).replace("'", "''") + "'"

        command = (
            "$ErrorActionPreference = 'Stop'; & "
            + quote(SKILL_ROOT / "scripts" / "AddSampleTestCase.ps1")
            + " -PackageRoot "
            + quote(self.root)
            + " -PythonExecutable "
            + quote(sys.executable)
            + " -SamplePath @("
            + ",".join(quote(path) for path in paths)
            + ") -AsJson "
            + " ".join(flags)
        )
        if overrides:
            command += (
                " -SanitizedValue @{"
                + ";".join(quote(name) + "=" + quote(value) for name, value in overrides.items())
                + "}"
            )
        result = subprocess.run(
            [POWERSHELL, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
            check=False,
        )
        if not success:
            self.assertNotEqual(result.returncode, 0)
            return {"stdout": result.stdout, "stderr": result.stderr}
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout[result.stdout.index("{") :])

    @unittest.skipUnless(POWERSHELL, "PowerShell is not installed")
    def test_powershell_scans_multiple_already_registered_samples_and_applies_once(self):
        first = self.sample("agents/sample_first.py", 'a = os.environ["NEW_API_KEY"]\nb = os.getenv("BARE_GET")\n')
        second = self.sample(
            "agents/sample_second.py",
            'a = get_required_env_var("HELPER_VALUE")\nb = os.environ["NEW_API_KEY"]\n'
            'c = os.getenv("OPTIONAL", "fallback")\nd = os.environ.get("OPTIONAL_OR") or "fallback"\n'
            'os.environ["ASSIGNED_ONLY"] = "not-a-read"\n',
        )
        harness = self.harness()
        original_harness = harness.read_bytes()
        original_template = self.template.read_bytes()
        private = self.root / ".env"
        private.write_text("NEW_API_KEY=private-sentinel-do-not-copy\n", encoding="utf-8")
        preview = self.invoke_powershell(["agents/sample_first.py", second])
        self.assertEqual(preview["Mode"], "preview")
        self.assertEqual([sample["action"] for sample in preview["Samples"]], ["already-registered"] * 2)
        self.assertEqual(preview["Environment"]["requiredNames"], ["BARE_GET", "HELPER_VALUE", "NEW_API_KEY"])
        self.assertEqual(preview["ChangedFiles"], [".env.template", "tests/test_base.py"])
        self.assertEqual(self.template.read_bytes(), original_template)
        applied = self.invoke_powershell([first, second], "-Apply", overrides={"HELPER_VALUE": "sanitized-helper"})
        self.assertEqual(applied["Mode"], "applied")
        self.assertEqual(harness.read_bytes(), original_harness)
        self.assertNotIn("private-sentinel", json.dumps(applied))
        self.assertEqual(private.read_text(encoding="utf-8"), "NEW_API_KEY=private-sentinel-do-not-copy\n")
        self.assertEqual(self.defaults(self.preparer.read_text(encoding="utf-8"))["helper_value"], "sanitized-helper")
        self.assertEqual(self.invoke_powershell([first, second], "-Apply")["Mode"], "unchanged")

    @unittest.skipUnless(POWERSHELL, "PowerShell is not installed")
    def test_powershell_combined_apply_registers_sync_async_and_environment(self):
        first = self.sample("new_folder/sample_basic.py", 'value = os.environ["NEW_PROJECT_ENDPOINT"]\n')
        asynchronous = self.sample("new_folder/sample_basic_async.py", 'value = os.environ["NEW_TENANT_ID"]\n')
        for path in (self.template, self.preparer):
            path.write_bytes(path.read_text(encoding="utf-8").replace("\n", "\r\n").encode("utf-8-sig"))
        preview = self.invoke_powershell([first, asynchronous])
        self.assertEqual(preview["Mode"], "preview")
        self.assertEqual(len(preview["ChangedFiles"]), 4)
        applied = self.invoke_powershell([first, asynchronous], "-Apply")
        self.assertEqual(applied["WrittenFiles"], preview["ChangedFiles"])
        self.assertEqual(applied["Environment"]["templateAdded"], ["NEW_PROJECT_ENDPOINT", "NEW_TENANT_ID"])
        for name in ("test_samples.py", "test_samples_async.py"):
            path = self.root / "tests" / "samples" / name
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        for path in (self.template, self.preparer):
            raw = path.read_bytes()
            self.assertTrue(raw.startswith(b"\xef\xbb\xbf"))
            self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))
        self.assertEqual(self.invoke_powershell([first, asynchronous], "-Apply")["Mode"], "unchanged")

    @unittest.skipUnless(POWERSHELL, "PowerShell is not installed")
    def test_powershell_whatif_preserves_every_file_in_combined_plan(self):
        sample = self.sample("new_folder/sample_basic.py", 'value = os.environ["NEW_ENDPOINT"]\n')
        before = {path: path.read_bytes() for path in (self.template, self.preparer)}
        result = self.invoke_powershell([sample], "-Apply", "-WhatIf")
        self.assertEqual(result["Mode"], "not-applied")
        self.assertEqual(len(result["ChangedFiles"]), 3)
        self.assertFalse((self.root / "tests" / "samples" / "test_samples.py").exists())
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)

    @unittest.skipUnless(POWERSHELL, "PowerShell is not installed")
    def test_powershell_environment_error_blocks_registration_writes(self):
        sample = self.sample("new_folder/sample_basic.py", 'value = os.environ["NEW_VALUE"]\n')
        self.preparer.write_text("servicePreparer = build_preparer()\n", encoding="utf-8")
        before = self.template.read_bytes()
        result = self.invoke_powershell([sample], "-Apply", success=False)
        self.assertIn("No files were changed", result["stderr"])
        self.assertEqual(self.template.read_bytes(), before)
        self.assertFalse((self.root / "tests" / "samples" / "test_samples.py").exists())


if __name__ == "__main__":
    unittest.main()
