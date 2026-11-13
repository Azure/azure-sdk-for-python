# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Refresh the reviewed create ledger; unknown observations remain unresolved.

Run with the package interpreter and --discovery <original discovery JSON> for
initial generation. Later runs reuse the persistent candidate inventory. Review
the resulting diff: regeneration is not approval or a semantic-equivalence test.
"""

import argparse
import ast
from collections import Counter
import importlib.util
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GUARD = ROOT / "tests" / "create_item" / "test_assertion_correspondence_unit.py"
SPEC = importlib.util.spec_from_file_location("create_correspondence_guard", GUARD)
GUARD_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GUARD_MODULE)

HEADER_TESTS = {
    "test_client_level_throughput_bucket",
    "test_request_precedence_throughput_bucket",
    "test_container_create_item_throughput_bucket",
    "test_client_level_priority",
    "test_request_precedence_priority",
}
AVAILABILITY_TESTS = {
    "test_availability_strategy_in_steady_state",
    "test_client_availability_strategy_failover",
    "test_non_transient_errors_from_failed_over_region",
    "test_transient_error_from_failed_over_region",
    "test_request_level_disable_override_client_strategy",
    "test_request_level_enable_override_client_disable",
    "test_no_cross_region_request_with_exclude_regions",
    "test_no_cross_region_request_with_retry_write_disabled",
    "test_per_partition_circular_breaker_with_cancelled_first_future",
    "test_custom_thread_pool_executor",
    "test_default_availability_strategy_with_ppaf_enabled",
    "test_per_request_none_falls_back_to_client_strategy",
}


def source_file(stem, asynchronous=False):
    return "tests\\" + stem + ("_async" if asynchronous else "") + ".py"


def functions(path):
    return GUARD_MODULE._read_file(path)  # pylint: disable=protected-access


def reference(path, symbol):
    text, names = functions(path)
    return GUARD_MODULE._reference(path, symbol, "function", names[symbol], text)  # pylint: disable=protected-access


def assertions(path, symbol, contains=None):
    text, names = functions(path)
    result = []
    for kind, node in GUARD_MODULE._observations(names[symbol]):  # pylint: disable=protected-access
        if kind not in {"assertion", "assertion-call"}:
            continue
        if contains is not None and contains not in ast.unparse(node):
            continue
        result.append(GUARD_MODULE._reference(path, symbol, kind, node, text))  # pylint: disable=protected-access
    assert result, (path, symbol, contains)
    return result


def select():
    selected = {}
    for asynchronous in (False, True):
        suffix = "_async" if asynchronous else ""
        families = {
            "test_headers": lambda name: name.removesuffix(suffix) in HEADER_TESTS if suffix else name in HEADER_TESTS,
            "test_retry_policy": lambda name: name.startswith("test_") and (
                "resource_" in name or "default_retry_policy_for_" in name or "timeout_failover_retry_policy_for_read" in name
            ),
            "test_container_properties_cache": lambda name: name.startswith((
                "test_container_properties_cache", "test_container_recreate_create_upsert_replace_item"
            )),
            "test_cosmos_responses": lambda name: name.startswith("test_point_operation_headers"),
            "test_crud": lambda name: name == "test_document_crud" + suffix,
            "test_crud_response_payload_on_write_disabled": lambda name: name.startswith("test_document_crud"),
            "test_backwards_compatibility": lambda name: name.startswith("test_etag_match_condition_compatibility"),
            "test_query_response_headers": lambda name: name.startswith("test_response_hook_parity_point_ops"),
        }
        for stem, predicate in families.items():
            path = source_file(stem, asynchronous)
            for symbol, node in functions(path)[1].items():
                if predicate(node.name):
                    selected[path, symbol] = stem
        path = source_file("test_headers", asynchronous)
        for helper in ("assert_client_throughput_bucket", "assert_request_throughput_bucket",
                       "assert_client_priority", "assert_request_priority"):
            selected[path, helper] = "test_headers"
        path = source_file("test_availability_strategy", asynchronous)
        for helper in ("_perform_write_operation", "_validate_response_uris"):
            selected[path, helper] = "test_availability_strategy"
        for symbol, node in functions(path)[1].items():
            normalized = node.name.removesuffix("_async")
            normalized = normalized.replace("disabled_override", "disable_override")
            normalized = normalized.replace("enabled_override_client_disabled", "enable_override_client_disable")
            if normalized in AVAILABILITY_TESTS or normalized == "test_max_concurrency":
                selected[path, symbol] = "test_availability_strategy"
    path = source_file("test_session", True)
    for symbol, node in functions(path)[1].items():
        if node.name in {"test_session_token_swr_for_ops_async", "test_session_token_mwr_for_ops_async"}:
            selected[path, symbol] = "test_session"
    for stem, prefixes in {
        "test_retryable_writes": ("test_retryable_writes_request_level", "test_retryable_writes_client_level"),
        "test_session": ("test_session_token_sm_for_ops", "test_session_token_mwr_for_ops"),
        "test_user_configs": ("test_default_account_consistency",),
        "test_fault_injection_transport": ("test_throws_injected_error", "test_swr_mrr_succeeds"),
    }.items():
        path = source_file(stem)
        for symbol, node in functions(path)[1].items():
            if node.name in prefixes:
                selected[path, symbol] = stem
    return selected


def disposition(path, symbol, kind, node):
    """Curated source dimensions, not test-name equality or historical verdicts."""
    _, names = functions(path)
    function = names[symbol]
    text = ast.unparse(node)
    name = function.name.removesuffix("_async")
    asynchronous = path.endswith("_async.py")
    surface = "aio" if asynchronous else "sync"
    replacement = f"tests\\create_item\\{surface}\\test_contracts.py"
    row = {
        "disposition": "unresolved",
        "rationale": "Observation retained for explicit review; no assertion-equivalent replacement established.",
        "replacements": [],
        "helper_sources": [],
        "replacement_context": [],
        "execution_level": "none",
        "verification": "no-per-row-execution-attribution",
        "verification_pending": ["semantic-review"],
        "policy_ids": [],
    }

    def set_result(status, reason, refs=(), level="none", pending=()):
        row.update(disposition=status, rationale=reason, replacements=list(refs), execution_level=level,
                   verification_pending=list(pending))

    def other(reason="Other API or setup/cleanup observation; create is seed, not the contract under test."):
        set_result("setup-or-other-api", reason)

    def mapped(reason, refs, partial=False, level="public-installed-native", pending=("public-native-run",)):
        set_result("partial-correspondence" if partial else "supported-correspondence", reason, refs, level, pending)

    if "test_headers" in path:
        priority = "priority" in name
        column = "x-ms-cosmos-priority-level" if priority else "x-ms-cosmos-throughput-bucket"
        level_name = "client_level" if "client" in name else "request_precedence"
        header_column = "priority" if priority else "throughput_bucket"
        target = f"tests\\create_item\\{surface}\\test_headers.py"
        suffix = "_async" if asynchronous else ""
        if name.startswith(("test_client_level_", "test_request_precedence_")):
            header_test = next(key for key in functions(target)[1]
                               if key.endswith(f".test_{level_name}_{header_column}{suffix}_rust"))
            mapped(
                "Original client default/request precedence values are asserted at the typed native boundary "
                "with a wrapped real create. Header conversion and service scheduling are separate from this "
                "assertion.",
                assertions(target, header_test, header_column), partial=True,
                pending=("public-native-run", "native-wire-header-observation"),
            )
        if "container_create_item_throughput_bucket" in name:
            target_symbol = next(key for key in functions(target)[1]
                                 if key.endswith(f".test_container_create_item_throughput_bucket{suffix}_rust"))
            mapped(
                "Original request bucket 3 is asserted at the typed native boundary with a wrapped real create. "
                "Header conversion and service scheduling are separate from this assertion.",
                assertions(target, target_symbol, "throughput_bucket"), partial=True,
                pending=("public-native-run", "native-wire-header-observation"),
            )
        for call in ast.walk(function):
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id.startswith("assert_"):
                if call.func.id in names:
                    row["helper_sources"].append(reference(path, call.func.id))
    elif "test_retry_policy" in path:
        cls = symbol.split(".")[0]
        helper = "_MockExecuteFunction" if "throttle" in name and "backoff" not in name else "MockExecuteFunctionConnectionReset.__call__"
        if "and_connection_retry_total" in name:
            helper = "_MockExecuteFunction"
        if "for_read" in name:
            helper = "MockExecuteFunctionTimeout.__call__"
        helper_symbol = cls + "." + helper
        if helper_symbol in names:
            row["helper_sources"] = [reference(path, helper_symbol)]
        if "query" in name or "for_read" in name:
            other("Create seeds a query/read retry scenario; its query/read failures and counters are not create gaps.")
        elif "ThrottleRetryCount" in text or "ThrottleRetryWaitTimeInMs" in text:
            set_result("driver-gap", "Gap29 remains open: create throttle retry-count/accumulated-wait response metadata "
                       "is not replaced by ordinary attempt totals or read-only fault tests.",
                       pending=("driver-gap29", "create-throttle-native-metadata"))
        elif "ConnectionRetryConfiguration" in text or "RetryOptions._max_wait_time_in_seconds" in text or ".counter" in text:
            set_result("retired-python-detail", "Exact Python policy object/counter is retired. This does not retire "
                       "the separate supported create status, retry-budget or persistence outcome.")
        elif "10054" in text:
            set_result("unresolved",
                       "Legacy mock represents a socket reset as Cosmos HTTP status 10054. Native transport failures "
                       "surface conservatively as ServiceResponseError; no equivalent ServiceRequestError/not-sent "
                       "guarantee is established. This difference is retained explicitly, not assumed approved "
                       "or attributed to an API-review decision that has not been located.",
                       pending=("transport-error-api-review",))
        elif "created_document" in text and "{}" in text:
            set_result("unresolved", "Empty local result after a pre-service mock reset does not prove stored absence "
                       "after a committed lost response. Map pre-service failure and committed failure separately.",
                       pending=("failure-result-and-persisted-state-correspondence",))
        else:
            set_result("unresolved", "Supported create exhaustion/status or retry-budget branch still needs "
                       "scenario-specific native correspondence. Retiring Python monkeypatches does not retire this outcome.",
                       pending=("create-throttle-or-reset-native-scenario",))
    elif "test_container_properties_cache" in path:
        if name == "test_container_properties_cache":
            if "_container_properties_cache" in text:
                set_result("retired-python-detail", "Python private cache dictionary emptiness/population is not a Rust "
                           "contract. Cold metadata identity and partition extraction remain supported independently.")
            elif "Container Should" in text or kind == "exception-branch":
                other("Container fixture creation guard, not an item-create assertion.")
            elif kind == "create-call":
                mapped("Public Rust adapter submits one create without Python metadata/cache lookup; fake extension "
                       "test does not establish native cached RID equality or real cold-cache extraction.",
                       assertions("tests\\create_item\\test_create_item_rust_regression_unit.py",
                                  "test_container_identity_is_resolved_by_driver_rust"),
                       partial=True, level="public-boundary-fake-extension",
                       pending=("native-cold-cache-identity",))
            else:
                set_result("unresolved", "Cold create / cached RID and partition-definition identity need exact "
                           "replacement assertions. Fake cold-identity regression and native RID tests are different levels.",
                           pending=("cold-cache-identity-assertion-correspondence",))
        else:
            calls = sorted((n.lineno, getattr(n.func, "attr", "")) for n in ast.walk(function)
                           if isinstance(n, ast.Call) and getattr(n.func, "attr", "") in {
                               "create_item", "upsert_item", "replace_item"
                           })
            previous = [op for line, op in calls if line <= node.lineno]
            if "Container Should" in text or not previous:
                other("Container recreation fixture guard.")
            elif previous[-1] != "create_item":
                other("Upsert/replace recovery branch is outside create; not swept into create Gap22.")
            else:
                set_result("driver-gap", "Gap22: recreate changes Hash or MultiHash definition; original create must "
                           "refresh stale extraction and succeed, then reject old-key input with 400. Existing native "
                           "failure characterization is not passing recovery evidence.",
                           pending=("driver-gap22", "public-recreation-success-and-old-key-rejection"))
    elif "test_cosmos_responses" in path:
        if "create_response" in text or kind == "create-call":
            needle = "lsn" if "int(lsn)" in text else "created.get_response_headers()"
            mapped("Real same-partition prior-write LSN+1 and nonempty create headers, including suppressed response. "
                   "AAD execution remains separate from key-auth native correspondence.",
                   assertions(replacement, "test_create_response_headers_advance_lsn_rust", needle),
                   pending=("public-native-run", "aad-environment"))
        else:
            other("Read/upsert/replace/batch response headers and LSN are independent operations.")
    elif "test_backwards_compatibility" in path:
        if kind == "create-call" or text == "assert item is not None":
            set_result("documented-api-change-unapproved",
                       "Original create accepted irrelevant etag/match_condition, including None. V5 rejects these "
                       "before metadata; documented API-review proposal, not accepted same-behavior parity.",
                       assertions("tests\\create_item\\test_create_item_contract_unit.py",
                                  "test_retired_options_are_rejected_before_metadata_rust"),
                       "public-boundary-fake-extension", ("api-review-approval",))
            row["approval"] = "not-recorded"
            row["policy_ids"] = ["create-inapplicable-options"]
        else:
            other("Control-plane/upsert/batch etag compatibility is not the create contract.")
    elif "test_query_response_headers" in path:
        create = next(n for n in ast.walk(function) if isinstance(n, ast.Call)
                      and getattr(n.func, "attr", "") == "create_item")
        read = next(n for n in ast.walk(function) if isinstance(n, ast.Call)
                    and getattr(n.func, "attr", "") == "read_item")
        if create.lineno <= node.lineno < read.lineno:
            file = "test_query_response_headers_async.py" if asynchronous else "test_query_response_headers.py"
            target = f"tests\\response_hook\\{surface}\\{file}"
            symbol2 = next(key for key in functions(target)[1]
                           if "test_response_hook_parity_point_ops" in key and key.endswith("_rust"))
            refs = assertions(target, symbol2)
            refs = [ref for ref in refs if ref["line"] < min(
                n.lineno for n in ast.walk(functions(target)[1][symbol2]) if isinstance(n, ast.Call)
                and getattr(n.func, "attr", "") == "read_item")]
            mapped("Create hook called once and callback request-charge equals returned header; read/replace/upsert/"
                   "delete assertions are separately excluded.", refs)
        else:
            other("Read/replace/upsert/delete hook observation, not create.")
    elif "test_crud" in path:
        first_query = min(n.lineno for n in ast.walk(function) if isinstance(n, ast.Call)
                          and getattr(n.func, "attr", "") == "query_items")
        if node.lineno < first_query:
            symbol2 = "_document_crud_create_persistence"
            suppressed_composite = "response_payload_on_write_disabled" in path
            if suppressed_composite and "assertIsNone(headerEnvelope.headers)" in text:
                other("Before-create callback envelope initialization, not missing native create coverage.")
            elif suppressed_composite and "assertIsNotNone(headerEnvelope.headers)" in text:
                mapped("Suppressed create invokes its hook and retains response headers at the fake native boundary. "
                       "This alone does not establish callback etag equality with the real stored item.",
                       assertions("tests\\create_item\\test_create_item_contract_unit.py",
                                  "test_falsey_hook_gets_independent_body_and_headers_rust", "len(calls)"),
                       partial=True, level="public-boundary-fake-extension",
                       pending=("suppressed-native-hook-headers",))
            elif suppressed_composite and not asynchronous and name == "test_document_crud" and (
                    "headerEnvelope" in text or "expectedEtag" in text):
                set_result("unresolved", "Original suppressed create invokes capture_response_headers, whose etag must "
                           "equal the independently read stored item's _etag. Header presence and generic hook charge "
                           "equality do not establish this combined native persistence/version assertion.",
                           pending=("suppressed-create-callback-etag-equals-stored-etag",))
                row["helper_sources"] = [reference(path, "CosmosResponseHeaderEnvelope.capture_response_headers")]
            elif suppressed_composite and asynchronous and "before_create_documents_count" in text:
                mapped("Original async suppression composite persists FOUR creates: generated with response, explicit "
                       "ID using implicit client suppression, explicit suppression, explicit response override. Current "
                       "replacement persists THREE with explicit no_response values; exact original default/override "
                       "four-write sequence remains unmapped.",
                       assertions("tests\\create_item\\_contract_cases.py", "assert_stored_sequence"),
                       partial=True, pending=("exact-four-write-implicit-and-explicit-suppression-sequence",))
            elif suppressed_composite and ("self.assertDictEqual(created_document, {})" in text or kind == "create-call"):
                mapped("Suppression and response override exist in the three-write replacement, but this original "
                       "branch includes client-default suppression of an explicit-ID write; exact sequence/persistence "
                       "correspondence remains partial, not native parity.",
                       assertions(replacement, symbol2, "no_response=True"), partial=True,
                       pending=("exact-suppression-branch-and-persistence",))
            elif suppressed_composite and "created_document is not {}" in text:
                mapped("Original identity comparison against a fresh {} is vacuous. Replacement field assertions "
                       "strengthen the intended nonempty-body contract; do not preserve the vacuous predicate.",
                       assertions(replacement, symbol2, "assert_fields"))
            elif "CONFLICT" in text:
                mapped("Explicit-ID duplicate raises 409; no extra stored item after duplicate.",
                       assertions(replacement, symbol2, "caught.value.status_code"))
                helper = next(key for key in names if "__assert" in key.lower())
                row["helper_sources"] = [reference(path, helper)]
            elif "before_create_documents_count" in text:
                mapped("Fresh-container stored-ID/field/count sequence proves one item per successful create. "
                       "Original count can be one/two/three creates; replacement uses three explicit modes. "
                       "Read-all paging itself is not claimed equivalent.",
                       assertions("tests\\create_item\\_contract_cases.py", "assert_stored_sequence"),
                       partial=asynchronous or suppressed_composite)
            elif "no_response" in text:
                mapped("Suppressed auto-ID create returns empty mapping and remains part of stored three-item sequence.",
                       assertions(replacement, symbol2, "no_response=True"))
            else:
                mapped("Generated and explicit IDs preserve original customer fields, with real create observation. "
                       "Per-call assertions and shared field helper are both pinned.",
                       assertions(replacement, symbol2, "assert_fields") +
                       assertions("tests\\create_item\\_input_variants.py", "assert_fields"))
        else:
            other("Query functionality, conditional replace, read-after-replace and delete assertions are not create.")
    elif "test_fault_injection_transport" in path:
        row["helper_sources"] = [
            reference("tests\\_fault_injection_transport.py", "FaultInjectionTransport.send"),
            reference("tests\\_fault_injection_transport.py", "FaultInjectionTransport.error_after_delay"),
        ]
        if "throws_injected" in name:
            mapped("Original helper injects 502 before send after ten seconds. Replacement pins failure type/status/"
                   "delay/hits and storage absence with no-injection control. Not a committed lost-response scenario.",
                   assertions("tests\\fault_injection\\_delayed_create.py", "assert_failure"))
        elif node.lineno < min(n.lineno for n in ast.walk(function) if isinstance(n, ast.Call)
                               and getattr(n.func, "attr", "") == "read_item"):
            row["helper_sources"].append(reference(
                "tests\\_fault_injection_transport.py", "FaultInjectionTransport.transform_topology_swr_mrr"
            ))
            mapped("Simulated single-writer topology: create destination is write region, with real native diagnostics/"
                   "storage. Emulator aliases are not deployed multi-region service verification.",
                   assertions("tests\\fault_injection\\_regional_routing.py", "assert_destination"),
                   pending=("installed-native-emulator-run", "deployed-multi-region-environment"))
        else:
            other("Two-second preferred-region read loop is a read-routing assertion.")
    elif "test_retryable_writes" in path:
        helper = symbol.split(".")[0] + ".MockExecuteFunction.__call__"
        row["helper_sources"] = [reference(path, helper)]
        if "client_level" in name:
            row["helper_sources"].append(reference(
                path, symbol.split(".")[0] + ".MockExecuteServiceResponseException.__call__"
            ))
        calls = sorted((n.lineno, getattr(n.func, "attr", "")) for n in ast.walk(function)
                       if isinstance(n, ast.Call) and getattr(n.func, "attr", "") in {
                           "create_item", "upsert_item", "patch_item", "delete_item", "replace_item", "read_item"
                       })
        previous = [op for line, op in calls if line <= node.lineno]
        if kind == "create-call" and "test_item_replace" in text:
            other("Create seeds the later replace retry scenario.")
        elif "read_item_create" in text:
            set_result("unresolved", "Original mock fails first attempt with 408 BEFORE forwarding, then retry writes "
                       "successfully; this read-back proves create persistence after recovery. Accepted retry_write knob "
                       "exclusion does not replace this supported native outcome; not a lost committed response.",
                       pending=("native-transient-408-create-recovery-and-readback",))
        elif "retry_write=2" in text and kind == "create-call":
            set_result("accepted-exclusion", "Pushback13: per-call non-None retry_write unsupported; Rust owns automatic "
                       "write retries. The later create persistence assertion is retained separately as unresolved.")
            row["policy_ids"] = ["pushback13"]
        elif kind == "create-call":
            set_result("unresolved", "Create branch requires distinguishing fixture writes, default automatic retries "
                       "and injected transport failure. Client/request policy counters are not native evidence.",
                       pending=("native-create-retry-scenario",))
        elif previous and previous[-1] not in {"create_item", "read_item"}:
            other("Failure/counter belongs to upsert/patch/delete/replace, not create.")
        elif "me.counter" in text or "mf.counter" in text:
            set_result("retired-python-detail", "Legacy ExecuteFunction mock attempt counter, not native retry parity. "
                       "Supported create failure/recovery/persistence remains separately unresolved.")
        elif "Exception was not raised" in text:
            set_result("unresolved", "Client-level ServiceResponseError failure sentinel still needs native outcome mapping; "
                       "source mock always throws without forwarding to storage.")
        elif "read_item" in text or "patched_item" in text or "replaced_item" in text:
            other("Upsert/patch/delete/replace result, not the create recovery result.")
        elif kind == "exception-branch" or "Expected an exception without retry_write" in text:
            set_result("unresolved", "Mixed-operation failure branch retained explicitly; do not blanket-retire supported "
                       "create outcomes because retry_write knobs/Python policies are excluded.")
    elif "test_availability_strategy" in path:
        helpers = [helper for helper in ("_perform_write_operation", "_validate_response_uris") if helper != symbol]
        row["helper_sources"] = [reference(path, helper) for helper in helpers]
        if name in {"test_custom_thread_pool_executor", "test_max_concurrency",
                    "test_per_request_none_falls_back_to_client_strategy"}:
            other("Create is only the seed for a READ hedging/executor scenario; not a create-policy gap.")
        elif symbol == "_validate_response_uris":
            if kind.startswith("assertion"):
                set_result("unresolved", "Exact destination set and no-excluded-region assertions are supported routing "
                           "requirements. Python log parser retires, but these cannot be blanket-excluded with hedging. "
                           "Need per-scenario native attempts and deployed topology verification.",
                           pending=("native-per-scenario-route-set", "deployed-multi-region-environment"))
            else:
                set_result("retired-python-detail", "Python logging-message parser/filter branch; native attempt diagnostics "
                           "replace this mechanism, not the separate destination-set assertions.")
        elif symbol == "_perform_write_operation":
            if kind == "if-branch" and any(op in text for op in ("UPSERT", "REPLACE", "DELETE", "PATCH", "BATCH")):
                other("Non-create operation branch in shared write dispatcher.")
            elif "availability_strategy" in text:
                set_result("accepted-exclusion", "Pushback14 excludes write hedging/progressive read hedging, not normal "
                           "create routing or excluded-location enforcement.")
                row["policy_ids"] = ["pushback14"]
            else:
                set_result("unresolved", "CREATE dispatcher combines supported excluded_locations routing with excluded "
                           "non-None retry_write/write hedging. Split policy exclusion from native write outcome.",
                           pending=("native-per-scenario-create-outcome",))
        elif kind == "create-call":
            other("Direct create seeds the operation matrix; actual CREATE-under-test occurs inside _perform_write_operation.")
        elif kind == "if-branch":
            other("Read/write dispatch: only operation=CREATE is in this create audit; other operation cases are not gaps.")
        elif kind == "helper-call" and "_perform_read_operation" in text:
            other("Read-operation matrix branch; the separately recorded write helper carries the CREATE scenario.")
        elif kind == "helper-call":
            set_result("unresolved", "Actual CREATE-under-test is reached through the shared write helper. "
                       "Record exact call/strategy/exclusion arguments; write-hedging exclusion does not dispose "
                       "of supported create success, regional exclusions or final error propagation.",
                       pending=("native-per-scenario-create-outcome-and-route-set",))
        elif "status_code" in text or "raises" in text:
            set_result("unresolved", "Error selection after hedging is excluded (Pushback14), but supported 400/nontransient "
                       "create propagation and excluded-region enforcement require separate native assertions. "
                       "No blanket availability-suite exclusion.", pending=("split-hedging-from-supported-error-outcome",))
    elif "test_session" in path:
        helper_names = ["assert_no_session_token", "assert_session_token"]
        row["helper_sources"] = [reference("tests\\test_config.py", helper) for helper in helper_names]
        create = next(n for n in ast.walk(function) if isinstance(n, ast.Call)
                      and getattr(n.func, "attr", "") == "create_item")
        read = next(n for n in ast.walk(function) if isinstance(n, ast.Call)
                    and getattr(n.func, "attr", "") == "read_item")
        if create.lineno <= node.lineno < read.lineno or "response_session_token" in text and "batch" not in text:
            set_result("unresolved", "Create cached-session policy is supported for single/multi-write topology. "
                       "Native cached/explicit policy tests exist, but exact original request-token presence and "
                       "subsequent read-token equality have not been assertion-mapped here. Explicit-token legacy "
                       "suppression is not automatically equivalent.",
                       pending=("native-session-assertion-map", "multi-region-public-environment"))
        else:
            other("Control-plane/upsert/replace/read/batch/delete session observation outside the create boundary.")
    elif "test_user_configs" in path:
        if "assertNotEqual(session_token, session_token2)" in text or kind == "create-call":
            set_result("unresolved", "Without explicitly requesting Session, successive creates must return updated "
                       "distinct session tokens. Generic explicit-token or cached-policy tests do not assert this "
                       "account-default inheritance sequence.", pending=("native-default-account-session-sequence",))
        elif "session_token2, read_session_token" in text:
            set_result("unresolved", "Read after second create retains its session token under account-default Session. "
                       "Retain as create-session persistence verification, not arbitrary read functionality.",
                       pending=("native-default-account-session-sequence",))
        else:
            other("Account configuration prerequisite or Eventual/Strong read override; no create-policy parity claim.")
    contexts = set()
    for replacement_ref in row["replacements"]:
        contexts.add((replacement_ref["path"], replacement_ref["symbol"]))
    if row["execution_level"] == "public-installed-native" and (
            "test_crud" in path or "test_cosmos_responses" in path):
        if "test_cosmos_responses" in path:
            test = "test_create_response_headers_advance_lsn_rust"
        elif "response_payload_on_write_disabled" not in path:
            test = "test_document_crud_create_persistence_rust"
        elif "enabled_via_override" in name:
            test = "test_document_crud_response_payload_enabled_via_override_rust"
        else:
            test = "test_document_crud_response_payload_on_write_disabled_rust"
        contexts.add((replacement, test))
        contexts.add((replacement, "_contract_client_fixture"))
        contexts.add(("tests\\create_item\\_input_variants.py", "observe_native_create"))
    if row["replacements"] and "test_fault_injection_transport" in path:
        if "throws_injected" in name:
            target = "tests\\fault_injection\\sync\\test_delayed_create_fault.py"
            contexts.add((target, "test_throws_injected_error_rust"))
            contexts.add(("tests\\fault_injection\\_delayed_create.py", "create_rule"))
        else:
            target = "tests\\fault_injection\\sync\\test_regional_routing_fault.py"
            contexts.add((target, "test_swr_mrr_succeeds_rust"))
            contexts.add(("tests\\fault_injection\\_regional_routing.py", "capture_native"))
            contexts.add(("tests\\fault_injection\\_regional_routing.py", "topology"))
        contexts.add(("tests\\fault_injection\\_delayed_create.py", "assert_route"))
    row["replacement_context"] = [reference(file, function_name) for file, function_name in sorted(contexts)]
    return row


def annotation_audit(scope, rows):
    """Keep annotation preservation distinct from assertion correspondence."""
    infrastructure = {
        "tests\\create_item\\_input_variants.py": [
            "_variant_database_fixture", "_make_variant_container_fixture", "observe_native_create",
        ],
        "tests\\read_item\\test_read_item_contract_unit.py": ["point_read"],
        "tests\\create_item\\test_create_item_contract_unit.py": ["point_create"],
        "tests\\create_item\\test_create_item_rust_regression_unit.py": ["rust_create"],
        "tests\\config\\collection.py": ["exclude_module", "exclude_parameters"],
        "tests\\conftest.py": [
            "pytest_ignore_collect", "pytest_pycollect_makemodule", "pytest_pycollect_makeitem",
            "pytest_collection_modifyitems", "pytest_collection_finish",
        ],
        "tests\\fault_injection\\conftest.py": ["regional_target"],
        "tests\\config\\fault_resources.py": ["owned_target"],
        "tests\\fault_injection\\_regional_routing.py": ["emulator_endpoints"],
        "tests\\config\\clients.py": ["create_data_client", "create_data_client_async", "create_fault_setup_client"],
        "tests\\test_availability_strategy.py": ["TestAvailabilityStrategy.setup_class"],
        "tests\\test_availability_strategy_async.py": ["setup"],
    }
    infrastructure_refs = [
        reference(path, symbol) for path, symbols in infrastructure.items() for symbol in symbols
    ]
    pairs = {(entry["source"]["path"], entry["source"]["symbol"]) for entry in scope}
    pairs.update((ref["path"], ref["symbol"]) for row in rows for ref in row["replacement_context"])
    pairs.update((ref["path"], ref["symbol"]) for ref in infrastructure_refs)
    contexts = {
        pair: GUARD_MODULE._annotation_context(*pair)  # pylint: disable=protected-access
        for pair in sorted(pairs)
    }

    def marks(context):
        return (context["module_marks"] + context["function_decorators"]
                + [mark for cls in context["classes"] for mark in cls["decorators"] + cls["marks"]])

    reviews = []
    for entry in scope:
        source = entry["source"]
        if not source["symbol"].split(".")[-1].startswith("test_"):
            continue
        pair = source["path"], source["symbol"]
        targets = {
            (ref["path"], ref["symbol"])
            for row in rows if (row["source"]["path"], row["source"]["symbol"]) == pair
            for ref in row["replacement_context"] if ref["symbol"].split(".")[-1].startswith("test_")
        }
        replacement_marks = [mark for target in sorted(targets) for mark in marks(contexts[target])]
        review = {
            "source": source,
            "replacement_tests": [reference(*target) for target in sorted(targets)],
            "annotations": [],
            "scope_note": "Source/replacement selection and vectors are audited statically; no native run is implied.",
        }
        for mark in marks(contexts[pair]):
            snippet = mark["snippet"]
            token = ast.unparse(ast.parse(snippet).body[0])
            matching = [
                candidate for candidate in replacement_marks
                if candidate["snippet"] == snippet
                or token.startswith("pytest.mark.") and "(" not in token
                and token in candidate["snippet"]
            ]
            status = "preserved" if matching else "unresolved-no-equivalent-replacement"
            reason = "Matching effective replacement mark is present." if matching else (
                "No assertion-equivalent replacement test has been established; do not claim its gates/vectors migrated."
            )
            if "test_fault_injection_transport" in source["path"] and mark["kind"] == "module-pytestmark":
                status = "intentional-legacy-skip-omission"
                reason = "Blanket skip retires only the Python injection suite. Copying it would disable genuine Rust tests."
            elif "test_default_retry_policy_for_query" in source["symbol"]:
                status = "other-api-not-carried"
                reason = "Skipped legacy query retry case only uses create as setup; not a create replacement obligation."
            elif targets and not matching:
                only_units = all(path.endswith("_unit.py") for path, _ in targets)
                if only_units:
                    status = "intentional-offline-replacement-level"
                    reason = "Live/emulator selection marks do not apply to fake/helper unit tests; those tests do not "
                    reason += "satisfy the original live execution gate or native assertion obligation."
                elif "cosmosAAD" in snippet:
                    status = "missing-live-aad-selection"
                    reason = "Original inherited AAD lane marker is absent. No approval or equivalent lane-selection "
                    reason += "rule was established. Runtime AAD capability must be examined separately."
                elif any(value in snippet for value in ("cosmosLong", "cosmosCircuitBreaker", "cosmosQuery")):
                    status = "changed-live-lane-needs-review"
                    reason = "Live/topology category is absent from the replacement. Extracting a create-only case "
                    reason += "may justify changing a composite suite category, but automatic preservation is unproved."
                elif "pytest.mark.unittest" in snippet:
                    status = "changed-runner-category"
                    reason = "Rust fault tests are ordinary pytest functions; legacy unittest category was not copied. "
                    reason += "Emulator selection is retained and explicit timeout/control vectors were added."
            review["annotations"].append({
                "source": mark, "disposition": status, "rationale": reason, "replacements": matching,
            })
        if any("IsolatedAsyncioTestCase" in base for cls in contexts[pair]["classes"] for base in cls["bases"]):
            review["async_runner"] = {
                "original": "unittest.IsolatedAsyncioTestCase",
                "replacement": [
                    {"path": path, "symbol": symbol, "classes": contexts[path, symbol]["classes"],
                     "module_marks": contexts[path, symbol]["module_marks"]}
                    for path, symbol in sorted(targets)
                ],
                "disposition": "inspect-effective-runner-not-function-marker-alone",
            }
        reviews.append(review)
    values = []
    for path, names in {
        "tests\\fault_injection\\_regional_routing.py": ["REGIONAL_ROUTING_CASES"],
        "tests\\config\\collection.py": ["ADAPTER_PARAMETER_MODULES"],
    }.items():
        text = functions(path)[0]
        tree = ast.parse(text)
        for name in names:
            node = next(node for node in tree.body if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == name for target in node.targets))
            values.append(GUARD_MODULE._reference(path, name, "annotation-value", node, text))  # pylint: disable=protected-access
    return {
        "all_applicable_annotations_preserved": False,
        "method": "Read effective function, enclosing-class and module marks, parameter values, fixture signatures/"
                  "decorators, lifecycle hooks, conftest ancestry and explicit infrastructure predicates. "
                  "Snapshots detect drift; they are not proof that missing annotations are approved.",
        "contexts": list(contexts.values()),
        "infrastructure_functions": infrastructure_refs,
        "infrastructure_values": values,
        "configuration_files": [
            {"path": "pytest.ini", "sha256": hashlib.sha256((ROOT / "pytest.ini").read_bytes()).hexdigest()}
        ],
        "reviews": reviews,
        "findings": [
            {
                "id": "AN-01",
                "status": "restored-selection-and-configured-auth-wiring",
                "finding": "Original headers and Cosmos response classes inherit cosmosAADLong. New typed bucket "
                           "copies and relevant legacy-contract functions now preserve it. Data operations use "
                           "existing configured key/AAD factories; provisioning and cleanup remain key-owned. "
                           "Marker/factory restoration alone is not evidence of live token-authenticated success.",
                "source_paths": ["tests\\test_headers.py", "tests\\test_headers_async.py",
                                 "tests\\test_cosmos_responses.py", "tests\\test_cosmos_responses_async.py"],
                "replacement_paths": ["tests\\create_item\\sync\\test_headers.py",
                                      "tests\\create_item\\aio\\test_headers.py",
                                      "tests\\create_item\\sync\\test_contracts.py",
                                      "tests\\create_item\\aio\\test_contracts.py"],
            },
            {
                "id": "AN-02",
                "status": "repaired-live-query-and-aad-selection",
                "finding": "Restored inherited cosmosQuery/cosmosAADQuery on both response-hook copy classes. "
                           "Their configured-data-auth factories were already retained. This restores selection, "
                           "not evidence of an executed live AAD lane.",
                "source_paths": ["tests\\test_query_response_headers.py", "tests\\test_query_response_headers_async.py"],
                "replacement_paths": ["tests\\response_hook\\sync\\test_query_response_headers.py",
                                      "tests\\response_hook\\aio\\test_query_response_headers_async.py"],
            },
            {
                "id": "AN-03",
                "status": "restored-by-explicit-user-request",
                "finding": "Composite CRUD originally inherits cosmosLong/cosmosCircuitBreaker/cosmosAADCircuitBreaker; "
                           "suppression composites inherit cosmosLong/cosmosAADLong. New create-only modules use "
                           "cosmosEmulator plus account/binding availability gates. cosmosLong is now restored on "
                           "both persistence tests. Original AADLong, circuit-breaker and AAD-circuit-breaker "
                           "categories are now restored as explicitly requested, without waiting for lane execution.",
            },
            {
                "id": "AN-04",
                "status": "intentional-infrastructure-replacement",
                "finding": "New create legacy-contract modules declare backend=[rust,core-python], but ordinary "
                           "conftest collection excludes core-python via ADAPTER_PARAMETER_MODULES/exclude_parameters. "
                           "--include-legacy-tests or --noconftest changes that selection; it must not be described as "
                           "unconditionally Rust-only. observe_native_create guards Rust against legacy fallback.",
            },
            {
                "id": "AN-05",
                "status": "intentional-legacy-skip-omission",
                "finding": "Original fault module blanket skip is deliberately not copied. Rust fault tests retain "
                           "cosmosEmulator, add timeout(180), injection/no-injection and regional guard controls. "
                           "regional_target rejects non-localhost endpoints before provisioning. No unconditional "
                           "xfail was added by this audit.",
            },
            {
                "id": "AN-06",
                "status": "unresolved-vector-and-topology-correspondence",
                "finding": "Availability classes require multi-region/AAD-multi-region lanes; setup enforces at least "
                           "two distinct regions. Original CREATE branch, three client/request strategy pairs and "
                           "seven nontransient status/substatus vectors are retained in snapshots, not claimed "
                           "migrated. Pushback14 excludes hedging dimensions, not supported create error/routing "
                           "vectors. A simulated emulator routing test is not a deployed multi-region gate replacement.",
            },
            {
                "id": "AN-07",
                "status": "conditional-gate-retained-for-review",
                "finding": "Original session multi-write tests skip only data_auth_mode=aad because localhost "
                           "topology injection is emulator-only. Keep that reason attached to the original scenario; "
                           "do not transplant its skip onto unrelated Rust token/session coverage.",
            },
            {
                "id": "AN-08",
                "status": "explicit-execution-level-and-vector-change",
                "finding": "Boundary tests inherit four sync/async x legacy/Rust cases from point_read fixture params; "
                           "Rust regression module overrides point_read with only two Rust cases. Fake units omit "
                           "live feature gates intentionally, without establishing native execution. Client-default "
                           "suppression gets False/True vectors and LSN gets no_response False/True, but the original "
                           "four-write async suppression sequence is still not replaced by the three-write sequence.",
            },
        ],
        "limitations": [
            "Only offline collection and AST/guard validation were performed; no live execution or CI lane run.",
            "Unambiguous cosmosLong and response-hook query/AAD lane omissions were repaired in migrated copies; "
            "remaining AAD and topology categories were subsequently restored with configured data-auth wiring. "
            "The broader unresolved assertion scope is not a remaining marker mismatch in reviewed actual copies.",
            "Source/replacement annotation contexts are pinned, but unresolved assertion mappings remain unresolved.",
        ],
        "summary": {
            "reviewed_test_functions": len(reviews),
            "annotation_contexts": len(contexts),
            "original_annotation_occurrences": sum(len(review["annotations"]) for review in reviews),
            "dispositions": dict(Counter(
                mark["disposition"] for review in reviews for mark in review["annotations"]
            )),
        },
    }


def create_copy_annotation_audit(rows):
    """Audit actual copied tests separately from unresolved composite assertions."""
    inventory = GUARD_MODULE._create_copy_inventory()  # pylint: disable=protected-access
    pairs = [(item["source"], item["replacement"]) for item in inventory if item["source"]]
    outside = []

    def named(path, leaf):
        found = [symbol for symbol, node in functions(path)[1].items() if node.name == leaf]
        assert len(found) == 1, (path, leaf, found)
        return reference(path, found[0])

    for surface in ("sync", "aio"):
        suffix = "_async" if surface == "aio" else ""
        path = f"tests\\response_hook\\{surface}\\test_query_response_headers{suffix}.py"
        outside.append((named(f"tests\\test_query_response_headers{suffix}.py",
                              f"test_response_hook_parity_point_ops{suffix}"),
                        named(path, f"test_response_hook_parity_point_ops{suffix}_rust")))
        for module, leaf in (("test_delayed_create_fault", "test_throws_injected_error"),
                             ("test_regional_routing_fault", "test_swr_mrr_succeeds")):
            path = f"tests\\fault_injection\\{surface}\\{module}{suffix}.py"
            outside.append((named(f"tests\\test_fault_injection_transport{suffix}.py", leaf + suffix),
                            named(path, leaf + suffix + "_rust")))
    helper_pairs = set()
    for row in rows:
        for target in row["replacement_context"]:
            if target["path"] == "tests\\common\\test_connection_free_items_unit.py" \
                    and target["symbol"].startswith("test_"):
                source = row["source"]
                if source["symbol"].split(".")[-1].startswith("test_"):
                    helper_pairs.add((source["path"], source["symbol"], target["path"], target["symbol"]))
    outside.extend((reference(path, symbol), reference(target_path, target_symbol))
                   for path, symbol, target_path, target_symbol in sorted(helper_pairs))
    pairs.extend(outside)
    pair_keys = {(source["path"], source["symbol"], target["path"], target["symbol"]) for source, target in pairs}
    target_keys = {(target["path"], target["symbol"]) for _, target in pairs}
    secondary = {}
    for row in rows:
        source = row["source"]
        if not source["symbol"].split(".")[-1].startswith("test_"):
            continue
        for target in row["replacement_context"]:
            key = source["path"], source["symbol"], target["path"], target["symbol"]
            if (target["path"], target["symbol"]) in target_keys and key not in pair_keys:
                secondary[key] = "Selected shared/composite assertions only; original sequence is not assumed equivalent."
    pairs.extend((reference(path, symbol), reference(target_path, target_symbol))
                 for path, symbol, target_path, target_symbol in sorted(secondary))
    contexts = {}

    def context(ref):
        key = ref["path"], ref["symbol"]
        if key not in contexts:
            contexts[key] = GUARD_MODULE._annotation_context(*key)  # pylint: disable=protected-access
        return contexts[key]

    def marks(value):
        return value["module_marks"] + value["function_decorators"] + [
            mark for cls in value["classes"] for mark in cls["decorators"] + cls["marks"]
        ]

    for item in inventory:
        context(item["replacement"])
    reviews = []
    for source, target in pairs:
        source_marks, target_marks = marks(context(source)), marks(context(target))
        annotations = []
        for mark in source_marks:
            snippet = mark["snippet"]
            token = ast.unparse(ast.parse(snippet).body[0])
            matching = [
                candidate for candidate in target_marks if candidate["snippet"] == snippet
                or token.startswith("pytest.mark.") and "(" not in token and token in candidate["snippet"]
            ]
            status, reason = "preserved", "Matching effective module/class/function selection is retained."
            if matching:
                pass
            elif target["path"].endswith("_unit.py"):
                status, reason = "intentional-offline-replacement-level", (
                    "Fake helper coverage intentionally omits live gates; it does not discharge native/live execution."
                )
            elif "test_fault_injection_transport" in source["path"] and mark["kind"] == "module-pytestmark":
                status, reason = "intentional-legacy-skip-omission", (
                    "Retired Python fault-suite blanket skip would disable the genuine Rust replacement."
                )
            elif "_skip" in snippet and "test_aad" in source["path"]:
                status, reason = "intentional-token-gate-broadening", (
                    "Emulator-only credential skip is replaced by localhost-or-complete-real-AAD-credentials gate; "
                    "the replacement supports both emulator and real token credentials."
                )
            elif "parametrize" in snippet and "test_excluded_locations" in source["path"]:
                status, reason = "preserved-twelve-write-vectors-changed-region-binding", (
                    "All twelve logical client/request exclusion and expected write destinations match in the "
                    "offline vector guard. Composite read expectations are not create obligations. Original "
                    "account-discovered region names become explicit legacy-location environment configuration; "
                    "actual topology validates preferred regions and determines single versus multi-write routing."
                )
            elif "usefixtures" in snippet and "test_excluded_locations" in source["path"]:
                status, reason = "intentional-isolated-resource-fixture", (
                    "Legacy shared-seed/logging/replication fixture is unnecessary: copy creates a uniquely named "
                    "item and owns/closes its client per invocation; do not restore legacy Python fixture."
                )
            elif "asyncio" in snippet and "loop_scope" in snippet:
                status, reason = "intentional-function-scoped-async-runner", (
                    "Class-scoped legacy fixture/client loop becomes per-invocation asyncio and owned client."
                )
            elif "pytest.mark.asyncio" in snippet and target["path"].endswith("test_regional_routing_fault_async.py"):
                status, reason = "intentional-asyncio-run-wrapper", (
                    "The replacement is a synchronous pytest function owning asyncio.run(run()); adding an "
                    "asyncio marker would incorrectly annotate a synchronous wrapper."
                )
            elif "cosmosAAD" in snippet:
                status, reason = "missing-live-aad-selection-and-credential-fixture", (
                    "Required source AAD selection is absent. Restore the explicitly authorized category; "
                    "credential wiring and actual token-authenticated execution are separate obligations."
                )
            elif "cosmosCircuitBreaker" in snippet:
                status, reason = "changed-topology-category-needs-review", (
                    "Required source topology category is absent despite explicit authorization to retain it. "
                    "Restoring selection does not establish deployed multi-region execution."
                )
            elif "unittest" in snippet:
                status, reason = "intentional-pytest-runner-replacement", (
                    "Ordinary pytest functions replace legacy unittest-style fault cases; effective async runner "
                    "and explicit timeout are retained separately."
                )
            else:
                status, reason = "unresolved-annotation-difference", "No equivalence or approved omission established."
            annotations.append({"source": mark, "disposition": status, "rationale": reason, "replacements": matching})
        reviews.append({
            "source": source, "replacement": target,
            "lineage_scope": secondary.get(
                (source["path"], source["symbol"], target["path"], target["symbol"]),
                "Primary Source-comment or explicit external create replacement; not whole-function assertion equivalence.",
            ),
            "disposition": "annotation-review-with-explicit-differences",
            "annotations": annotations,
            "replacement_effective_annotations": target_marks,
            "execution_level": "offline-fake-helper" if target["path"].endswith("_unit.py") else
                               "statically-reviewed-live-test; targeted-case execution is recorded separately",
            "fixture_review": (
                "Original class lifecycle, module fixtures, imported gate aliases, parameter decorators and "
                "replacement fixture/lifecycle snapshots are retained in contexts. Rust availability/resource "
                "ownership fixtures intentionally replace Python client fixtures. Backend parameterization is "
                "filtered by normal root conftest; --noconftest/--include-legacy-tests changes this selection."
            ),
        })
    infrastructure = {
        "tests\\test_excluded_locations.py": [
            "get_test_data_with_expected_output", "write_item_test_data", "read_and_write_item_test_data",
        ],
        "tests\\create_item\\_routing.py": ["expected_write_region"],
        "tests\\auth\\_token_credentials.py": [
            "token_lane_enabled", "skip_unless_token_auth", "make_sync_token_credential", "make_async_token_credential",
            "have_real_aad", "_is_emulator_host",
        ],
        "tests\\create_item\\_input_variants.py": [
            "_variant_database_fixture", "_make_variant_container_fixture", "observe_native_create",
        ],
        "tests\\config\\clients.py": [
            "_credential", "_aad_credential", "create_data_client", "create_data_client_async",
            "create_data_client_for_endpoint", "create_data_client_async_for_endpoint",
        ],
    }
    refs = [reference(path, symbol) for path, symbols in infrastructure.items() for symbol in symbols]
    for ref in refs:
        context(ref)
    vectors = []
    for path, names in {
        "tests\\test_excluded_locations.py": ["CLIENT_ONLY_TEST_DATA", "CLIENT_AND_REQUEST_TEST_DATA", "L0", "L1", "L2", "L3"],
        "tests\\create_item\\_routing.py": [
            "CREATE_ITEM_TEST_DATA", "WRITE_LOCATION", "READ_LOCATION", "THIRD_LOCATION", "DEFAULT_LOCATION",
        ],
        "tests\\create_item\\_contract_cases.py": ["INVALID_IDS", "INCOMPLETE_KEYS", "EMOJI_CASES"],
        "tests\\create_item\\_input_variants.py": [
            "CASES", "RESPONSE_MODES", "ENCODING_CASES", "UNICODE_KEY", "UNICODE_CONTENT",
        ],
        "tests\\auth\\_token_credentials.py": ["_AAD_ENV"],
    }.items():
        text, _ = functions(path)
        for name in names:
            node = next(node for node in ast.parse(text).body if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == name for target in node.targets))
            vectors.append(GUARD_MODULE._reference(path, name, "annotation-value", node, text))  # pylint: disable=protected-access
    adaptations = {
        "intentional-offline-replacement-level", "intentional-legacy-skip-omission",
        "intentional-token-gate-broadening", "preserved-twelve-write-vectors-changed-region-binding",
        "intentional-isolated-resource-fixture", "intentional-function-scoped-async-runner",
        "intentional-asyncio-run-wrapper", "intentional-pytest-runner-replacement",
    }
    mismatches = [
        mark for review in reviews for mark in review["annotations"]
        if mark["disposition"] != "preserved" and mark["disposition"] not in adaptations
    ]
    return {
        "all_applicable_annotations_preserved": not mismatches,
        "applicable_marker_mismatch_count": len(mismatches),
        "all_original_annotations_copied_literally": False,
        "scope": "Every test function in tests/create_item except this audit's own guard and concurrently owned "
                 "test_service_failures.py is inventoried. All direct Source-comment copies plus explicitly named "
                 "external create replacements receive lineage reviews, together with the original scalar/HPK/"
                 "Unicode/emoji/noncompact-CJK parameter sources and mapped suppression composites. Tests without "
                 "source lineage are not claimed copied. Secondary assertion equivalence remains separate.",
        "inventory": inventory,
        "lineage_reviews": reviews,
        "contexts": list(contexts.values()),
        "infrastructure_functions": refs,
        "vector_sources": vectors,
        "vector_files": [{
            "path": "tests\\create_item\\partition_key_reference_cases.json",
            "sha256": hashlib.sha256((ROOT / "tests" / "create_item" / "partition_key_reference_cases.json").read_bytes()).hexdigest(),
        }],
        "remaining_differences": [
            "Marker preservation is verified independently of live credential availability and service execution.",
            "Configured data factories retain the repository's existing emulator/key/AAD selection policy; "
            "on remote accounts an AAD-lane credential failure must not fall back to account-key data operations.",
            "Exclusion vector shape is exact, but region names move from account discovery to configured legacy "
            "region variables; native topology behavior and deployed multi-region execution are separate.",
            "Primary Source-comment lineage does not imply all secondary scalar/HPK/shared-policy assertions "
            "or every original composite sequence is replaced, even where secondary annotations are reviewed. "
            "Four-write async suppression remains distinct "
            "from the three-write replacement despite expanded suppression parameterization.",
        ],
        "parameter_review": [
            "Excluded-location copies preserve all twelve logical write-routing vectors; a guard compares "
            "original input/output provider AST values directly, without importing live legacy modules.",
            "Invalid-ID cases preserve the exact union of sync/async originals (11 unique values), including "
            "their distinct oversized values; a guard compares literal expressions.",
            "PK variants pin all 15 JSON cases and four response modes; their semantic assertion correspondence "
            "is separate from decorator preservation. Six scalar bodies are compared against all four original "
            "sync/async normal/suppressed functions. Unicode and emoji/query values are compared to both original "
            "surfaces. Added suppression/compact/backend cross-products are extensions, not lost vectors.",
            "Fault copies replace retired injection implementation with inject False/True and regional guard "
            "controls. Async regional wrapper is synchronous asyncio.run and must not receive pytest.asyncio.",
            "AAD compact/token copies intentionally broaden the original localhost-only credential gate to "
            "real configured AAD. Copying the original emulator-only skip would remove supported coverage.",
        ],
        "summary": {
            "inventoried_create_item_test_functions": len(inventory),
            "inventory_classifications": dict(Counter(item["classification"] for item in inventory)),
            "direct_source_copy_functions": sum(bool(item["source"]) for item in inventory),
            "external_replacement_functions": len({(target["path"], target["symbol"]) for _, target in outside}),
            "source_replacement_pairs": len(reviews),
            "secondary_parameter_or_composite_pairs": len(secondary),
            "unique_original_functions": len({(source["path"], source["symbol"]) for source, _ in pairs}),
            "annotation_contexts": len(contexts),
            "original_annotation_occurrences": sum(len(review["annotations"]) for review in reviews),
            "annotation_dispositions": dict(Counter(
                mark["disposition"] for review in reviews for mark in review["annotations"]
            )),
        },
    }


def build(discovery=None, reviewed_annotation_refresh=False):
    ledger_path = GUARD.with_name("assertion_correspondence.json")
    if discovery:
        candidates = [
            (entry["file"], entry["name"])
            for entry in json.loads(Path(discovery).read_text(encoding="utf-8"))["legacy"]
        ]
    else:
        candidates = [(entry["source"]["path"], entry["source"]["symbol"])
                      for entry in json.loads(ledger_path.read_text(encoding="utf-8"))["candidate_inventory"]]
    selected = select()
    if ledger_path.exists() and not discovery:
        prior = json.loads(ledger_path.read_text(encoding="utf-8"))
        for reviewed in prior["reviewed_functions"]:
            original = reviewed["source"]
            current = reference(original["path"], original["symbol"])
            if current["ast_sha256"] != original["ast_sha256"]:
                raise ValueError(f"Review changed source and its disposition rules before regeneration: "
                                 f"{original['path']}::{original['symbol']}")
        for reviewed in prior.get("create_copy_annotation_audit", {}).get("lineage_reviews", []):
            original = reviewed["source"]
            if reference(original["path"], original["symbol"])["ast_sha256"] != original["ast_sha256"]:
                raise ValueError(f"Review changed copy source before regeneration: "
                                 f"{original['path']}::{original['symbol']}")
        for section in ("annotation_audit", "create_copy_annotation_audit"):
            for context in prior.get(section, {}).get("contexts", []):
                # A deleted file or function is a changed snapshot, not a crash.
                try:
                    current = GUARD_MODULE._annotation_context(context["path"], context["symbol"])  # pylint: disable=protected-access
                except (FileNotFoundError, KeyError):
                    current = None
                if current != context and not reviewed_annotation_refresh:
                    raise ValueError(f"Review changed inherited annotations, fixture vectors or infrastructure before "
                                     f"regeneration: {context['path']}::{context['symbol']}")
    rows = []
    scope = []
    for (path, symbol), family in sorted(selected.items()):
        text, names = functions(path)
        scope.append({"source": reference(path, symbol), "family": family})
        observations = sorted(GUARD_MODULE._observations(names[symbol]),  # pylint: disable=protected-access
                              key=lambda pair: (pair[1].lineno, pair[1].col_offset, pair[0]))
        for kind, node in observations:
            row = disposition(path, symbol, kind, node)
            row.update(
                id=f"SC-{len(rows) + 1:04d}",
                source=GUARD_MODULE._reference(path, symbol, kind, node, text),  # pylint: disable=protected-access
            )
            rows.append(row)
    inventory = []
    removed = []
    for path, symbol in sorted(set(candidates)):
        if not ROOT.joinpath(*path.split("\\")).exists() or symbol not in functions(path)[1]:
            removed.append({"path": path, "symbol": symbol, "disposition": "historical-source-no-longer-present"})
            continue
        inventory.append({
            "source": reference(path, symbol),
            "review": "reviewed" if (path, symbol) in selected else "unresolved-not-reviewed",
        })
    # Helpers are deliberately added to scope; discovery had omitted their assertions.
    present = {(entry["source"]["path"], entry["source"]["symbol"]) for entry in inventory}
    for path, symbol in sorted(set(selected) - present):
        inventory.append({"source": reference(path, symbol), "review": "reviewed"})
    ledger = {
        "schema_version": 1,
        "purpose": "Assertion/branch correspondence, not test-name matching or an execution report.",
        "verification": {
            "kind": "static-correspondence-with-separately-recorded-targeted-execution",
            "native_executed_by_this_audit": True,
            "note": "All replacements denote available assertion locations, never a passing run. Only backend=rust "
                    "with native observation/no fallback qualifies as installed-native execution. Helper/fake tests do not.",
        },
        "reported_execution": {
            "reported_at": "2026-11-05T00:14:25.952-06:00",
            "provenance": "Parent-agent report; not independently rerun or source-reviewed by this audit.",
            "mapping_effect": "Context only: does not discharge unresolved assertion correspondence.",
            "public_installed_native": {
                "suite": "tests\\create_item\\test_service_failures.py",
                "passed_cases": 9,
                "final_public_result": "9 passed; 2 normal indexing failures; no unconditional xfails.",
                "scope": [
                    "Sync/async pre-service ConnectionError and synthetic ResponseTimeout failures and recovery.",
                    "Sync/async one-second operation budget before service and recovery.",
                    "Sync/async cold MetadataReadContainer failure blocks create, with positive control and recovery.",
                    "Async pending native create cancellation and recovery.",
                ],
                "transport_contract": "ServiceResponseError is conservative; not ServiceRequestError equivalence "
                                      "or a general not-sent guarantee.",
                "installed_extension_modified": False,
                "lineage": "Five new scenario functions, including the additional indexing check; not direct "
                           "original copies or evidence that legacy assertions were migrated.",
                "reported_selection": {
                    "module_marks": [
                        "cosmosEmulator", "asyncio",
                    ],
                    "fixture_parameters": "sync/async",
                    "verification": "Parent-reported only; this independently owned module remains outside "
                                    "the audit's source/annotation snapshots.",
                },
            },
            "native_driver_in_memory": {
                "test": "create_lost_response_and_post_commit_deadline_preserve_item_rust",
                "reported_result": "passed",
                "scenario_cases": 10,
                "scope": "Five scenarios with/without response suppression: pre-service failure, committed lost "
                         "response, post-commit deadline, pre-commit cancellation, post-commit cancellation. "
                         "Exact stored original value and duplicate-conflict controls.",
                "execution_level": "Real native driver with in-memory transport/storage, not live service.",
            },
            "native_live_service": {
                "test": "create_live_lost_response_and_deadline_preserve_item_rust",
                "reported_result": "passed-when-explicitly-executed",
                "ignored_by_default": True,
                "passed_cases": 6,
                "scope": "Lost successful response, post-commit timeout and post-commit cancellation, each "
                         "with/without response suppression, "
                         "against uniquely owned remote resources. Transport forwards to service BEFORE dropping "
                         "the successful response; successful-fault hit count is one. Independent point read and "
                         "duplicate 409 prove commit. Default Rust retries produced 409 after the lost response.",
                "live_future_cancellation": "Passed. Cancellation waits for an independent read of the stored "
                                            "item before dropping the future. A provisional fault hit counter "
                                            "is not used as a commit signal.",
                "current_scenario_cases": 6,
                "current_suite_result": "final-six-case-rerun-passed",
                "reported_log": "create-lost-response-live-native.log",
                "build_scope": "Staged Python binding Rust crate uses local checkout; no Rust-driver edits.",
            },
            "native_item_suite": {
                "default_run": "17 passed, 1 ignored",
                "explicit_live_run": "Ignored live test explicitly executed afterward and passed all six cases.",
                "driver_head_prefix": "52ffc977",
                "driver_subtree": "clean (parent-reported; not independently inspected by this audit)",
            },
            "indexing_service_effect": {
                "test": "test_service_applies_create_indexing_directive_rust",
                "reported_result": "Known local service-effect failure on both baseline backends; not passing.",
                "test_policy": "Normal assertion retained. The xfail marker and custom exception were removed "
                               "at the user's request; no expected-failure/XPASS classification is current.",
                "probe": "Both legacy and Rust returned all items for automatic=True/False and directives "
                         "None/Include/Exclude/1/2.",
                "disposition": "NEW additional supported-pipeline check, not a migrated legacy assertion. "
                               "Service effect remains open; matching failures are not passing exclusion evidence.",
            },
            "priority_and_bucket_service_scheduling": {
                "status": "blocked-by-explicit-user-decision",
                "decision": "Leave blocked and document the prerequisites.",
                "authorization": "No feature enablement or saturation load authorized.",
                "prerequisites": [
                    "Appropriately configured account features and priority/bucket capacity.",
                    "An approved competing-load plan that can demonstrate scheduling behavior.",
                    "Explicit authorization for feature changes, saturation load and associated capacity/cost.",
                ],
                "mapping_effect": "Header/default/precedence checks remain distinct from service scheduling. "
                                  "This is a blocked verification obligation, not an accepted API exclusion "
                                  "or evidence of passing scheduling behavior.",
            },
        },
        "policy_references": [
            {
                "id": "pushback13",
                "path": "docs\\V5\\api-review\\RUST_PARITY_PUSHBACKS.md",
                "excerpt": "## 13 — Closed: Rust owns automatic write retries",
                "status": "accepted-exclusion",
            },
            {
                "id": "pushback14",
                "path": "docs\\V5\\api-review\\RUST_PARITY_PUSHBACKS.md",
                "excerpt": "## 14 - Closed: progressive read hedging and write hedging are excluded",
                "status": "accepted-exclusion",
            },
            {
                "id": "create-inapplicable-options",
                "path": "docs\\api-review.md",
                "excerpt": "Supplying any of them raises `TypeError`, including `None` or `False`.",
                "approval_excerpt": "**Proposed API changes; approval is not recorded**",
                "status": "documented-api-change-unapproved",
            },
        ],
        "limitations": [
            "Candidate inventory is the historical 556-function discovery plus explicitly reviewed helpers. "
            "Unreviewed candidates are NOT claimed create-relevant or migrated; many are setup/other-API false positives.",
            "Every observation in reviewed_functions is mapped or explicitly unresolved. This is not completion "
            "of every candidate's semantic audit; candidate_inventory records exact remaining scope.",
            "CA01-07 historical verdicts were not imported. Current replacements were read and referenced directly.",
            "Main-agent service/lost-response tests are concurrent work and intentionally not assertion-mapped here.",
            "Only one deployed West US2 region; no deployed multi-region or live AAD passing evidence.",
            "Priority/bucket header or typed-boundary mapping is not capacity-dependent service scheduling evidence. "
            "User explicitly left scheduling verification blocked; feature enablement and saturation load are "
            "not authorized. Prerequisites are recorded in reported_execution.",
            "Indexing-directive service effect is unresolved; queries returning excluded items on both backends "
            "do not establish passing index exclusion.",
            "Gap5 operation-wide budget is a design change, not identical legacy per-attempt timings. "
            "Gap34 read_all continuation is not a create gap.",
        ],
        "source_files": sorted({path for path, _ in selected}),
        "annotation_audit": annotation_audit(scope, rows),
        "create_copy_annotation_audit": create_copy_annotation_audit(rows),
        "reviewed_functions": scope,
        "correspondences": rows,
        "candidate_inventory": inventory,
        "historical_missing_sources": removed,
        "summary": {
            "candidate_functions": len(inventory),
            "reviewed_functions": len(scope),
            "reviewed_test_functions": sum(
                entry["source"]["symbol"].split(".")[-1].startswith("test_") for entry in scope
            ),
            "reviewed_source_files": len({entry["source"]["path"] for entry in scope}),
            "observations": len(rows),
            "dispositions": dict(Counter(row["disposition"] for row in rows)),
            "observation_kinds": dict(Counter(row["source"]["kind"] for row in rows)),
            "unreviewed_candidates": sum(entry["review"] != "reviewed" for entry in inventory),
        },
    }
    ledger_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps(ledger["summary"], indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--discovery", type=Path)
    parser.add_argument("--reviewed-annotation-refresh", action="store_true",
                        help="Explicitly accept manually reviewed annotation/fixture snapshot changes; "
                             "reviewed original assertion/function AST changes remain prohibited.")
    args = parser.parse_args()
    build(args.discovery, args.reviewed_annotation_refresh)
