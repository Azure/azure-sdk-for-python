"""Shared, non-executable evidence policy and deterministic management checks."""

import ast
import datetime
import hashlib
import json
import re
import tomllib
from urllib.parse import quote

CHECKS = (
    "Version consistency",
    "Preview version",
    "Changelog date",
    "Stability flags",
    "Client signature",
    "Client name consistency",
    "README snippets",
)
AUTOMATIC_CHECKS = CHECKS[:4]
SEMANTIC_CHECKS = CHECKS[4:]
MAX_REGISTERED_FILES = 20
MAX_REGISTERED_BYTES = 1024 * 1024
MAX_SNAPSHOT_BYTES = 8 * 1024 * 1024
RULES_SHA256 = "85f9803e18f608cf206bdefce2b8b1d3f2036c7139d35376879b43bccf671b83"


def allowed_sdk_file(relative, check=None):
    if relative.startswith(("generated_samples/", "generated_tests/")):
        return False
    if relative.startswith("azure/mgmt/"):
        return relative.endswith("/_client.py") or (
            relative.endswith("/_version.py") and check in set(AUTOMATIC_CHECKS) - {"Changelog date"}
        )
    return True


def source_id(repository, revision, path):
    return hashlib.sha256(f"{repository}\n{revision}\n{path}".encode()).hexdigest()


def entry_id(entry):
    return hashlib.sha256(json.dumps(entry, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:24]


def source_record(repository, evidence, package, role="sdk"):
    path, revision = evidence["path"], evidence["revision"]
    content = evidence.get("content", "")
    status = evidence["status"]
    if status == "unverified" and evidence.get("httpStatus"):
        status = "access_error"
    return {
        "id": source_id(repository, revision, path),
        "repository": repository,
        "revision": revision,
        "path": path,
        "package": package,
        "roles": [role],
        "allowedChecks": (
            [check for check in CHECKS if allowed_sdk_file(path[len(package) + 1 :], check)] if role == "sdk" else []
        ),
        "status": status,
        "error": evidence.get("error", ""),
        "content": content,
        "lineCount": len(content.splitlines()) if status == "available" else 0,
        "sha256": hashlib.sha256(content.encode()).hexdigest() if status == "available" else None,
    }


def citation(record, start=0, end=0, reason=""):
    url = f"https://github.com/{record['repository']}/blob/{record['revision']}/{quote(record['path'], safe='/')}"
    if start:
        url += f"#L{start}" + (f"-L{end}" if end != start else "")
    return {"url": url, "line_status": "verified" if start else "unavailable", "reason": reason}


def deterministic_checks(context, package):
    """Evaluate data literals only. Unsupported/missing syntax stays unverified."""
    records = [
        item
        for item in context["sources"]
        if item["package"] == package and item["revision"] == context["latestRevision"] and "sdk" in item["roles"]
    ]

    def file(suffix):
        matches = [item for item in records if item["path"].endswith(suffix)]
        if len(matches) != 1:
            raise ValueError(f"Expected one pinned {suffix}; found {len(matches)} (discovery may be incomplete).")
        result = matches[0]
        if result["status"] != "available" or not result["lineCount"]:
            raise ValueError(f"{result['path']}: {result['status']}: {result['error']}")
        return result

    def version():
        record = file("/_version.py")
        tree = ast.parse(record["content"])
        assignments = [
            node
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "VERSION" for t in node.targets)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ]
        if len(assignments) != 1 or not re.fullmatch(r"\d+\.\d+\.\d+(?:b\d+)?", assignments[0].value.value):
            raise ValueError("Expected one literal VERSION assignment in the pinned _version.py.")
        node = assignments[0]
        return node.value.value, citation(record, node.lineno, node.end_lineno)

    def release():
        record = file("/CHANGELOG.md")
        latest = re.search(r"^##\s+(.+)$", record["content"], re.M)
        heading = re.fullmatch(r"(\S+)\s+\(([^)]+)\)\s*", latest[1]) if latest else None
        if heading is None:
            raise ValueError("Latest changelog release heading or date is malformed.")
        line = record["content"][: latest.start()].count("\n") + 1
        return heading[1], heading[2], citation(record, line, line)

    checks, findings = [], []
    for name in AUTOMATIC_CHECKS:
        evidence = []
        observation = None
        try:
            rules = context.get("mgmtSdkCodeReviewRules", "")
            if hashlib.sha256(rules.strip().encode()).hexdigest() != RULES_SHA256:
                raise ValueError(
                    "Authoritative management review rules changed or are unavailable; update the deterministic policy before trusting this check."
                )
            if name == "Changelog date":
                _, date, ref = release()
                evidence.append(ref)
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
                    raise ValueError("Changelog release date must use YYYY-MM-DD.")
                days = (datetime.date.fromisoformat(date) - datetime.date.fromisoformat(context["reviewDate"])).days
                if days > 21:
                    observation = f"Latest changelog date {date} is {days} days in the future (more than 21)."
            else:
                value, ref = version()
                evidence.append(ref)
                beta = "b" in value
                if name == "Version consistency":
                    released, _, ref = release()
                    evidence.append(ref)
                    if value != released:
                        observation = f"VERSION {value} differs from the latest changelog version {released}."
                elif name == "Preview version":
                    record = file("/_metadata.json")
                    metadata = json.loads(record["content"])
                    api = metadata.get("apiVersion") if isinstance(metadata, dict) else None
                    if not isinstance(api, str) or not api:
                        raise ValueError("_metadata.json lacks a nonempty string apiVersion.")
                    # JSON/TOML parsers do not expose locations. Cite the parsed document,
                    # not a text match that could point at a comment or a nested key.
                    evidence.append(citation(record, 1, record["lineCount"]))
                    if "preview" in api.lower() and not beta:
                        observation = f"Preview API {api} requires a beta SDK version, not {value}."
                else:
                    record = file("/pyproject.toml")
                    project = tomllib.loads(record["content"])
                    flags = project.get("packaging", {})
                    metadata = project.get("project", {})
                    if not isinstance(flags, dict) or not isinstance(metadata, dict):
                        raise ValueError("pyproject.toml project and packaging must be tables.")
                    classifiers = metadata.get("classifiers")
                    expected = (
                        "Development Status :: 4 - Beta" if beta else "Development Status :: 5 - Production/Stable"
                    )
                    evidence.append(citation(record, 1, record["lineCount"]))
                    if (
                        flags.get("is_stable") is not (not beta)
                        or not isinstance(classifiers, list)
                        or expected not in classifiers
                    ):
                        observation = f"Version {value} requires is_stable = {str(not beta).lower()} and {expected}."
            evidence = list({item["url"]: item for item in evidence}.values())
            checks.append({"name": name, "outcome": "completed", "reason": "", "sources": evidence})
            if observation:
                findings.append(
                    {
                        "severity": "Warning" if name == "Changelog date" else "Blocking",
                        "check": name,
                        "title": name,
                        "observation": observation,
                        "remediation": (
                            "Verify and update the release date."
                            if name == "Changelog date"
                            else "Align the package metadata with the management SDK review rule."
                        ),
                        "sources": evidence,
                    }
                )
        except (ValueError, SyntaxError, TypeError) as error:
            checks.append({"name": name, "outcome": "unverified", "reason": str(error), "sources": evidence})
    return checks, findings
