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
                         compatibility.ORIGINAL_CONTRACTS + ["training-type-enum"] + compatibility.SERVICE_CONTRACTS
                         + [compatibility.INPUT_CHUNK_CONTRACT, compatibility.FOUNDRY_FEATURES_CONTRACT])

    def test_positive_legacy_contract_definitions_and_baselines(self):
        for contracts in (compatibility.ORIGINAL_CONTRACTS,
                          compatibility.ORIGINAL_CONTRACTS + ["training-type-enum"],
                          compatibility.ORIGINAL_CONTRACTS + ["training-type-enum"] + compatibility.SERVICE_CONTRACTS):
            legacy = deepcopy(DELTAS)
            legacy["fixture_contracts"] = contracts
            del legacy["input_chunk_contract"]
            del legacy["foundry_features_contract"]
            if "raw-request-id-polling" not in contracts:
                del legacy["service_contracts"]
            self.assertEqual(compatibility._review_contracts(legacy), contracts)
            projected = surface._apply_review_contracts(REPORTS["reference-surface"], compatibility, contracts)
            self.assertNotIn("InputChunk", projected["surface"]["models"])
        compatibility._require_baseline(projected["surface"],
            "1834b78806e53c6cac72fe112454cc06edf922da8d0d60a6f6272a0d079ec112", "prior reviewed surface")
        compatibility._require_baseline(projected["raw"],
            "641f397095f9b9fa0bcf435a167c9cfcd3eb7bb630878c2b69214b8a4958e4c6", "prior reviewed raw cases")

    def test_positive_input_projection_does_not_walk_opaque_tokens(self):
        opaque = {"tokens": [91], "chunks": [{"tokens": [92]}], "prompt": {"chunks": [{"tokens": [93]}]}}
        original = {"forward_input": {"data": [{"model_input": {
            "chunks": [{"tokens": [1]}, {"type": "future", "tokens": [2], "extension": opaque}],
            "extension": opaque}, "loss_fn_inputs": {"target_tokens": opaque}}]},
            "extension": opaque, "sequences": [{"tokens": [3]}]}
        expected = deepcopy(original)
        expected["forward_input"]["data"][0]["model_input"]["chunks"][0]["type"] = "text"
        self.assertEqual(compatibility._input_chunk_body(original), expected)
        self.assertNotIn("type", original["forward_input"]["data"][0]["model_input"]["chunks"][0])

    def test_positive_original_serialization_probes_retained(self):
        expected = surface._apply_review_contracts(REPORTS["reference-surface"], compatibility,
                                                   compatibility._review_contracts(DELTAS))["surface"]
        self.assertEqual(len(expected["models"]), 49)
        self.assertEqual(expected["modules"][".models"][15:17], ["ImageChunk", "InputChunk"])
        self.assertEqual(expected["modules"][".models"][-2:], ["FromCheckpoint", "SamplingOperationResult"])
        self.assertEqual(expected["models"]["SamplingOperationResult"], expected["models"]["SampleOperationResult"])
        for observation in expected["serialization"]["ModelInput"]:
            for kind in ("all", "writable", "attributes"):
                self.assertEqual(observation[kind]["chunks"], [{"tokens": [2], "type": "text"}])
        for name in ("SampledSequence", "LossFnInputs", "TensorData", "SampleOperationResult"):
            legacy = surface._apply_review_contracts(REPORTS["reference-surface"], compatibility,
                                                     compatibility._review_contracts(DELTAS)[:-2])
            self.assertEqual(expected["serialization"][name], legacy["surface"]["serialization"][name])

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
        expected = compatibility._apply_input_chunk_contract(expected)
        expected = compatibility._apply_foundry_features_contract(expected)
        self.assertEqual(compatibility._differences(expected, REPORTS["candidate-convenience"]["cases"]), [])
        self.assertEqual(reference, original)
        self.assertEqual(set(expected), set(compatibility.CASE_NAMES))

    def test_positive_features_only_projection(self):
        contracts = compatibility._review_contracts(DELTAS)
        old = surface._apply_review_contracts(REPORTS["reference-surface"], compatibility, contracts[:-1])
        original = deepcopy(old)
        expected = surface._apply_foundry_features_contract(old, compatibility)
        members = expected["surface"]["models"]["FoundryFeaturesOptInKeys"]["enum"]
        self.assertEqual(len(members), 13)
        self.assertEqual({name: value for name, value in members if name in compatibility.LEGACY_FOUNDRY_FEATURES},
                         compatibility.LEGACY_FOUNDRY_FEATURES)
        expected["surface"]["models"]["FoundryFeaturesOptInKeys"] = old["surface"]["models"]["FoundryFeaturesOptInKeys"]
        self.assertEqual(expected, old, "Enum projection changed another surface or wire observation")
        self.assertEqual(old, original, "Enum projection mutated its baseline")

    def test_positive_previous_discriminator_contract(self):
        previous = deepcopy(DELTAS)
        previous["fixture_contracts"].pop()
        del previous["foundry_features_contract"]
        self.assertEqual(compatibility._review_contracts(previous), compatibility._review_contracts(DELTAS)[:-1])


