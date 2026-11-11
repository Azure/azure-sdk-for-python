#!/usr/bin/env python3
"""Read-only management SDK PR queues for release rotators (Python 3.10+)."""

from __future__ import annotations

import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import re
import subprocess
import sys
from threading import RLock
from urllib.parse import quote

WORKFLOW = "mgmt-sdk-pr-review.lock.yml"
ACTIVE_STATUSES = ("queued", "in_progress", "waiting", "pending", "requested")
PACKAGE = re.compile(r"^\[AutoPR (azure-mgmt-[^\]\s]+)\]")
SECTIONS = (
    "Automated review needs triggering",
    "Automated review active",
    "Human review needed",
    "Changes after approval",
    "Author follow-up after approval",
)


class CollectionError(RuntimeError):
    """GitHub evidence could not be collected."""


def gh(*args):
    try:
        result = subprocess.run(
            ["gh", *args], capture_output=True, text=True, encoding="utf-8", timeout=90, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise CollectionError(f"GitHub CLI unavailable or timed out: {error}") from error
    if result.returncode:
        raise CollectionError(f"gh {' '.join(args)}: {result.stderr.strip()}")
    try:
        return json.loads(result.stdout)
    except ValueError as error:
        raise CollectionError("GitHub CLI returned invalid JSON.") from error


class GitHub:
    def __init__(self, repo):
        self.repo = repo
        self.cache = {}
        self.lock = RLock()

    def get(self, endpoint):
        return gh("api", endpoint)

    def cached(self, endpoint):
        with self.lock:
            if endpoint not in self.cache:
                try:
                    self.cache[endpoint] = self.get(endpoint)
                except CollectionError as error:
                    self.cache[endpoint] = error
            value = self.cache[endpoint]
        if isinstance(value, CollectionError):
            raise value
        return value

    def pages(self, endpoint, key=None):
        pages = gh("api", "--paginate", "--slurp", endpoint)
        items = [item for page in pages for item in (page[key] if key else page)]
        if key and pages and len(items) < pages[0].get("total_count", len(items)):
            raise CollectionError(f"Incomplete pagination for {endpoint}.")
        return items

    def owners(self, base_sha, files, package):
        with self.lock:
            cache_key = ("owners", base_sha)
            if cache_key not in self.cache:
                self.cache[cache_key] = self.load_rules(base_sha)
            rules = self.cache[cache_key]
        owners = set()
        paths = []
        for file in files:
            path = file["filename"]
            if package in path.split("/"):
                paths.append(file.get("previous_filename", path) if file["status"] == "renamed" else path)
        if not paths:
            raise CollectionError("No changed package files; cannot resolve maintainers.")
        for path in paths:
            matched = ()
            for pattern, candidates in rules:
                if pattern.search(path):
                    matched = candidates
            if not matched:
                raise CollectionError(f"No CODEOWNERS for {path}.")
            owners.update(matched)
        maintainers = set()
        skipped_team = False
        for owner in owners:
            if not owner.startswith("@"):
                raise CollectionError(f"Cannot resolve CODEOWNERS identity {owner}.")
            if "/" in owner:
                org, team = owner[1:].split("/", 1)
                with self.lock:
                    key = ("team", owner.casefold())
                    if key not in self.cache:
                        try:
                            self.cache[key] = self.pages(f"orgs/{org}/teams/{team}/members?per_page=100")
                        except CollectionError as error:
                            self.cache[key] = error
                    members = self.cache[key]
                if isinstance(members, CollectionError):
                    if owner.casefold() == "@azure/azure-arm-sdk-reviewers" and "HTTP 403" in str(members):
                        skipped_team = True
                        continue
                    raise members
                maintainers.update(member["login"].casefold() for member in members)
            else:
                maintainers.add(owner[1:].casefold())
        return maintainers, sorted(owners, key=str.casefold), skipped_team

    def load_rules(self, base_sha):
        for path in (".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS"):
            try:
                data = self.cached(f"repos/{self.repo}/contents/{path}?ref={quote(base_sha, safe='')}")
            except CollectionError as error:
                if "HTTP 404" in str(error):
                    continue
                raise
            if data.get("encoding") != "base64":
                raise CollectionError(f"Cannot decode {path}.")
            return parse_codeowners(base64.b64decode(data["content"]).decode("utf-8"))
        raise CollectionError("No base-branch CODEOWNERS found.")


def parse_codeowners(text):
    rules = []
    for line in text.splitlines():
        fields = line.split("#", 1)[0].split()
        if not fields or fields[0].startswith("!") or any(char in fields[0] for char in "[]"):
            continue
        pattern = fields[0]
        if "\\" in pattern:
            raise CollectionError("Escaped CODEOWNERS patterns require manual ownership verification.")
        rooted = pattern.startswith("/") or "/" in pattern.rstrip("/")
        directory = pattern.endswith("/")
        parts = pattern.strip("/").split("/")
        expression = "^" if rooted else r"(?:^|/)"
        for index, part in enumerate(parts):
            if part == "**":
                expression += ".*" if index == len(parts) - 1 else "(?:[^/]+/)*"
            else:
                expression += "".join(
                    "[^/]*" if char == "*" else "[^/]" if char == "?" else re.escape(char) for char in part
                )
                if index < len(parts) - 1:
                    expression += "/"
        expression += "/" if directory else r"(?:/|$)"
        rules.append((re.compile(expression), tuple(fields[1:])))
    if not rules:
        raise CollectionError("No usable CODEOWNERS rules.")
    return rules


def timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def effective_approval(reviews, maintainers):
    latest = {}
    for review in sorted(
        (item for item in reviews if item.get("submitted_at")),
        key=lambda item: (timestamp(item["submitted_at"]), item["id"]),
    ):
        login = (review.get("user") or {}).get("login", "").casefold()
        if login in maintainers and review["state"] in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}:
            latest[login] = review
    approvals = [review for review in latest.values() if review["state"] == "APPROVED"]
    return max(approvals, key=lambda review: timestamp(review["submitted_at"]), default=None)


