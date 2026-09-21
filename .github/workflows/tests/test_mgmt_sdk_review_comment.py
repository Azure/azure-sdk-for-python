import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from unittest import mock


WORKFLOW = Path(__file__).parents[1] / "mgmt-sdk-pr-review.md"
SOURCE = WORKFLOW.read_text(encoding="utf-8")
GUARD = textwrap.dedent(
    SOURCE.split("python - <<'PY'")[2].split("\n        PY", 1)[0]
)
MARKER = "<!-- gh-aw-workflow-id: mgmt-sdk-pr-review -->"
REVIEW = (
    MARKER + "\n\n## Management SDK PR review\n\n"
    "**Findings:** None.\n\n"
    "### Unverified checks\n\n**Unverified checks:** None.\n\n"
    "### Breaking-change attribution\n\n"
    "**Breaking-change attribution:** No newly added or modified entries.\n\n"
    "### Review summary\n\n"
    "Reviewed azure-mgmt-example: version consistency, client signature, README, and API-version drift.\n"
)
NOT_APPLICABLE = (
    MARKER + "\n## Management SDK review not applicable\n\n"
    "This pull request does not change a package matching `sdk/*/azure-mgmt-*`."
)


class ReviewCommentTests(unittest.TestCase):
    def run_guard(self, payload):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "agent_output.json"
            output.write_text(json.dumps(payload), encoding="utf-8")
            with mock.patch.dict(os.environ, {"GH_AW_AGENT_OUTPUT": str(output)}):
                exec(compile(GUARD, "review-comment-guard", "exec"), {})

    def assert_rejected(self, payload):
        publisher = mock.Mock()
        with self.assertRaisesRegex(SystemExit, "No review will be published or hidden"):
            self.run_guard(payload)
            publisher()
        publisher.assert_not_called()

    def test_valid_review(self):
        self.run_guard({"items": [{"type": "add_comment", "body": REVIEW}]})

    def test_not_applicable(self):
        self.run_guard({"items": [{"type": "add_comment", "body": NOT_APPLICABLE}]})

    def test_sanitized_bodies_without_html_marker(self):
        for body in (REVIEW, NOT_APPLICABLE):
            with self.subTest(body=body):
                self.run_guard({"items": [{"type": "add_comment", "body": body.removeprefix(MARKER).lstrip()}]})

    def test_none_sections_without_headings_remain_valid(self):
        body = REVIEW.replace("### Unverified checks\n\n", "").replace("### Breaking-change attribution\n\n", "")
        self.run_guard({"items": [{"type": "add_comment", "body": body}]})

    def test_findings_unverified_and_attribution_evidence(self):
        body = REVIEW.replace(
            "**Findings:** None.",
            "| Severity | Finding | Location | Evidence | Rule | Remediation |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| Blocking | API version changed | [metadata](https://github.com/Azure/example/blob/"
            + "a" * 40
            + "/_metadata.json#L2) | old \\| new | API drift | Restore original version |",
        ).replace(
            "**Unverified checks:** None.",
            "| Check | Reason |\n| --- | --- |\n| README | File was truncated |",
        ).replace(
            "**Breaking-change attribution:** No newly added or modified entries.",
            "**Package: azure-mgmt-example | Release: 1.0.0**\n\n"
            "| Changelog entry | Cause | Evidence and explanation | Confidence |\n"
            "| --- | --- | --- | --- |\n"
            "| Removed Widget | Human review | Needs human review: baseline unavailable | N/A |",
        )
        self.run_guard({"items": [{"type": "add_comment", "body": body}]})

    def test_placeholder_and_malformed_bodies_do_not_reach_publisher(self):
        for body in ("-", "", " ", None, 123, "@comment.md", "Full review pending", MARKER):
            with self.subTest(body=body):
                self.assert_rejected({"items": [{"type": "add_comment", "body": body}]})
        self.assert_rejected({"items": [{"type": "add_comment"}]})

    def test_missing_or_empty_sections_do_not_reach_publisher(self):
        for heading in ("Unverified checks", "Breaking-change attribution", "Review summary"):
            with self.subTest(heading=heading):
                body = re.sub(rf"(?ms)^### {heading}\n.*?(?=^### |\Z)", "", REVIEW)
                self.assert_rejected({"items": [{"type": "add_comment", "body": body}]})
        for content in (
            "**Findings:** None.",
            "**Unverified checks:** None.",
            "**Breaking-change attribution:** No newly added or modified entries.",
            "Reviewed azure-mgmt-example: version consistency, client signature, README, and API-version drift.",
        ):
            with self.subTest(content=content):
                self.assert_rejected({"items": [{"type": "add_comment", "body": REVIEW.replace(content, "-")}]})

    def test_header_only_table_and_duplicate_sections_are_rejected(self):
        bodies = [
            REVIEW.replace("**Findings:** None.",
                           "| Severity | Finding | Location | Evidence | Rule | Remediation |\n"
                           "| --- | --- | --- | --- | --- | --- |"),
            REVIEW + "\n### Review summary\nDuplicate summary.",
            REVIEW.replace("### Review summary", "### Unverified checks"),
            NOT_APPLICABLE.replace("This pull request does not change a package", "-"),
        ]
        for body in bodies:
            with self.subTest(body=body):
                self.assert_rejected({"items": [{"type": "add_comment", "body": body}]})

    def test_missing_multiple_and_diagnostic_outputs_are_rejected(self):
        comment = {"type": "add_comment", "body": REVIEW}
        for payload in (None, {}, {"items": None}, {"items": []}, {"items": [comment, comment]}, {"items": [None]}):
            with self.subTest(payload=payload):
                self.assert_rejected(payload)
        for kind in ("report_incomplete", "missing_tool", "missing_data", "noop"):
            diagnostic = {"type": kind, "reason": "Could not submit review"}
            with self.subTest(kind=kind):
                self.assert_rejected({"items": [diagnostic]})
                self.assert_rejected({"items": [comment, diagnostic]})

    def test_missing_or_invalid_artifact_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "agent_output.json"
            with mock.patch.dict(os.environ, {"GH_AW_AGENT_OUTPUT": str(output)}):
                with self.assertRaisesRegex(SystemExit, "No review will be published or hidden"):
                    exec(compile(GUARD, "review-comment-guard", "exec"), {})
                output.write_text("{", encoding="utf-8")
                with self.assertRaisesRegex(SystemExit, "No review will be published or hidden"):
                    exec(compile(GUARD, "review-comment-guard", "exec"), {})

    def test_compiled_guard_precedes_unconditional_builtin_publisher(self):
        lock = WORKFLOW.with_suffix(".lock.yml").read_text(encoding="utf-8")
        job = lock.split("\n  safe_outputs:\n", 1)[1]
        guard_index = job.index("name: Validate management SDK review comment")
        publisher_index = job.index("name: Process Safe Outputs")
        self.assertLess(job.index("name: Download agent output artifact"), guard_index)
        self.assertLess(job.index("id: setup-agent-output-env"), guard_index)
        self.assertLess(guard_index, publisher_index)
        guard_step = job[guard_index:publisher_index]
        self.assertNotIn("continue-on-error", guard_step)
        self.assertNotIn("if:", guard_step)
        publisher_step = job[publisher_index:].split("\n      - name:", 1)[0]
        self.assertNotIn("if:", publisher_step)
        self.assertIn("process_safe_outputs.cjs", publisher_step)
        self.assertIn('\\"hide_older_comments\\":true', publisher_step)
        self.assertIn('\\"max\\":1', publisher_step)
        compiled_guard = textwrap.dedent(
            guard_step.split("python - <<'PY'\n", 1)[1].split("\n          PY", 1)[0]
        )
        self.assertEqual(GUARD.strip(), compiled_guard.strip())
        agent = re.split(r"\n  [a-z_]+:\n", lock.split("\n  agent:\n", 1)[1])[0]
        self.assertNotIn("pull-requests: write", agent)
        self.assertIn("checkout: false", SOURCE)

    def test_documented_jq_submission_preserves_complete_evidence(self):
        jq = shutil.which("jq")
        self.assertIsNotNone(jq, "Install jq to test the workflow's actual submission command.")
        command = re.search(r"(?m)^jq -Rs '([^']+)' .* \| safeoutputs add_comment \.$", SOURCE)
        self.assertIsNotNone(command)
        evidence = (
            "\n".join(
                '`@renamedFrom(Versions.v1, "OldWidget")` and `@typeChangedFrom(Versions.v1, string)`'
                for _ in range(13)
            )
            + "\nhttps://github.com/Azure/example/blob/" + "a" * 40 + "/main.tsp#L42-L48"
            + "\nhttps://github.com/Azure/example/blob/" + "b" * 40 + "/@renamedFrom.tsp#L1"
            + '\nQuoted "text", escaped \\ path, and Markdown | delimiters.'
        )
        body = REVIEW.replace(
            "**Breaking-change attribution:** No newly added or modified entries.", evidence
        )
        result = subprocess.run(
            [jq, "-Rs", command[1]], input=body, text=True, capture_output=True, check=True
        )
        payload = json.loads(result.stdout)
        self.assertEqual({"body": body.replace("`@renamedFrom", "`renamedFrom").replace("`@typeChangedFrom", "`typeChangedFrom")},
                         payload)
        self.assertNotIn("`@", payload["body"])
        self.run_guard({"items": [{"type": "add_comment", **payload}]})
        self.assertIn('"jq"', SOURCE.split("safe-outputs:", 1)[0])


if __name__ == "__main__":
    unittest.main()
