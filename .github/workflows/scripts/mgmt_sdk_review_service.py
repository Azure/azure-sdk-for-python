#!/usr/bin/env python3
"""Read-only host service: bounded evidence, format checks and semantic attempts.

Only GET requests reach GitHub. No package content is executed. State lives in
memory for this job; a restart loses corrections rather than authorizing output.
"""

import argparse
import copy
import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

import mgmt_sdk_review_contract as contract
from mgmt_sdk_review_context import (
    API_TIMEOUT_SECONDS,
    MAX_TEXT_FILE_BYTES,
    REPOSITORY_PATTERN,
    SHA_PATTERN,
    authorize_current_run,
)
from mgmt_sdk_review_evidence import (
    MAX_REGISTERED_BYTES,
    MAX_REGISTERED_FILES,
    SEMANTIC_CHECKS,
    entry_id,
    source_record,
)


class NoSpecificationRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def read_public_specification_file(repository, revision, path):
    """Read pinned public content without credentials or REST API rate-limit usage."""
    url = f"https://raw.githubusercontent.com/{repository}/{revision}/" + urllib.parse.quote(path, safe="/")
    request = urllib.request.Request(url, headers={"User-Agent": "azure-sdk-python-mgmt-review"})
    record = {"path": path, "revision": revision, "status": "unverified"}
    try:
        # A fresh opener cannot inherit a global authenticated opener. Redirects
        # are rejected rather than following a new host or mutable destination.
        opener = urllib.request.build_opener(NoSpecificationRedirects())
        with opener.open(request, timeout=API_TIMEOUT_SECONDS) as response:
            declared_size = response.headers.get("Content-Length")
            declared_size = int(declared_size) if declared_size is not None else None
            if declared_size is not None and declared_size < 0:
                raise ValueError("negative Content-Length")
            if declared_size is not None and declared_size > MAX_TEXT_FILE_BYTES:
                return {
                    **record,
                    "status": "truncated",
                    "error": f"Public specification exceeded the {MAX_TEXT_FILE_BYTES}-byte evidence limit.",
                }
            content = response.read(MAX_TEXT_FILE_BYTES + 1)
            if len(content) > MAX_TEXT_FILE_BYTES:
                return {
                    **record,
                    "status": "truncated",
                    "error": f"Public specification exceeded the {MAX_TEXT_FILE_BYTES}-byte evidence limit.",
                }
            if declared_size is not None and len(content) != declared_size:
                raise ValueError("Content-Length does not match received content")
            return {**record, "status": "available", "content": content.decode("utf-8"), "error": ""}
    except urllib.error.HTTPError as error:
        error.close()
        return {
            **record,
            "status": "missing" if error.code == 404 else "unverified",
            "httpStatus": error.code,
            "error": (
                f"Public specification read returned HTTP {error.code} for {path} at {revision}. "
                "Only public, immutable GitHub content is supported; no authenticated fallback is attempted."
            ),
        }
    except (OSError, ValueError, http.client.HTTPException) as error:
        return {
            **record,
            "error": f"Could not read public specification {path} at {revision}: {error}",
        }


