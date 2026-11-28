"""Opt-in live public-evidence smoke; synthetic review, no GitHub comment writes."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from test_mgmt_sdk_review_reliability import (
    HEAD,
    PACKAGE,
    REPO,
    SCRIPT,
    TOOLING,
    envelope,
    evidence,
    fixture,
    reference,
    service,
)

# Public provenance from SDK PR #48997's d6c22a02210c7728b9686066b9fab0d221d53527 metadata.
SPEC_REPOSITORY = "Azure/azure-rest-api-specs"
SPEC_REVISION = "eac980067e41d5e5f8b0e9a4aa0e3359f2790912"
SPEC_PATH = "specification/compute/resource-manager/Microsoft.Compute/Compute/client.tsp"


def register(directory):
    draft, context = fixture()
    breaking = context["breakingChangeContext"][0]
    breaking["specificationSources"]["latest"].update(repository=SPEC_REPOSITORY, revision=SPEC_REVISION)
    entry = {
        "text": "Synthetic source-access smoke, not an SDK review.",
        "release": "1.0.0b1 (2026-09-28)",
        "startLine": 1,
        "endLine": 1,
        "changeKind": "added",
    }
    breaking["introducedEntries"] = [entry]
    host = service.ReviewService(context)
    record = host.call(
        {
            "operation": "register",
            "package": PACKAGE,
            "repository": SPEC_REPOSITORY,
            "revision": SPEC_REVISION,
            "path": SPEC_PATH,
        }
    )
    if record["status"] != "available" or not record["lineCount"]:
        raise RuntimeError(f"Live registration failed: {record['status']}: {record['error']}")
    draft["packages"][0]["attribution"] = [
        {
            "entry_id": evidence.entry_id(entry),
            "cause": "typespec_api",
            "explanation": "Synthetic source-access smoke only; not evidence of breaking-change causality.",
            "sources": [reference(record)],
            "sdk_context": [],
        }
    ]
    result = host.call({"operation": "preflight", "draft": draft})
    if not result["ok"]:
        raise RuntimeError(f"Live preflight failed: {result['errors']}")
    # The publisher receives the original context, not the service's fetched content.
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "context.json").write_text(json.dumps(context), encoding="utf-8")
    (directory / "agent-output.json").write_text(json.dumps(envelope(result["submission"]["data"])), encoding="utf-8")
    report = {
        "repository": SPEC_REPOSITORY,
        "revision": SPEC_REVISION,
        "path": SPEC_PATH,
        "sha256": record["sha256"],
        "lineCount": record["lineCount"],
    }
    (directory / "expected.json").write_text(json.dumps(report), encoding="utf-8")
    return report


def publish(directory):
    subprocess.run(
        [sys.executable, str(SCRIPT), "publish"],
        env={
            **os.environ,
            "GH_REPOSITORY": REPO,
            "PR_NUMBER": "49107",
            "REVIEW_CONTEXT": str(directory / "context.json"),
            "GH_AW_AGENT_OUTPUT": str(directory / "agent-output.json"),
            "REVIEW_HEAD_SHA": HEAD,
            "REVIEW_TOOLING_SHA": TOOLING,
        },
        check=True,
        timeout=120,
    )
    output = json.loads((directory / "agent-output.json").read_text(encoding="utf-8"))
    body = output["items"][0]["body"]
    if SPEC_REVISION not in body or "TypeSpec/API" not in body:
        raise RuntimeError("Independent publisher did not retain the verified specification citation.")
    return json.loads((directory / "expected.json").read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("register", "publish"))
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    directory = args.directory.resolve()
    report = register(directory) if args.phase == "register" else publish(directory)
    print(
        json.dumps(
            {
                "phase": args.phase,
                "status": "validated",
                "githubActions": os.environ.get("GITHUB_ACTIONS") == "true",
                "jobTokenPresent": bool(os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")),
                "workflowRevision": os.environ.get("GITHUB_SHA"),
                "commentPublisherInvoked": False,
                **report,
            }
        )
    )


if __name__ == "__main__":
    main()