def sdk_version(files):
    for file in files:
        if file["filename"].endswith("/_version.py"):
            match = re.search(r"""^\+\s*VERSION\s*=\s*["']([^"']+)""", file.get("patch", ""), re.MULTILINE)
            if match:
                return match[1]
    for file in files:
        if file["filename"].endswith("/CHANGELOG.md"):
            match = re.search(r"^\+##\s+([0-9][^\s(]*)", file.get("patch", ""), re.MULTILINE)
            if match:
                return match[1]
    return "unknown"


def run_pr(run, number):
    return next((pr for pr in run.get("pull_requests", []) if pr["number"] == number), None)


def active_reviews(client):
    runs = {}
    issues = []
    try:
        for run in client.pages(
            f"repos/{client.repo}/actions/workflows/{WORKFLOW}/runs?per_page=100",
            "workflow_runs",
        ):
            if run["status"] != "completed":
                runs[run["id"]] = run
    except CollectionError as error:
        issues.append(f"Review activity unknown: {error}")
    for run in runs.values():
        if not run.get("pull_requests"):
            issues.append(f"Review activity unknown: active run has no PR association: {run['html_url']}")
    return list(runs.values()), issues


def bot_review(comments):
    candidates = []
    for comment in comments:
        body = comment.get("body") or ""
        if (
            (comment.get("user") or {}).get("login", "").casefold() == "github-actions[bot]"
            and "## Management SDK PR review" in body
            and ("<!-- gh-aw-workflow-id: mgmt-sdk-pr-review -->" in body or "workflow_id: mgmt-sdk-pr-review," in body)
        ):
            candidates.append(comment)
    return max(candidates, key=lambda item: (timestamp(item["created_at"]), item["id"]), default=None)


def review_freshness(client, workflow_id, pr, comment):
    if comment is None:
        return "missing"
    match = re.search(
        rf"https://github\.com/{re.escape(client.repo)}/actions/runs/([0-9]+)\b", comment["body"], re.IGNORECASE
    )
    if not match:
        raise CollectionError(f"Automated review freshness unknown: no linked workflow run in {comment['html_url']}")
    run = client.cached(f"repos/{client.repo}/actions/runs/{match[1]}")
    association = run_pr(run, pr["number"])
    if run["workflow_id"] != workflow_id or association is None or not association.get("head", {}).get("sha"):
        raise CollectionError(f"Automated review freshness unknown: cannot verify linked run {run['html_url']}")
    return "current" if association["head"]["sha"] == pr["head"]["sha"] else "outdated"


