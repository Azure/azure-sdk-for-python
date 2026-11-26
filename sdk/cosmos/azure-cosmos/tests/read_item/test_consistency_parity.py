# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Local isolated-V4 versus V5/Rust comparisons on an explicitly configured account.

Set ACCOUNT_HOST, ACCOUNT_KEY, COSMOS_TEST_EXPECTED_CONSISTENCY, and
COSMOS_V4_SOURCE (a pristine V4 package root). Each run checks the account
setting before creating owned resources. These comparisons measure API
outcomes, not cross-region freshness or replication guarantees.
"""

import asyncio
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
import sysconfig
from types import SimpleNamespace
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from common._rust_checks import backend_name, run_on_rust, run_on_rust_async


LEVELS = ("Eventual", "ConsistentPrefix", "Session", "BoundedStaleness", "Strong")
OPERATIONS = ("read_item", "read_items", "query_items", "read_all_items")
SOURCES = ("client", "request_options", "feed_options", "initial_headers")
CASES = [
    (operation, source, level)
    for operation in OPERATIONS
    for source in SOURCES
    for level in LEVELS
] + [
    ("read_items", "keyword", level) for level in LEVELS
] + [
    (operation, "account", None) for operation in OPERATIONS
]


@pytest.fixture(scope="module")
def consistency_account(record_testsuite_property, request):
    expected_level = os.environ.get("COSMOS_TEST_EXPECTED_CONSISTENCY")
    assert expected_level in LEVELS, "Set COSMOS_TEST_EXPECTED_CONSISTENCY explicitly before running."
    source = Path(os.environ["COSMOS_V4_SOURCE"]).resolve()
    assert (source / "azure" / "cosmos" / "__init__.py").is_file()
    cases = []
    for test in request.session.items:
        if test.path != Path(__file__):
            continue
        parameters = getattr(getattr(test, "callspec", None), "params", {})
        if "operation" in parameters:
            cases.append([
                "_async_" in test.name,
                parameters["operation"], parameters["source"], parameters["level"],
            ])
    endpoint, key = os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"]
    with CosmosClient(endpoint, key, _backend="core-python") as setup:
        account = setup.client_connection.GetDatabaseAccount()
        assert account.ConsistencyPolicy["defaultConsistencyLevel"] == expected_level
        record_testsuite_property("consistency_policy", json.dumps(account.ConsistencyPolicy))
        record_testsuite_property("read_regions", json.dumps(account.ReadableLocations))
        record_testsuite_property("write_regions", json.dumps(account.WritableLocations))
        record_testsuite_property("multiple_write_locations", str(account._EnableMultipleWritableLocations))
        database = setup.create_database("consistency-parity-" + uuid.uuid4().hex)
        try:
            container = database.create_container(
                id="orders", partition_key=PartitionKey(path="/pk"), offer_throughput=400,
            )
            item = {"id": "order-42", "pk": "customer-17", "value": 1}
            container.create_item(dict(item))
            account = SimpleNamespace(
                endpoint=endpoint, key=key, database_id=database.id, item=item,
                consistency=expected_level,
            )
            # Ignore inherited source paths and editable-install hooks in the V4 process.
            command = [
                sys.executable, "-I", "-S", "-c",
                "import runpy,sys; sys.path[:0]=sys.argv[1:4]; runpy.run_path(sys.argv[4],run_name='__main__')",
                str(source), sysconfig.get_paths()["purelib"], str(Path(__file__).resolve().parents[1]),
                str(Path(__file__).resolve()),
            ]
            baseline = subprocess.run(
                command,
                input=json.dumps({
                    "endpoint": endpoint, "database_id": database.id, "item": item, "source": str(source),
                    "cases": cases,
                }),
                capture_output=True, text=True, timeout=600, check=False,
            )
            assert baseline.returncode == 0, baseline.stderr
            result = json.loads(baseline.stdout)
            record_testsuite_property("v4_version", result["version"])
            record_testsuite_property("v4_source", result["module"])
            record_testsuite_property("v4_outcomes", json.dumps(result["outcomes"]))
            account.v4 = result["outcomes"]
            yield account
        finally:
            setup.delete_database(database.id)


def _client_options(source, level):
    return {"consistency_level": level} if source == "client" else {}


def _request_options(source, level):
    if source in ("account", "client"):
        return {}
    if source == "keyword":
        return {"consistency_level": level}
    name = "x-ms-consistency-level" if source == "initial_headers" else "consistencyLevel"
    return {source: {name: level}}


def _headers_observer(snapshots):
    def observe(headers, _body):
        snapshots.append({
            "request_charge": headers.get("x-ms-request-charge"),
            "activity_id": headers.get("x-ms-activity-id"),
            "has_session_token": bool(headers.get("x-ms-session-token")),
        })
    return observe


def _observed_options(operation, source, level, snapshots):
    options = _request_options(source, level)
    # Pristine V4 duplicates an explicit read_all_items response_hook internally.
    # Do not let optional observation change the consistency request under test.
    if operation != "read_all_items":
        options["response_hook"] = _headers_observer(snapshots)
    return options


def _read(container, operation, item, options):
    if operation == "read_item":
        return [container.read_item(item["id"], partition_key=item["pk"], **options)]
    if operation == "read_items":
        return list(container.read_items([(item["id"], item["pk"])], **options))
    if operation == "query_items":
        return list(container.query_items("SELECT * FROM c", partition_key=item["pk"], **options))
    return list(container.read_all_items(**options))


async def _read_async(container, operation, item, options):
    if operation == "read_item":
        return [await container.read_item(item["id"], partition_key=item["pk"], **options)]
    if operation == "read_items":
        return list(await container.read_items([(item["id"], item["pk"])], **options))
    if operation == "query_items":
        return [
            row async for row in container.query_items("SELECT * FROM c", partition_key=item["pk"], **options)
        ]
    return [row async for row in container.read_all_items(**options)]


def _compare(outcomes, expected, record_property):
    for backend, outcome in outcomes.items():
        record_property(backend, json.dumps(outcome))
    for backend, outcome in outcomes.items():
        assert "status" in outcome, (backend, outcome)
    assert outcomes["rust"]["status"] == outcomes["v4"]["status"], outcomes
    for outcome in outcomes.values():
        if outcome["status"] == 200:
            assert outcome["items"] == [expected]


@pytest.mark.parametrize("operation,source,level", CASES)
def test_read_consistency_matches_v4(consistency_account, operation, source, level, record_property):
    account = consistency_account
    outcomes = {"v4": account.v4[_case_key(False, operation, source, level)]}
    snapshots = []
    with CosmosClient(
        account.endpoint, account.key, _backend="rust", **_client_options(source, level),
    ) as client:
        container = client.get_database_client(account.database_id).get_container_client("orders")
        options = _observed_options(operation, source, level, snapshots)
        try:
            rows = run_on_rust(client, lambda: _read(container, operation, account.item, options))
            outcomes["rust"] = {
                "status": 200,
                "items": [{field: row[field] for field in account.item} for row in rows],
                "responses": snapshots,
            }
        except CosmosHttpResponseError as error:
            assert error.status_code == 400, "Unexpected service failure, not a consistency comparison"
            if level == "Strong":
                assert "default consistency level is Strong" in error.message
            outcomes["rust"] = {"status": error.status_code, "message": error.message, "responses": snapshots}
    _compare(outcomes, account.item, record_property)


@pytest.mark.asyncio
@pytest.mark.parametrize("operation,source,level", CASES)
async def test_read_consistency_async_matches_v4(
    consistency_account, operation, source, level, record_property,
):
    account = consistency_account
    outcomes = {"v4": account.v4[_case_key(True, operation, source, level)]}
    snapshots = []
    async with AsyncCosmosClient(
        account.endpoint, account.key, _backend="rust", **_client_options(source, level),
    ) as client:
        container = client.get_database_client(account.database_id).get_container_client("orders")
        options = _observed_options(operation, source, level, snapshots)
        try:
            rows = await run_on_rust_async(client, lambda: _read_async(container, operation, account.item, options))
            outcomes["rust"] = {
                "status": 200,
                "items": [{field: row[field] for field in account.item} for row in rows],
                "responses": snapshots,
            }
        except CosmosHttpResponseError as error:
            assert error.status_code == 400, "Unexpected service failure, not a consistency comparison"
            if level == "Strong":
                assert "default consistency level is Strong" in error.message
            outcomes["rust"] = {"status": error.status_code, "message": error.message, "responses": snapshots}
    _compare(outcomes, account.item, record_property)


@pytest.mark.parametrize("backend", ["core-python", "rust"])
def test_default_session_consistency_retains_legacy_assertions(consistency_account, backend):
    """Retain the public assertions from TestUserConfigs.test_default_account_consistency."""
    account = consistency_account
    if account.consistency != "Session":
        pytest.skip("The original test explicitly requires a Session account.")
    identifiers = ["session-" + uuid.uuid4().hex for _ in range(2)]
    with CosmosClient(account.endpoint, account.key, _backend=backend) as client:
        assert backend_name(client) == backend
        container = client.get_database_client(account.database_id).get_container_client("orders")

        def checked(owner, call):
            return run_on_rust(owner, call) if backend == "rust" else call()

        created = []
        try:
            tokens = []
            for identifier in identifiers:
                response = checked(client, lambda: container.create_item({"id": identifier, "pk": "session"}))
                created.append(identifier)
                tokens.append(response.get_response_headers()["x-ms-session-token"])
            assert tokens[0] != tokens[1]
            response = checked(client, lambda: container.read_item(identifiers[1], partition_key="session"))
            assert response.get_response_headers()["x-ms-session-token"] == tokens[1]
            for level in ("Eventual", "Strong"):
                with CosmosClient(
                    account.endpoint, account.key, _backend=backend, consistency_level=level,
                ) as override_client:
                    override_container = override_client.get_database_client(
                        account.database_id,
                    ).get_container_client("orders")
                    call = lambda: override_container.read_item(identifiers[1], partition_key="session")
                    if level == "Strong":
                        with pytest.raises(CosmosHttpResponseError) as caught:
                            checked(override_client, call)
                        assert caught.value.status_code == 400
                    else:
                        assert checked(override_client, call)["id"] == identifiers[1]
            with CosmosClient(account.endpoint, account.key, _backend="core-python") as setup:
                properties = setup.client_connection.GetDatabaseAccount()
                assert properties.ConsistencyPolicy["defaultConsistencyLevel"] == account.consistency
        finally:
            for identifier in created:
                checked(client, lambda: container.delete_item(identifier, partition_key="session"))


def _case_key(asynchronous, operation, source, level):
    return json.dumps([asynchronous, operation, source, level])


async def _v4_outcomes(configuration):
    import azure.cosmos

    module = Path(inspect.getfile(CosmosClient)).resolve()
    assert module.is_relative_to(Path(configuration["source"]).resolve()), str(module)
    assert azure.cosmos.__version__.startswith("4."), azure.cosmos.__version__
    outcomes = {}
    for asynchronous in (False, True):
        for is_async, operation, source, level in configuration["cases"]:
            if is_async != asynchronous:
                continue
            snapshots = []
            options = _observed_options(operation, source, level, snapshots)
            client_type = AsyncCosmosClient if asynchronous else CosmosClient
            client = client_type(
                configuration["endpoint"], os.environ["ACCOUNT_KEY"], **_client_options(source, level),
            )
            try:
                if asynchronous:
                    async with client:
                        container = client.get_database_client(
                            configuration["database_id"],
                        ).get_container_client("orders")
                        rows = await _read_async(container, operation, configuration["item"], options)
                else:
                    with client:
                        container = client.get_database_client(
                            configuration["database_id"],
                        ).get_container_client("orders")
                        rows = _read(container, operation, configuration["item"], options)
                outcome = {
                    "status": 200,
                    "items": [{field: row[field] for field in configuration["item"]} for row in rows],
                    "responses": snapshots,
                }
            except CosmosHttpResponseError as error:
                assert error.status_code == 400, "Unexpected V4 service failure"
                outcome = {"status": error.status_code, "message": error.message, "responses": snapshots}
            except (TypeError, NotImplementedError) as error:
                # Surface this individual V4 call as a failed comparison, not 180 setup errors.
                outcome = {"error_type": type(error).__name__, "message": str(error)}
            outcomes[_case_key(asynchronous, operation, source, level)] = outcome
    return {"version": azure.cosmos.__version__, "module": str(module), "outcomes": outcomes}


if __name__ == "__main__":
    print(json.dumps(asyncio.run(_v4_outcomes(json.load(sys.stdin)))))
