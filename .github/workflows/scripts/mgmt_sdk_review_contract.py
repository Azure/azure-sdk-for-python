#!/usr/bin/env python3
"""Validate structured management reviews against a pre-agent snapshot, then render.

The schema uses the JSON Schema subset supported by gh-aw v0.88.8 safe-outputs.data.
It is also validated here, independently of the agent-side tool/collector.
"""

import argparse
import html
import json
import os
from pathlib import Path
import re
import unicodedata
from urllib.parse import quote, unquote, urlsplit

MARKER = "<!-- gh-aw-workflow-id: mgmt-sdk-pr-review -->"
SUBMISSION = "Structured management SDK review."
CHECKS = (
    "Version consistency",
    "Preview version",
    "Changelog date",
    "Stability flags",
    "Client signature",
    "Client name consistency",
    "README snippets",
)
SEVERITIES = ("Blocking", "Warning", "Suggestion")
MAX_BYTES = 2 * 1024 * 1024


def obj(properties):
    return {
        "type": "object",
        "properties": properties,
        "required": sorted(properties),
        "additionalProperties": False,
    }


def array(items):
    return {"type": "array", "items": items}


def enum(*values):
    return {"type": "string", "enum": list(values)}


TEXT = {"type": "string", "maxLength": 12000}
SOURCE = obj(
    {
        "url": {"type": "string", "minLength": 1, "maxLength": 2048},
        "line_status": enum("verified", "unavailable"),
        "reason": TEXT,
    }
)
SCHEMA = obj(
    {
        "schema_version": enum("1"),
        "outcome": enum("reviewed", "not_applicable"),
        "packages": array(
            obj(
                {
                    "package": {"type": "string", "pattern": r"^sdk/[^/]+/azure-mgmt-[a-z0-9-]+$"},
                    "checks": array(
                        obj(
                            {
                                "name": enum(*CHECKS),
                                "outcome": enum("completed", "unverified", "not_applicable"),
                                "reason": TEXT,
                                "sources": array(SOURCE),
                            }
                        )
                    ),
                    "findings": array(
                        obj(
                            {
                                "severity": enum(*SEVERITIES),
                                "check": enum(*CHECKS),
                                "title": TEXT,
                                "observation": TEXT,
                                "remediation": TEXT,
                                "sources": array(SOURCE),
                            }
                        )
                    ),
                    "attribution": obj(
                        {
                            "outcome": enum("no_entries", "entries", "incomplete"),
                            "initial_release": {"type": "boolean"},
                            "reason": TEXT,
                            "entries": array(
                                obj(
                                    {
                                        "entry_index": {"type": "integer", "minimum": 0},
                                        "release": TEXT,
                                        "cause": enum("typespec_api", "human_review"),
                                        "confidence": enum("high", "not_applicable"),
                                        "explanation": TEXT,
                                        "sources": array(SOURCE),
                                    }
                                )
                            ),
                        }
                    ),
                }
            )
        ),
    }
)


def require(condition, path, message):
    if not condition:
        raise ValueError(f"{path}: {message}")


def validate_characters(value, path):
    require(
        not any(unicodedata.category(char) in {"Cc", "Cf"} and char not in "\n\r\t" for char in value),
        path,
        "control/format characters are not allowed",
    )


def validate_schema(value, schema=SCHEMA, path="data"):
    kind = schema["type"]
    valid = {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": type(value) is int,
        "boolean": type(value) is bool,
    }[kind]
    require(valid, path, f"expected {kind}")
    if "enum" in schema:
        require(value in schema["enum"], path, f"expected one of {schema['enum']}")
    if kind == "object":
        require(
            set(value) == set(schema["properties"]),
            path,
            f"expected fields {sorted(schema['properties'])}; got {sorted(value)}",
        )
        for key, child in schema["properties"].items():
            validate_schema(value[key], child, f"{path}.{key}")
    elif kind == "array":
        require(len(value) <= 1000, path, "too many records (maximum 1000)")
        for index, item in enumerate(value):
            validate_schema(item, schema["items"], f"{path}[{index}]")
    elif kind == "string":
        require(len(value) <= schema.get("maxLength", 12000), path, "text exceeds size limit")
        require(len(value) >= schema.get("minLength", 0), path, "text is required")
        if "pattern" in schema:
            require(re.fullmatch(schema["pattern"], value), path, "invalid identity")
        validate_characters(value, path)
    elif kind == "integer":
        require(value >= schema.get("minimum", value), path, "value below minimum")