def collect_pr(client, summary):
    number = summary["number"]
    endpoint = f"repos/{client.repo}/pulls/{number}"
    pr = client.get(endpoint)
    if pr["state"] != "open" or pr["draft"]:
        return None
    if summary.get("updatedAt") != pr["updated_at"]:
        raise CollectionError(f"PR #{number} changed since initial listing; rerun before acting.")
    match = PACKAGE.match(pr["title"])
    if not match:
        return None
    name = match[1]
    files = client.pages(f"{endpoint}/files?per_page=100")
    package_files = [file for file in files if name in file["filename"].split("/")]
    if len(files) < pr["changed_files"]:
        raise CollectionError(f"Changed-file listing incomplete for PR #{number}.")
    comments = client.pages(f"repos/{client.repo}/issues/{number}/comments?per_page=100")
    reviews = client.pages(f"{endpoint}/reviews?per_page=100")
    issues = []
    try:
        maintainers, owners, skipped_team = client.owners(pr["base"]["sha"], files, name)
    except CollectionError as error:
        maintainers, owners, skipped_team = None, [], False
        issues.append(f"Approval verification incomplete: {error}")
    approval = effective_approval(reviews, maintainers) if maintainers is not None else None
    if (
        skipped_team
        and approval is None
        and summary.get("reviewDecision")
        not in {
            "APPROVED",
            "REVIEW_REQUIRED",
            "CHANGES_REQUESTED",
        }
    ):
        issues.append("GitHub review decision unavailable; cannot verify team-only approval.")
    followups = []
    if approval:
        inline = client.pages(f"{endpoint}/comments?per_page=100")
        author = pr["user"]["login"].casefold()
        for comment in comments + inline + reviews:
            created = comment.get("submitted_at") if "state" in comment else comment.get("created_at")
            if (
                created
                and (comment.get("user") or {}).get("login", "").casefold() == author
                and (comment.get("body") or "").strip()
                and timestamp(created) > timestamp(approval["submitted_at"])
            ):
                followups.append(comment)
    version = sdk_version(package_files)
    if version == "unknown":
        issues.append("SDK version unknown: no added version metadata in the package diff.")
    current = client.get(endpoint)
    changed = (
        any(current[key]["sha"] != pr[key]["sha"] for key in ("head", "base"))
        or current["updated_at"] != pr["updated_at"]
    )
    if current["state"] != "open" or current["draft"]:
        return None
    if changed:
        raise CollectionError(f"PR #{number} changed during collection; rerun before acting.")
    return {
        "pr": pr,
        "name": name,
        "version": version,
        "approval": approval,
        "owners": owners,
        "ownership_known": maintainers is not None and not skipped_team,
        "review_decision": summary.get("reviewDecision"),
        "bot_review": bot_review(comments),
        "followups": followups,
        "issues": issues,
        "queues": {},
    }


def classify(row, client, workflow_id, runs, activity_issues):
    pr = row["pr"]
    queues = row["queues"]
    active = [run for run in runs if run_pr(run, pr["number"])]
    if active:
        links = []
        for run in active:
            head = run_pr(run, pr["number"]).get("head", {}).get("sha")
            revision = "; older/different head" if head and head != pr["head"]["sha"] else ""
            links.append(f"[{run['status']}{revision}]({run['html_url']})")
        queues[2] = f"Review active: {', '.join(links)}. Wait; do not request a duplicate."
    elif activity_issues:
        row["issues"].append("Review activity unknown; inspect workflow runs before changing any review label.")
    else:
        try:
            freshness = review_freshness(client, workflow_id, pr, row["bot_review"])
        except CollectionError as error:
            row["issues"].append(str(error))
        else:
            if freshness in {"missing", "outdated"}:
                labeled = any(label["name"].casefold() == "mgmt-review-needed" for label in pr["labels"])
                action = "Remove and reapply" if labeled else "Add"
                queues[1] = (
                    f"Bot review {freshness}; no active review detected. "
                    f"{action} `mgmt-review-needed` after confirming activity at the run link."
                )
    approval = row["approval"]
    if row["ownership_known"] and approval is None:
        queues[3] = f"No effective maintainer approval. Ask {', '.join(row['owners'])} to review."
    elif row["review_decision"] in {"REVIEW_REQUIRED", "CHANGES_REQUESTED"}:
        queues[3] = f"GitHub review decision: {row['review_decision']}. Inspect outstanding review requirements."
    if approval:
        if not approval.get("commit_id"):
            row["issues"].append("Approved commit unknown; cannot verify changes after approval.")
        elif approval["commit_id"] != pr["head"]["sha"]:
            queues[4] = (
                f"Head changed since [@{approval['user']['login']}'s approval]({approval['html_url']}). "
                "Inspect the changes and current review requirements; re-approve only if required."
            )
        if row["followups"]:
            links = ", ".join(f"[comment]({comment['html_url']})" for comment in row["followups"])
            queues[5] = (
                f"Author follow-up after approval: {links}. Read and respond or route; do not duplicate approval."
            )


