#!/usr/bin/env python3
"""Build the generated SDK review report for a management-plane package.

The script only reads the JSON context it is given.
It does not edit the package, regenerate code, or call the network.
"""

import argparse
import ast
import json
import re
import sys

SCHEMA_VERSION = 1
PLACEHOLDER = "tool can't generate changelog for this release, please update manually."
SEVERITIES = {"high", "medium", "low"}
REPORT_KEYS = {"schemaVersion", "status", "skillRevision", "source", "reviews"}
SOURCE_KEYS = {"specPrNumber", "specHeadSha"}
REVIEW_KEYS = {"baselineCommitSha", "packages", "findings"}
FINDING_KEYS = {"severity", "file", "line", "title", "description"}
VERSION_RE = re.compile(r"\d+\.\d+\.\d+(?:b\d+)?")


class ReviewError(ValueError):
    """The review context is incomplete or outside the supported plane."""


def build_report(context):
    """Return the schema version 1 report for one reconstructed package."""
    package_name = _require_package(context)
    changed = list(context["changedFiles"])
    files = context["files"]
    findings = []
    findings.extend(_api_version_drift(changed, files))
    findings.extend(_preview_version(changed, files))
    findings.extend(_changelog_placeholder(changed, files))
    findings.extend(_client_name(changed, files, context.get("firstRelease")))
    findings.extend(_client_signature(changed, files))
    findings.sort(key=lambda item: (item["file"], item["line"], item["title"]))
    report = {
        "schemaVersion": SCHEMA_VERSION,
        "status": "completed",
        "skillRevision": context["skillRevision"],
        "source": {
            "specPrNumber": context["specPrNumber"],
            "specHeadSha": context["specHeadSha"],
        },
        "reviews": [
            {
                "baselineCommitSha": context["baselineCommitSha"],
                "packages": [package_name],
                "findings": findings,
            }
        ],
    }
    errors = validate_report(report, context)
    if errors:
        raise ReviewError("; ".join(errors))
    return report


def validate_report(report, context):
    """Return contract errors. An empty list means the report is acceptable."""
    errors = []
    if set(report) != REPORT_KEYS:
        errors.append("report keys do not match the version 1 contract")
        return errors
    if report["schemaVersion"] != SCHEMA_VERSION or report["status"] != "completed":
        errors.append("schemaVersion must be 1 and status must be completed")
    if not isinstance(report["skillRevision"], str) or not report["skillRevision"]:
        errors.append("skillRevision must be a non-empty string")
    source = report["source"]
    if set(source) != SOURCE_KEYS:
        errors.append("source keys do not match the version 1 contract")
    elif source["specPrNumber"] != context["specPrNumber"] or source["specHeadSha"] != context["specHeadSha"]:
        errors.append("source does not match the spec pull request in the context")
    reviews = report["reviews"]
    if not isinstance(reviews, list) or len(reviews) != 1:
        errors.append("the report must contain exactly one review")
        return errors
    review = reviews[0]
    if set(review) != REVIEW_KEYS:
        errors.append("review keys do not match the version 1 contract")
        return errors
    if review["baselineCommitSha"] != context["baselineCommitSha"]:
        errors.append("baselineCommitSha does not match the context")
    if review["packages"] != [context["packageName"]]:
        errors.append("packages do not match the context")
    changed = set(context["changedFiles"])
    titles = []
    for finding in review["findings"]:
        if set(finding) != FINDING_KEYS:
            errors.append("finding keys do not match the version 1 contract")
            continue
        titles.append(finding["title"])
        if finding["severity"] not in SEVERITIES:
            errors.append("severity must be high, medium, or low")
        if finding["file"] not in changed:
            errors.append("finding file is not a declared changed file: {0}".format(finding["file"]))
        if not isinstance(finding["line"], int) or finding["line"] < 1:
            errors.append("finding line must be a positive integer")
        if not finding["title"] or not finding["description"]:
            errors.append("finding title and description must be non-empty")
        if not isinstance(finding["title"], str) or not isinstance(finding["description"], str):
            errors.append("finding title and description must be strings")
    if len(titles) != len(set(titles)):
        errors.append("duplicate finding titles are not allowed")
    return errors


def _require_package(context):
    package_name = context.get("packageName")
    if not isinstance(package_name, str) or not package_name.startswith("azure-mgmt-"):
        raise ReviewError(
            "This skill reviews management-plane packages named azure-mgmt-*. Data-plane packages are not supported."
        )
    for key in ("specPrNumber", "specHeadSha", "skillRevision", "baselineCommitSha", "changedFiles", "files"):
        if key not in context:
            raise ReviewError("review context is missing {0}".format(key))
    if not isinstance(context["changedFiles"], list) or not isinstance(context["files"], dict):
        raise ReviewError("changedFiles and files have the wrong type")
    marker = "/{0}/".format(package_name)
    for path in context["changedFiles"]:
        if marker not in "/{0}".format(path):
            raise ReviewError("changed file is outside the package: {0}".format(path))
    return package_name


def _file_text(files, path, side):
    entry = files.get(path)
    if not isinstance(entry, dict):
        return None
    text = entry.get(side)
    return text if isinstance(text, str) else None


def _line_containing(text, needle):
    for number, line in enumerate(text.splitlines(), 1):
        if needle in line:
            return number
    return 1


def _finding(path, line, title, description):
    return {
        "severity": "high",
        "file": path,
        "line": line,
        "title": title,
        "description": description,
    }


