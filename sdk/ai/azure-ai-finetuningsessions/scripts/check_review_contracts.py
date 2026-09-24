# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Mutation tests for review gates using durably captured isolated worker JSON.

Run after verify_compatibility.py --artifacts <directory>. This tests verifier
rejection, not SDK runtime behavior, and imports no runtime regression tests.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_compatibility as compatibility
import verify_surface as surface


REPORTS = {}
DELTAS = {}


def _mutate(value, path, operation, replacement):
    result = deepcopy(value)
    target = result
    for key in path[:-1]:
        target = target[key]
    key = path[-1]
    if operation == "delete":
        del target[key]
    elif operation == "append":
        target[key].append(deepcopy(replacement))
    else:
        target[key] = deepcopy(replacement)
    return result


class ReviewContractTests(unittest.TestCase):
    def test_positive_contract_definitions(self):
        self.assertEqual(compatibility._review_contracts(DELTAS),
                         compatibility.ORIGINAL_CONTRACTS + ["training-type-enum"] + compatibility.SERVICE_CONTRACTS)

    def test_positive_exact_surface_and_all_raw_cases(self):
        reference = REPORTS["reference-surface"]
        original = deepcopy(reference)
        expected = surface._apply_review_contracts(reference, compatibility, compatibility._review_contracts(DELTAS))
        candidate = deepcopy(REPORTS["candidate-surface"])
        surface._validate_service_report(candidate)
        del candidate["service"]
        self.assertEqual(compatibility._differences(expected, candidate), [])
        self.assertEqual(reference, original, "Projection mutated the immutable report")
        self.assertEqual(set(expected["raw"]), set(original["raw"]))
        self.assertEqual(len(expected["raw"]), 336)
        self.assertTrue(all(c["ok"] for c in original["raw"].values()))
        self.assertTrue(all(c["ok"] for c in candidate["raw"].values()))

    def test_positive_twenty_case_projection(self):
        reference = REPORTS["reference-convenience"]
        original = deepcopy(reference)
        expected = compatibility._apply_service_contracts(reference["cases"])
        expected = compatibility._apply_review_header_contract(expected, raw=False)
        observed = expected["surface_and_signatures"]["output"]
        observed["exports"]["models"] = sorted([*observed["exports"]["models"], "TrainingType"])
        observed["enums"]["TrainingType"] = {
            "GLOBAL_STANDARD": "GlobalStandard", "DATAZONE_STANDARD": "DatazoneStandard", "DEVELOPER_TIER": "DeveloperTier",
        }
        self.assertEqual(compatibility._differences(expected, REPORTS["candidate-convenience"]["cases"]), [])
        self.assertEqual(reference, original)
        self.assertEqual(set(expected), set(compatibility.CASE_NAMES))


def _negative_definition(path, operation, value):
    def test(self):
        with self.assertRaises(ValueError):
            compatibility._review_contracts(_mutate(DELTAS, path, operation, value))
    return test


for name, path, operation, value in (
    ("unknown", ["fixture_contracts"], "append", "ignore-all-raw-differences"),
    ("duplicate", ["fixture_contracts"], "append", "raw-request-id-polling"),
    ("partial", ["fixture_contracts", -1], "delete", None),
    ("extra_definition", ["service_contracts", "allow_extra_fields"], "set", True),
    ("wrong_default", ["service_contracts", "response_format", "default"], "set", {}),
    ("wrong_rank_default", ["service_contracts", "required_lora", "default"], "set", 32),
    ("wrong_status", ["service_contracts", "raw_polling", "acceptance_status"], "set", 202),
    ("numeric_bool", ["service_contracts", "version"], "set", True),
    ("missing_definition", ["service_contracts", "alias"], "delete", None),
):
    setattr(ReviewContractTests, "test_reject_contract_" + name, _negative_definition(path, operation, value))


def _negative_reference(path, operation, value, convenience=False):
    def test(self):
        report = REPORTS["reference-convenience" if convenience else "reference-surface"]
        changed = _mutate(report, path, operation, value)
        with self.assertRaises((ValueError, RuntimeError)):
            if convenience:
                compatibility._apply_service_contracts(changed["cases"])
            else:
                surface._apply_review_contracts(changed, compatibility, compatibility._review_contracts(DELTAS))
    return test


