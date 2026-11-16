# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Read-only, whole-result query measurements against a separately prepared corpus."""

import asyncio
from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import time

from workload_utils import _extra_kwargs, _record_error
import workload_configs as config

SCENARIOS = {
    "cross_partition": (
        "SELECT TOP 1000 c.id, c.tenantId, c.priceCents FROM c "
        "WHERE c.priceCents >= @minPriceCents ORDER BY c.priceCents, c.id"
    ),
    "aggregate": "SELECT VALUE SUM(c.priceCents) FROM c",
    "full_text": "SELECT TOP 20 c.id, c.tenantId FROM c ORDER BY RANK FullTextScore(c.text, @term)",
    "vector": "SELECT TOP 20 c.id, c.tenantId FROM c ORDER BY VectorDistance(c.embedding, @vector)",
    "hybrid": (
        "SELECT TOP 20 c.id, c.tenantId FROM c "
        "ORDER BY RANK RRF(FullTextScore(c.text, @term), VectorDistance(c.embedding, @vector))"
    ),
}
_PARAMETERS = {
    "cross_partition": {"@minPriceCents"},
    "aggregate": set(),
    "full_text": {"@term"},
    "vector": {"@vector"},
    "hybrid": {"@term", "@vector"},
}
_POLICIES = ("partitionKey", "indexingPolicy", "vectorEmbeddingPolicy", "fullTextPolicy")


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def fingerprint(value):
    """Hash canonical JSON, including array order."""
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def result_fingerprint(rows, *, ordered):
    """Build a reference digest from independently verified projected result rows."""
    return fingerprint(rows if ordered else sorted(rows, key=_json))


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _positive_int(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _digest(value, length=64):
    return isinstance(value, str) and re.fullmatch(rf"[0-9a-f]{{{length}}}", value) is not None


def _identity(row):
    _require(
        isinstance(row, dict) and all(isinstance(row.get(key), str) and row[key] for key in ("tenantId", "id")),
        "Ranked results require nonempty tenantId and id",
    )
    return row["tenantId"], row["id"]


def _validate_expectation(name, expected):
    _require(
        isinstance(expected, dict) and _positive_int(expected.get("count")),
        "Every scenario requires a positive expected result count",
    )
    mode = expected.get("mode")
    if name in ("cross_partition", "aggregate"):
        _require(
            mode == ("ordered" if name == "cross_partition" else "unordered"),
            "Ordered results and scalar aggregates require their respective digest modes",
        )
        _require(_digest(expected.get("sha256")), "Expected results require a SHA256 digest")
        if name == "cross_partition":
            _require(expected["count"] == 1000, "Cross-partition scenario requires 1000 expected rows")
        else:
            _require(expected["count"] == 1, "The scalar aggregate requires one expected result")
        return
    _require(expected["count"] == 20, "Search scenarios require 20 expected results")
    _require(
        mode == "rank_groups" or (mode == "recall" and name in ("vector", "hybrid")),
        "Search results require rank_groups, or explicit vector/hybrid recall validation",
    )
    groups = expected.get("groups")
    _require(
        isinstance(groups, list) and groups and all(isinstance(g, list) and g for g in groups),
        "Expected ranking requires nonempty groups of tenantId/id objects",
    )
    keys = [_identity(row) for group in groups for row in group]
    _require(
        len(keys) == len(set(keys)) and len(keys) >= expected["count"],
        "Expected ranking identities must be unique and cover the requested result count",
    )
    if mode == "recall":
        recall = expected.get("minimum_recall")
        _require(
            type(recall) in (float, int) and math.isfinite(recall) and 0 < recall <= 1,
            "Approximate search requires an explicit minimum_recall in (0, 1]",
        )
        _require(len(keys) == expected["count"], "Recall reference must contain exactly the expected top K")


class QueryScenario:
    """An explicit suite contract; loading it does not contact a service or seed data."""

    def __init__(self, manifest, name, target):
        _require(isinstance(manifest, dict) and manifest.get("version") == 1, "Unsupported query suite version")
        _require(name in SCENARIOS, f"Select a query scenario from {sorted(SCENARIOS)}")
        _require(manifest.get("target") == target, "Query suite target differs from the selected workload")
        dataset = manifest.get("dataset", {})
        _require(
            isinstance(dataset.get("id"), str)
            and dataset["id"]
            and _digest(dataset.get("sha256"))
            and _positive_int(dataset.get("item_count"))
            and dataset["item_count"] >= 1000,
            "Query dataset requires an ID, corpus SHA256 and item_count of at least 1000",
        )
        _require(
            _digest(manifest.get("expected_driver_commit"), 40),
            "Query suite requires the intended full Rust driver commit",
        )
        seconds = manifest.get("query_timeout_seconds")
        _require(
            type(seconds) in (int, float) and math.isfinite(seconds) and 0 < seconds <= 60,
            "Whole-query timeout must be positive and at most 60 seconds",
        )
        options = manifest.get("query_options", {})
        _require(
            set(options) == {"max_item_count", "full_text_score_scope"}
            and _positive_int(options["max_item_count"])
            and options["max_item_count"] < 1000
            and options["full_text_score_scope"] in ("Local", "Global"),
            "Specify max_item_count in [1, 999] and full_text_score_scope Local or Global",
        )
        policies = manifest.get("container_properties", {})
        _require(
            set(policies) == set(_POLICIES) and all(isinstance(policies[k], dict) for k in _POLICIES),
            "Specify partition, indexing, vector embedding and full-text policies",
        )
        _require(
            policies["partitionKey"].get("paths") == ["/tenantId"], "The search corpus requires partition key /tenantId"
        )
        embeddings = policies["vectorEmbeddingPolicy"].get("vectorEmbeddings", [])
        _require(
            len(embeddings) == 1
            and embeddings[0].get("path") == "/embedding"
            and _positive_int(embeddings[0].get("dimensions"))
            and embeddings[0].get("dataType") == "float32"
            and embeddings[0].get("distanceFunction") in ("cosine", "dotproduct", "euclidean"),
            "Specify one float32 /embedding vector policy with dimensions and distanceFunction",
        )
        indexing = policies["indexingPolicy"]
        _require(
            indexing.get("indexingMode") == "consistent"
            and indexing.get("fullTextIndexes") == [{"path": "/text"}]
            and len(indexing.get("vectorIndexes", [])) == 1
            and indexing["vectorIndexes"][0].get("path") == "/embedding"
            and indexing["vectorIndexes"][0].get("type") in ("flat", "quantizedFlat", "diskANN"),
            "Specify consistent full-text and vector indexes for /text and /embedding",
        )
        _require(
            [{"path": "/priceCents", "order": "ascending"}, {"path": "/id", "order": "ascending"}]
            in indexing.get("compositeIndexes", []),
            "Ordered query requires the priceCents/id composite index",
        )
        _require(
            any(
                p.get("path") == "/text" and p.get("language")
                for p in policies["fullTextPolicy"].get("fullTextPaths", [])
            ),
            "Specify the /text full-text language",
        )
        entries = manifest.get("scenarios", {})
        _require(set(entries) == set(SCENARIOS), "The manifest must define all five query scenarios")
        for scenario_name, entry in entries.items():
            parameters = entry.get("parameters", {})
            _require(set(parameters) == _PARAMETERS[scenario_name], f"Incorrect parameters for {scenario_name}")
            if "@minPriceCents" in parameters:
                _require(
                    isinstance(parameters["@minPriceCents"], int)
                    and not isinstance(parameters["@minPriceCents"], bool)
                    and parameters["@minPriceCents"] >= 0,
                    "Minimum price must be a nonnegative integer",
                )
            if "@term" in parameters:
                _require(
                    isinstance(parameters["@term"], str) and parameters["@term"].strip(),
                    "Full-text search term must be nonempty",
                )
            if "@vector" in parameters:
                vector = parameters["@vector"]
                _require(
                    isinstance(vector, list)
                    and len(vector) == embeddings[0]["dimensions"]
                    and all(type(v) in (float, int) and math.isfinite(v) for v in vector)
                    and any(v != 0 for v in vector),
                    "Query vector must match the embedding policy",
                )
            _validate_expectation(scenario_name, entry.get("expected"))
        _require(
            entries["hybrid"]["parameters"]["@vector"] == entries["vector"]["parameters"]["@vector"]
            and entries["hybrid"]["parameters"]["@term"] == entries["full_text"]["parameters"]["@term"],
            "Hybrid search must reuse the standalone search term and query vector",
        )
        self.manifest = deepcopy(manifest)
        self.name = name
        self.expected = self.manifest["scenarios"][name]["expected"]
        self.timeout = seconds
        self.kwargs = {
            "query": SCENARIOS[name],
            "parameters": [
                {"name": key, "value": value} for key, value in self.manifest["scenarios"][name]["parameters"].items()
            ],
            "enable_cross_partition_query": True,
            **options,
        }

    def metadata(self):
        return {
            "scenario": self.name,
            "suite_sha256": fingerprint(self.manifest),
            "dataset": self.manifest["dataset"],
            "container_properties": self.manifest["container_properties"],
            "query": self.kwargs,
            "expected": self.expected,
            "query_timeout_seconds": self.timeout,
            "latency_boundary": "query_items_through_full_materialization",
            "validation": "every_result_after_latency_timer; included_in_wall_time_throughput",
            "ru_scope": "sum_of_observed_response_hooks_per_completed_query",
            "service_qualification": "pending",
            "physical_partition_fanout": "not_verified",
            "corpus_digest_verification": "declared_only; requires_external_seed_inventory",
            "execution_settings": {
                "request_excluded_locations": list(config.REQUEST_EXCLUDED_LOCATIONS),
                "gc_freeze": config.WORKLOAD_GC_FREEZE,
                "loop_lag_monitor": config.WORKLOAD_LOOP_LAG_MONITOR,
                "diagnostics_logging": config.ENABLE_DIAGNOSTICS_LOGGING,
                "circuit_breaker": config.CIRCUIT_BREAKER_ENABLED,
                "multiple_write_locations": config.USE_MULTIPLE_WRITABLE_LOCATIONS,
            },
            "search_environment": {
                key: os.environ.get(key)
                for key in (
                    "AZURE_COSMOS_HYBRID_SEARCH_MAX_ITEMS",
                    "AZURE_COSMOS_MAX_ITEM_BUFFER_VECTOR_SEARCH",
                )
            },
        }

    def validate(self, rows):
        _require(len(rows) == self.expected["count"], "Query returned an unexpected result count")
        mode = self.expected["mode"]
        if mode in ("ordered", "unordered"):
            _require(
                result_fingerprint(rows, ordered=mode == "ordered") == self.expected["sha256"],
                "Query result differs from the independently verified reference",
            )
            return
        keys = [_identity(row) for row in rows]
        _require(len(keys) == len(set(keys)), "Query returned duplicate result identities")
        ranks = {_identity(row): rank for rank, group in enumerate(self.expected["groups"]) for row in group}
        if mode == "recall":
            _require(
                len(set(keys) & ranks.keys()) / len(keys) >= self.expected["minimum_recall"],
                "Approximate result missed the required recall",
            )
        else:
            expected_ranks = sorted(ranks.values())[: len(keys)]
            _require(
                [ranks.get(key, -1) for key in keys] == expected_ranks,
                "Query returned incorrect ranking (ties are permitted only within declared groups)",
            )

    def validate_results_target(self, reporting):
        from profiling_restore_orders import target as normalize_target

        selected = self.manifest["target"]
        workload_target = normalize_target(selected["endpoint"], selected["database"], selected["container"])
        results_target = normalize_target(
            reporting["results_endpoint"], reporting["results_database"], reporting["results_container"]
        )
        _require(workload_target != results_target, "Query results must not be written into the corpus container")


def load_scenario(path, name):
    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    return QueryScenario(
        manifest,
        name,
        {
            "endpoint": config.COSMOS_URI,
            "database": config.COSMOS_DATABASE,
            "container": config.COSMOS_CONTAINER,
        },
    )


def build_identity(expected_driver):
    """Fingerprint installed SDK files, not a neighboring checkout or an environment label."""
    from azure import cosmos
    from azure.cosmos import _rust

    actual = getattr(_rust, "__rust_driver_commit__", None)
    _require(actual == expected_driver, "Loaded Rust driver differs from query manifest; rebuild before comparison")
    sources = {}
    for label, root in (
        ("wrapper", Path(cosmos.__file__).resolve().parent),
        ("harness", Path(__file__).resolve().parent),
    ):
        source = {
            path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(root.rglob("*.py"))
        }
        sources[f"{label}_sha256"] = fingerprint(source)
    return {
        "driver_commit": actual,
        "native_sha256": hashlib.sha256(Path(_rust.__file__).read_bytes()).hexdigest(),
        **sources,
    }


def _matches_policy(actual, expected):
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and _matches_policy(actual[key], value) for key, value in expected.items()
        )
    if isinstance(expected, list):
        return (
            isinstance(actual, list)
            and len(actual) == len(expected)
            and all(_matches_policy(left, right) for left, right in zip(actual, expected))
        )
    return actual == expected