def _api_versions(text):
    try:
        metadata = json.loads(text)
    except json.JSONDecodeError:
        return None
    versions = metadata.get("apiVersions") if isinstance(metadata, dict) else None
    if not isinstance(versions, dict) or not versions:
        return None
    if not all(isinstance(key, str) and isinstance(value, str) for key, value in versions.items()):
        return None
    return versions


def _api_version_drift(changed, files):
    findings = []
    for path in changed:
        if not path.endswith("/_metadata.json"):
            continue
        baseline = _api_versions(_file_text(files, path, "baseline") or "")
        head_text = _file_text(files, path, "head")
        head = _api_versions(head_text or "")
        if baseline is None or head is None or head_text is None:
            continue
        keys = sorted(set(baseline) | set(head))
        changed_keys = [key for key in keys if baseline.get(key) != head.get(key)]
        if not changed_keys:
            continue
        details = []
        for key in changed_keys:
            if key not in baseline:
                details.append("{0} was added with {1}".format(key, head[key]))
            elif key not in head:
                details.append("{0} was removed. The baseline value was {1}".format(key, baseline[key]))
            else:
                details.append("{0} changed from {1} to {2}".format(key, baseline[key], head[key]))
        findings.append(
            _finding(
                path,
                _line_containing(head_text, changed_keys[0]),
                "API versions changed",
                "The apiVersions map changed. " + ". ".join(details) + ".",
            )
        )
    return findings


def _version_value(files):
    for path, entry in files.items():
        if path.endswith("/_version.py"):
            text = entry.get("head") if isinstance(entry, dict) else None
            if not isinstance(text, str):
                return None
            match = VERSION_RE.search(text)
            return match.group(0) if match else None
    return None


def _preview_version(changed, files):
    version = _version_value(files)
    if version is None or "b" in version:
        return []
    findings = []
    for path in changed:
        if not path.endswith("/_metadata.json"):
            continue
        head_text = _file_text(files, path, "head")
        versions = _api_versions(head_text or "")
        if versions is None or head_text is None:
            continue
        previews = {key: value for key, value in versions.items() if "preview" in value.lower()}
        if not previews:
            continue
        rendered = json.dumps(previews, sort_keys=True)
        findings.append(
            _finding(
                path,
                _line_containing(head_text, next(iter(sorted(previews)))),
                "Preview API requires a beta package version",
                "apiVersions contains preview APIs {0} and VERSION is {1}, which has no beta marker.".format(
                    rendered, version
                ),
            )
        )
    return findings


def _latest_release_body(text):
    lines = text.splitlines()
    start = next((index for index, line in enumerate(lines) if line.startswith("## ")), None)
    if start is None:
        return ""
    end = next((index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")), len(lines))
    return "\n".join(lines[start:end])


def _changelog_placeholder(changed, files):
    findings = []
    for path in changed:
        if not path.endswith("/CHANGELOG.md"):
            continue
        text = _file_text(files, path, "head")
        if text is None or PLACEHOLDER not in _latest_release_body(text):
            continue
        findings.append(
            _finding(
                path,
                _line_containing(text, PLACEHOLDER),
                "Changelog placeholder would be published",
                "The latest release notes are the generator placeholder: {0}".format(PLACEHOLDER),
            )
        )
    return findings


def _public_classes(text):
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    return [node for node in tree.body if isinstance(node, ast.ClassDef) and not node.name.startswith("_")]


def _client_name(changed, files, first_release):
    if first_release is not True:
        return []
    findings = []
    for path in changed:
        if not path.endswith("/_client.py"):
            continue
        text = _file_text(files, path, "head")
        classes = _public_classes(text) if text is not None else None
        if not classes:
            continue
        invalid = [node for node in classes if not node.name.endswith("MgmtClient")]
        if not invalid:
            continue
        names = ", ".join(sorted(node.name for node in invalid))
        findings.append(
            _finding(
                path,
                invalid[0].lineno,
                "First-release client name must end with MgmtClient",
                "Confirmed first release: public client class {0} must end with MgmtClient.".format(names),
            )
        )
    return findings


def _init_parameters(text):
    classes = _public_classes(text)
    if not classes:
        return None
    for node in classes[0].body:
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            names = [arg.arg for arg in node.args.args if arg.arg != "self"]
            return names[:3], node.lineno
    return None


def _client_signature(changed, files):
    expected = ["credential", "subscription_id", "base_url"]
    findings = []
    for path in changed:
        if not path.endswith("/_client.py"):
            continue
        text = _file_text(files, path, "head")
        if text is None:
            continue
        parsed = _init_parameters(text)
        if parsed is None:
            continue
        names, line = parsed
        if names == expected:
            continue
        findings.append(
            _finding(
                path,
                line,
                "Client constructor parameter order",
                "Client __init__ parameters start with {0}. Management clients start with credential, subscription_id, base_url.".format(
                    ", ".join(names) or "no parameters"
                ),
            )
        )
    return findings


def main(argv):
    parser = argparse.ArgumentParser(description="Build a generated SDK review report from a JSON context file.")
    parser.add_argument("context_path")
    args = parser.parse_args(argv)
    with open(args.context_path, encoding="utf-8") as handle:
        context = json.load(handle)
    try:
        report = build_report(context)
    except ReviewError as error:
        print(str(error), file=sys.stderr)
        return 2
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