class EvidenceRegistry:
    def __init__(self, context):
        self.context = context
        self.records = {}
        self.requests = {}
        self.bytes = {}

    def register(self, package, repository, revision, path):
        field = "registration"
        breaking = next(
            (item for item in self.context["breakingChangeContext"] if item["packagePath"] == package), None
        )
        contract.require(
            breaking is not None, field + ".package", "Select a trusted affected package.", "package_coverage"
        )
        permitted = {
            (item["repository"], item["revision"])
            for item in breaking["specificationSources"].values()
            if item["status"] == "available"
        }
        contract.require(
            (repository, revision) in permitted,
            field + ".revision",
            "Use a pinned specification repository/revision.",
            "wrong_revision",
        )
        contract.require(
            isinstance(repository, str)
            and REPOSITORY_PATTERN.fullmatch(repository)
            and isinstance(revision, str)
            and SHA_PATTERN.fullmatch(revision),
            field + ".revision",
            "Use a GitHub owner/repository and immutable commit SHA.",
            "wrong_revision",
        )
        contract.require(
            isinstance(path, str)
            and len(path) <= 1024
            and path.startswith("specification/")
            and not any(part in {"", ".", ".."} for part in path.split("/"))
            and not re.search(r"[%\\?#\x00-\x1f]", path)
            and path.endswith((".tsp", ".json", ".yaml", ".yml", ".md")),
            field + ".path",
            "Select one specification data file, without traversal or URL encoding.",
            "invalid_source_path",
        )
        key = (package, repository, revision, path)
        if key in self.records:
            return self.records[key]
        count = self.requests.get(package, 0)
        contract.require(
            count < MAX_REGISTERED_FILES, field, "20-file evidence retrieval budget exhausted.", "evidence_budget"
        )
        self.requests[package] = count + 1
        if MAX_REGISTERED_BYTES - self.bytes.get(package, 0) < MAX_TEXT_FILE_BYTES:
            record = source_record(
                repository,
                {
                    "path": path,
                    "revision": revision,
                    "status": "truncated",
                    "error": "Insufficient remaining 1 MiB evidence budget for a bounded file request.",
                },
                package,
                "specification",
            )
            self.records[key] = record
            return record
        record = source_record(
            repository, read_public_specification_file(repository, revision, path), package, "specification"
        )
        size = len(record["content"].encode())
        if self.bytes.get(package, 0) + size > MAX_REGISTERED_BYTES:
            record.update(
                status="truncated",
                content="",
                lineCount=0,
                sha256=None,
                error="1 MiB specification evidence budget exhausted.",
            )
            size = 0
        self.bytes[package] = self.bytes.get(package, 0) + size
        self.records[key] = record
        return record

    def manifests(self):
        return [
            {key: record[key] for key in ("package", "repository", "revision", "path")}
            | {"sha256": record["sha256"] or ""}
            for record in self.records.values()
        ]

    def resolve(self, context, registration):
        record = self.register(*(registration[key] for key in ("package", "repository", "revision", "path")))
        contract.require(
            (record["sha256"] or "") == registration["sha256"],
            "data.registrations",
            "Independent retrieval differs from preflight; retain diagnostics and rerun.",
            "evidence_changed",
        )
        context["sources"].append(record)


