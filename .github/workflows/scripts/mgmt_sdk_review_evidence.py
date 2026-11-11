"""Shared, non-executable evidence policy and deterministic management checks."""

import ast
import datetime
import hashlib
import json
import re
import tomllib
from urllib.parse import quote

AUTOMATIC_CHECKS = (
    "Version consistency",
    "Preview version",
    "Changelog date",
    "Stability flags",
    "Initial client name",
)
SEMANTIC_CHECKS = (
    "Client signature",
    "Client name consistency",
    "README snippets",
)
CHECKS = AUTOMATIC_CHECKS + SEMANTIC_CHECKS
MAX_REGISTERED_FILES = 20
MAX_REGISTERED_BYTES = 1024 * 1024
MAX_SNAPSHOT_BYTES = 8 * 1024 * 1024
RULES_SHA256 = "7fc8c130317dc8b856d247cdd7f880a23ad784b5a2e75612b50c59c42b577b88"


def allowed_sdk_file(relative, check=None):
    if relative.startswith(("generated_samples/", "generated_tests/")):
        return False
    if relative.startswith("azure/mgmt/"):
        return relative.endswith("/_client.py") or (
            relative.endswith("/_version.py") and check in {"Version consistency", "Preview version", "Stability flags"}
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


def normalize_api_versions(value):
    if not isinstance(value, dict) or not value:
        raise ValueError("apiVersions must be a nonempty object mapping service names to API-version strings.")
    for service, version in value.items():
        if not isinstance(service, str) or not service.strip() or service != service.strip():
            raise ValueError("apiVersions service names must be nonempty strings without surrounding whitespace.")
        if not isinstance(version, str) or not version.strip() or version != version.strip():
            raise ValueError(
                f"apiVersions[{service!r}] must be a nonempty API-version string without surrounding whitespace."
            )
    return dict(sorted(value.items()))


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
            elif name == "Initial client name":
                breaking = next(item for item in context["breakingChangeContext"] if item["packagePath"] == package)
                baseline = breaking["releaseBaseline"]
                if baseline["status"] == "available":
                    _, _, ref = release()
                    checks.append(
                        {
                            "name": name,
                            "outcome": "not_applicable",
                            "reason": "The trusted release baseline confirms a previously released package.",
                            "sources": [ref],
                        }
                    )
                    continue
                if baseline["status"] != "not_applicable":
                    raise ValueError("First-release status is unverified; do not infer it from a missing baseline.")
                clients = [item for item in records if item["path"].endswith("/_client.py")]
                synchronous = [item for item in clients if not item["path"].endswith("/aio/_client.py")]
                if len(synchronous) != 1:
                    raise ValueError("Expected one pinned synchronous _client.py to verify the initial client name.")
                invalid = []
                for record in clients:
                    if record["path"].endswith("/aio/_client.py") and record["status"] == "missing":
                        continue
                    if record["status"] != "available" or not record["lineCount"]:
                        raise ValueError(f"{record['path']}: {record['status']}: {record['error']}")
                    classes = [
                        node
                        for node in ast.parse(record["content"]).body
                        if isinstance(node, ast.ClassDef) and not node.name.startswith("_")
                    ]
                    if len(classes) != 1:
                        raise ValueError(f"{record['path']}: expected one public client class declaration.")
                    client = classes[0]
                    evidence.append(citation(record, client.lineno, client.lineno))
                    if not client.name.endswith("MgmtClient"):
                        invalid.append(client.name)
                if invalid:
                    names = ", ".join(sorted(set(invalid)))
                    observation = (
                        f"Confirmed first release: client names {names} must end with the exact suffix MgmtClient."
                    )
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
                    apis = normalize_api_versions(metadata.get("apiVersions") if isinstance(metadata, dict) else None)
                    # JSON/TOML parsers do not expose locations. Cite the parsed document,
                    # not a text match that could point at a comment or a nested key.
                    evidence.append(citation(record, 1, record["lineCount"]))
                    previews = {service: api for service, api in apis.items() if "preview" in api.lower()}
                    if previews and not beta:
                        observation = f"Preview APIs {json.dumps(previews, sort_keys=True)} require a beta SDK version, not {value}."
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
                            else (
                                "Add or update the client-name customization in client.tsp to choose a descriptive name "
                                "ending in MgmtClient, then regenerate the SDK."
                                if name == "Initial client name"
                                else "Align the package metadata with the management SDK review rule."
                            )
                        ),
                        "sources": evidence,
                    }
                )
        except (ValueError, SyntaxError, TypeError) as error:
            checks.append({"name": name, "outcome": "unverified", "reason": str(error), "sources": evidence})
    return checks, findings
