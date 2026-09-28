import json
from pathlib import Path
import re
import subprocess
import textwrap
import unittest


WORKFLOWS = Path(__file__).parents[1]
TARGET = "${{ github.event.inputs.issue_number }}"


def read_workflow(name, suffix=".md"):
    return (WORKFLOWS / (name + suffix)).read_text(encoding="utf-8")


def metadata(lock, kind):
    prefix = f"# gh-aw-{kind}: "
    return json.loads(next(line.removeprefix(prefix) for line in lock.splitlines() if line.startswith(prefix)))


def environment_json(lock, name):
    values = re.findall(rf"^\s+{re.escape(name)}: (.+)$", lock, re.MULTILINE)
    if len(values) != 1:
        raise AssertionError(f"Expected one {name}, found {len(values)}")
    return json.loads(json.loads(values[0]))


def job(lock, name):
    return re.split(r"(?m)^  [\w-]+:\n", lock.split(f"\n  {name}:\n", 1)[1], maxsplit=1)[0]


class InvestigationWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = read_workflow("issue-investigation")
        cls.lock = read_workflow("issue-investigation", ".lock.yml")
        cls.config = environment_json(cls.lock, "GH_AW_SAFE_OUTPUTS_HANDLER_CONFIG")

    def test_mutations_are_bound_to_dispatched_issue(self):
        for operation in ("add_comment", "close_issue", "assign_to_agent"):
            with self.subTest(operation=operation):
                self.assertEqual(TARGET, self.config[operation]["target"])
                self.assertEqual(1, self.config[operation]["max"])
        self.assertNotIn("create_issue", self.config)
        self.assertNotIn("add_labels", self.config)
        self.assertNotIn("remove_labels", self.config)

    def test_closure_requires_customer_label_and_not_planned_reason(self):
        self.assertEqual(["customer-reported"], self.config["close_issue"]["required_labels"])
        self.assertEqual("not_planned", self.config["close_issue"]["state_reason"])

    def test_assignment_is_copilot_only_and_best_effort(self):
        self.assertEqual("copilot", self.config["assign_to_agent"]["name"])
        self.assertEqual(["copilot"], self.config["assign_to_agent"]["allowed"])
        self.assertTrue(self.config["assign_to_agent"]["ignore-if-error"])

    def test_failure_reporting_does_not_create_issues(self):
        self.assertIn('GH_AW_MISSING_TOOL_CREATE_ISSUE: "false"', self.lock)
        self.assertIn('GH_AW_REPORT_INCOMPLETE_CREATE_ISSUE: "false"', self.lock)
        self.assertNotIn("create_report_incomplete_issue", self.config)
        self.assertEqual("false", self.config["noop"]["report-as-issue"])
        self.assertIn("report-failure-as-issue: false", self.source)
        self.assertIn("report_incomplete", self.config)

    def test_handoff_prompt_excludes_stale_and_pending_triage_issues(self):
        handoff = self.source.split("## Required Handoff Validation\n", 1)[1].split("\n## ", 1)[0]
        for condition in (
            "positive integer issue number",
            "The target is an issue.",
            "It is open and is not locked.",
            "exactly one service label",
            "exactly one category label",
            "customer-reported",
            "needs-triage",
            "needs-team-triage",
            "issue-addressed",
            "needs-author-feedback",
            "recheck all handoff conditions",
        ):
            with self.subTest(condition=condition):
                self.assertIn(condition, handoff)
        self.assertIn("case-insensitively", handoff)
        self.assertIn("instead of repeating the comment or assignment", handoff)
        self.assertIn("`report_incomplete`", handoff)

    def test_version_prompt_preserves_supported_and_preview_reports(self):
        self.assertNotIn("support is only available for the latest", self.source)
        self.assertNotIn("support applies to the latest package version", self.source)
        self.assertIn("An older minor or patch release is not automatically unsupported.", self.source)
        self.assertIn("Treat preview reports as preview reports.", self.source)
        self.assertIn("Do not recommend a yanked release or an unreleased repository version.", self.source)
        self.assertIn("Python runtime, dependency requirements, and target Azure cloud", self.source)
        self.assertIn("Do not short-circuit solely because the version is older.", self.source)
        self.assertIn("do not invent a version or declare the customer unsupported", self.source)

    def test_examples_do_not_assert_a_current_repository_bug(self):
        template = self.source.split("Template, actionable path.", 1)[1]
        self.assertIn("<the specific source/documentation location", template)
        self.assertNotIn("set_configuration_setting", template)
        self.assertNotIn("PageIterator", template)

    def test_required_documentation_domains_are_allowed(self):
        domain_lines = re.findall(r'^\s+GH_AW_ALLOWED_DOMAINS: "([^"]+)"$', self.lock, re.MULTILINE)
        self.assertTrue(domain_lines)
        for domains in domain_lines:
            with self.subTest(domains=domains):
                self.assertTrue(
                    {"azure.github.io", "learn.microsoft.com", "feedback.azure.com", "pypi.org"}
                    <= set(domains.split(","))
                )