def _negative_definition(path, operation, value):
    def test(self):
        with self.assertRaises(ValueError):
            compatibility._review_contracts(_mutate(DELTAS, path, operation, value))
    return test


for name, path, operation, value in (
    ("unknown", ["fixture_contracts"], "append", "ignore-all-raw-differences"),
    ("duplicate", ["fixture_contracts"], "append", "raw-request-id-polling"),
    ("partial", ["fixture_contracts", -2], "delete", None),
    ("extra_definition", ["service_contracts", "allow_extra_fields"], "set", True),
    ("wrong_default", ["service_contracts", "response_format", "default"], "set", {}),
    ("wrong_rank_default", ["service_contracts", "required_lora", "default"], "set", 32),
    ("wrong_status", ["service_contracts", "raw_polling", "acceptance_status"], "set", 202),
    ("numeric_bool", ["service_contracts", "version"], "set", True),
    ("missing_definition", ["service_contracts", "alias"], "delete", None),
    ("input_missing_definition", ["input_chunk_contract"], "delete", None),
    ("input_missing_contract", ["fixture_contracts", -2], "delete", None),
    ("input_extra_definition", ["input_chunk_contract", "allow_extra_fields"], "set", True),
    ("input_extra_export", ["input_chunk_contract", "exports"], "append", "TextChunk"),
    ("input_wrong_enum", ["input_chunk_contract", "enum", "TEXT"], "set", "encoded_text"),
    ("input_wrong_tag", ["input_chunk_contract", "variants", "ModelInputChunk"], "set", "encoded_text"),
    ("input_closed_base", ["input_chunk_contract", "base", "type"], "set", "InputChunkType"),
    ("input_numeric_bool", ["input_chunk_contract", "version"], "set", True),
    ("input_wire_scope", ["input_chunk_contract", "wire_scope"], "append", "sequences.tokens"),
    ("features_missing_definition", ["foundry_features_contract"], "delete", None),
    ("features_missing_contract", ["fixture_contracts", -1], "delete", None),
    ("features_wrong_header", ["foundry_features_contract", "header"], "set", "FineTuningSessions=V2Preview"),
    ("features_extra_member", ["foundry_features_contract", "members", "UNAPPROVED"], "set", "Unapproved=V1Preview"),
    ("features_wrong_member", ["foundry_features_contract", "members", "FINETUNING_SESSIONS_V1_PREVIEW"], "set", "other"),
    ("features_numeric_bool", ["foundry_features_contract", "version"], "set", True),
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
    ("input_wrong_tag", ["surface", "serialization", "ModelInputChunk", 0, "all", "type"], "set", "encoded_text"),
    ("input_missing_text_tag", ["surface", "serialization", "ModelInput", 0, "all", "chunks", 0, "type"], "delete", None),
    ("input_enum", ["surface", "models", "InputChunkType", "enum", 0, 1], "set", "encoded_text"),
    ("input_base", ["surface", "models", "ModelInputChunk", "bases"], "set", ["Model"]),
    ("input_image_base", ["surface", "models", "ImageChunk", "bases"], "set", ["Model"]),
    ("input_open_base", ["surface", "models", "InputChunk", "fields", "type", "type"], "set", "InputChunkType"),
    ("input_wire_name", ["surface", "models", "ModelInputChunk", "fields", "type", "wire_name"], "set", "kind"),
    ("input_discriminator", ["surface", "models", "ModelInputChunk", "fields", "type", "discriminator"], "set", False),
    ("input_image_format", ["surface", "models", "ImageChunk", "fields", "data", "format"], "set", None),
    ("input_image_wire", ["surface", "serialization", "ImageChunk", 0, "all", "data"], "set", "not-base64"),
    ("input_export_position", ["surface", "modules", ".models", 15], "set", "InputChunk"),
    ("input_alias", ["surface", "serialization", "SamplingOperationResult", 0, "class"], "set", "SamplingOperationResult"),
    ("input_image_fallback", ["surface", "input_chunks", "mapping", "classes", 1], "set", "ModelInputChunk"),
    ("input_public_image", ["surface", "input_chunks", "mapping", "public_image"], "set", False),
    ("input_unknown_variant", ["surface", "input_chunks", "mapping", "wire", "chunks", 2, "type"], "set", "text"),
    ("input_opaque_tag", ["surface", "input_chunks", "mapping", "wire", "extension", "type"], "set", "text"),
    ("input_image_validation", ["surface", "input_chunks", "incorrect_image_type", 0], "set", {"accepted": True}),
    ("input_loss_tensor_tag", ["surface", "serialization", "Datum", 0, "all", "loss_fn_inputs", "target_tokens", "type"], "set", "text"),
    ("input_returned_tokens_tag", ["surface", "serialization", "SampledSequence", 0, "all", "type"], "set", "text"),
    ("features_missing_member", ["surface", "models", "FoundryFeaturesOptInKeys", "enum", 4], "delete", None),
    ("features_extra_member", ["surface", "models", "FoundryFeaturesOptInKeys", "enum"], "append", ["UNAPPROVED", "Other"]),
    ("features_wrong_value", ["surface", "models", "FoundryFeaturesOptInKeys", "enum", -1, 1], "set", "FineTuningSessions=V2Preview"),
    ("features_reordered", ["surface", "models", "FoundryFeaturesOptInKeys", "enum", 0], "set", ["SCHEDULES_V1_PREVIEW", "Schedules=V1Preview"]),
):
    setattr(ReviewContractTests, "test_reject_candidate_" + name, _negative_candidate(path, operation, value))