def normalized_text(value, path):
    # Share the bounded fixed point: gh-aw decodes entities and normalizes Unicode.
    validate_characters(value, path)
    for _ in range(10):
        decoded = html.unescape(unicodedata.normalize("NFKC", value))
        validate_characters(decoded, path)
        if decoded == value:
            return value
        value = decoded
    require(html.unescape(unicodedata.normalize("NFKC", value)) == value, path, "excessively nested HTML entities")
    return value


def substantive(text, path):
    # This is placeholder detection on prose, not parsing the publication layout.
    visible = normalized_text(text, path)
    visible = re.sub(r"!?\[([^\]\n]*)\]\([^\n]*?\)", r"\1", visible)
    # cspell:ignore hgroup noscript samp
    visible = re.sub(
        r"</?(?:a|abbr|acronym|address|area|article|aside|audio|b|base|bdi|bdo|big|blockquote|body|br|button|"
        r"canvas|caption|center|cite|code|col|colgroup|data|datalist|dd|del|details|dfn|dialog|dir|div|dl|dt|em|"
        r"embed|fieldset|figcaption|figure|font|footer|form|frame|frameset|h[1-6]|head|header|hgroup|hr|html|i|"
        r"iframe|img|input|ins|kbd|label|legend|li|link|main|map|mark|marquee|math|menu|meta|meter|nav|noscript|"
        r"object|ol|optgroup|option|output|p|param|picture|pre|progress|q|rp|rt|ruby|s|samp|script|section|select|"
        r"slot|small|source|span|strike|strong|style|sub|summary|sup|svg|table|tbody|td|template|textarea|tfoot|"
        r"th|thead|time|title|tr|track|tt|u|ul|var|video|wbr)\b(?:[^>'\"]|\"[^\"]*\"|'[^']*')*>",
        "",
        visible,
        flags=re.I,
    )
    visible = re.sub(r"[*_`~]", "", visible).lower()
    visible = " ".join(visible.split())
    visible = visible.strip("".join(char for char in set(visible) if unicodedata.category(char).startswith("P")) + " ")
    require(
        bool(re.search(r"[a-z0-9]", visible))
        and visible
        not in {
            "todo",
            "tbd",
            "n/a",
            "none",
            "done",
            "reason",
            "explanation",
            "evidence",
            "finding",
            "remediation",
            "unable to complete review",
            "unable to complete review because",
        }
        and not re.match(r"(?:(?:the |a )?(?:full )?review (?:is )?pending|pending review)\b", visible),
        path,
        "expected substantive analysis or a concrete missing-evidence reason, not a placeholder",
    )


def reason(text, path):
    substantive(text, path)
    require(len(normalized_text(text, path).split()) >= 2, path, "provide a specific missing-evidence reason")


def unique_index(records, key, path):
    result = {}
    for index, record in enumerate(records):
        identity = record[key]
        require(identity not in result, f"{path}[{index}].{key}", f"duplicate {identity!r}")
        result[identity] = record
    return result


def source_identity(source, path):
    url = source["url"]
    match = re.fullmatch(
        r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/blob/([0-9a-f]{40})/"
        r"([^?#\s<>\"\\]+)(?:#L([1-9][0-9]*)(?:-L([1-9][0-9]*))?)?",
        url,
    )
    require(match, path + ".url", "expected an immutable GitHub blob URL with a full commit SHA")
    repository, revision, filename, start, end = match.groups()
    decoded = unquote(filename)
    normalized_text(decoded, path + ".url")
    require(
        not any(part in {"", ".", ".."} for part in decoded.split("/")) and not re.search(r"[\x00-\x20\\]", decoded),
        path + ".url",
        "invalid source path",
    )
    require(not end or int(end) >= int(start), path + ".url", "line range ends before it starts")
    if source["line_status"] == "verified":
        require(start and not source["reason"], path, "verified lines require an anchor and an empty reason")
    else:
        require(not start, path, "unavailable lines must not invent an anchor")
        reason(source["reason"], path + ".reason")
    return repository, revision, decoded


