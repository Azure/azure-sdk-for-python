import hashlib
import json
import os
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


def job_needs(block):
    field = re.search(r"(?m)^    needs:([^\n]*)\n((?:      - [^\n]+\n)*)", block)
    if not field:
        return []
    inline = field.group(1).strip()
    return [inline] if inline else re.findall(r"(?m)^      - (.+)$", field.group(2))


def job_condition(block):
    field = re.search(r"(?m)^    if:([^\n]*)\n((?:      [^\n]+\n)*)", block)
    if not field:
        return ""
    inline = field.group(1).strip()
    return " ".join(line.strip() for line in field.group(2).splitlines()) if inline in (">", ">-", "|", "|-") else inline


def job_permissions(block):
    field = re.search(r"(?m)^    permissions:\n((?:      [\w-]+: [^\n]+\n)+)", block)
    return dict(re.findall(r"(?m)^      ([\w-]+): (.+)$", field.group(1))) if field else {}

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
        self.assertIn("perPage: 100", handoff)
        self.assertIn("paginating through all pages", handoff)
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
                self.assertIn('GH_AW_ENGINE_VERSION: "1.0.80"', lock)
                ci = (WORKFLOWS / "issue-workflow-contracts.yml").read_text(encoding="utf-8")
                self.assertIn(f"github/gh-aw-actions/setup@{setup['sha']}", ci)
                self.assertIn("GH_AW_RUNTIME:", ci)

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

    def test_investigation_is_independent_and_opt_in(self):
        lock = read_workflow("issue-triage", ".lock.yml")
        config = environment_json(lock, "GH_AW_SAFE_OUTPUTS_HANDLER_CONFIG")
        self.assertNotIn("dispatch_workflow", config)
        self.assertNotIn("issue_investigation", lock)
        self.assertNotIn("investigation_handoff", lock)
        self.assertNotIn("issue_workflow_support.cjs", lock)
        relay = read_workflow("issue-investigation-handoff", ".yml")
        self.assertIn("workflow_run:", relay)
        self.assertIn("workflows: [Agentic Triage]", relay)
        self.assertIn("GH_AW_ENABLE_ISSUE_INVESTIGATION == 'true'", relay)
        self.assertIn("head_repository.full_name == github.repository", relay)
        self.assertIn("head_branch == github.event.repository.default_branch", relay)
        self.assertIn("ref: ${{ github.workflow_sha }}", relay)
        self.assertIn("artifact-ids:", relay)
        self.assertIn("run-id:", relay)
        self.assertIn("process_safe_outputs.cjs", relay)
        self.assertIn("issues: read", relay)
        self.assertNotIn("issues: write", relay)
        self.assertNotIn("copilot-requests", relay)

    def test_handoff_runtime(self):
        result = subprocess.run(
            ["node", str(WORKFLOWS / "tests" / "issue_investigation_handoff.cjs")],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Handoff runtime cases passed", result.stdout)

    def test_close_issue_uses_body(self):
        source = read_workflow("issue-investigation")
        self.assertIn("Supply this explanation directly in the `body` parameter of `close_issue`.", source)
        self.assertIn("The `close_issue` handler posts the explanation comment first and aborts closure if comment posting fails", source)
        self.assertIn("Do not call `add_comment` separately when closing an issue.", source)

    def test_copilot_assignment_job_and_runtime(self):
        source = read_workflow("issue-investigation")
        self.assertIn("Defer Copilot assignment until investigation comment is applied", source)
        lock = read_workflow("issue-investigation", ".lock.yml")
        assignment = job(lock, "copilot_assignment")
        for dependency in ("agent", "detection", "safe_outputs"):
            self.assertIn(f"- {dependency}", assignment)
            self.assertIn(f"needs.{dependency}.result == 'success'", assignment)
        self.assertIn("process_safe_outputs_status == 'success'", assignment)
        self.assertIn("process_safe_outputs_items_applied", assignment)
        self.assertIn("needs.safe_outputs.outputs.comment_id != ''", assignment)
        self.assertIn("ref: ${{ github.workflow_sha }}", assignment)
        self.assertIn("process_safe_outputs.cjs", assignment)
        self.assertIn("completed_with_skips", assignment)
        result = subprocess.run(
            ["node", str(WORKFLOWS / "tests" / "copilot_assignment.cjs")],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Copilot assignment cases passed", result.stdout)

    def test_pinned_workflow_runtime_contracts(self):
        source = read_workflow("issue-investigation")
        step = source.split("- name: Confirm Copilot assignment succeeded\n", 1)[1]
        condition = textwrap.dedent(step.split("if: >-\n", 1)[1].split("\n        uses:", 1)[0]).strip()
        if not os.environ.get("GH_AW_RUNTIME"):
            self.skipTest("Set GH_AW_RUNTIME to run pinned native handler contracts")
        result = subprocess.run(
            ["node", str(WORKFLOWS / "tests" / "issue_workflow_runtime.cjs")],
            input=json.dumps({"assignmentCondition": condition}),
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Pinned workflow runtime contracts passed", result.stdout)

    def test_investigation_guard_executes_before_its_mutations(self):
        lock = read_workflow("issue-investigation", ".lock.yml")
        section = job(lock, "safe_outputs")
        self.assertIn("contents: read", section)
        self.assertIn("ref: ${{ github.workflow_sha }}", section)
        self.assertIn("issue_workflow_support.cjs", section)
        self.assertLess(section.index("Checkout trusted output guard"), section.index("Process Safe Outputs"))
        self.assertLess(section.index("validate"), section.index("Process Safe Outputs"))
        self.assertIn('GH_AW_MISSING_TOOL_CREATE_ISSUE: "false"', lock)
        self.assertIn('GH_AW_REPORT_INCOMPLETE_CREATE_ISSUE: "false"', lock)

    def test_independent_relay_runtime(self):
        relay = read_workflow("issue-investigation-handoff", ".yml")
        condition = textwrap.dedent(relay.split("    if: >-\n", 1)[1].split("\n    runs-on:", 1)[0]).strip()
        result = subprocess.run(
            ["node", str(WORKFLOWS / "tests" / "completed_triage_handoff.cjs")],
            input=json.dumps({"source": read_workflow("issue-triage"), "relayCondition": condition}),
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Independent triage relay contracts passed", result.stdout)

    def test_legacy_triage_output_and_routing_contracts_are_preserved(self):
        baseline = json.loads((WORKFLOWS / "tests" / "fixtures" / "triage-controls.json").read_text(encoding="utf-8"))
        source = read_workflow("issue-triage")
        outputs = source.split("\nsafe-outputs:\n", 1)[1].split("\ntools:\n", 1)[0].strip()
        self.assertEqual(baseline["safe_outputs_source_hash"], hashlib.sha256(outputs.encode()).hexdigest())
        lock = read_workflow("issue-triage", ".lock.yml")
        for name, expected in baseline["jobs"].items():
            with self.subTest(job=name):
                block = job(lock, name)
                self.assertEqual(expected["needs"], job_needs(block))
                self.assertEqual(expected["condition"], job_condition(block))
                self.assertEqual(expected["permissions"], job_permissions(block))
        self.assertEqual(baseline["handler_config"], environment_json(lock, "GH_AW_SAFE_OUTPUTS_HANDLER_CONFIG"))
        self.assertNotIn("safe_outputs", job_needs(job(lock, "mention_owners")))
        self.assertNotIn("investigation", job(lock, "conclusion"))
        self.assertNotIn("workflow-output-guard", job(lock, "safe_outputs"))
        lint = (WORKFLOWS / "actionlint.yml").read_text(encoding="utf-8")
        self.assertEqual(baseline["actionlint_source_hash"], hashlib.sha256(lint.encode()).hexdigest())
        self.assertNotIn("workflow-contract-runtime", lint)
        self.assertIn("paths:", (WORKFLOWS / "issue-workflow-contracts.yml").read_text(encoding="utf-8"))

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
