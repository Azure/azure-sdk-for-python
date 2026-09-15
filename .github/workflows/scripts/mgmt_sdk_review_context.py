#!/usr/bin/env python3
"""Collect immutable, non-executable evidence for the management SDK PR reviewer."""

import base64
import binascii
import difflib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request


API_ROOT = os.environ.get("GH_API_ROOT", "https://api.github.com")
MAX_API_RESPONSE_BYTES = 12 * 1024 * 1024
MAX_TEXT_FILE_BYTES = 256 * 1024
MAX_PAGES = 30
MAX_API_REQUESTS = 500
API_TIMEOUT_SECONDS = 30
PACKAGE_PATTERN = re.compile(r"^(sdk/[^/]+/azure-mgmt-[^/]+)(?:/|$)")
REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
RELEASE_HEADING = re.compile(r"^##\s+(.+?)\s*$")
SECTION_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
BULLET = re.compile(r"^\s*[-*]\s+(.*)$")
VERSION_LIKE_KEY = re.compile(
    r"typespec|emitter|compiler|generator|client-generator|http-client-python|autorest",
    re.IGNORECASE,
)
PROVENANCE_PATHS = (
    "_metadata.json",
    "tsp-location.yaml",
    "api.metadata.yml",
    "pyproject.toml",
    "TempTypeSpecFiles/package-lock.json",
)
MAX_PACKAGE_API_REQUESTS = 4 * len(PROVENANCE_PATHS) + 2 + 2


class GitHubApiError(RuntimeError):
    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