def _negative_prior_review(path, operation, value, convenience=False):
    def test(self):
        if convenience:
            # Rebuild the PRIOR projection from the oracle, never the candidate.
            prior = compatibility._apply_service_contracts(REPORTS["reference-convenience"]["cases"])
            prior = compatibility._apply_review_header_contract(prior, raw=False)
            api = prior["surface_and_signatures"]["output"]
            api["exports"]["models"] = sorted([*api["exports"]["models"], "TrainingType"])
            api["enums"]["TrainingType"] = {
                "GLOBAL_STANDARD": "GlobalStandard", "DATAZONE_STANDARD": "DatazoneStandard", "DEVELOPER_TIER": "DeveloperTier"}
            project = compatibility._apply_input_chunk_contract
        else:
            prior = surface._apply_review_contracts(REPORTS["reference-surface"], compatibility,
                                                    compatibility._review_contracts(DELTAS)[:-2])
            project = lambda value: surface._apply_input_chunk_contract(value, compatibility)
        with self.assertRaises(ValueError):
            project(_mutate(prior, path, operation, value))
    return test


for name, path, operation, value, convenience in (
    ("extra_export", ["surface", "modules", ".models"], "append", "Unapproved", False),
    ("image_format", ["surface", "models", "ImageChunk", "fields", "data", "format"], "set", "base64", False),
    ("chunks_annotation", ["surface", "models", "ModelInput", "fields", "chunks", "type"], "set", "InputChunk", False),
    ("text_probe", ["surface", "serialization", "ModelInput", 0, "all", "chunks", 0, "tokens"], "set", [99], False),
    ("raw_body", ["raw", "sync:sessions.begin_create:normal", "requests", 0, "body"], "set", {"extra": 1}, False),
    ("convenience_text", ["serialization_and_error_contracts", "output", "ModelInput", "json", "chunks", 0, "type"], "set", "text", True),
    ("convenience_export", ["surface_and_signatures", "output", "exports", "models"], "append", "InputChunk", True),
):
    setattr(ReviewContractTests, "test_reject_prior_review_" + name,
            _negative_prior_review(path, operation, value, convenience))


