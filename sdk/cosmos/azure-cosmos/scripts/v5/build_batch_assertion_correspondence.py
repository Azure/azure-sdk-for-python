# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Build the reviewed batch ledger. Regeneration is not parity certification."""

import ast
from collections import Counter
from functools import lru_cache
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
SERIALIZATION = r"tests\execute_item_batch\test_serialization_compatibility_unit.py"
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


@lru_cache(maxsize=None)
def imported_functions(path):
    aliases = {}
    tree = ast.parse(REF._read_file(path)[0])
    for node in tree.body:
        if (
            isinstance(node, ast.ImportFrom)
            and node.module
            and node.module.startswith("test_")
        ):
            target = "tests\\" + node.module.replace(".", "\\") + ".py"
            if not ROOT.joinpath(*target.split("\\")).exists():
                continue
            functions = REF._read_file(target)[1]
            for alias in node.names:
                if alias.name in functions:
                    aliases[alias.asname or alias.name] = (target, alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "test_config":
                    target = r"tests\test_config.py"
                    for symbol in REF._read_file(target)[1]:
                        aliases[(alias.asname or alias.name) + "." + symbol] = (
                            target,
                            symbol,
                        )
    return aliases


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


def disposition(
    path, symbol, kind, node
):  # pylint: disable=too-many-branches,too-many-statements
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
        if name in {"_assert_pk", "_batch_and_assert"} or "_batch_and_assert(" in text:
            selector = None
            if kind != "batch-call":
                selector = (
                    "len(response)"
                    if "len(" in text
                    else ("item['pk']" if " is None" in text else "None not in item")
                )
                if "_assert_pk(" in text or "_batch_and_assert(" in text:
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
            function = REF._read_file(path)[1][symbol]
            preceding = sorted(
                (
                    call
                    for call in ast.walk(function)
                    if isinstance(call, ast.Call)
                    and call.lineno <= node.lineno
                    and REF._call_name(call)
                    in {
                        "execute_item_batch",
                        "create_item",
                        "upsert_item",
                        "read_item",
                        "replace_item",
                        "delete_item",
                        "create_container",
                        "delete_container",
                        "read",
                    }
                ),
                key=lambda call: call.lineno,
            )
            if preceding and REF._call_name(preceding[-1]) != "execute_item_batch":
                other(
                    "Request/response session assertion outside the batch portion of the composite."
                )
            else:
                row["rationale"] = (
                    "Outgoing batch session-token presence and the original mixed-operation session vectors "
                    "are not proved by response-token progression. Existing delete_item copies skip request "
                    "checks; removing raw_request_hook does not retire session correctness."
                )
                row["remaining"] = [
                    "Native outgoing batch token and multi-write session-vector correspondence."
                ]
    elif "test_encoding" in path:
        function = REF._read_file(path)[1][symbol]
        calls = sorted(
            (
                call
                for call in ast.walk(function)
                if isinstance(call, ast.Call)
                and REF._call_name(call) == "execute_item_batch"
            ),
            key=lambda call: call.lineno,
        )
        if calls and node.lineno < calls[0].lineno:
            other(
                "Create/upsert/replace/patch portion preceding the first batch in the encoding composite."
            )
        else:
            target = "test_batch_unicode_write_read_delete_rust"
            variables = {
                child.id for child in ast.walk(node) if isinstance(child, ast.Name)
            } & {"batch_result", "read_batch_result", "delete_batch_result"}
            if variables and kind != "batch-call":
                variable = next(iter(variables))
                field = (
                    "['resourceBody']['content']"
                    if "resourceBody" in text
                    else "['statusCode']"
                )
                mapped(
                    "Retains the exact Unicode batch service status/content assertion on both public surfaces.",
                    refs(SHARED, target, variable + "[0]" + field),
                )
            elif kind == "batch-call":
                targets = refs(SHARED, target, kinds=("batch-call",))
                mapped(
                    "Original create/read/delete Unicode batch vector executes through the real native export.",
                    [targets[calls.index(node)]],
                )
            else:
                mapped(
                    "Original bytes/text/escaping requirement is checked at a wrapped real native batch boundary "
                    "with the original Japanese/Thai/emoji payload. This is not outgoing HTTP capture.",
                    refs(SHARED, target, "body"),
                    partial=True,
                    remaining=("Actual outgoing-body/Content-Length observation.",),
                )
    elif "test_item_body_serialization" in path:
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
        if (
            "_perform_read_operation(" in text
            or "read_operation" in name
            or name.removesuffix("_async")
            in {
                "test_custom_thread_pool_executor",
                "test_max_concurrency",
            }
        ):
            other(
                "Read-only helper/test selected through the shared operation-type helper; no batch execution."
            )
        else:
            mapped(
                "Regional fault checks provide only nonhedged write-routing evidence. "
                "Gap 14 excludes progressive/write "
                "hedging, not ordinary status propagation, disabled-policy overrides or exclusion correctness. "
                "No blanket exclusion of this shared assertion is made.",
                refs(
                    FAILURES,
                    "regional_case",
                    (
                        "_debug_fault_injection_rule_hit_count"
                        if "uri" in name
                        else "caught.value.status_code"
                    ),
                ),
                partial=True,
                remaining=(
                    "Per-vector split of accepted hedging exclusions versus retained URI/status/override assertions.",
                    "Exact original status/substatus matrix and first/second-region error-selection assertions.",
                ),
            )
    elif "test_per_partition_circuit_breaker_mm" in path:
        if name == "perform_read_operation":
            other(
                "Read/query-only helper reached through a shared policy composite; no batch assertion."
            )
        elif "health_info." in text or "exc_info.value == error" in text:
            row.update(
                disposition="retired-python-detail",
                rationale="Exact private Python counter fields/injected Python exception-object identity are "
                "implementation details. Error type/status and externally visible threshold, partition "
                "isolation, failover and recovery remain open in the enclosing policy cases.",
            )
        else:
            row["rationale"] = (
                "Ordinary circuit-breaker failover/recovery is not write hedging. Exact consecutive/failure-rate "
                "thresholds, destination changes and recovery have no established batch replacement."
            )
            row["remaining"] = [
                "Native threshold/failure-rate/recovery assertions; do not substitute exclusion-routing tests."
            ]
    elif "test_container_properties_cache" in path:
        if "Container Should not Already Exist" in text:
            other(
                "Owned-container setup failure sentinel, not a batch response assertion."
            )
        elif kind == "batch-call":
            function = REF._read_file(path)[1][symbol]
            calls = sorted(
                (
                    call
                    for call in ast.walk(function)
                    if isinstance(call, ast.Call)
                    and REF._call_name(call) == "execute_item_batch"
                ),
                key=lambda call: call.lineno,
            )
            if calls.index(node) < 2:
                mapped(
                    "The replacement loop retains both 100-create operations, original property names and key "
                    "value, while reusing a warm native proxy across same-name container recreation.",
                    refs(
                        SHARED,
                        "test_batch_same_name_container_recreation_rust",
                        kinds=("batch-call",),
                    ),
                )
            else:
                row["rationale"] = (
                    "Original purported negative call has a valid new-key body and no failure sentinel."
                )
                row["remaining"] = [
                    "Establish a nonvacuous negative-case contract rather than inventing a 400 expectation."
                ]
        elif "len(batch_response)" in text or "e.http_error_message" in text:
            mapped(
                "Both 100-create batches are exercised on the same public proxy before/after same-name recreation "
                "with /PK changed to /partkey. Native metadata remains warm; no Python cache is injected. "
                "Unexpected batch exceptions fail the replacement directly.",
                refs(
                    SHARED,
                    "test_batch_same_name_container_recreation_rust",
                    "len(batch_response)",
                ),
            )
        else:
            row["rationale"] = (
                "Positive recreation assertions have a native replacement. Original setup-failure sentinels "
                "and the final conditional 400 assertion need separate disposition: the latter has no failure "
                "sentinel, supplies a valid new key/body, and may never execute. Cold metadata faults are not "
                "a replacement for this scenario."
            )
            row["remaining"] = [
                "Original negative-case validity and batch-call/setup correspondence."
            ]
    elif "test_headers" in path:
        mapped(
            "The original request value 3 overrides client value 2 in a wrapped real native batch call. "
            "The original outgoing HTTP-header assertion remains distinct from this typed-boundary assertion.",
            refs(
                SHARED,
                "test_batch_request_throughput_bucket_rust",
                "settings.throughput_bucket",
            ),
            partial=True,
            remaining=(
                "Outgoing batch header value 3; service-applied scheduling is separate evidence.",
            ),
        )
    return row


def imported_references(path, function, external_helpers):
    imported = []
    for call in ast.walk(function):
        if not isinstance(call, ast.Call):
            continue
        dependency = imported_functions(path).get(ast.unparse(call.func))
        if dependency is None:
            continue
        target_path, target_symbol = dependency
        key = target_path + "::" + target_symbol
        imported.append(key)
        if key not in external_helpers:
            target_text, target_functions = REF._read_file(target_path)
            target = target_functions[target_symbol]
            external_helpers[key] = {
                "source": REF._reference(
                    target_path, target_symbol, "function", target, target_text
                ),
                "observations": [
                    REF._reference(target_path, target_symbol, kind, node, target_text)
                    for kind, node in observations(target)
                ],
            }
    return sorted(set(imported))


def build():
    records = []
    contexts = {}
    external_helpers = {}
    module_contexts = {}
    for path in source_paths():
        text, functions, edges, roots, selected = inventory(path)
        module_contexts[path] = [
            REF._reference(path, "<module>", "module-value-or-import", node, text)
            for node in ast.parse(text).body
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.Import, ast.ImportFrom))
        ]
        for symbol in sorted(selected):
            function = functions[symbol]
            imported = imported_references(path, function, external_helpers)
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
                    "imported_helpers": imported,
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
        "module_contexts": module_contexts,
        "external_helpers": external_helpers,
        "replacement_contexts": contexts,
        "replacement_modules": {
            path: REF._fingerprint(ast.parse(REF._read_file(path)[0]))
            for path in sorted({context["path"] for context in contexts.values()})
        },
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