class ReviewService:
    def __init__(self, context):
        self.context = copy.deepcopy(context)
        self.registry = EvidenceRegistry(self.context)
        self.attempts = 0
        self.format_checks = 0
        self.accepted = False
        self.incomplete = False

    def call(self, request):
        contract.require(isinstance(request, dict), "request", "Expected a JSON object.")
        operation = request.get("operation")
        if operation == "describe":
            contract.require(set(request) == {"operation"}, "request", "describe takes no other fields.")
            return {
                "schema": contract.DRAFT_SCHEMA,
                "draft": contract.draft_template(self.context),
                "schemaVersion": "2",
                "toolingRevision": self.context["toolingRevision"],
                "packages": [
                    {
                        "package": item["packagePath"],
                        "requiredChecks": list(SEMANTIC_CHECKS),
                        "entries": [{"entry_id": entry_id(entry), **entry} for entry in item["introducedEntries"]],
                    }
                    for item in self.context["breakingChangeContext"]
                ],
                "sources": [
                    {key: value for key, value in item.items() if key != "content"} for item in self.context["sources"]
                ],
                "deterministicChecks": self.context["deterministicChecks"],
            }
        if operation == "incomplete":
            contract.require(set(request) == {"operation", "reason"}, "request", "incomplete requires only reason.")
            contract.require(not self.accepted, "request", "A review was already accepted.", "correction_limit")
            submission = contract.incomplete_submission(request["reason"])
            self.incomplete = True
            result = {
                "ok": False,
                "outcome": "incomplete",
                "reason": request["reason"],
                "attempt": self.attempts,
                "schemaVersion": "2",
                "toolingRevision": self.context["toolingRevision"],
            }
            print(json.dumps(result), file=sys.stderr, flush=True)
            return {**result, "incompleteSubmission": submission}
        if operation == "read":
            contract.require(set(request) == {"operation", "source_id"}, "request", "read requires only source_id.")
            records = self.context["sources"] + list(self.registry.records.values())
            record = next((item for item in records if item["id"] == request["source_id"]), None)
            contract.require(
                record is not None, "request.source_id", "Use an ID from describe/register.", "unknown_source"
            )
            return self.display(record)
        if operation == "register":
            contract.require(
                set(request) == {"operation", "package", "repository", "revision", "path"},
                "request",
                "register requires package, repository, revision and path only.",
            )
            contract.require(
                not self.accepted and not self.incomplete and self.attempts < 3,
                "request",
                "Review is already accepted or exhausted.",
                "correction_limit",
            )
            record = self.registry.register(*(request[key] for key in ("package", "repository", "revision", "path")))
            return self.display(record)
        contract.require(
            operation in {"check", "preflight"} and set(request) == {"operation", "draft"},
            "request.operation",
            "Use describe, read, register, check, preflight or incomplete.",
        )
        contract.require(
            not self.accepted and not self.incomplete and self.attempts < 3,
            "request",
            "Initial attempt and two corrections are exhausted, or a review was already accepted. Report incomplete; do not submit again.",
            "correction_limit",
        )
        contract.require(
            self.format_checks < 10,
            "request",
            "Ten format checks are exhausted. Use incomplete; do not submit a review.",
            "format_check_limit",
        )
        self.format_checks += 1
        errors = contract.schema_errors(request["draft"])
        if operation == "check" or errors:
            result = {
                "ok": not errors,
                "phase": "format",
                "errors": errors,
                "attempt": self.attempts,
                "correctionsRemaining": 3 - self.attempts,
                "formatChecksRemaining": 10 - self.format_checks,
                "schemaVersion": "2",
                "toolingRevision": self.context["toolingRevision"],
            }
            print(json.dumps(result), file=sys.stderr, flush=True)
            return result
        self.attempts += 1
        context = copy.deepcopy(self.context)
        context["sources"].extend(self.registry.records.values())
        result = contract.preflight(request["draft"], context)
        result.update(attempt=self.attempts, correctionsRemaining=3 - self.attempts)
        if result["ok"]:
            data = {**request["draft"], "registrations": self.registry.manifests()}
            data["preflight"] = {"attempt": self.attempts, "digest": contract.digest(data)}
            try:
                contract.validate_schema(data)
                contract.require(
                    len(json.dumps(data).encode()) <= contract.MAX_BYTES,
                    "data",
                    "Final submission exceeds the transport budget.",
                    "publication_size_budget",
                )
                self.accepted = True
                result["submission"] = {
                    "body": contract.SUBMISSION,
                    "data": data,
                    "item_number": str(self.context["pullRequestNumber"]),
                }
            except contract.ReviewError as error:
                result.update(ok=False, errors=[error.diagnostic])
        print(
            json.dumps({key: value for key, value in result.items() if key != "submission"}),
            file=sys.stderr,
            flush=True,
        )
        return result

    @staticmethod
    def display(record):
        return {key: value for key, value in record.items() if key != "content"} | {
            "numberedContent": "\n".join(f"{i}: {line}" for i, line in enumerate(record["content"].splitlines(), 1)),
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", required=True)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    authorize_current_run()
    context = contract.load_json(args.context, 64 * 1024 * 1024)
    contract.validate_context(
        context,
        os.environ["GH_REPOSITORY"],
        int(os.environ["PR_NUMBER"]),
        os.environ["REVIEW_HEAD_SHA"],
        os.environ["REVIEW_TOOLING_SHA"],
    )
    service = ReviewService(context)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_POST(self):
            try:
                length = int(self.headers.get("Content-Length", "0"))
                contract.require(
                    self.path == "/review" and 0 < length <= contract.MAX_BYTES,
                    "request",
                    "Invalid request path or size.",
                )
                request = json.loads(self.rfile.read(length), object_pairs_hook=contract.strict_object)
                result = service.call(request)
            except (ValueError, TypeError, KeyError) as error:
                result = {
                    "ok": False,
                    "errors": [
                        (
                            error.diagnostic
                            if isinstance(error, contract.ReviewError)
                            else {"code": "invalid_request", "path": "request", "message": str(error)}
                        )
                    ],
                }
                print(json.dumps(result), file=sys.stderr, flush=True)
            payload = json.dumps(result).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    HTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