class WorkflowIntegrationTests(unittest.TestCase):
    def test_bootstrap_matches_compiler_and_uses_mounted_copilot(self):
        for name in ("issue-investigation", "issue-triage"):
            with self.subTest(workflow=name):
                lock = read_workflow(name, ".lock.yml")
                compiled = metadata(lock, "metadata")
                manifest = metadata(lock, "manifest")
                self.assertTrue(compiled["strict"])
                version = tuple(int(part) for part in compiled["compiler_version"].lstrip("v").split("."))
                self.assertGreaterEqual(version, (0, 87, 1))
                setups = [action for action in manifest["actions"] if action["repo"] == "github/gh-aw-actions/setup"]
                setup = next(action for action in setups if action["version"] == compiled["compiler_version"])
                self.assertTrue(all(action["sha"] == setup["sha"] for action in setups))
                self.assertIn(f"uses: github/gh-aw-actions/setup@{setup['sha']} # {setup['version']}", lock)
                self.assertIn('GH_AW_COPILOT_SRC="$(command -v copilot', lock)
                self.assertIn('cp "$GH_AW_COPILOT_SRC" "$GH_AW_COPILOT_BIN"', lock)
                self.assertIn('"${RUNNER_TEMP}/gh-aw/bin/copilot"', lock)
                self.assertNotIn("/usr/local/bin/copilot", lock)

    def test_inference_is_read_only_with_native_authentication(self):
        for name in ("issue-investigation", "issue-triage"):
            with self.subTest(workflow=name):
                lock = read_workflow(name, ".lock.yml")
                agent = job(lock, "agent")
                detection = job(lock, "detection")
                for section in (agent, detection):
                    self.assertIn("copilot-requests: write", section)
                    self.assertIn("contents: read", section)
                    self.assertNotIn("contents: write", section)
                    self.assertNotIn("issues: write", section)
                    self.assertNotIn("actions: write", section)
                self.assertNotIn("--allow-tool shell", lock)
                self.assertIn("bash: false", read_workflow(name))
                self.assertNotIn("get_issue", read_workflow(name))
                manifest = metadata(lock, "manifest")
                github = next(server for server in manifest["mcp_servers"] if server["name"] == "github")
                self.assertIn("issue_read", github["tools"])
                self.assertNotIn("get_issue", github["tools"])

    def test_dispatch_is_single_allowlisted_workflow_on_default_branch(self):
        lock = read_workflow("issue-triage", ".lock.yml")
        config = environment_json(lock, "GH_AW_SAFE_OUTPUTS_HANDLER_CONFIG")
        dispatch = config["dispatch_workflow"]
        self.assertEqual(["issue-investigation"], dispatch["workflows"])
        self.assertEqual(1, dispatch["max"])
        self.assertEqual(".lock.yml", dispatch["workflow_files"]["issue-investigation"])
        self.assertEqual(["refs/heads/${{ github.event.repository.default_branch }}"], dispatch["allowed_refs"])
        self.assertIn('"name": "issue_investigation"', lock)
        self.assertIn("actions: write", job(lock, "safe_outputs"))
        source = read_workflow("issue-triage")
        self.assertIn("Do not call `dispatch_workflow` or `issue_investigation` from the agent.", source)
        handoff = job(lock, "investigation_handoff")
        for dependency in ("agent", "detection", "safe_outputs", "mention_owners"):
            self.assertIn(f"- {dependency}", handoff)
            self.assertIn(f"needs.{dependency}.result == 'success'", handoff)
        self.assertIn("process_safe_outputs_status == 'success'", handoff)
        self.assertIn("process_safe_outputs_items_applied", handoff)
        self.assertIn("needs.safe_outputs.outputs.comment_id != ''", handoff)
        self.assertIn("ref: ${{ github.workflow_sha }}", handoff)
        self.assertIn("issues: read", handoff)
        self.assertNotIn("issues: write", handoff)
        self.assertIn("process_safe_outputs.cjs", handoff)
        self.assertIn("needs.mention_owners.result == 'skipped'", handoff)
        self.assertIn("name: safe-outputs-items", handoff)
        self.assertIn("safe-output-items.jsonl", handoff)
        self.assertIn("normalizeAssignment", handoff)
        owners = job(lock, "mention_owners")
        self.assertIn("- safe_outputs", owners)
        self.assertIn("process_safe_outputs_status == 'success'", owners)
        self.assertIn("process_safe_outputs_items_applied", owners)

    def test_handoff_runtime(self):
        source = read_workflow("issue-triage")
        defer_step = source.split("- name: Defer investigation dispatch until triage is applied\n", 1)[1]
        script = textwrap.dedent(defer_step.split("script: |\n", 1)[1].split("\n  jobs:", 1)[0])
        result = subprocess.run(
            ["node", str(WORKFLOWS / "tests" / "issue_investigation_handoff.cjs")],
            input=json.dumps({"deferScript": script}),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Handoff runtime cases passed", result.stdout)

    def test_concurrency_is_partitioned_by_issue(self):
        for name in ("issue-investigation", "issue-triage"):
            with self.subTest(workflow=name):
                lock = read_workflow(name, ".lock.yml")
                groups = re.findall(r"^\s+group: (.+)$", lock, re.MULTILINE)
                self.assertEqual(2, len(groups))
                self.assertTrue(all("github.event.inputs.issue_number" in group for group in groups))
                self.assertIn("cancel-in-progress: false", lock)
                self.assertIn("queue: max", lock)


if __name__ == "__main__":
    unittest.main()
