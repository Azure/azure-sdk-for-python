# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Build the reviewed batch ledger. Regeneration is not parity certification."""

import ast
from collections import Counter
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "batch_source_references",
    ROOT / "tests" / "create_item" / "test_assertion_correspondence_unit.py",
)
REF = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REF)
# Reuse the existing source/annotation fingerprint format rather than another parser.
# pylint: disable=protected-access
FUNCTIONS = REF.FUNCTIONS
FAMILIES = (
    "availability_strategy",
    "backwards_compatibility",
    "container_properties_cache",
    "cosmos_responses",
    "encoding",
    "excluded_locations",
    "headers",
    "none_options",
    "partition_key",
    "per_partition_circuit_breaker_mm",
    "query_response_headers",
    "session",
    "transactional_batch",
)
SHARED = r"tests\execute_item_batch\test_shared_contracts.py"
SERIALIZATION = r"tests\execute_item_batch\test_legacy_serialization_unit.py"
FAILURES = r"tests\execute_item_batch\test_service_failures.py"
OUTPUT = ROOT / "tests" / "execute_item_batch" / "assertion_correspondence.json"


def source_paths():
    return sorted(
        [
            *(
                f"tests\\test_{family}{suffix}.py"
                for family in FAMILIES
                for suffix in ("", "_async")
            ),
            r"tests\test_item_body_serialization.py",
        ]
    )


def is_batch(node):
    return (
        (
            isinstance(node, ast.Attribute)
            and node.attr in {"execute_item_batch", "Batch", "_format_batch_operations"}
        )
        or isinstance(node, ast.Constant)
        and node.value == "execute_item_batch"
    )


def inventory(path):
    """Find composite tests and their transitive local helpers.

    :param str path: Package-relative original test file.
    :return: Source text, functions, call edges, root candidates and helper closure.
    :rtype: tuple
    """
    text, functions = REF._read_file(path)
    short_names = {}
    for symbol, function in functions.items():
        short_names.setdefault(function.name, []).append(symbol)
    edges = {}
    for symbol, function in functions.items():
        dependencies = set()
        for node in ast.walk(function):
            if not isinstance(node, ast.Call):
                continue
            for candidate in short_names.get(REF._call_name(node), ()):
                # Resolve module functions and same-owner methods/closures, not
                # unrelated classes with a coincidentally matching method name.
                owner = candidate.rpartition(".")[0]
                if not owner or symbol == owner or symbol.startswith(owner + "."):
                    dependencies.add(candidate)
        edges[symbol] = dependencies - {symbol}
    selected = {
        symbol
        for symbol, function in functions.items()
        if any(is_batch(node) for node in ast.walk(function))
    }
    while True:
        expanded = selected | {
            symbol for symbol, calls in edges.items() if calls & selected
        }
        if expanded == selected:
            break
        selected = expanded
    roots = set(selected)
    while True:
        expanded = selected | {
            callee for symbol in selected for callee in edges[symbol]
        }
        if expanded == selected:
            break
        selected = expanded
    return text, functions, edges, roots, selected


def observations(function):
    for kind, node in REF._observations(function):
        if kind in {"assertion", "assertion-call", "helper-call"}:
            yield kind, node
    for node in ast.walk(function):
        if not isinstance(node, ast.Call):
            continue
        direct = REF._call_name(node) in {"execute_item_batch", "Batch"}
        invoked = (
            REF._call_name(node) == "invoke"
            and node.args
            and isinstance(node.args[0], ast.Attribute)
        )
        if direct or invoked and node.args[0].attr == "execute_item_batch":
            yield "batch-call", node


def refs(path, name, contains=None, kinds=("assertion", "assertion-call")):
    text, functions = REF._read_file(path)
    matches = [
        (symbol, function)
        for symbol, function in functions.items()
        if function.name == name
    ]
    assert len(matches) == 1, (path, name, matches)
    symbol, function = matches[0]
    result = [
        REF._reference(path, symbol, kind, node, text)
        for kind, node in observations(function)
        if kind in kinds and (contains is None or contains in ast.unparse(node))
    ]
    assert result, (path, name, contains, kinds)
    return result


