# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Offline regression tests; every file mutation is confined to a temporary package."""

import ast
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

SKILL_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sample_test_plan", SKILL_ROOT / "scripts" / "sample_test_plan.py")
assert SPEC is not None and SPEC.loader is not None
PLANNER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PLANNER
SPEC.loader.exec_module(PLANNER)
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell")


class SampleTestPlanTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="sample registration ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        (self.root / "samples").mkdir()
        (self.root / "tests" / "samples").mkdir(parents=True)

    def sample(self, relative):
        path = self.root / "samples" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        # Planning must not execute sample modules.
        path.write_text('raise RuntimeError("Samples must not execute during registration")\n', encoding="utf-8")
        return path

    def group(self, folder, selection="samples_to_skip=[]", *, is_async=False, additional="", name="test_samples"):
        discover = "get_async_sample_paths" if is_async else "get_sample_paths"
        declaration = "async def" if is_async else "def"
        decorators = "@servicePreparer()\n" + (additional + "\n" if additional else "")
        return (
            decorators
            + f'@pytest.mark.parametrize("sample_path", {discover}({json.dumps(folder, ensure_ascii=False)}, {selection}))\n'
            + f"{declaration} {name}(self, sample_path, **kwargs):\n    pass\n"
        )

    def harness(self, method, *, is_async=False, filename=None, newline="\n", bom=False, footer=""):
        filename = filename or ("test_samples_async.py" if is_async else "test_samples.py")
        class_name = "TestSamplesAsync" if is_async else "TestSamples"
        source = f"class {class_name}(AzureRecordedTestCase):\n" + textwrap.indent(method, "    ") + footer
        source = source.replace("\n", newline)
        path = self.root / "tests" / "samples" / filename
        path.write_bytes(source.encode("utf-8-sig" if bom else "utf-8"))
        return path

    def plan(self, *paths):
        return PLANNER.build_plan(self.root, [str(path) for path in paths])

    def apply_to_fixture(self, plan):
        for change in plan["files"]:
            path = Path(change["path"])
            self.assertTrue(path.is_relative_to(self.root))
            path.write_bytes(change["after"].encode("utf-8-sig" if change["bom"] else "utf-8"))

    def test_discovered_sync_async_and_duplicate_requests_are_noops(self):
        sync = self.sample("agents/sample_basic.py")
        asynchronous = self.sample("agents/sample_basic_async.py")
        self.harness(self.group("agents"))
        self.harness(self.group("agents", is_async=True), is_async=True)
        plan = self.plan(sync, asynchronous, sync)
        self.assertEqual(plan["files"], [])
        self.assertEqual([item["action"] for item in plan["samples"]], ["already-registered"] * 2)
        self.assertIn("[sample_basic_async]", plan["samples"][1]["nodeIds"][0])

    def test_removes_exclusion_and_its_reason_but_preserves_other_entries(self):
        sample = self.sample("agents/sample_basic.py")
        selection = (
            'samples_to_skip=[\n    "sample_basic.py",  # waiting for recording\n    "sample_other.py",  # keep\n]'
        )
        path = self.harness(self.group("agents", selection))
        original = path.read_bytes()
        plan = self.plan(sample)
        self.assertEqual(path.read_bytes(), original)
        updated = plan["files"][0]["after"]
        self.assertNotIn("waiting for recording", updated)
        self.assertIn('"sample_other.py",  # keep', updated)
        self.assertEqual(plan["samples"][0]["action"], "exclude-removed")
        self.apply_to_fixture(plan)
        self.assertEqual(self.plan(sample)["files"], [])

    def test_adds_multiple_includes_without_duplicates(self):
        first = self.sample("models/sample_first.py")
        second = self.sample("models/sample_second.py")
        self.harness(self.group("models", 'samples_to_test=["sample_existing.py"]'))
        plan = self.plan(first, second, first)
        self.assertEqual(len(plan["files"]), 1)
        self.assertEqual([item["action"] for item in plan["samples"]], ["include-added"] * 2)
        self.assertIn('["sample_existing.py", "sample_first.py", "sample_second.py"]', plan["files"][0]["after"])
        self.apply_to_fixture(plan)
        self.assertEqual(self.plan(first, second)["files"], [])

    def test_multiline_include_keeps_comments_and_adds_missing_comma(self):
        sample = self.sample("models/sample_new.py")
        selection = 'samples_to_test=[\n    "sample_existing.py"  # preserve this\n]'
        self.harness(self.group("models", selection))
        updated = self.plan(sample)["files"][0]["after"]
        self.assertIn('"sample_existing.py",  # preserve this', updated)
        self.assertIn('"sample_new.py",', updated)
        ast.parse(updated)

    def test_active_custom_variant_does_not_get_a_duplicate_baseline(self):
        sample = self.sample("hosted_agents/sample_build.py")
        additional = '@additionalSampleTests([AdditionalSampleTestDetail(sample_filename="sample_build.py", env_vars={}, test_id="remote_build")])'
        self.harness(self.group("hosted_agents", 'samples_to_skip=["sample_build.py"]', additional=additional))
        plan = self.plan(sample)
        self.assertEqual(plan["files"], [])
        self.assertTrue(plan["samples"][0]["nodeIds"][0].endswith("[remote_build]"))

    def test_generated_variant_id_uses_sorted_environment_keys(self):
        sample = self.sample("hosted_agents/sample_build.py")
        additional = '@additionalSampleTests([AdditionalSampleTestDetail(sample_filename="sample_build.py", env_vars={"Z": "x", "A": "y"})])'
        self.harness(self.group("hosted_agents", 'samples_to_skip=["sample_build.py"]', additional=additional))
        plan = self.plan(sample)
        self.assertEqual(plan["files"], [])
        self.assertTrue(plan["samples"][0]["nodeIds"][0].endswith("[sample_build-[A,Z]]"))

    def test_commented_out_test_id_is_not_a_registration(self):
        sample = self.sample("agents/sample_basic.py")
        additional = '# @additionalSampleTests([AdditionalSampleTestDetail(sample_filename="sample_basic.py", env_vars={}, test_id="sample_basic")])'
        self.harness(self.group("agents", 'samples_to_skip=["sample_basic.py"]', additional=additional))
        self.assertEqual(self.plan(sample)["samples"][0]["action"], "exclude-removed")

    def test_existing_specialized_folder_test_is_preserved(self):
        sample = self.sample("evaluations/sample_special.py")
        main = self.group("evaluations", 'samples_to_skip=["sample_special.py"]', name="test_main")
        special = self.group("evaluations", 'samples_to_test=["sample_special.py"]', name="test_special")
        self.harness(main + "\n" + special, filename="test_samples_evaluations.py")
        self.assertEqual(self.plan(sample)["files"], [])

    def test_prefers_general_exclusion_group_over_unrelated_specialized_include(self):
        sample = self.sample("evaluations/sample_new.py")
        main = self.group("evaluations", 'samples_to_skip=["sample_new.py"]', name="test_main")
        special = self.group("evaluations", 'samples_to_test=["sample_special.py"]', name="test_special")
        self.harness(main + "\n" + special, filename="test_samples_evaluations.py")
        result = self.plan(sample)["samples"][0]
        self.assertEqual(result["action"], "exclude-removed")
        self.assertIn("::test_main[", result["nodeIds"][0])

    def test_ambiguous_groups_require_manual_selection(self):
        sample = self.sample("agents/sample_basic.py")
        first = self.group("agents", 'samples_to_skip=["sample_basic.py"]', name="test_first")
        second = self.group("agents", 'samples_to_skip=["sample_basic.py"]', name="test_second")
        self.harness(first + "\n" + second)
        with self.assertRaisesRegex(ValueError, "Multiple folder tests"):
            self.plan(sample)

    def test_new_nested_folder_creates_one_method_per_execution_kind(self):
        first = self.sample("new/nested-folder/sample_first.py")
        second = self.sample("new/nested-folder/sample_second.py")
        asynchronous = self.sample("new/nested-folder/sample_first_async.py")
        self.sample("new/nested-folder/sample_not_requested.py")
        self.harness(self.group("agents"))
        self.harness(self.group("agents", is_async=True), is_async=True)
        plan = self.plan(first, second, asynchronous)
        self.assertEqual(len(plan["files"]), 2)
        self.assertEqual(
            [item["action"] for item in plan["samples"]],
            ["folder-test-created", "include-added", "folder-test-created"],
        )
        for change in plan["files"]:
            ast.parse(change["after"])
            self.assertTrue(change["after"].endswith("\n"))
            self.assertTrue(all(line.rstrip(" \t") == line for line in change["after"].splitlines()))
            self.assertNotIn("sample_not_requested.py", change["after"])
            self.assertIn("@servicePreparer()", change["after"])
            self.assertIn("RecordedTransport.HTTPX2", change["after"])
        asynchronous_source = next(
            change["after"] for change in plan["files"] if change["path"].endswith("test_samples_async.py")
        )
        self.assertIn("await executor.execute_async()", asynchronous_source)
        self.assertIn("await executor.validate_print_calls_by_llm_async()", asynchronous_source)
        self.apply_to_fixture(plan)
        self.assertEqual(self.plan(first, second, asynchronous)["files"], [])

    def test_can_create_missing_canonical_harness_modules(self):
        sample = self.sample("routines/sample_new.py")
        plan = self.plan(sample)
        source = plan["files"][0]["after"]
        self.assertIsNone(plan["files"][0]["before"])
        self.assertIn("from test_base import servicePreparer", source)
        self.assertIn("class TestSamples(AzureRecordedTestCase)", source)
        ast.parse(source)

    def test_methods_are_inserted_inside_class_before_module_footer(self):
        sample = self.sample("routines/sample_new.py")
        self.harness(self.group("agents"), footer="\n\ndef helper_after_class():\n    pass\n")
        tree = ast.parse(self.plan(sample)["files"][0]["after"])
        target = next(node for node in tree.body if isinstance(node, ast.ClassDef))
        self.assertIn("test_routines_samples", [node.name for node in target.body if isinstance(node, ast.FunctionDef)])
        self.assertEqual(tree.body[-1].name, "helper_after_class")

    def test_identical_stems_in_other_folders_are_not_mistaken_for_existing_ids(self):
        self.sample("agents/sample_basic.py")
        sample = self.sample("routines/sample_basic.py")
        self.harness(self.group("agents"))
        self.assertEqual(self.plan(sample)["samples"][0]["action"], "folder-test-created")

    def test_new_method_names_avoid_slug_collisions(self):
        first = self.sample("a-b/sample_first.py")
        second = self.sample("a_b/sample_second.py")
        plan = self.plan(first, second)
        self.assertIn("def test_a_b_samples_2(", plan["files"][0]["after"])

    def test_non_ascii_columns_and_duplicate_inline_exclusions(self):
        sample = self.sample("mémoire/sample_basic.py")
        selection = 'samples_to_skip=["sample_other.py", "sample_basic.py", "sample_basic.py"]'
        self.harness(self.group("mémoire", selection))
        updated = self.plan(sample)["files"][0]["after"]
        self.assertIn('samples_to_skip=["sample_other.py"]', updated)

    def test_preserves_bom_crlf_and_custom_preparer(self):
        sample = self.sample("models/sample_basic.py")
        method = self.group("models", 'samples_to_skip=["sample_basic.py"]').replace(
            "@servicePreparer()", "@modelsServicePreparer()"
        )
        self.harness(method, newline="\r\n", bom=True)
        change = self.plan(sample)["files"][0]
        self.assertTrue(change["bom"])
        self.assertNotIn("\n", change["after"].replace("\r\n", ""))
        self.assertIn("@modelsServicePreparer()", change["after"])

    def test_invalid_input_in_batch_does_not_write_any_files(self):
        sample = self.sample("agents/sample_basic.py")
        path = self.harness(self.group("agents", 'samples_to_skip=["sample_basic.py"]'))
        original = path.read_bytes()
        with self.assertRaisesRegex(ValueError, "missing or ambiguous"):
            self.plan(sample, "missing.py")
        self.assertEqual(path.read_bytes(), original)

    def test_rejects_files_outside_samples_and_ambiguous_filenames(self):
        outside = self.root / "sample_outside.py"
        outside.write_text("pass\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Not a sample"):
            self.plan(outside)
        self.sample("agents/sample_basic.py")
        self.sample("routines/sample_basic.py")
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            self.plan("sample_basic.py")

    def test_accepts_samples_relative_package_relative_and_unique_filename(self):
        first = self.sample("agents/sample_first.py")
        second = self.sample("agents/sample_second.py")
        self.harness(self.group("agents"))
        plan = self.plan("agents/sample_first.py", "samples\\agents\\sample_second.py", first, "sample_second.py")
        self.assertEqual(len(plan["samples"]), 2)
        self.assertEqual(plan["files"], [])

    def test_dynamic_include_is_rejected_without_guessing(self):
        sample = self.sample("models/sample_basic.py")
        self.harness(self.group("models", "samples_to_test=SOME_VARIABLE"))
        with self.assertRaisesRegex(ValueError, "literal include/exclude"):
            self.plan(sample)

    def invoke_powershell(self, paths, *flags):
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
        result = subprocess.run(
            [POWERSHELL, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return json.loads(result.stdout[result.stdout.index("{") :])

    @unittest.skipUnless(POWERSHELL, "PowerShell is not installed")
    def test_powershell_preview_batch_apply_and_repeat(self):
        first = self.sample("routines/sample_first.py")
        second = self.sample("routines/sample_second.py")
        preview = self.invoke_powershell([first, second])
        self.assertEqual(preview["Mode"], "preview")
        self.assertFalse((self.root / "tests" / "samples" / "test_samples.py").exists())
        applied = self.invoke_powershell([first, second], "-Apply")
        self.assertEqual(applied["Mode"], "applied")
        self.assertEqual(applied["WrittenFiles"], ["tests/samples/test_samples.py"])
        repeated = self.invoke_powershell([first, second], "-Apply")
        self.assertEqual(repeated["Mode"], "unchanged")
        self.assertEqual(repeated["ChangedFiles"], [])

    @unittest.skipUnless(POWERSHELL, "PowerShell is not installed")
    def test_powershell_whatif_and_bom_crlf_apply(self):
        sample = self.sample("agents/sample_basic.py")
        path = self.harness(self.group("agents", 'samples_to_skip=["sample_basic.py"]'), newline="\r\n", bom=True)
        original = path.read_bytes()
        result = self.invoke_powershell([sample], "-Apply", "-WhatIf")
        self.assertEqual(result["Mode"], "not-applied")
        self.assertEqual(path.read_bytes(), original)
        self.invoke_powershell([sample], "-Apply")
        raw = path.read_bytes()
        self.assertTrue(raw.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))


if __name__ == "__main__":
    unittest.main()
