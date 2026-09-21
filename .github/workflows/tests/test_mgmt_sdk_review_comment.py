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
NO_ENTRIES = "**Breaking-change attribution:** No newly added or modified entries."
CHECKS = "Version consistency; Client signature; README snippets; API-version drift"
SUMMARY = (
    "| Package | Completed checks |\n| --- | --- |\n"
    f"| azure-mgmt-example | {CHECKS} |"
)
ATTRIBUTION = (
    "**Package: azure-mgmt-example | Release: 1.0.0**\n\n"
    "| Changelog entry | Cause | Evidence and explanation | Confidence |\n"
    "| --- | --- | --- | --- |\n"
    "| Removed Widget | Human review | Needs human review: baseline unavailable | N/A |"
)
REVIEW = (
    MARKER + "\n\n## Management SDK PR review\n\n"
    "**Findings:** None.\n\n"
    "### Unverified checks\n\n**Unverified checks:** None.\n\n"
    "### Breaking-change attribution\n\n"
    "**Breaking-change attribution:** No newly added or modified entries.\n\n"
    "### Review summary\n\n"
    + SUMMARY + "\n"
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
            ATTRIBUTION,
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
            SUMMARY,
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

    def test_diagnostic_attribution_and_summary_are_rejected(self):
        for placeholder in ("Full review pending", "None.", "**None.**", "Review pending", "TBD"):
            for section in (NO_ENTRIES, SUMMARY):
                with self.subTest(placeholder=placeholder, section=section):
                    self.assert_rejected({"items": [{"type": "add_comment", "body": REVIEW.replace(section, placeholder)}]})

    def test_formatted_placeholders_in_cells_and_handoffs_are_rejected(self):
        for placeholder in (
            "`None.`", "_Done_", "**`None.`**", "`_Done_`", "~~**None.**~~",
            "_Full_ **review** `pending`", "**Full   review pending.**",
        ):
            bodies = (
                REVIEW.replace(CHECKS, placeholder),
                REVIEW.replace(NO_ENTRIES, ATTRIBUTION.replace("Removed Widget", placeholder)),
                REVIEW.replace(NO_ENTRIES, ATTRIBUTION.replace("Needs human review: baseline unavailable", placeholder)),
                REVIEW.replace(NO_ENTRIES,
                               "**Package: azure-mgmt-example | Release: unverified**\n\n"
                               "**Needs human review:** " + placeholder),
            )
            for body in bodies:
                with self.subTest(placeholder=placeholder, body=body):
                    self.assert_rejected({"items": [{"type": "add_comment", "body": body}]})

    def test_formatted_evidence_is_preserved(self):
        evidence = (
            '`Widget._check()` returns `None` per **API documentation**, not a review placeholder; '
            '[source](https://github.com/Azure/example/blob/' + "a" * 40 + '/_widget.py#L42).'
        )
        body = REVIEW.replace(NO_ENTRIES, ATTRIBUTION.replace(
            "Needs human review: baseline unavailable", "Needs human review: source unresolved; " + evidence
        ))
        payload = {"items": [{"type": "add_comment", "body": body}]}
        self.run_guard(payload)
        self.assertEqual(body, payload["items"][0]["body"])
        for evidence in ("`<Widget>`", "<https://github.com/Azure/example>", "`value & other`"):
            with self.subTest(evidence=evidence):
                body = REVIEW.replace(NO_ENTRIES, ATTRIBUTION.replace(
                    "Needs human review: baseline unavailable", "Needs human review: source unresolved; " + evidence
                ))
                self.run_guard({"items": [{"type": "add_comment", "body": body}]})

    def test_rendered_placeholders_are_rejected(self):
        for placeholder in (
            "None!", "Done?!", "[None.](https://example.invalid)", "![None.](https://example.invalid/image.png)",
            "<strong>None.</strong>", "<em>Full review pending!</em>", "&#78;one&#33;",
            "[**None!**](https://example.invalid)", "<strong>&#78;one!</strong>",
        ):
            for body in (
                REVIEW.replace(CHECKS, placeholder),
                REVIEW.replace(NO_ENTRIES, ATTRIBUTION.replace("Needs human review: baseline unavailable", placeholder)),
                REVIEW.replace(NO_ENTRIES, "**Package: azure-mgmt-example | Release: unverified**\n\n"
                               "**Needs human review:** " + placeholder),
            ):
                with self.subTest(placeholder=placeholder, body=body):
                    self.assert_rejected({"items": [{"type": "add_comment", "body": body}]})

    def test_handoff_is_one_wrapped_prose_paragraph(self):
        handoff = (
            "**Package: azure-mgmt-example | Release: unverified**\n\n"
            "**Needs human review:** The [changelog](https://github.com/Azure/example/blob/"
            + "a" * 40 + "/CHANGELOG.md#L1) was truncated\n"
            "before the <strong>release heading</strong> &amp; entry evidence."
        )
        self.run_guard({"items": [{"type": "add_comment", "body": REVIEW.replace(NO_ENTRIES, handoff)}]})
        for trailing in (
            "\n| Bad | Table |", "\nBad | Table", "\n### Extra heading", "\n## Extra heading",
            "\n\nAnother paragraph.", "\n- Extra list", "\n```text\nExtra block\n```", "\n---",
            "\n<table><tr><td>Bad table</td></tr></table>",
        ):
            with self.subTest(trailing=trailing):
                self.assert_rejected({"items": [{"type": "add_comment",
                                                "body": REVIEW.replace(NO_ENTRIES, handoff + trailing)}]})

    def test_completed_checks_use_positive_reporting_names(self):
        for checks in (
            "Unable to complete review because the evidence tool failed",
            "README snippets; Unable to complete review because the evidence tool failed",
            "README snippets;", "README snippets; README snippets", "Everything looks fine",
        ):
            with self.subTest(checks=checks):
                self.assert_rejected({"items": [{"type": "add_comment", "body": REVIEW.replace(CHECKS, checks)}]})
        for check in (
            "Management package discovery", "Version consistency", "Preview version", "Changelog date",
            "Stability flags", "Client signature", "Client name consistency", "README snippets", "API-version drift",
        ):
            with self.subTest(check=check):
                self.run_guard({"items": [{"type": "add_comment", "body": REVIEW.replace(CHECKS, check)}]})

    def test_optional_none_headings_allow_trailing_whitespace(self):
        for unverified_suffix in ("", "   ", "\t", " \t "):
            for attribution_suffix in ("", "   ", "\t", " \t "):
                for omitted in (None, "Unverified checks", "Breaking-change attribution"):
                    with self.subTest(unverified=unverified_suffix, attribution=attribution_suffix, omitted=omitted):
                        body = REVIEW
                        for heading, suffix in (
                            ("Unverified checks", unverified_suffix),
                            ("Breaking-change attribution", attribution_suffix),
                        ):
                            body = body.replace(
                                f"### {heading}\n",
                                "" if heading == omitted else f"### {heading}{suffix}\n",
                            )
                        self.run_guard({"items": [{"type": "add_comment", "body": body}]})

    def test_attribution_requires_package_release_and_populated_table(self):
        for attribution in (
            "**Package: azure-mgmt-example | Release: 1.0.0**",
            ATTRIBUTION.rsplit("\n", 1)[0],
            ATTRIBUTION.replace("**Package: azure-mgmt-example | Release: 1.0.0**\n\n", ""),
            ATTRIBUTION.replace("Release: 1.0.0", "Release: None."),
            ATTRIBUTION.replace("Needs human review: baseline unavailable", "Full review pending"),
            ATTRIBUTION.replace("Removed Widget", ""),
            ATTRIBUTION.replace("Evidence and explanation", "Evidence"),
        ):
            with self.subTest(attribution=attribution):
                self.assert_rejected({"items": [{"type": "add_comment", "body": REVIEW.replace(NO_ENTRIES, attribution)}]})

    def test_attribution_cause_confidence_and_handoff_reason(self):
        template = ATTRIBUTION.rsplit("\n", 1)[0] + "\n| Removed Widget | {} | {} | {} |"
        invalid = (
            ("Human review", "Needs human review", "N/A"),
            ("Human review", "Needs human review: **None!**", "N/A"),
            ("Human review", "Needs human review: baseline unavailable", "High"),
            ("TypeSpec/API", "Explicit renamedFrom evidence", "N/A"),
            ("Generator", "An emitter version changed", "High"),
            ("TypeSpec/API", "Explicit renamedFrom evidence", "Low"),
            ("Human review", "No baseline found", "N/A"),
        )
        for row in invalid:
            with self.subTest(row=row):
                body = REVIEW.replace(NO_ENTRIES, template.format(*row))
                self.assert_rejected({"items": [{"type": "add_comment", "body": body}]})
        valid = (
            ("`Human review`", "**Needs human review:** baseline unavailable", "**N/A**"),
            ("Human review", "Needs human review - baseline unavailable", "`N/A`"),
            ("`TypeSpec/API`", "Explicit renamedFrom evidence", "`High`"),
            ("**TypeSpec/API**", "Explicit renamedFrom evidence", "**High**: directly mapped source"),
            ("TypeSpec/API", "Explicit renamedFrom evidence", "High (directly mapped source)"),
        )
        for row in valid:
            with self.subTest(row=row):
                self.run_guard({"items": [{"type": "add_comment", "body": REVIEW.replace(NO_ENTRIES, template.format(*row))}]})

    def test_summary_requires_package_names_and_completed_checks(self):
        for summary in (
            SUMMARY.rsplit("\n", 1)[0],
            SUMMARY.replace("azure-mgmt-example", "example"),
            SUMMARY.replace("azure-mgmt-example", ""),
            SUMMARY.replace(CHECKS, "None."),
            SUMMARY.replace(CHECKS, "Full review pending"),
            SUMMARY.replace(CHECKS, ""),
            SUMMARY.replace(CHECKS, "Done"),
            SUMMARY + "\n" + SUMMARY.splitlines()[-1],
        ):
            with self.subTest(summary=summary):
                self.assert_rejected({"items": [{"type": "add_comment", "body": REVIEW.replace(SUMMARY, summary)}]})

    def test_multi_package_review_and_incomplete_collection(self):
        handoff = (
            "**Package: azure-mgmt-another | Release: unverified**\n\n"
            "**Needs human review:** Changelog collection was truncated before the release heading."
        )
        body = REVIEW.replace(NO_ENTRIES, ATTRIBUTION + "\n\n" + handoff).replace(
            SUMMARY, SUMMARY + "\n| `sdk/another/azure-mgmt-another` | API-version drift; README snippets |"
        )
        self.run_guard({"items": [{"type": "add_comment", "body": body}]})
        self.assert_rejected({"items": [{"type": "add_comment", "body": REVIEW.replace(NO_ENTRIES, handoff)}]})
        handoff = handoff.replace("azure-mgmt-another", "azure-mgmt-example")
        limited_review = REVIEW.replace(NO_ENTRIES, handoff).replace(
            CHECKS, "README snippets"
        ).replace("**Unverified checks:** None.",
                  "| Check | Reason |\n| --- | --- |\n| Client signature | Client file unavailable |")
        self.run_guard({"items": [{"type": "add_comment", "body": limited_review}]})
        for reason in ("None.", "Full review pending", "", "| Header | Reason |"):
            invalid = handoff.split("**Needs human review:**", 1)[0] + "**Needs human review:** " + reason
            self.assert_rejected({"items": [{"type": "add_comment", "body": REVIEW.replace(NO_ENTRIES, invalid)}]})

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
                ' with `@clientName("Widget")` and `@Azure.ClientGenerator.Core.clientName("Widget")`'
                for _ in range(13)
            )
            + "\nhttps://github.com/Azure/example/blob/" + "a" * 40 + "/main.tsp#L42-L48"
            + "\nhttps://github.com/Azure/example/blob/" + "b" * 40 + "/@renamedFrom.tsp#L1"
            + "\nhttps://github.com/Azure/example/blob/" + "c" * 40 + "/@clientName.tsp#L1"
            + "\ncontact@example.com and identifier@clientName remain unchanged."
            + '\nQuoted "text", escaped \\ path, and Markdown | delimiters.'
        )
        body = REVIEW.replace(NO_ENTRIES, ATTRIBUTION.replace(
            "Needs human review: baseline unavailable",
            "Needs human review: source unresolved; " + evidence.replace("\n", "<br>").replace("|", "\\|")
        ))
        result = subprocess.run(
            [jq, "-Rs", command[1]], input=body, text=True, capture_output=True, check=True
        )
        payload = json.loads(result.stdout)
        self.assertEqual({"body": body.replace("`@", "`")},
                         payload)
        self.assertNotIn("`@", payload["body"])
        self.run_guard({"items": [{"type": "add_comment", **payload}]})
        self.assertIn('"jq"', SOURCE.split("safe-outputs:", 1)[0])


if __name__ == "__main__":
    unittest.main()