for name, path, operation, value, convenience in (
    ("rank_default", ["surface", "models", "LoRAConfig", "overloads", 0, "parameters", 0, "default"], "set", 32, False),
    ("extra_field", ["surface", "models", "LoRAConfig", "fields", "unexpected"], "set", {}, False),
    ("extra_export", ["surface", "modules", ".models"], "append", "UnexpectedType", False),
    ("extra_method", ["surface", "clients", ".FineTuningSession", "unexpected"], "set", {}, False),
    ("wire_name", ["surface", "models", "LoRAConfig", "fields", "rank", "wire_name"], "set", "otherRank", False),
    ("serialization", ["surface", "serialization", "SamplingParams", 0, "all", "max_tokens"], "set", 999, False),
    ("missing_raw", ["raw", "async:sessions.begin_create:default_poll"], "delete", None, False),
    ("changed_raw", ["raw", "sync:sessions.begin_create:normal", "requests", 0, "body"], "set", {"rank": 32}, False),
    ("changed_custom", ["raw", "async:sampling.begin_sample:custom_poll", "output", "type"], "set", "dict", False),
    ("convenience_default", ["cases", "surface_and_signatures", "output", "signatures", "sync.create", 2, "default"], "set", {}, True),
    ("convenience_wire", ["cases", "sync_create_identifiers", "requests", 0, "body", "unapproved"], "set", True, True),
    ("missing_convenience", ["cases", "async_create_identifiers"], "delete", None, True),
):
    setattr(ReviewContractTests, "test_reject_baseline_" + name, _negative_reference(path, operation, value, convenience))


def _negative_candidate(path, operation, value):
    def test(self):
        candidate = _mutate(REPORTS["candidate-surface"], path, operation, value)
        expected = surface._apply_review_contracts(REPORTS["reference-surface"], compatibility,
                                                   compatibility._review_contracts(DELTAS))
        del candidate["service"]
        self.assertTrue(compatibility._differences(expected, candidate), "Unauthorized candidate delta was accepted")
    return test


for name, path, operation, value in (
    ("extra_api", ["surface", "clients", ".FineTuningSession", "unreviewed"], "set", {}),
    ("extra_export", ["surface", "modules", ".models"], "append", "Unreviewed"),
    ("extra_field", ["surface", "models", "SamplingParams", "fields", "unreviewed"], "set", {}),
    ("default", ["surface", "models", "LoRAConfig", "overloads", 0, "parameters", 0, "default"], "set", 16),
    ("post_shape", ["raw", "sync:training.begin_optim_step:default_poll", "requests", 0, "body", "extra"], "set", 1),
    ("poll_route", ["raw", "async:training.begin_optim_step:default_poll", "requests", 1, "url"], "set", "https://other.invalid/poll"),
    ("poll_result", ["raw", "async:sampling.begin_sample:default_poll", "output", "value", "sequences"], "set", [{}]),
    ("custom_status", ["raw", "async:sampling.begin_sample:cls", "output", "value", "status"], "set", 202),
    ("missing_case", ["raw", "sync:sampling.begin_sample:continuation"], "delete", None),
):
    setattr(ReviewContractTests, "test_reject_candidate_" + name, _negative_candidate(path, operation, value))


def _negative_service(path, operation, value):
    def test(self):
        with self.assertRaises(ValueError):
            surface._validate_service_report(_mutate(REPORTS["candidate-surface"], path, operation, value))
    return test


for name, path, operation, value in (
    ("missing", ["service", "security:async:post503"], "delete", None),
    ("extra", ["service", "unapproved"], "set", {"ok": True, "checks": 1, "remaining_responses": 0}),
    ("failed", ["service", "service:sync:training.begin_optim_step:engine_dead", "ok"], "set", False),
    ("unconsumed", ["service", "service:sync:training.begin_optim_step:pending", "remaining_responses"], "set", 1),
    ("unchecked", ["service", "model:sampling_alias", "checks"], "set", 0),
):
    setattr(ReviewContractTests, "test_reject_service_" + name, _negative_service(path, operation, value))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True)
    args = parser.parse_args()
    for name in ("reference-surface", "candidate-surface", "reference-convenience", "candidate-convenience"):
        REPORTS[name] = json.loads((args.artifacts / f"{name}.json").read_text(encoding="utf-8"))
    DELTAS.update(json.loads((compatibility.PACKAGE / "eng/generation/review-deltas.json").read_text(encoding="utf-8")))
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ReviewContractTests)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())