def disposition(path, symbol, kind, node):  # pylint: disable=too-many-branches,too-many-statements
    name = symbol.rsplit(".", 1)[-1]
    text = ast.unparse(node)
    asynchronous = path.endswith("_async.py")
    surface = "aio" if asynchronous else "sync"
    row = {
        "disposition": "unresolved",
        "rationale": "No assertion-equivalent replacement established for this observation.",
        "replacements": [],
        "execution_level": "none",
        "verification": "source-correspondence-only; see LIVE_VERIFICATION.md for executed scope",
        "remaining": [],
    }

    def mapped(
        reason, targets, *, partial=False, level="public-installed-native", remaining=()
    ):
        row.update(
            disposition=(
                "partial-correspondence" if partial else "supported-correspondence"
            ),
            rationale=reason,
            replacements=targets,
            execution_level=level,
            remaining=list(remaining),
        )

    def other(reason):
        row.update(disposition="setup-or-other-api", rationale=reason)

    if "test_transactional_batch" in path or "test_query_response_headers" in path:
        directory = (
            "execute_item_batch" if "transactional_batch" in path else "response_hook"
        )
        target = f"tests\\{directory}\\{surface}\\{path.split(chr(92))[-1]}"
        candidates = refs(target, name + "_rust", kinds=(kind,))
        equivalents = [
            candidate
            for candidate in candidates
            if candidate["ast_sha256"] == REF._fingerprint(node)
        ]
        if equivalents:
            mapped(
                "Identical assertion/call AST in the corresponding copied test, not just its name.",
                equivalents,
            )
        else:
            row["remaining"] = [
                "Original observation has no identical observation in its corresponding copy."
            ]
    elif "test_none_options" in path:
        mapped(
            "The original either-ID assertion is retained, with an additional both-ID assertion; "
            "session_token/priority/throughput_bucket are explicitly None on both surfaces.",
            refs(SHARED, "test_batch_none_options_rust", kinds=(kind,)),
        )
    elif "test_backwards_compatibility" in path:
        if (
            kind == "batch-call"
            or "batch_results" in text
            or "result['statusCode']" in text
        ):
            mapped(
                "Four original operations, including the differing replacement-body ID, and ignored top-level "
                "etag/IfModified are retained; result count and every status are checked.",
                refs(
                    SHARED,
                    "test_batch_ignored_top_level_conditions_rust",
                    kinds=(kind,),
                ),
            )
        else:
            other(
                "Database/container/item assertions preceding the batch are not batch assertions."
            )
    elif "test_cosmos_responses" in path:
        if kind == "batch-call" or "batch_response" in text:
            mapped(
                "Retains the pre-replace LSN baseline, intervening replacement, 50-create batch, "
                "nonempty headers and strict baseline+1 < batch LSN comparison.",
                refs(
                    SHARED,
                    "test_batch_headers_lsn_and_session_progression_rust",
                    (
                        None
                        if kind == "batch-call"
                        else "batch_response.get_response_headers"
                    ),
                    kinds=(kind,),
                ),
            )
        else:
            other(
                "Other point-operation headers/LSNs are setup or another API's contract."
            )
    elif "test_partition_key" in path:
        if name in {"_assert_pk", "_batch_and_assert"}:
            selector = None
            if kind != "batch-call":
                selector = (
                    "len(response)"
                    if "len(" in text
                    else ("item['pk']" if " is None" in text else "None not in item")
                )
                if "_assert_pk(" in text:
                    selector = None
            mapped(
                "Batch-only projection of the composite: Hash versions 1/2, Python None and null sentinel "
                "(present-null property), undefined sentinel (absent property), one upsert result. "
                "The replacement additionally reads stored state; other API helpers are not credited.",
                refs(
                    SHARED,
                    "test_batch_null_and_undefined_partition_keys_rust",
                    selector,
                    kinds=("batch-call",) if kind == "batch-call" else ("assertion",),
                ),
            )
        else:
            other(
                "Non-batch portion of the partition-key composite; "
                "batch assertions live in _batch_and_assert/_assert_pk."
            )
    elif "test_session" in path:
        if "batch_response_token" in text and "response_session_token" in text:
            mapped(
                "Retains non-equality of pre-batch and post-batch response session tokens, "
                "and additionally rejects missing tokens. Does not prove outgoing automatic session headers.",
                refs(
                    SHARED,
                    "test_batch_headers_lsn_and_session_progression_rust",
                    "batch_response_token != response_session_token",
                ),
                partial="mwr" in symbol,
                remaining=(
                    (
                        "Multi-write topology/token-vector branch still requires native equivalence.",
                    )
                    if "mwr" in symbol
                    else ()
                ),
            )
        else:
            row["rationale"] = (
                "Session composite includes outgoing token presence/absence, multi-write vectors and other APIs. "
                "Existing delete_item copies skip unobservable request checks; those are not replacement evidence. "
                "Removal of raw_request_hook does not retire session correctness."
            )
            row["remaining"] = [
                "Native outgoing-token and multi-write assertion correspondence; isolate other-API branches."
            ]
    elif "test_item_body_serialization" in path or "test_encoding" in path:
        wire_shape = "wire_shape" in symbol
        target = (
            "test_original_batch_wire_shape_rust"
            if wire_shape
            else "test_original_batch_serialization_vectors_rust"
        )
        mapped(
            "Pins all four item-body operations, read/delete/mixed/empty body-free batches and mixed read/create, "
            "with compact enabled/disabled on both surfaces. Raw UTF-8/escaped text and bytes are checked. "
            "This is Python/native-boundary evidence, not actual HTTP Content-Length or service round-trip evidence.",
            refs(SERIALIZATION, target),
            partial=not wire_shape,
            level="python-helper-fake",
            remaining=(
                ()
                if wire_shape
                else (
                    "Separate actual wire Content-Length and service response/content assertions "
                    "from internal serializer details.",
                    "Non-batch branches of the shared encoding composite are not claimed as batch replacements.",
                )
            ),
        )
    elif "test_excluded_locations" in path:
        mapped(
            "Real native region-specific fault counters cover six exclusion cases and single-write fallback. "
            "The original twelve input vectors and exact endpoint-set assertions are not all equivalent.",
            refs(FAILURES, "regional_case", "_debug_fault_injection_rule_hit_count"),
            partial=True,
            remaining=(
                "Complete original twelve-vector destination/override matrix, including nonpreferred region.",
            ),
        )
    elif "test_availability_strategy" in path:
        if "read_operation" in name or name in {
            "test_custom_thread_pool_executor",
            "test_max_concurrency",
        }:
            other(
                "Read-only helper/test selected through the shared operation-type helper; no batch execution."
            )
        else:
            mapped(
                "Regional fault checks provide only nonhedged write-routing evidence. "
                "Gap 14 excludes progressive/write "
                "hedging, not ordinary status propagation, disabled-policy overrides or exclusion correctness. "
                "No blanket exclusion of this shared assertion is made.",
                refs(FAILURES, "regional_case", "caught.value.status_code"),
                partial=True,
                remaining=(
                    "Per-vector split of accepted hedging exclusions versus retained URI/status/override assertions.",
                    "Exact original status/substatus matrix and first/second-region error-selection assertions.",
                ),
            )
    elif "test_per_partition_circuit_breaker_mm" in path:
        row["rationale"] = (
            "Ordinary circuit-breaker failover/recovery is not write hedging. Exact consecutive/failure-rate "
            "thresholds, destination changes and recovery have no established batch replacement. Python health-map "
            "internals and exception object identity must be separated from retained customer behavior."
        )
        row["remaining"] = [
            "Native threshold/failure-rate/recovery assertions; do not substitute exclusion-routing tests."
        ]
    elif "test_container_properties_cache" in path:
        if "len(batch_response)" in text or "e.http_error_message" in text:
            mapped(
                "Both 100-create batches are exercised on the same public proxy before/after same-name recreation "
                "with /PK changed to /partkey. Native metadata remains warm; no Python cache is injected. "
                "Unexpected batch exceptions fail the replacement directly.",
                refs(SHARED, "test_batch_same_name_container_recreation_rust", "len(batch_response)"),
            )
        else:
            row["rationale"] = (
                "Positive recreation assertions have a native replacement. Original setup-failure sentinels "
                "and the final conditional 400 assertion need separate disposition: the latter has no failure "
                "sentinel, supplies a valid new key/body, and may never execute. Cold metadata faults are not "
                "a replacement for this scenario."
            )
            row["remaining"] = ["Original negative-case validity and batch-call/setup correspondence."]
    elif "test_headers" in path:
        mapped(
            "The original request value 3 overrides client value 2 in a wrapped real native batch call. "
            "The original outgoing HTTP-header assertion remains distinct from this typed-boundary assertion.",
            refs(SHARED, "test_batch_request_throughput_bucket_rust", "settings.throughput_bucket"),
            partial=True,
            remaining=("Outgoing batch header value 3; service-applied scheduling is separate evidence.",),
        )
    return row