def render_report(repo, rows, issues):
    rows = sorted(rows, key=lambda row: timestamp(row["pr"]["updated_at"]), reverse=True)
    warnings = list(issues)
    for row in rows:
        warnings.extend(f"[{repo}#{row['pr']['number']}]({row['pr']['html_url']}): {issue}" for issue in row["issues"])
    runs_url = f"https://github.com/{repo}/actions/workflows/{WORKFLOW}"
    output = [
        f"Scanned {len(rows)} open, non-draft management AutoPRs" + ("; verification incomplete." if warnings else "."),
        "",
        f"[Management review runs]({runs_url}). Point-in-time report; confirm activity before changing labels.",
    ]
    for index, title in enumerate(SECTIONS, 1):
        entries = [row for row in rows if index in row["queues"]]
        if entries:
            output.extend(["", f"## {index}. {title}", ""])
            for row in entries:
                pr = row["pr"]
                output.append(
                    f"- [{repo}#{pr['number']}]({pr['html_url']}) - `{row['name']}` `{row['version']}`"
                    f" - {row['queues'][index]}"
                )
    if warnings:
        output.extend(["", "## Verification warnings", ""])
        output.extend(f"- {' '.join(issue.split())}" for issue in dict.fromkeys(warnings))
    elif not any(row["queues"] for row in rows):
        output.extend(["", "No PRs need action in these queues. Release readiness is not assessed."])
    return "\n".join(output), bool(warnings)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="Azure/azure-sdk-for-python")
    parser.add_argument("--package", help="Exact package name")
    parser.add_argument("--version", help="Exact SDK version (first releases included by default)")
    parser.add_argument("--limit", type=int, default=500, help="Maximum initial PR listing size")
    args = parser.parse_args(argv)
    if args.limit < 1:
        parser.error("--limit must be positive")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo):
        parser.error("--repo must be owner/name")
    if args.package and not re.fullmatch(r"azure-mgmt-[A-Za-z0-9-]+", args.package):
        parser.error("--package must be an azure-mgmt-* package name")
    client = GitHub(args.repo)
    issues = []
    try:
        prs = gh(
            "pr",
            "list",
            "--repo",
            args.repo,
            "--state",
            "open",
            "--search",
            '"[AutoPR azure-mgmt-" in:title draft:false sort:updated-desc',
            "--limit",
            str(args.limit),
            "--json",
            "number,title,isDraft,reviewDecision,updatedAt",
        )
        if len(prs) >= args.limit:
            issues.append(f"PR listing reached --limit {args.limit}; increase it for a complete scan.")
        selected = []
        for pr in prs:
            match = PACKAGE.match(pr["title"])
            if match and not pr["isDraft"] and (not args.package or match[1] == args.package):
                selected.append(pr)
        rows = []

        def collect(summary):
            try:
                return collect_pr(client, summary), None
            except CollectionError as error:
                return None, f"PR #{summary['number']}: collection incomplete: {error}"

        with ThreadPoolExecutor(max_workers=4) as pool:
            for row, error in pool.map(collect, selected):
                if error:
                    issues.append(error)
                elif row:
                    if not args.version or row["version"] == args.version:
                        rows.append(row)
                    elif row["version"] == "unknown":
                        issues.append(f"PR #{row['pr']['number']}: unknown version; cannot apply --version filter.")
        # Refresh activity after collecting PR evidence, close to report generation.
        runs, activity_issues = active_reviews(client) if rows else ([], [])
        issues.extend(activity_issues)
        try:
            workflow_id = client.cached(f"repos/{args.repo}/actions/workflows/{WORKFLOW}")["id"] if rows else None
        except CollectionError as error:
            workflow_id = None
            issues.append(f"Automated review workflow identity unknown: {error}")
        for row in rows:
            classify(row, client, workflow_id, runs, activity_issues)
        report, incomplete = render_report(args.repo, rows, issues)
        print(f"Observed at {datetime.now(timezone.utc).isoformat()}.")
        print(report)
        return 2 if incomplete else 0
    except CollectionError as error:
        print(f"Scan failed; no complete PR report is available: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