def validate_sources(sources, path, context, breaking, package, required=False, specification=False, check=None):
    require(not required or sources, path, "at least one immutable source reference is required")
    seen = set()
    allowed = {
        (context["repository"], context[key]) for key in ("firstRevision", "latestRevision", "mergeBaseRevision")
    }
    baseline = breaking["releaseBaseline"]
    if baseline["status"] == "available":
        allowed.add((context["repository"], baseline["revision"]))
    specs = {
        (item["repository"], item["revision"])
        for item in breaking["specificationSources"].values()
        if item["status"] == "available"
    }
    for index, source in enumerate(sources):
        field = f"{path}[{index}]"
        repo, revision, filename = source_identity(source, field)
        require(source["url"] not in seen, field, "duplicate source reference")
        seen.add(source["url"])
        require(
            (repo, revision) in (specs if specification else allowed | specs),
            field,
            "source repository/revision is not in the trusted SDK or specification context",
        )
        if repo == context["repository"]:
            require(filename.startswith(package + "/"), field, "source belongs to another package")
            relative = filename[len(package) + 1 :]
            version_metadata = relative.endswith("/_version.py") and check in {"Version consistency", "Preview version"}
            require(
                not relative.startswith(("generated_samples/", "generated_tests/"))
                and not (
                    relative.startswith("azure/mgmt/") and not relative.endswith("/_client.py") and not version_metadata
                ),
                field,
                "source is excluded by management SDK review rules",
            )
        if specification:
            require(
                source["line_status"] == "verified", field, "TypeSpec/API attribution requires verified source lines"
            )


def validate_context(context, repository, pr_number, head, tooling_revision):
    require(isinstance(context, dict), "context", "expected trusted collector snapshot")
    for key, expected in (
        ("repository", repository),
        ("pullRequestNumber", pr_number),
        ("latestRevision", head),
        ("toolingRevision", tooling_revision),
    ):
        require(context.get(key) == expected, f"context.{key}", "does not match the executing workflow event")
    for key in ("firstRevision", "latestRevision", "mergeBaseRevision", "toolingRevision"):
        require(re.fullmatch(r"[0-9a-f]{40}", context.get(key, "")), f"context.{key}", "expected immutable SHA")
    for key in ("packageDiscovery", "commitDiscovery"):
        require(context.get(key, {}).get("status") in {"complete", "unverified"}, f"context.{key}", "invalid status")
    packages = context["affectedPackages"]
    require(
        isinstance(packages, list) and len(packages) == len(set(packages)),
        "context.affectedPackages",
        "invalid/duplicate package identities",
    )
    for key in ("breakingChangeContext", "apiVersionDrift"):
        records = unique_index(context[key], "packagePath", "context." + key)
        require(set(records) == set(packages), "context." + key, "package coverage differs from discovery")


