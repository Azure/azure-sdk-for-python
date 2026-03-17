"""Local test script for legacy endpoint backwards compatibility.

Tests all 4 content safety evaluators with both _use_legacy_endpoint=True/False
against both OneDP and AML project types.
"""

import sys
import traceback
from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import ViolenceEvaluator, HateUnfairnessEvaluator, SelfHarmEvaluator, SexualEvaluator

# --- Config ---
ONEDP_ENDPOINT = "https://sydneylister-4786-resource.services.ai.azure.com/api/projects/sydneylister-4786"
AML_PROJECT = {
    "subscription_id": "fac34303-435d-4486-8c3f-7094d82a0b60",
    "resource_group_name": "rg-naarkalgaihub",
    "project_name": "naarkalg-rai-test",
}

SAFE_INPUT = {"query": "What is the capital of Japan?", "response": "The capital of Japan is Tokyo."}

EVALUATORS = [
    ("Violence", ViolenceEvaluator),
    ("HateUnfairness", HateUnfairnessEvaluator),
    ("SelfHarm", SelfHarmEvaluator),
    ("Sexual", SexualEvaluator),
]

PROJECT_CONFIGS = [
    ("OneDP", ONEDP_ENDPOINT),
    ("AML", AML_PROJECT),
]


def run_test(eval_name, eval_cls, project_name, project_scope, credential):
    """Run a single evaluator test with both legacy and sync endpoints."""
    results = {}
    for mode, use_legacy in [("legacy", True), ("sync", False)]:
        label = f"{eval_name} | {project_name} | {mode}"
        try:
            evaluator = eval_cls(credential, project_scope, _use_legacy_endpoint=use_legacy)
            result = evaluator(**SAFE_INPUT)
            results[mode] = result
            keys = sorted(result.keys())
            print(f"  ✅ {label}: {len(keys)} keys")
            for k, v in sorted(result.items()):
                print(f"       {k} = {v}")
        except Exception as e:
            results[mode] = None
            print(f"  ❌ {label}: {type(e).__name__}: {e}")
            traceback.print_exc(limit=3)

    # Compare key sets
    if results.get("legacy") and results.get("sync"):
        legacy_keys = set(results["legacy"].keys())
        sync_keys = set(results["sync"].keys())
        if legacy_keys == sync_keys:
            print(f"  🟢 {eval_name} | {project_name} | Key sets MATCH ({len(legacy_keys)} keys)")
        else:
            only_legacy = legacy_keys - sync_keys
            only_sync = sync_keys - legacy_keys
            print(f"  🔴 {eval_name} | {project_name} | Key sets DIFFER")
            if only_legacy:
                print(f"       Only in legacy: {only_legacy}")
            if only_sync:
                print(f"       Only in sync: {only_sync}")
    print()


def main():
    from azure.ai.evaluation._version import VERSION
    print(f"azure-ai-evaluation version: {VERSION}")
    print()

    credential = DefaultAzureCredential()

    total_pass = 0
    total_fail = 0

    for project_name, project_scope in PROJECT_CONFIGS:
        print(f"{'='*60}")
        print(f"PROJECT: {project_name}")
        print(f"{'='*60}")
        for eval_name, eval_cls in EVALUATORS:
            print(f"\n--- {eval_name} ---")
            run_test(eval_name, eval_cls, project_name, project_scope, credential)

    print(f"\n{'='*60}")
    print("DONE")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