def build():
    records = []
    contexts = {}
    for path in source_paths():
        text, functions, edges, roots, selected = inventory(path)
        for symbol in sorted(selected):
            function = functions[symbol]
            nested = [
                functions[child]
                for child in selected
                if child.startswith(symbol + ".")
                and isinstance(functions[child], FUNCTIONS)
            ]
            rows = []
            for kind, node in observations(function):
                if any(
                    child.lineno <= node.lineno <= child.end_lineno for child in nested
                ):
                    continue
                row = disposition(path, symbol, kind, node)
                row["source"] = REF._reference(path, symbol, kind, node, text)
                rows.append(row)
                for target in row["replacements"]:
                    key = target["path"] + "::" + target["symbol"]
                    if key not in contexts:
                        contexts[key] = REF._annotation_context(
                            target["path"], target["symbol"]
                        )
            records.append(
                {
                    "source": REF._reference(path, symbol, "function", function, text),
                    "discovery": (
                        "batch-or-caller" if symbol in roots else "forward-helper"
                    ),
                    "helpers": sorted(edges[symbol] & selected),
                    "annotation_context": REF._annotation_context(path, symbol),
                    "controls": [
                        REF._reference(path, symbol, kind, node, text)
                        for kind, node in REF._observations(function)
                        if kind.endswith("-branch")
                    ],
                    "observations": rows,
                }
            )
    counts = Counter(
        row["disposition"] for record in records for row in record["observations"]
    )
    return {
        "scope": "27 original modules; observations, transitive helpers, controls, annotations "
                 "and fixture fingerprints",
        "not_a_completion_certificate": True,
        "source_modules": source_paths(),
        "counts": dict(sorted(counts.items())),
        "records": records,
        "replacement_contexts": contexts,
        "fixture_boundary": {
            "path": FAILURES,
            "ast_sha256": REF._fingerprint(ast.parse(REF._read_file(FAILURES)[0])),
            "meaning": "Shared replacements use configured key/AAD clients, key-owned resources, real native spies "
            "and legacy Batch failure guards. AAD collection is not execution.",
        },
    }


if __name__ == "__main__":
    ledger = build()
    OUTPUT.write_text(
        json.dumps(ledger, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "modules": len(ledger["source_modules"]),
                "functions": len(ledger["records"]),
                "observations": ledger["counts"],
            },
            indent=2,
        )
    )