def validate_review(data, context):
    validate_schema(data)
    packages = unique_index(data["packages"], "package", "data.packages")
    require(
        set(packages) == set(context["affectedPackages"]),
        "data.packages",
        "must cover exactly the trusted affectedPackages",
    )
    if data["outcome"] == "not_applicable":
        require(
            not packages and context["packageDiscovery"]["status"] == "complete",
            "data.outcome",
            "not_applicable requires complete trusted discovery with no management packages",
        )
        return
    require(packages, "data.packages", "no package checks completed; report_incomplete instead")
    breaking_by_package = unique_index(context["breakingChangeContext"], "packagePath", "context.breakingChangeContext")
    completed = 0
    for package, review in packages.items():
        path = f"data.packages[{package}]"
        breaking = breaking_by_package[package]
        checks = unique_index(review["checks"], "name", path + ".checks")
        require(
            set(checks) == set(CHECKS),
            path + ".checks",
            "account for every rule with completed, unverified, or justified not_applicable",
        )
        for name, check in checks.items():
            field = path + f".checks[{name}]"
            if check["outcome"] == "completed":
                require(not check["reason"], field + ".reason", "completed check must not carry an incomplete reason")
                completed += 1
            else:
                reason(check["reason"], field + ".reason")
            validate_sources(
                check["sources"],
                field + ".sources",
                context,
                breaking,
                package,
                required=check["outcome"] != "unverified",
                check=name,
            )
        for index, finding in enumerate(review["findings"]):
            field = path + f".findings[{index}]"
            require(
                checks[finding["check"]]["outcome"] == "completed",
                field + ".check",
                "a finding requires the corresponding check to be completed",
            )
            for name in ("title", "observation", "remediation"):
                substantive(finding[name], field + "." + name)
            validate_sources(
                finding["sources"],
                field + ".sources",
                context,
                breaking,
                package,
                required=True,
                check=finding["check"],
            )
        attribution = review["attribution"]
        field = path + ".attribution"
        initial = breaking["releaseBaseline"]["status"] == "not_applicable"
        require(
            attribution["initial_release"] == initial,
            field + ".initial_release",
            "must match corroborated collector initial-release evidence",
        )
        entries = attribution["entries"]
        indexes = unique_index(entries, "entry_index", field + ".entries")
        trusted_entries = breaking["introducedEntries"]
        require(
            set(indexes) == set(range(len(trusted_entries))),
            field + ".entries",
            "must account for every trusted introduced entry exactly once",
        )
        incomplete = (
            breaking["status"] != "complete"
            or bool(breaking["collectionIssues"])
            or bool(breaking["emptyBreakingChangeSections"])
            or context["commitDiscovery"]["status"] != "complete"
            or context["packageDiscovery"]["status"] != "complete"
        )
        expected = "incomplete" if incomplete else ("entries" if trusted_entries else "no_entries")
        require(
            attribution["outcome"] == expected,
            field + ".outcome",
            f"trusted collection requires {expected!r}, not {attribution['outcome']!r}",
        )
        if incomplete:
            reason(attribution["reason"], field + ".reason")
        else:
            require(not attribution["reason"], field + ".reason", "complete attribution must have an empty reason")
        for index, entry in indexes.items():
            row = field + f".entries[{index}]"
            trusted_release = trusted_entries[index]["release"]
            require(
                entry["release"] == ("" if trusted_release is None else trusted_release),
                row + ".release",
                "must match the trusted changelog release heading, or be empty when that heading is missing",
            )
            reason(entry["explanation"], row + ".explanation")
            direct = entry["cause"] == "typespec_api"
            require(
                entry["confidence"] == ("high" if direct else "not_applicable"),
                row + ".confidence",
                "TypeSpec/API requires high; human review requires not_applicable",
            )
            if direct:
                require(
                    breaking["releaseBaseline"]["status"] == "available",
                    row + ".cause",
                    "TypeSpec/API attribution requires an available release baseline",
                )
            validate_sources(
                entry["sources"], row + ".sources", context, breaking, package, required=direct, specification=direct
            )
    require(completed, "data.packages[].checks", "diagnostic-only review: no rule checks completed")


def text(value):
    """Use code spans so gh-aw's sanitizer preserves literal markup and decorators."""
    value = normalized_text(value, "rendered.text")
    lines = value.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    result = []
    for line in lines:
        if not line:
            result.append("")
            continue
        parts = []
        for part in line.split("|"):
            delimiter = "`" * (max((len(run) for run in re.findall(r"`+", part)), default=0) + 1)
            parts.append(delimiter + " " + part + " " + delimiter if part else "")
        result.append(r"\|".join(parts))
    return "<br>".join(result)


def link(url, label):
    # URI-encode syntax that gh-aw would otherwise treat as mentions, HTML or
    # look-alike characters. Preserve the destination, including its SHA and line anchors.
    destination = quote(url, safe="/:%#._-~")
    return f"[{text(label)}]({destination})"


def sources(values):
    result = []
    for source in values:
        label = unquote(urlsplit(source["url"]).path.rsplit("/", 1)[-1])
        rendered = link(source["url"], label)
        if source["line_status"] == "unavailable":
            rendered += " (lines unverified: " + text(source["reason"]) + ")"
        result.append(rendered)
    return "<br>".join(result)


def table(headers, rows):
    return "\n".join(
        ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
        + ["| " + " | ".join(row) + " |" for row in rows]
    )


def file_url(context, path, revision, start=None, end=None):
    url = f"https://github.com/{context['repository']}/blob/{revision}/{quote(path, safe='/@')}"
    if start:
        url += f"#L{start}"
        if end and end != start:
            url += f"-L{end}"
    return url