def _negative_convenience(path, operation, value):
    def test(self):
        candidate = _mutate(REPORTS["candidate-convenience"], path, operation, value)
        # Exercise the actual comparator, including every exact request body/header.
        from contextlib import redirect_stdout
        from io import StringIO
        with redirect_stdout(StringIO()):
            result = compatibility._compare(REPORTS["reference-convenience"], candidate, reviewed=True,
                training_type_enum=True, service_contracts=True, input_chunk_discriminator=True,
                canonical_foundry_features=True)
        self.assertEqual(result, 1)
    return test


for name, path, operation, value in (
    ("missing_text", ["cases", "sync_training", "requests", 0, "body", "forward_input", "data", 0, "model_input", "chunks", 0, "type"], "delete", None),
    ("wrong_text", ["cases", "sync_sampling", "requests", 0, "body", "prompt", "chunks", 0, "type"], "set", "encoded_text"),
    ("loss_tensor", ["cases", "sync_training", "requests", 0, "body", "forward_input", "data", 0, "loss_fn_inputs", "target_tokens", "type"], "set", "text"),
    ("returned_tokens", ["cases", "sync_sampling", "output", 0, "json", "sequences", 0, "type"], "set", "text"),
    ("features_header", ["cases", "sync_sampling", "requests", 0, "headers", "foundry-features"], "set", "FineTuningSessions=V2Preview"),
    ("features_missing", ["cases", "surface_and_signatures", "output", "enums", "FoundryFeaturesOptInKeys", "AGENT_INSIGHTS_V1_PREVIEW"], "delete", None),
    ("features_extra", ["cases", "surface_and_signatures", "output", "enums", "FoundryFeaturesOptInKeys", "UNAPPROVED"], "set", "Other"),
):
    setattr(ReviewContractTests, "test_reject_convenience_input_" + name,
            _negative_convenience(path, operation, value))


class FoundryFeatureBaselineTests(unittest.TestCase):
    def test_reject_changed_surface_enum(self):
        old = surface._apply_review_contracts(REPORTS["reference-surface"], compatibility,
                                             compatibility._review_contracts(DELTAS)[:-1])
        old["surface"]["models"]["FoundryFeaturesOptInKeys"]["enum"][0][1] = "changed"
        with self.assertRaises(ValueError):
            surface._apply_foundry_features_contract(old, compatibility)

    def test_reject_changed_convenience_enum(self):
        old = deepcopy(REPORTS["reference-convenience"]["cases"])
        old["surface_and_signatures"]["output"]["enums"]["FoundryFeaturesOptInKeys"]["UNAPPROVED"] = "other"
        with self.assertRaises(ValueError):
            compatibility._apply_foundry_features_contract(old)


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
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(FoundryFeatureBaselineTests))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())