class GitHubClient:
    def __init__(self, repository, token, api_root=API_ROOT):
        if not REPOSITORY_PATTERN.fullmatch(repository):
            raise ValueError(f"Invalid GitHub repository reference: {repository!r}")
        self.repository = repository
        self.token = token
        self.api_root = api_root.rstrip("/")
        self.request_count = 0

    def get(self, path):
        if not path.startswith("/"):
            raise ValueError("GitHub API paths must be absolute")
        if self.request_count >= MAX_API_REQUESTS:
            raise GitHubApiError(f"GitHub API request limit ({MAX_API_REQUESTS}) was reached")
        self.request_count += 1
        request = urllib.request.Request(
            f"{self.api_root}{path}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "User-Agent": "azure-sdk-python-mgmt-review",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=API_TIMEOUT_SECONDS) as response:
                content_length = response.headers.get("Content-Length")
                if content_length and int(content_length) > MAX_API_RESPONSE_BYTES:
                    raise GitHubApiError(f"GitHub API response exceeded the size limit for {path}")
                payload = response.read(MAX_API_RESPONSE_BYTES + 1)
                if len(payload) > MAX_API_RESPONSE_BYTES:
                    raise GitHubApiError(f"GitHub API response exceeded the size limit for {path}")
                return json.loads(payload.decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read(4096).decode("utf-8", errors="replace")
            raise GitHubApiError(
                f"GitHub API request failed ({error.code}) for {path}: {detail}", status=error.code
            ) from error
        except urllib.error.URLError as error:
            raise GitHubApiError(f"GitHub API request failed for {path}: {error.reason}") from error
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            raise GitHubApiError(f"GitHub API returned invalid or oversized data for {path}: {error}") from error

    def paged_get(self, path, max_items):
        items = []
        for page in range(1, MAX_PAGES + 1):
            separator = "&" if "?" in path else "?"
            batch = self.get(f"{path}{separator}per_page=100&page={page}")
            if not isinstance(batch, list):
                raise GitHubApiError(f"GitHub API returned a non-list response for {path}")
            items.extend(batch)
            if len(items) >= max_items:
                return items[:max_items], len(batch) == 100
            if len(batch) < 100:
                return items, False
        return items, True

    def read_file(self, path, revision):
        encoded_path = urllib.parse.quote(path, safe="/")
        encoded_ref = urllib.parse.quote(revision, safe="")
        api_path = f"/repos/{self.repository}/contents/{encoded_path}?ref={encoded_ref}"
        try:
            payload = self.get(api_path)
        except GitHubApiError as error:
            return {
                "status": "missing" if error.status == 404 else "unverified",
                "path": path,
                "revision": revision,
                "error": str(error),
            }
        try:
            if not isinstance(payload, dict):
                raise TypeError("GitHub API response was not an object")
            if payload.get("type") != "file" or payload.get("encoding") != "base64":
                raise ValueError("content was unavailable as a base64 file")
            declared_size = payload.get("size")
            if isinstance(declared_size, int) and declared_size > MAX_TEXT_FILE_BYTES:
                return {
                    "status": "truncated",
                    "path": path,
                    "revision": revision,
                    "htmlUrl": payload.get("html_url"),
                    "size": declared_size,
                    "error": f"File exceeded the {MAX_TEXT_FILE_BYTES}-byte evidence limit",
                }
            encoded_content = re.sub(r"\s+", "", payload["content"])
            content = base64.b64decode(encoded_content, validate=True)
            if len(content) > MAX_TEXT_FILE_BYTES:
                raise ValueError(f"decoded content exceeded {MAX_TEXT_FILE_BYTES} bytes")
            return {
                "status": "available",
                "path": path,
                "revision": revision,
                "htmlUrl": payload.get("html_url"),
                "sha": payload.get("sha"),
                "content": content.decode("utf-8"),
            }
        except (binascii.Error, KeyError, TypeError, ValueError, UnicodeDecodeError) as error:
            return {
                "status": "unverified",
                "path": path,
                "revision": revision,
                "error": f"Could not read {path} at {revision}: {error}",
            }


def parse_breaking_changes(content):
    """Parse Breaking Changes bullets while preserving release and source lines."""
    lines = content.splitlines()
    entries = []
    empty_sections = []
    releases = []
    release = None
    index = 0
    while index < len(lines):
        release_match = RELEASE_HEADING.match(lines[index])
        if release_match:
            release = release_match.group(1)
            releases.append({"heading": release, "line": index + 1})
            index += 1
            continue
        heading_match = SECTION_HEADING.match(lines[index])
        if not heading_match or len(heading_match.group(1)) != 3 or heading_match.group(2).lower() != "breaking changes":
            index += 1
            continue

        section_line = index + 1
        index += 1
        section_entry_count = 0
        while index < len(lines):
            next_heading = SECTION_HEADING.match(lines[index])
            if next_heading and len(next_heading.group(1)) <= 3:
                break
            bullet_match = BULLET.match(lines[index])
            if not bullet_match:
                index += 1
                continue
            start = index
            entry_lines = [bullet_match.group(1).rstrip()]
            index += 1
            while index < len(lines):
                if BULLET.match(lines[index]) or SECTION_HEADING.match(lines[index]):
                    break
                entry_lines.append(lines[index].rstrip())
                index += 1
            while entry_lines and not entry_lines[-1]:
                entry_lines.pop()
            text = "\n".join(entry_lines).strip()
            entries.append(
                {
                    "release": release,
                    "text": text,
                    "startLine": start + 1,
                    "endLine": start + max(1, len(entry_lines)),
                    "sectionLine": section_line,
                }
            )
            section_entry_count += 1
        if section_entry_count == 0:
            empty_sections.append({"release": release, "sectionLine": section_line})
    return {"entries": entries, "emptySections": empty_sections, "releases": releases}


def release_key(entry):
    heading = entry.get("release")
    return heading.split()[0] if heading else None


def introduced_breaking_changes(old_entries, new_entries):
    """Return new or modified target entries, excluding exact historical entries."""
    unmatched_old = list(old_entries)
    introduced = []
    for new_entry in new_entries:
        exact_index = next(
            (
                index
                for index, old_entry in enumerate(unmatched_old)
                if release_key(old_entry) == release_key(new_entry) and old_entry["text"] == new_entry["text"]
            ),
            None,
        )
        if exact_index is not None:
            unmatched_old.pop(exact_index)
            continue

        candidates = [entry for entry in unmatched_old if release_key(entry) == release_key(new_entry)]
        previous = None
        similarity = 0.0
        for candidate in candidates:
            ratio = difflib.SequenceMatcher(None, candidate["text"], new_entry["text"]).ratio()
            if ratio > similarity:
                similarity = ratio
                previous = candidate
        result = dict(new_entry)
        if previous is not None and similarity >= 0.55:
            result["changeKind"] = "modified"
            result["previousText"] = previous["text"]
            unmatched_old.remove(previous)
        else:
            result["changeKind"] = "added"
            result["previousText"] = None
        introduced.append(result)
    return introduced


def parse_json_evidence(file_evidence):
    if file_evidence.get("status") != "available":
        return None, file_evidence.get("error")
    try:
        return json.loads(file_evidence["content"]), None
    except (json.JSONDecodeError, TypeError) as error:
        return None, f"Invalid JSON in {file_evidence['path']}: {error}"


def version_value_kind(value):
    if not isinstance(value, str):
        return "other"
    return "range" if re.search(r"[<>=~^*| ]", value) else "resolved"


def extract_lock_versions(lock_data):
    versions = []
    packages = lock_data.get("packages", {}) if isinstance(lock_data, dict) else {}
    if isinstance(packages, dict):
        for path, details in packages.items():
            if not isinstance(details, dict):
                continue
            name = path.rsplit("node_modules/", 1)[-1] if "node_modules/" in path else details.get("name", path)
            version = details.get("version")
            if VERSION_LIKE_KEY.search(str(name)) and isinstance(version, str):
                versions.append({"name": name, "version": version, "kind": "resolved"})
    return sorted(versions, key=lambda item: (item["name"], item["version"]))[:100]


def parse_tsp_location(content):
    result = {"additionalDirectories": []}
    current_list = None
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-") and current_list:
            result[current_list].append(line[1:].strip().strip("'\""))
            continue
        match = re.fullmatch(r"([A-Za-z][A-Za-z0-9]*):\s*(.*?)\s*", line)
        if not match:
            continue
        key, value = match.groups()
        if key == "additionalDirectories":
            current_list = key
            if value and value != "[]":
                result[key].append(value.strip("'\""))
        else:
            current_list = None
            result[key] = value.strip("'\"")
    return result


def summarize_provenance(files):
    summary = {
        "files": [],
        "metadata": None,
        "tspLocation": None,
        "resolvedDependencies": [],
        "issues": [],
    }
    for evidence in files:
        compact = {key: value for key, value in evidence.items() if key != "content"}
        summary["files"].append(compact)
        if evidence["path"].endswith("_metadata.json"):
            metadata, error = parse_json_evidence(evidence)
            if error:
                summary["issues"].append(error)
            elif isinstance(metadata, dict):
                selected = {}
                for key, value in metadata.items():
                    if key in {
                        "apiVersion",
                        "apiVersions",
                        "commit",
                        "repository_url",
                        "typespec_src",
                        "typespecAdditionalOptions",
                        "emitterVersion",
                        "httpClientPythonVersion",
                    } or VERSION_LIKE_KEY.search(key):
                        selected[key] = {
                            "value": value,
                            "kind": version_value_kind(value),
                        }
                summary["metadata"] = selected
        elif evidence["path"].endswith("tsp-location.yaml") and evidence.get("status") == "available":
            summary["tspLocation"] = parse_tsp_location(evidence["content"])
        elif evidence["path"].endswith("package-lock.json") and evidence.get("status") == "available":
            lock_data, error = parse_json_evidence(evidence)
            if error:
                summary["issues"].append(error)
            else:
                summary["resolvedDependencies"] = extract_lock_versions(lock_data)
        elif evidence.get("status") == "available":
            summary["files"][-1]["content"] = evidence["content"]
        if evidence.get("status") in {"unverified", "truncated"}:
            summary["issues"].append(evidence.get("error"))
    metadata = summary.get("metadata") or {}
    tsp_location = summary.get("tspLocation") or {}
    comparisons = (("commit", "commit"), ("typespec_src", "directory"))
    for metadata_key, location_key in comparisons:
        metadata_value = (metadata.get(metadata_key) or {}).get("value")
        location_value = tsp_location.get(location_key)
        if metadata_value and location_value and metadata_value != location_value:
            summary["issues"].append(
                f"Conflicting provenance: _metadata.json {metadata_key}={metadata_value!r}, "
                f"tsp-location.yaml {location_key}={location_value!r}"
            )
    repository_url = (metadata.get("repository_url") or {}).get("value")
    location_repository = tsp_location.get("repo")
    if repository_url and location_repository:
        match = re.fullmatch(
            r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?/?", repository_url
        )
        metadata_repository = match.group(1) if match else repository_url
        if metadata_repository.lower() != location_repository.lower():
            summary["issues"].append(
                "Conflicting provenance: _metadata.json repository_url="
                f"{repository_url!r}, tsp-location.yaml repo={location_repository!r}"
            )
    return summary


def metadata_api_version(provenance):
    metadata = provenance.get("metadata") or {}
    item = metadata.get("apiVersion") or {}
    value = item.get("value")
    return value if isinstance(value, str) and value else None


def collect_provenance(client, package_path, revision):
    files = [client.read_file(f"{package_path}/{relative_path}", revision) for relative_path in PROVENANCE_PATHS]
    return summarize_provenance(files)


def api_version_drift(package_path, first_revision, latest_revision, first_provenance, latest_provenance):
    first_api_version = metadata_api_version(first_provenance)
    latest_api_version = metadata_api_version(latest_provenance)
    drift_errors = first_provenance["issues"] + latest_provenance["issues"]
    for label, revision, version in (
        ("first", first_revision, first_api_version),
        ("latest", latest_revision, latest_api_version),
    ):
        if not version:
            drift_errors.append(
                f"{package_path}/_metadata.json at {label} revision {revision} "
                "does not contain a non-empty string apiVersion"
            )
    return {
        "packagePath": package_path,
        "metadataPath": f"{package_path}/_metadata.json",
        "status": (
            "unverified"
            if not first_api_version or not latest_api_version
            else "unchanged" if first_api_version == latest_api_version else "changed"
        ),
        "firstRevision": first_revision,
        "firstApiVersion": first_api_version,
        "latestRevision": latest_revision,
        "latestApiVersion": latest_api_version,
        "error": "; ".join(drift_errors) if (not first_api_version or not latest_api_version) else None,
    }


def latest_release_version(parsed_changelog):
    for release in parsed_changelog.get("releases", []):
        version = release["heading"].split()[0]
        if version != "0.0.0" and not re.search(r"\(\s*unreleased\s*\)", release["heading"], re.IGNORECASE):
            return version
    return None


def resolve_release_tag(client, package_name, version):
    if not version:
        return {"status": "unverified", "error": "No previous release heading was found at the merge base"}
    tag = f"{package_name}_{version}"
    encoded_tag = urllib.parse.quote(tag, safe="")
    try:
        ref = client.get(f"/repos/{client.repository}/git/ref/tags/{encoded_tag}")
        if not isinstance(ref, dict):
            raise GitHubApiError(f"Tag lookup for {tag} returned a non-object response")
        target = ref.get("object", {})
        if target.get("type") == "tag":
            tag_payload = client.get(f"/repos/{client.repository}/git/tags/{target.get('sha')}")
            if not isinstance(tag_payload, dict):
                raise GitHubApiError(f"Annotated tag lookup for {tag} returned a non-object response")
            target = tag_payload.get("object", {})
        sha = target.get("sha")
        if target.get("type") != "commit" or not isinstance(sha, str) or not SHA_PATTERN.fullmatch(sha):
            raise GitHubApiError(f"Tag {tag} did not resolve to an immutable commit")
        return {"status": "available", "tag": tag, "revision": sha}
    except GitHubApiError as error:
        return {"status": "unverified", "tag": tag, "error": str(error)}


def validated_source_reference(provenance):
    conflicts = [issue for issue in provenance.get("issues", []) if issue.startswith("Conflicting provenance:")]
    if conflicts:
        return {"status": "unverified", "error": "; ".join(conflicts)}
    metadata = provenance.get("metadata") or {}
    repository_item = metadata.get("repository_url") or {}
    commit_item = metadata.get("commit") or {}
    repository_url = repository_item.get("value")
    commit = commit_item.get("value")
    tsp_location = provenance.get("tspLocation") or {}
    repository = tsp_location.get("repo")
    if repository_url:
        match = re.fullmatch(
            r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?/?", repository_url
        )
        repository = match.group(1) if match else None
    commit = commit or tsp_location.get("commit")
    match = REPOSITORY_PATTERN.fullmatch(repository or "")
    if not match or not isinstance(commit, str) or not SHA_PATTERN.fullmatch(commit):
        return {
            "status": "unverified",
            "error": "Specification repository URL or commit was missing or invalid",
        }
    return {"status": "available", "repository": repository, "revision": commit}


def collect():
    repository = os.environ["GH_REPOSITORY"]
    pr_number = int(os.environ["PR_NUMBER"])
    client = GitHubClient(repository, os.environ["GH_TOKEN"])

    repository_data = client.get(f"/repos/{repository}")
    default_branch = repository_data.get("default_branch")
    branch_data = client.get(f"/repos/{repository}/branches/{urllib.parse.quote(default_branch, safe='')}")
    rules_revision = branch_data.get("commit", {}).get("sha")
    if not isinstance(rules_revision, str) or not SHA_PATTERN.fullmatch(rules_revision):
        raise GitHubApiError("Default branch metadata did not contain an immutable commit SHA")
    rules_file = client.read_file(".github/copilot-instructions.md", rules_revision)
    if rules_file.get("status") != "available":
        raise GitHubApiError(rules_file.get("error", "Could not load review rules"))
    lines = rules_file["content"].splitlines()
    heading = "## MGMT SDK Code Review Rules"
    try:
        start = lines.index(heading)
    except ValueError as error:
        raise GitHubApiError(f"{heading} was not found in .github/copilot-instructions.md") from error
    end = next((index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")), len(lines))

    pull_request = client.get(f"/repos/{repository}/pulls/{pr_number}")
    expected_changed_files = pull_request.get("changed_files")
    latest_revision = pull_request.get("head", {}).get("sha")
    base_revision = pull_request.get("base", {}).get("sha")
    if not isinstance(expected_changed_files, int) or expected_changed_files < 0:
        raise GitHubApiError("Pull request metadata did not contain a valid changed_files count")
    if not all(isinstance(value, str) and SHA_PATTERN.fullmatch(value) for value in (latest_revision, base_revision)):
        raise GitHubApiError("Pull request metadata did not contain valid base and head SHAs")

    compare = client.get(f"/repos/{repository}/compare/{base_revision}...{latest_revision}")
    merge_base_revision = compare.get("merge_base_commit", {}).get("sha")
    if not isinstance(merge_base_revision, str) or not SHA_PATTERN.fullmatch(merge_base_revision):
        raise GitHubApiError("The compare API did not return a valid merge-base SHA")

    changed_files, file_list_truncated = client.paged_get(
        f"/repos/{repository}/pulls/{pr_number}/files", max_items=3000
    )
    package_discovery_complete = len(changed_files) == expected_changed_files and not file_list_truncated
    package_discovery_error = None
    if not package_discovery_complete:
        package_discovery_error = (
            "Management package discovery is incomplete: pull request metadata reports "
            f"{expected_changed_files} changed files, the API returned {len(changed_files)}, "
            "or the bounded pagination limit was reached."
        )

    package_paths = sorted(
        {
            match.group(1)
            for item in changed_files
            for field in ("filename", "previous_filename")
            for path in (item.get(field),)
            if isinstance(path, str)
            for match in (PACKAGE_PATTERN.match(path),)
            if match
        }
    )
    commits, commits_truncated = client.paged_get(f"/repos/{repository}/pulls/{pr_number}/commits", max_items=250)
    commit_shas = [item.get("sha") for item in commits if isinstance(item.get("sha"), str)]
    expected_commits = pull_request.get("commits")
    commit_discovery_complete = (
        isinstance(expected_commits, int)
        and not isinstance(expected_commits, bool)
        and expected_commits > 0
        and len(commits) == expected_commits
        and len(commit_shas) == len(commits)
        and not commits_truncated
    )
    if not commit_shas:
        raise GitHubApiError("Pull request metadata returned an empty commit list")
    first_revision = commit_shas[0]

    drift_results = []
    breaking_change_context = []
    for package_path in package_paths:
        remaining_requests = MAX_API_REQUESTS - client.request_count
        if remaining_requests < MAX_PACKAGE_API_REQUESTS:
            reason = (
                f"Needs human review: evidence collection for {package_path} was skipped because only "
                f"{remaining_requests} API requests remain; a package requires a budget of up to "
                f"{MAX_PACKAGE_API_REQUESTS} requests (four provenance snapshots, two changelogs, "
                "and two tag lookups). Completed package results are preserved."
            )
            unavailable = {"status": "unverified", "error": reason}
            drift_results.append(
                {
                    "packagePath": package_path,
                    "metadataPath": f"{package_path}/_metadata.json",
                    "status": "unverified",
                    "firstRevision": first_revision,
                    "firstApiVersion": None,
                    "latestRevision": latest_revision,
                    "latestApiVersion": None,
                    "error": reason,
                }
            )
            breaking_change_context.append(
                {
                    "packagePath": package_path,
                    "changelogPath": f"{package_path}/CHANGELOG.md",
                    "baseChangelogPath": None,
                    "mergeBaseRevision": merge_base_revision,
                    "latestRevision": latest_revision,
                    "status": "unverified",
                    "introducedEntries": [],
                    "emptyBreakingChangeSections": [],
                    "collectionIssues": [reason],
                    "releaseBaseline": unavailable,
                    "provenance": {"mergeBase": unavailable, "latest": unavailable},
                    "specificationSources": {"mergeBase": unavailable, "latest": unavailable, "release": unavailable},
                }
            )
            continue
        first_provenance = collect_provenance(client, package_path, first_revision)
        latest_provenance = collect_provenance(client, package_path, latest_revision)
        drift_results.append(
            api_version_drift(package_path, first_revision, latest_revision, first_provenance, latest_provenance)
        )

        head_changelog_path = f"{package_path}/CHANGELOG.md"
        changelog_change = next(
            (item for item in changed_files if item.get("filename") == head_changelog_path), None
        )
        base_changelog_path = (
            changelog_change.get("previous_filename")
            if changelog_change and changelog_change.get("status") == "renamed"
            else head_changelog_path
        )
        old_file = client.read_file(base_changelog_path, merge_base_revision)
        new_file = client.read_file(head_changelog_path, latest_revision)
        collection_issues = []
        old_parsed = {"entries": [], "emptySections": [], "releases": []}
        new_parsed = {"entries": [], "emptySections": [], "releases": []}
        baseline_available = old_file.get("status") == "available" or (
            old_file.get("status") == "missing"
            and changelog_change is not None
            and changelog_change.get("status") == "added"
        )
        if old_file.get("status") == "available":
            old_parsed = parse_breaking_changes(old_file["content"])
        elif not baseline_available:
            collection_issues.append(
                old_file.get("error") or f"Merge-base changelog was unavailable: {base_changelog_path}"
            )
        if new_file.get("status") == "available":
            new_parsed = parse_breaking_changes(new_file["content"])
        else:
            collection_issues.append(new_file.get("error"))

        introduced = (
            introduced_breaking_changes(old_parsed["entries"], new_parsed["entries"])
            if baseline_available and new_file.get("status") == "available"
            else []
        )
        previous_version = latest_release_version(old_parsed)
        release_baseline = resolve_release_tag(client, package_path.rsplit("/", 1)[-1], previous_version)
        if release_baseline["status"] == "available":
            release_baseline["provenance"] = collect_provenance(
                client, package_path, release_baseline["revision"]
            )
            release_baseline["differsFromMergeBase"] = release_baseline["revision"] != merge_base_revision
            release_baseline["basis"] = (
                "Inferred from the newest release heading at the merge base; the changelog generator's exact "
                "comparison target is not recorded by CHANGELOG.md."
            )
        else:
            collection_issues.append(release_baseline.get("error"))

        merge_base_provenance = collect_provenance(client, package_path, merge_base_revision)
        collection_issues.extend(merge_base_provenance["issues"])
        collection_issues.extend(latest_provenance["issues"])
        if release_baseline.get("provenance"):
            collection_issues.extend(release_baseline["provenance"]["issues"])
        collection_issues = list(dict.fromkeys(issue for issue in collection_issues if issue))
        breaking_change_context.append(
            {
                "packagePath": package_path,
                "changelogPath": head_changelog_path,
                "baseChangelogPath": base_changelog_path,
                "mergeBaseRevision": merge_base_revision,
                "latestRevision": latest_revision,
                "status": "unverified" if collection_issues else "complete",
                "introducedEntries": introduced,
                "emptyBreakingChangeSections": new_parsed["emptySections"],
                "collectionIssues": [issue for issue in collection_issues if issue],
                "releaseBaseline": release_baseline,
                "provenance": {
                    "mergeBase": merge_base_provenance,
                    "latest": latest_provenance,
                },
                "specificationSources": {
                    "mergeBase": validated_source_reference(merge_base_provenance),
                    "latest": validated_source_reference(latest_provenance),
                    "release": (
                        validated_source_reference(release_baseline["provenance"])
                        if release_baseline.get("provenance")
                        else {"status": "unverified", "error": "Release provenance was unavailable"}
                    ),
                },
            }
        )

    context = {
        "repository": repository,
        "pullRequestNumber": pr_number,
        "rulesSource": f".github/copilot-instructions.md@{rules_revision}",
        "mgmtSdkCodeReviewRules": "\n".join(lines[start:end]).strip(),
        "packageDiscovery": {
            "status": "complete" if package_discovery_complete else "unverified",
            "expectedChangedFiles": expected_changed_files,
            "returnedChangedFiles": len(changed_files),
            "error": package_discovery_error,
        },
        "affectedPackages": package_paths,
        "changedFiles": [
            {
                "filename": item.get("filename"),
                "previousFilename": item.get("previous_filename"),
                "status": item.get("status"),
                "additions": item.get("additions"),
                "deletions": item.get("deletions"),
            }
            for item in changed_files
        ],
        "firstRevision": first_revision,
        "latestRevision": latest_revision,
        "mergeBaseRevision": merge_base_revision,
        "commitDiscovery": {
            "status": "complete" if commit_discovery_complete else "unverified",
            "expectedCommits": expected_commits,
            "returnedCommits": len(commits),
            "error": (
                None
                if commit_discovery_complete
                else f"PR commit discovery is incomplete: expected {expected_commits!r}, returned {len(commits)} "
                f"with {len(commit_shas)} commit SHAs; the commit endpoint is limited to 250 commits "
                "and bounded pagination may be incomplete."
            ),
        },
        "apiVersionDrift": drift_results,
        "breakingChangeContext": breaking_change_context,
        "collectionLimits": {
            "maxApiResponseBytes": MAX_API_RESPONSE_BYTES,
            "maxTextFileBytes": MAX_TEXT_FILE_BYTES,
            "maxPages": MAX_PAGES,
            "maxApiRequests": MAX_API_REQUESTS,
            "maxPackageApiRequests": MAX_PACKAGE_API_REQUESTS,
            "apiTimeoutSeconds": API_TIMEOUT_SECONDS,
            "githubApiRequests": client.request_count,
        },
    }
    with open("review-context.json", "w", encoding="utf-8") as output:
        json.dump(context, output, indent=2)
        output.write("\n")


if __name__ == "__main__":
    collect()