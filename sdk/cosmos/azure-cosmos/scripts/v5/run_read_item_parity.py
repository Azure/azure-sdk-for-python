# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Run original item tests or copied reads using exclusively owned resources.

Runs the original test methods; their setUp uses TestConfig pointing to a
fresh database and container. Shared conftest provisioning is disabled. This
checks key authentication, not the original shared fixture or AAD setup.
Run each backend in a separate process and save stdout for the parity reporter
with the same --op. The default operation is read_item; create_item,
replace_item and delete_item select their original test or Rust copy. Upsert selects both the
None-options test and test_document_upsert (two tests). Other original selections expect one test;
--suite copied supports read_item only and expects seven. Copied-suite baseline
files change only the explicit backend.
query_items defaults to the None-parameters/filter test or its Rust copy
(one test with four query calls). --query-test ordering selects the original
partition-scoped ORDER BY/paging test or its Rust copy instead.
--query-test offset selects the original seven OFFSET LIMIT queries or their
self-contained copy; --surface aio selects its async counterpart (sync is default).
--query-test distinct selects the original four DISTINCT queries or their
self-contained copy, also supporting --surface aio.
--query-test top compares the self-contained TOP copy on both backends,
changing only its backend pin for core Python. Its adapted fixture and
public paging checks do not audit the original cross-partition setup or
legacy private iterator-class assertion. No selection includes lesson scenarios.
"""

import argparse
import os
from pathlib import Path
import sys
import uuid
from tempfile import TemporaryDirectory

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from azure.cosmos import CosmosClient, PartitionKey  # pylint: disable=wrong-import-position


QUERY_METHODS = {
    "parameters": "::TestQuery::test_query_items_with_parameters_none",
    "ordering": "::TestQuery::test_query_pagination_with_max_item_count",
    "top": "::TestCrossPartitionTopOrderBy::test_orderby_top_query",
    "offset": "::TestQuery::test_offset_limit",
    "distinct": "::TestQuery::test_distinct",
}

ASYNC_QUERY_METHODS = {
    "offset": "::TestQueryAsync::test_offset_limit_async",
    "distinct": "::TestQueryAsync::test_distinct_async",
}

METHODS = {
    "read_item": "::TestNoneOptions::test_container_read_item_none_options",
    "create_item": "::TestNoneOptions::test_container_create_item_none_options",
    "replace_item": "::TestNoneOptions::test_replace_item_none_options",
    "upsert_item": "::TestNoneOptions::test_upsert_item_none_options",
    "delete_item": "::TestNoneOptions::test_delete_item_none_options",
    "query_items": QUERY_METHODS["parameters"],
}
METHOD = METHODS["read_item"]


def run_copied_suite(backend, options):
    from run_database_throughput_parity import _source_for_backend

    files = [
        ROOT / "tests" / "read_item" / surface / "legacy" / name
        for surface, names in (
            ("sync", ("test_none_options.py", "test_headers.py", "test_crud.py")),
            ("aio", ("test_none_options.py", "test_headers.py", "test_crud_async.py")),
        )
        for name in names
    ]
    for path in files:
        _source_for_backend(path, "rust")
    if backend == "rust":
        return pytest.main(options + [str(path) for path in files])
    artifacts = ROOT / "docs" / "V5" / "_parity_runs"
    artifacts.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="read_item_corepy_", dir=artifacts) as temporary:
        baseline_files = []
        for path in files:
            target = Path(temporary) / path.parent.parent.name / path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(_source_for_backend(path, "core-python"), encoding="utf-8")
            baseline_files.append(str(target))
        return pytest.main(options + baseline_files)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", required=True, choices=("core-python", "rust"))
    parser.add_argument("--suite", choices=("original", "copied"), default="original")
    parser.add_argument("--op", choices=tuple(METHODS), default="read_item")
    parser.add_argument("--query-test", choices=tuple(QUERY_METHODS))
    parser.add_argument("--surface", choices=("sync", "aio"), default="sync")
    args = parser.parse_args(argv)
    if args.suite == "copied" and args.op != "read_item":
        parser.error("--suite copied only supports --op read_item")
    if args.query_test is not None and args.op != "query_items":
        parser.error("--query-test requires --op query_items")
    if args.surface == "aio" and not (args.op == "query_items" and args.query_test in ASYNC_QUERY_METHODS):
        parser.error("--surface aio requires --op query_items --query-test offset or distinct")
    for name in ("ACCOUNT_HOST", "ACCOUNT_KEY"):
        if not os.environ.get(name):
            parser.error(f"{name} must be set explicitly for the test target")

    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT / "tests"))
    os.environ["COSMOS_BACKEND"] = args.backend
    os.environ["COSMOS_TEST_DATA_AUTH_MODE"] = "key"
    os.environ["COSMOS_PARITY_CAPTURE_OP"] = args.op
    os.environ.pop("COSMOS_PARITY_CAPTURE_BACKEND_LABEL", None)
    method = QUERY_METHODS[args.query_test] if args.query_test else METHODS[args.op]
    source_file = "test_query.py" if args.op == "query_items" else "test_none_options.py"
    if args.query_test == "top":
        source_file = "test_orderby.py"
    if args.surface == "aio":
        source_file = "test_query_async.py"
        method = ASYNC_QUERY_METHODS[args.query_test]
    selections = [(source_file, method)]
    if args.op == "upsert_item":
        selections.append(("test_crud.py", "::TestCRUDOperations::test_document_upsert"))
    options = [
        "--noconftest", "--import-mode=importlib", "-p", "common.parity_capture_plugin",
        "-p", "no:cacheprovider", "-v", "-s", "--disable-warnings", "--tb=short",
    ]
    if args.suite == "copied":
        return run_copied_suite(args.backend, options)
    if args.backend == "rust":
        folder = ROOT / "tests" / args.op / args.surface / "legacy"
        return pytest.main(options + [str(folder / filename) + node for filename, node in selections])

    if args.query_test == "top":
        from run_database_throughput_parity import _source_for_backend

        source = ROOT / "tests" / "query_items" / "sync" / "legacy" / source_file
        artifacts = ROOT / "docs" / "V5" / "_parity_runs"
        artifacts.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(prefix="query_top_corepy_", dir=artifacts) as temporary:
            target = Path(temporary) / source_file
            target.write_text(_source_for_backend(source, args.backend), encoding="utf-8")
            return pytest.main(options + [str(target) + method])

    import test_config  # pylint: disable=import-outside-toplevel

    config = test_config.TestConfig
    previous_ids = (
        config.TEST_DATABASE_ID, config.TEST_SINGLE_PARTITION_CONTAINER_ID,
        config.TEST_MULTI_PARTITION_CONTAINER_ID,
    )
    database_id = args.op.removesuffix("_item") + "_parity_core_" + uuid.uuid4().hex
    container_id = "orders"
    with CosmosClient(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python",
    ) as client:
        database = client.create_database(database_id)
        print(f"Owned core-python database: {database_id}")
        try:
            database.create_container(id=container_id, partition_key=PartitionKey(path="/pk"))
            config.TEST_DATABASE_ID = database_id
            config.TEST_SINGLE_PARTITION_CONTAINER_ID = container_id
            if args.op == "upsert_item":
                config.TEST_MULTI_PARTITION_CONTAINER_ID = container_id
            return pytest.main(options + [
                str(ROOT / "tests" / filename) + node for filename, node in selections
            ])
        finally:
            (config.TEST_DATABASE_ID, config.TEST_SINGLE_PARTITION_CONTAINER_ID,
             config.TEST_MULTI_PARTITION_CONTAINER_ID) = previous_ids
            client.delete_database(database_id)
            print(f"Deleted owned core-python database: {database_id}")


if __name__ == "__main__":
    sys.exit(main())
