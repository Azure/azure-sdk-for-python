# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Compare both public read APIs with an isolated pre-migration Python SDK.

Set COSMOS_LEGACY_SOURCE to a source-only baseline containing azure/cosmos.
Each implementation runs in its own interpreter against the same owned data.
Continuation tokens and removed scheduling options are intentional differences,
not part of this shared-contract comparison.
"""

import asyncio
from contextlib import ExitStack
import importlib
import inspect
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlsplit
from unittest.mock import patch

import pytest

if __name__ != "__main__":
    from read_items.test_read_items_native import native_database  # pylint: disable=unused-import

pytestmark = pytest.mark.cosmosEmulator


async def probe_read_items_ru(database, backend, asynchronous, *, case_names=None):
    module_name = (
        "azure.cosmos._helpers._read_many" if backend == "rust"
        else "azure.cosmos.aio._read_items_helper_async" if asynchronous
        else "azure.cosmos._read_items_helper"
    )
    collector = importlib.import_module(module_name)
    page_charges = []

    class CapturingAccumulator(collector.ResponseHeaderAccumulator):
        def __call__(self, headers, body):
            if "x-ms-request-charge" in headers:
                page_charges.append(float(headers["x-ms-request-charge"]))
            return super().__call__(headers, body)

    cases = [
        ("empty", "ru-by-id", [], None),
        ("single_existing", "ru-by-id", [("0", "0")], None),
        ("single_missing", "ru-by-id", [("missing", "missing")], None),
        ("three_same_key", "items", [(str(i), "p") for i in range(3)], None),
        ("three_distinct_keys", "ru-by-id", [(str(i), str(i)) for i in range(3)], None),
        ("three_distinct_keys_page_1", "ru-by-id", [(str(i), str(i)) for i in range(3)], 1),
        ("seventy_same_key_page_4", "items", [(str(i), "p") for i in range(70)], 4),
        ("seventy_distinct_keys", "ru-by-id", [(str(i), str(i)) for i in range(70)], None),
        ("seventy_distinct_keys_page_4", "ru-by-id", [(str(i), str(i)) for i in range(70)], 4),
        ("duplicates_and_missing", "ru-by-id", [("2", "2"), ("0", "0"), ("2", "2"), ("missing", "missing")], None),
        ("all_missing", "ru-by-id", [("missing", "missing"), ("also-missing", "also-missing")], None),
    ]
    measured = []
    for name, container_id, pairs, page_size in cases:
        if case_names is not None and name not in case_names:
            continue
        container = database.get_container_client(container_id)
        charges = []
        page_samples = []
        expected = [item_id for item_id, _ in pairs if item_id.isdecimal()]
        documents = None
        for repetition in range(4):
            page_charges.clear()
            hooks = []

            def hook(headers, body):
                hooks.append((dict(headers), list(body)))

            options = {"response_hook": hook}
            if page_size is not None:
                options["max_item_count"] = page_size
            with patch.object(collector, "ResponseHeaderAccumulator", CapturingAccumulator):
                result = container.read_items(pairs, **options)
                result = await result if asynchronous else result
            assert [row["id"] for row in result] == expected
            headers = dict(result.get_response_headers())
            assert hooks == [(headers, list(result))]
            if pairs:
                charge = float(headers["x-ms-request-charge"])
                assert math.isfinite(charge) and charge > 0
            else:
                assert headers == {}
                charge = 0.0
            if documents is not None:
                assert list(result) == documents
            documents = list(result)
            if len(pairs) > 1:
                assert page_charges
            if page_charges:
                assert sum(page_charges) == pytest.approx(charge)
            # The first call warms metadata and connections; record the next three.
            if repetition:
                charges.append(charge)
                page_samples.append(list(page_charges))
        measured.append({
            "case": name, "container": container_id, "requested": len(pairs),
            "page_size": page_size, "documents": documents, "ru": charges, "page_ru": page_samples,
        })
    return measured


def rust_style_query(items, definition):
    """Reproduce the inspected driver's scalar-key predicate for a controlled comparison."""
    assert len(definition["paths"]) == 1
    selector = "c[" + json.dumps(definition["paths"][0][1:]) + "]"
    parameters = {}
    predicates = []
    for index, (item_id, key) in enumerate(items):
        id_name, key_name = f"@__read_many_{2 * index}", f"@__read_many_{2 * index + 1}"
        parameters[id_name], parameters[key_name] = item_id, key
        predicates.append(f"(c.id = {id_name} AND {selector} = {key_name})")
    return {
        "query": "SELECT * FROM c WHERE (" + " OR ".join(predicates) + ")",
        "parameters": [{"name": name, "value": value} for name, value in sorted(parameters.items())],
    }