def render(data, context):
    validate_review(data, context)
    if data["outcome"] == "not_applicable":
        return (
            MARKER
            + "\n\n## Management SDK review not applicable\n\n"
            + ("This pull request does not change a package matching `sdk/*/azure-mgmt-*`.\n")
        )
    findings, unverified, summary, attribution_sections = [], [], [], []
    if context["packageDiscovery"]["status"] == "unverified":
        unverified.append(["All packages", "Management package discovery", text(context["packageDiscovery"]["error"])])
    drift_by_package = {item["packagePath"]: item for item in context["apiVersionDrift"]}
    breaking_by_package = {item["packagePath"]: item for item in context["breakingChangeContext"]}
    for package in sorted(data["packages"], key=lambda item: item["package"]):
        name = package["package"]
        completed = []
        for check in sorted(package["checks"], key=lambda item: CHECKS.index(item["name"])):
            if check["outcome"] == "unverified":
                unverified.append(
                    [
                        text(name),
                        text(check["name"]),
                        text(check["reason"]) + ("<br>" + sources(check["sources"]) if check["sources"] else ""),
                    ]
                )
            else:
                label = text(check["name"])
                if check["outcome"] == "not_applicable":
                    label += " (not applicable: " + text(check["reason"]) + ")"
                label += " " + sources(check["sources"])
                completed.append(label)
        for finding in package["findings"]:
            findings.append(
                [
                    finding["severity"],
                    text(finding["title"]),
                    text(name) + "<br>" + sources(finding["sources"]),
                    text(finding["observation"]),
                    text(finding["check"]),
                    text(finding["remediation"]),
                ]
            )
        drift = drift_by_package[name]
        if context["commitDiscovery"]["status"] != "complete" or drift["status"] == "unverified":
            error = (
                context["commitDiscovery"]["error"]
                if context["commitDiscovery"]["status"] != "complete"
                else drift["error"]
            )
            unverified.append([text(name), "API-version drift", text(error)])
        else:
            completed.append("API-version drift")
            if drift["status"] == "changed":
                evidence = "<br>".join(
                    link(file_url(context, drift["metadataPath"], drift[which + "Revision"]), drift[which + "Revision"])
                    + ": "
                    + text(drift[which + "ApiVersion"])
                    for which in ("first", "latest")
                )
                findings.append(
                    [
                        "Blocking",
                        "API version changed",
                        text(name),
                        evidence + "<br>Line anchors unavailable in collector summary.",
                        "API-version drift",
                        "Restore the original API version or explain the change and obtain approval.",
                    ]
                )
        if context["packageDiscovery"]["status"] == "complete":
            completed.insert(0, "Management package discovery")
        summary.append([text(name), "; ".join(completed) or "No completed checks for this package"])
        breaking = breaking_by_package[name]
        analysis = package["attribution"]
        groups = {}
        for entry in sorted(analysis["entries"], key=lambda item: item["entry_index"]):
            trusted = breaking["introducedEntries"][entry["entry_index"]]
            url = file_url(
                context, breaking["changelogPath"], context["latestRevision"], trusted["startLine"], trusted["endLine"]
            )
            explanation = text(entry["explanation"])
            if entry["cause"] == "human_review":
                explanation = "**Needs human review:** " + explanation
            if entry["sources"]:
                explanation += "<br>" + sources(entry["sources"])
            release = trusted["release"] if trusted["release"] is not None else "Unverified release (missing heading)"
            groups.setdefault(release, []).append(
                [
                    link(url, trusted["text"]) + "<br>Change: " + text(trusted["changeKind"]),
                    "TypeSpec/API" if entry["cause"] == "typespec_api" else "Human review",
                    explanation,
                    "High" if entry["confidence"] == "high" else "N/A",
                ]
            )
        if any(entry["release"] is None for entry in breaking["introducedEntries"]):
            unverified.append(
                [
                    text(name),
                    "Breaking-change release identity",
                    "Introduced entries appear before a release heading. Correct the changelog release structure.",
                ]
            )
        for release, rows in groups.items():
            attribution_sections.append(
                f"**Package: {text(name)} | Release: {text(release)}**\n\n"
                + table(["Changelog entry", "Cause", "Evidence and explanation", "Confidence"], rows)
            )
        if analysis["outcome"] == "no_entries":
            explanation = "**Breaking-change attribution:** No newly added or modified entries."
            if analysis["initial_release"]:
                explanation += "\n\n" + text(breaking["releaseBaseline"]["reason"])
            release = (
                breaking.get("releases", [{}])[0].get("heading", "unverified")
                if breaking.get("releases")
                else "unverified"
            )
            attribution_sections.append(f"**Package: {text(name)} | Release: {text(release)}**\n\n" + explanation)
        elif analysis["outcome"] == "incomplete":
            issues = list(breaking["collectionIssues"])
            for section in breaking["emptyBreakingChangeSections"]:
                issues.append("Empty Breaking Changes section: " + str(section["release"]))
            for key in ("commitDiscovery", "packageDiscovery"):
                if context[key]["status"] == "unverified":
                    issues.append(context[key]["error"])
            attribution_sections.append(
                f"**Package: {text(name)} | Release: unverified collection**\n\n"
                + "**Needs human review:** "
                + text(analysis["reason"])
                + "<br>"
                + "<br>".join(text(issue) for issue in issues)
            )
    findings.sort(key=lambda row: (SEVERITIES.index(row[0]), row[2], row[1]))
    body = (
        "\n\n".join(
            [
                MARKER,
                "## Management SDK PR review",
                (
                    table(["Severity", "Finding", "Location", "Evidence", "Rule", "Remediation"], findings)
                    if findings
                    else "**Findings:** None."
                ),
                "### Unverified checks",
                table(["Package", "Check", "Reason"], unverified) if unverified else "**Unverified checks:** None.",
                "### Breaking-change attribution",
                "\n\n".join(attribution_sections),
                "### Review summary",
                table(["Package", "Completed checks"], summary),
            ]
        )
        + "\n"
    )
    require(len(body.encode("utf-8")) <= 60000, "rendered.body", "review exceeds publication size limit")
    require(
        len(re.findall(r"https?://[^\s]+", body)) <= 48,
        "rendered.body",
        "review exceeds the 48-link budget (two reserved for gh-aw metadata); reduce redundant references",
    )
    return body


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "JSON", f"duplicate object key {key!r}")
        result[key] = value
    return result