class QueryMeasurement:
    operation = "query"
    label = "QueryItems"

    def __init__(self, container, scenario):
        self.container = container
        self.scenario = scenario

    async def prepare(self, stop_event):
        if stop_event.is_set():
            raise RuntimeError("Query measurement interrupted before preflight")
        properties = await asyncio.wait_for(
            self.container.read(**_extra_kwargs(config.REQUEST_EXCLUDED_LOCATIONS)),
            self.scenario.timeout,
        )
        _require(properties.get("defaultTtl") is None, "Query corpus must not have container TTL")
        _require(
            _matches_policy(properties, self.scenario.manifest["container_properties"]),
            "Query container policies differ from the suite manifest",
        )

    async def run(self, stats):
        hooks, charge = 0, 0.0
        pages, empty_pages = 0, 0
        call_kwargs = deepcopy(self.scenario.kwargs)
        call_kwargs.update(_extra_kwargs(config.REQUEST_EXCLUDED_LOCATIONS))

        def hook(headers, _body):
            nonlocal hooks, charge
            hooks += 1
            value = headers.get("x-ms-request-charge") if headers else None
            _require(value is not None and not isinstance(value, bool), "Query response hook omitted a valid RU charge")
            value = float(value)
            _require(math.isfinite(value) and value >= 0, "Query RU charge must be finite and nonnegative")
            charge += value
            duration = headers.get("x-ms-request-duration-ms")
            if duration is not None:
                stats.record_server_ms(self.label, float(duration))

        async def consume():
            nonlocal pages, empty_pages
            rows = []
            iterator = self.container.query_items(
                **call_kwargs,
                response_hook=hook,
            )
            # Keep one pager for the complete invocation. Do not read its continuation
            # property: aggregate/ranked shapes can continue without being bookmarkable.
            async for page in iterator.by_page():
                pages += 1
                before = len(rows)
                async for row in page:
                    rows.append(row)
                    _require(len(rows) <= self.scenario.expected["count"], "Query returned too many results")
                empty_pages += int(len(rows) == before)
            return rows

        start = time.perf_counter_ns()
        try:
            rows = await asyncio.wait_for(consume(), self.scenario.timeout)
            duration_ms = (time.perf_counter_ns() - start) / 1_000_000
            _require(duration_ms <= self.scenario.timeout * 1000, "Whole-query deadline exceeded")
            _require(hooks > 0, "Query completed without response-hook RU coverage")
            if self.scenario.name == "cross_partition":
                _require(pages > 1, "Cross-partition scenario did not exercise multiple public pages")
            self.scenario.validate(rows)
            stats.record_ru(self.label, charge)
            stats.record_query_result(self.label, len(rows), pages, empty_pages, hooks)
            stats.record(self.label, duration_ms)
        except Exception as error:
            _record_error(stats, self.label, error)
            raise

    async def cleanup(self):
        # This lifecycle never creates, updates or deletes corpus items.
        return