async def probe_query_shape_controls(database, backend, asynchronous):
    case_names = {
        "three_same_key", "seventy_same_key_page_4",
        "seventy_distinct_keys", "seventy_distinct_keys_page_4",
    }
    if backend == "rust":
        return {"actual": await probe_read_items_ru(database, backend, asynchronous, case_names=case_names)}

    builder = importlib.import_module("azure.cosmos._query_builder")._QueryBuilder
    module = importlib.import_module(
        "azure.cosmos.aio._read_items_helper_async" if asynchronous else "azure.cosmos._read_items_helper"
    )
    helper = module.ReadItemsHelperAsync if asynchronous else module.ReadItemsHelperSync
    original_init = helper.__init__
    results = {}
    for label, batch_size, use_or in (
        ("legacy", 1000, False),
        ("batch_64_only", 64, False),
        ("or_predicate_only", 1000, True),
        ("or_predicate_and_batch_64", 64, True),
    ):
        def initialize(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            self.max_items_per_query = batch_size

        with ExitStack() as patches:
            patches.enter_context(patch.object(helper, "__init__", initialize))
            if use_or:
                patches.enter_context(patch.object(
                    builder, "build_pk_and_id_in_query", staticmethod(rust_style_query)
                ))
                patches.enter_context(patch.object(
                    builder, "build_id_in_query",
                    staticmethod(lambda items: rust_style_query(items, {"paths": ["/id"]})),
                ))
            results[label] = await probe_read_items_ru(
                database, backend, asynchronous, case_names=case_names
            )
    return results


async def probe_read_all_ru(database, asynchronous, *, use_query=False):
    cases = [
        ("empty", "ru-scan-empty", 0, None),
        ("one_item", "hpk", 1, None),
        ("mixed_keys_default", "items", 76, None),
        ("mixed_keys_page_4", "items", 76, 4),
        ("mixed_keys_page_100", "items", 76, 100),
        ("by_id_default", "ru-by-id", 70, None),
        ("by_id_page_1", "ru-by-id", 70, 1),
        ("by_id_page_4", "ru-by-id", 70, 4),
        ("by_id_page_100", "ru-by-id", 70, 100),
        ("multiple_partitions_default", "ru-scan-multi", 70, None),
        ("multiple_partitions_page_4", "ru-scan-multi", 70, 4),
        ("multiple_partitions_page_100", "ru-scan-multi", 70, 100),
    ]
    measured = []
    for name, container_id, expected_count, page_size in cases:
        container = database.get_container_client(container_id)
        charges, hook_samples, page_samples = [], [], []
        documents = None
        for repetition in range(4):
            hook_charges, hook_documents = [], []

            def hook(headers, body):
                charge = float(headers["x-ms-request-charge"])
                assert math.isfinite(charge) and charge > 0
                hook_charges.append(charge)
                rows = body["Documents"] if isinstance(body, dict) else body
                assert isinstance(rows, list) and all(isinstance(row, dict) for row in rows)
                hook_documents.extend(rows)

            options = {"response_hook": hook}
            if page_size is not None:
                options["max_item_count"] = page_size
            pager = (
                container.query_items("SELECT * FROM c", enable_cross_partition_query=True, **options)
                if use_query else container.read_all_items(**options)
            )
            pages = pager.by_page()
            if asynchronous:
                groups = [[row async for row in page] async for page in pages]
            else:
                groups = [list(page) for page in pages]
            rows = sorted(
                (row for group in groups for row in group),
                key=lambda row: json.dumps(row, sort_keys=True),
            )
            assert len(rows) == expected_count and hook_charges
            assert sorted(hook_documents, key=lambda row: json.dumps(row, sort_keys=True)) == rows
            if documents is not None:
                assert rows == documents
            documents = rows
            if repetition:
                charges.append(math.fsum(hook_charges))
                hook_samples.append(hook_charges)
                page_samples.append([len(group) for group in groups])
        measured.append({
            "case": name, "container": container_id, "page_size": page_size,
            "documents": documents, "ru": charges, "hook_ru": hook_samples, "page_sizes": page_samples,
        })
    return measured


async def probe(
    endpoint, key, database_id, backend, asynchronous,
    measure_ru=False, query_controls=False, measure_all_ru=False,
):
    from azure.cosmos import CosmosClient
    from azure.cosmos.aio import CosmosClient as AsyncCosmosClient

    client = (AsyncCosmosClient if asynchronous else CosmosClient)(
        endpoint, key, _backend=backend, timeout=30
    )
    if asynchronous:
        await client.__aenter__()
    try:
        database = client.get_database_client(database_id)
        if measure_all_ru:
            return {
                "read_all": await probe_read_all_ru(database, asynchronous),
                "select_all_query": await probe_read_all_ru(database, asynchronous, use_query=True),
            }
        if query_controls:
            return await probe_query_shape_controls(database, backend, asynchronous)
        if measure_ru:
            return await probe_read_items_ru(database, backend, asynchronous)
        container = database.get_container_client("items")
        requested = [(str(index), "p") for index in reversed(range(70))]
        requested.extend([("69", "p"), ("missing", "p")])
        selected = container.read_items(requested, max_item_count=4)
        selected = await selected if asynchronous else selected
        assert [row["id"] for row in selected] == [item_id for item_id, _ in requested[:-1]]
        assert float(selected.get_response_headers()["x-ms-request-charge"]) > 0
        assert "x-ms-continuation" not in selected.get_response_headers()
        missing = container.read_items([("missing", "p"), ("also-missing", "p")])
        missing = await missing if asynchronous else missing
        assert not missing and float(missing.get_response_headers()["x-ms-request-charge"]) > 0

        pages = container.read_all_items(max_item_count=4).by_page()
        if asynchronous:
            groups = [[row async for row in page] async for page in pages]
        else:
            groups = [list(page) for page in pages]
        all_rows = [row for group in groups for row in group]
        assert len(groups) > 1 and len(all_rows) == 76

        hpk = database.get_container_client("hpk")
        selected_hpk = hpk.read_items([("a", ["t", "u"]), ("missing", ["t", "u"])])
        selected_hpk = await selected_hpk if asynchronous else selected_hpk
        assert len(selected_hpk) == 1 and selected_hpk[0]["id"] == "a"
        with pytest.raises(ValueError):
            invalid = hpk.read_items([("a", ["t"])])
            if asynchronous:
                await invalid
        return {
            "selected": list(selected),
            "all": sorted(all_rows, key=lambda row: json.dumps(row, sort_keys=True)),
            "hpk": list(selected_hpk),
        }
    finally:
        closed = client.close()
        if inspect.isawaitable(closed):
            await closed


def compare_implementations(
    native_database, tmp_path, asynchronous, *,
    measure_ru=False, query_controls=False, measure_all_ru=False,
):
    from config.settings import TestSettings

    baseline = os.environ.get("COSMOS_LEGACY_SOURCE")
    source = Path(baseline).resolve()
    current = Path(__file__).resolve().parents[2]
    assert source != current and (source / "azure" / "cosmos" / "container.py").is_file()
    assert urlsplit(TestSettings.host).hostname in ("localhost", "127.0.0.1", "::1")
    results = []
    for package, backend in ((source, "core-python"), (current, "rust")):
        env = dict(os.environ, PYTHONPATH=str(package))
        completed = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), backend, str(int(asynchronous))],
            input=json.dumps({
                "endpoint": TestSettings.host,
                "key": TestSettings.masterKey,
                "database_id": native_database.id,
                "source": str(package),
                "measure_ru": measure_ru,
                "query_controls": query_controls,
                "measure_all_ru": measure_all_ru,
            }),
            text=True, capture_output=True, check=True, timeout=120, cwd=tmp_path, env=env,
        )
        results.append(json.loads(completed.stdout))
    return results


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.skipif(
    not os.environ.get("COSMOS_LEGACY_SOURCE"),
    reason="Set COSMOS_LEGACY_SOURCE to an isolated pre-migration source tree.",
)
def test_read_apis_match_pre_migration_python(native_database, tmp_path, asynchronous):
    results = compare_implementations(native_database, tmp_path, asynchronous)
    assert results[0] == results[1]