def load_json(path):
    raw = Path(path).read_bytes()
    require(len(raw) <= MAX_BYTES, str(path), "JSON exceeds size limit")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=strict_object)


def prepare_output(payload, context):
    require(isinstance(payload, dict), "output", "expected an agent output object")
    require(
        payload.get("errors") == [] and isinstance(payload.get("errors"), list),
        "output.errors",
        "expected empty collector errors; inspect the agent artifact",
    )
    items = payload.get("items")
    require(
        isinstance(items, list) and len(items) == 1,
        "output.items",
        "expected exactly one review; duplicate, missing, or mixed outputs cannot be published",
    )
    item = items[0]
    require(
        isinstance(item, dict) and item.get("type") == "add_comment",
        "output.items[0].type",
        "expected add_comment; report_incomplete reason/details remain in the agent artifact",
    )
    require(
        set(item) <= {"type", "body", "data", "temporary_id"},
        "output.items[0]",
        "unexpected target or publication fields",
    )
    # v0.88.8 appends a pretty-printed data block during ingestion. It is not review Markdown.
    data = item.get("data")
    expected = SUBMISSION + "\n\nStructured data:\n```json\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n```"
    require(
        item.get("body") == expected,
        "output.items[0].body",
        "expected only the fixed submission label and gh-aw structured data block, not mixed prose",
    )
    body = render(data, context)
    return {"items": [{"type": "add_comment", "body": body}], "errors": []}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("schema", "publish"))
    args = parser.parse_args()
    if args.command == "schema":
        print(json.dumps(SCHEMA, separators=(",", ":")))
        return
    try:
        context = load_json(os.environ["REVIEW_CONTEXT"])
        validate_context(
            context,
            os.environ["GH_REPOSITORY"],
            int(os.environ["PR_NUMBER"]),
            os.environ["REVIEW_HEAD_SHA"],
            os.environ["REVIEW_TOOLING_SHA"],
        )
        output = Path(os.environ["GH_AW_AGENT_OUTPUT"])
        prepared = prepare_output(load_json(output), context)
        # Leave the original artifact untouched on any validation/rendering failure.
        temporary = output.with_suffix(".validated.json")
        temporary.write_text(json.dumps(prepared, ensure_ascii=False), encoding="utf-8")
        temporary.replace(output)
    except (OSError, ValueError, KeyError, TypeError) as error:
        message = str(error).replace("\r", " ").replace("\n", " ")
        raise SystemExit(
            f"Management SDK review rejected: {message}. No review will be published or hidden. "
            "Inspect the retained agent artifact and trusted snapshot before rerunning."
        ) from error


if __name__ == "__main__":
    main()
