# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Run original or legacy-derived read tests using exclusively owned resources.

The original test body is unchanged; its setUp uses TestConfig pointing to a
fresh database and container. Shared conftest provisioning is disabled. This
checks key authentication, not the original shared fixture or AAD setup.
Run each backend in a separate process and save stdout for the parity reporter
with --op read_item. The default original suite expects one test; --suite copied
expects seven. Copied-suite baseline files change only the explicit backend.
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


METHOD = "::TestNoneOptions::test_container_read_item_none_options"


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
    args = parser.parse_args(argv)
    for name in ("ACCOUNT_HOST", "ACCOUNT_KEY"):
        if not os.environ.get(name):
            parser.error(f"{name} must be set explicitly for the test target")

    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT / "tests"))
    os.environ["COSMOS_BACKEND"] = args.backend
    os.environ["COSMOS_TEST_DATA_AUTH_MODE"] = "key"
    os.environ["COSMOS_PARITY_CAPTURE_OP"] = "read_item"
    options = [
        "--noconftest", "--import-mode=importlib", "-p", "common.parity_capture_plugin",
        "-p", "no:cacheprovider", "-v", "-s", "--disable-warnings", "--tb=short",
    ]
    if args.suite == "copied":
        return run_copied_suite(args.backend, options)
    if args.backend == "rust":
        path = ROOT / "tests" / "read_item" / "sync" / "legacy" / "test_none_options.py"
        return pytest.main(options + [str(path) + METHOD])

    import test_config  # pylint: disable=import-outside-toplevel

    config = test_config.TestConfig
    previous_ids = (config.TEST_DATABASE_ID, config.TEST_SINGLE_PARTITION_CONTAINER_ID)
    database_id = "read_parity_core_" + uuid.uuid4().hex
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
            path = ROOT / "tests" / "test_none_options.py"
            return pytest.main(options + [str(path) + METHOD])
        finally:
            config.TEST_DATABASE_ID, config.TEST_SINGLE_PARTITION_CONTAINER_ID = previous_ids
            client.delete_database(database_id)
            print(f"Deleted owned core-python database: {database_id}")


if __name__ == "__main__":
    sys.exit(main())