@pytest.fixture(scope="module")
def ru_database(native_database):
    from azure.cosmos import PartitionKey

    container = native_database.create_container(
        id="ru-by-id", partition_key=PartitionKey(path="/id"), offer_throughput=400
    )
    try:
        ranges = list(container.read_feed_ranges())
        assert len(ranges) == 1, "The grouped-RU comparison requires one confirmed physical partition."
        for index in range(70):
            container.create_item({"id": str(index), "nested": [index], "text": "\u00e9"})
        yield native_database
    finally:
        native_database.delete_container(container.id)


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.skipif(
    not os.environ.get("COSMOS_LEGACY_SOURCE"),
    reason="Set COSMOS_LEGACY_SOURCE to an isolated pre-migration source tree.",
)
def test_read_items_reported_ru_comparison(ru_database, tmp_path, asynchronous):
    legacy, rust = compare_implementations(ru_database, tmp_path, asynchronous, measure_ru=True)
    comparisons = []
    assert len(legacy) == len(rust)
    for before, after in zip(legacy, rust):
        assert {key: value for key, value in before.items() if key not in {"ru", "page_ru"}} == {
            key: value for key, value in after.items() if key not in {"ru", "page_ru"}
        }
        comparisons.append({
            "case": before["case"], "requested": before["requested"],
            "returned": len(before["documents"]), "page_size": before["page_size"],
            "legacy_ru": before["ru"], "rust_ru": after["ru"],
            "legacy_page_ru": before["page_ru"], "rust_page_ru": after["page_ru"],
        })
    report = {
        "client": "async" if asynchronous else "sync",
        "environment": "local emulator", "by_id_physical_partitions": 1,
        "measurement": "reported read_items charge; one warm-up then three samples",
        "page_measurement": "accumulator inputs, not transport-attempt counts; legacy point reads bypass this collector",
        "cases": comparisons,
    }
    (tmp_path / "read-items-ru.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.skipif(
    not os.environ.get("COSMOS_LEGACY_SOURCE"),
    reason="Set COSMOS_LEGACY_SOURCE to an isolated pre-migration source tree.",
)
def test_read_items_ru_query_shape_controls(ru_database, tmp_path, asynchronous):
    controls, rust = compare_implementations(ru_database, tmp_path, asynchronous, query_controls=True)
    comparisons = []
    for index, actual in enumerate(rust["actual"]):
        variants = {}
        for label, records in controls.items():
            record = records[index]
            assert record["case"] == actual["case"] and record["documents"] == actual["documents"]
            variants[label] = {"ru": record["ru"], "page_ru": record["page_ru"]}
        comparisons.append({
            "case": actual["case"], "controls": variants,
            "rust_ru": actual["ru"], "rust_page_ru": actual["page_ru"],
        })
    report = {
        "client": "async" if asynchronous else "sync",
        "measurement": "legacy-only in-process query-shape/batch controls; unchanged Rust execution",
        "cases": comparisons,
    }
    (tmp_path / "read-items-ru-query-controls.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


@pytest.fixture(scope="module")
def read_all_ru_database(ru_database):
    from azure.cosmos import PartitionKey

    partition_counts = {}
    with ExitStack() as cleanup:
        for name, throughput, count in (("ru-scan-empty", 400, 0), ("ru-scan-multi", 12000, 70)):
            container = ru_database.create_container(
                id=name, partition_key=PartitionKey(path="/id"), offer_throughput=throughput
            )
            cleanup.callback(ru_database.delete_container, container.id)
            partition_counts[name] = len(list(container.read_feed_ranges()))
            if name == "ru-scan-multi":
                assert partition_counts[name] > 1, "The scan comparison requires multiple physical partitions."
            for index in range(count):
                container.create_item({"id": str(index), "nested": [index], "text": "\u00e9"})
        for name in ("items", "hpk", "ru-by-id"):
            partition_counts[name] = len(list(ru_database.get_container_client(name).read_feed_ranges()))
        yield ru_database, partition_counts


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.skipif(
    not os.environ.get("COSMOS_LEGACY_SOURCE"),
    reason="Set COSMOS_LEGACY_SOURCE to an isolated pre-migration source tree.",
)
def test_read_all_items_reported_ru_comparison(read_all_ru_database, tmp_path, asynchronous):
    database, partition_counts = read_all_ru_database
    legacy_report, rust_report = compare_implementations(database, tmp_path, asynchronous, measure_all_ru=True)
    legacy, rust = legacy_report["read_all"], rust_report["read_all"]
    comparisons = []
    assert len(legacy) == len(rust)
    for index, (before, after) in enumerate(zip(legacy, rust)):
        assert {key: value for key, value in before.items() if key not in {"ru", "hook_ru", "page_sizes"}} == {
            key: value for key, value in after.items() if key not in {"ru", "hook_ru", "page_sizes"}
        }
        legacy_query = legacy_report["select_all_query"][index]
        rust_query = rust_report["select_all_query"][index]
        for control in (legacy_query, rust_query):
            assert control["case"] == before["case"] and control["documents"] == before["documents"]
        comparisons.append({
            "case": before["case"], "returned": len(before["documents"]),
            "physical_partitions": partition_counts[before["container"]],
            "page_size": before["page_size"],
            "legacy_ru": before["ru"], "rust_ru": after["ru"],
            "legacy_hook_ru": before["hook_ru"], "rust_hook_ru": after["hook_ru"],
            "legacy_page_sizes": before["page_sizes"], "rust_page_sizes": after["page_sizes"],
            "legacy_query_ru": legacy_query["ru"], "rust_query_ru": rust_query["ru"],
            "legacy_query_hook_ru": legacy_query["hook_ru"], "rust_query_hook_ru": rust_query["hook_ru"],
        })
    report = {
        "client": "async" if asynchronous else "sync", "environment": "local emulator",
        "measurement": "sum of response-hook charges over each complete scan; one warm-up then three samples",
        "control": "ordinary SELECT * FROM c queries on both implementations, with the same page-size hint",
        "cases": comparisons,
    }
    (tmp_path / "read-all-items-ru.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    import azure.cosmos

    inputs = json.load(sys.stdin)
    expected = Path(inputs.pop("source")).resolve()
    assert Path(azure.cosmos.__file__).resolve().is_relative_to(expected), "Wrong SDK imported"
    print(json.dumps(asyncio.run(probe(
        **inputs, backend=sys.argv[1], asynchronous=bool(int(sys.argv[2]))
    ))))
