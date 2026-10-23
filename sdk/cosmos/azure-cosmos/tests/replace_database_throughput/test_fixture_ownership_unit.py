# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Replacement coverage must survive failures without hiding errors or leaking fixtures."""

import asyncio
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos import ThroughputProperties, exceptions
from replace_database_throughput import _fixtures


ROOT = Path(__file__).resolve().parents[2]


def _load(surface, filename):
    path = Path(__file__).parent / surface / "legacy" / filename
    spec = importlib.util.spec_from_file_location("owned_replacement_" + surface + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("autoscale", [False, True], ids=["manual", "autoscale"])
@pytest.mark.parametrize("failure", [
    None, "setup", "create", "lookup", "replace", "assertion", "delete", "close",
    "assertion-and-delete", "conflict",
])
def test_copied_fixture_cleans_up_without_hiding_failures_rust(monkeypatch, asynchronous, autoscale, failure):
    module = _load("aio" if asynchronous else "sync", "test_auto_scale.py" if autoscale else "test_crud_database.py")
    events = []
    attempted = []
    mock_type = AsyncMock if asynchronous else MagicMock
    client = MagicMock()
    target_call = 2 if autoscale else 1

    def resource(capacity, resource_id):
        value = capacity if isinstance(capacity, ThroughputProperties) else ThroughputProperties(
            offer_throughput=capacity,
        )
        proxy = MagicMock(id=resource_id)

        def get():
            if failure == "lookup":
                raise RuntimeError("lookup failed")
            if failure in ("assertion", "assertion-and-delete"):
                return ThroughputProperties(offer_throughput=-1, auto_scale_max_throughput=-1)
            return value

        def replace(throughput):
            nonlocal value
            if failure == "replace":
                raise RuntimeError("replacement failed")
            value = throughput if isinstance(throughput, ThroughputProperties) else ThroughputProperties(
                offer_throughput=throughput,
            )
            return value

        proxy.get_throughput = mock_type(side_effect=get)
        proxy.replace_throughput = mock_type(side_effect=replace)
        proxy.create_container = mock_type(
            side_effect=lambda *, id, offer_throughput, **kwargs: resource(offer_throughput, id),
        )
        return proxy

    def create(*, id, offer_throughput=None):
        attempted.append(id)
        if (failure == "setup" and len(attempted) == 1) or (
            failure == "create" and len(attempted) == target_call
        ):
            raise RuntimeError("creation failed")
        if failure == "conflict" and len(attempted) == target_call:
            raise exceptions.CosmosResourceExistsError(status_code=409, message="not owned")
        return resource(offer_throughput, id)

    def delete(database_id):
        events.append(("delete", database_id))
        if failure in ("delete", "assertion-and-delete"):
            raise RuntimeError("cleanup failed")

    def close():
        events.append(("close", None))
        if failure == "close":
            raise RuntimeError("close failed")

    client.create_database = mock_type(side_effect=create)
    client.delete_database = mock_type(side_effect=delete)
    client.close = mock_type(side_effect=close)
    monkeypatch.setattr(module, "CosmosClient", MagicMock(return_value=client))
    classname = "TestAutoScale" if autoscale else "TestCRUDDatabaseOperations"
    method = "test_autoscale_replace_throughput" if autoscale else "test_database_level_offer_throughput"
    if asynchronous:
        classname += "Async"
        method = "test_replace_throughput_async" if autoscale else method + "_async"
    case = getattr(module, classname)(method + "_rust")
    result = unittest.TestResult()
    case.run(result)

    assert result.testsRun == 1
    assert result.wasSuccessful() is (failure is None)
    assert events[-1] == ("close", None)
    client.close.assert_called_once()
    expected = set(attempted)
    if failure == "conflict":
        expected.remove(attempted[-1])
    assert {database_id for event, database_id in events if event == "delete"} == expected
    assert None not in expected
    if failure in ("assertion", "assertion-and-delete"):
        assert len(result.failures) == 1
    if failure in ("delete", "assertion-and-delete"):
        assert any("cleanup failed" in trace for _, trace in result.errors)
    if failure in ("setup", "create"):
        assert any("creation failed" in trace for _, trace in result.errors)
    assert "delete_container" not in [call[0] for call in client.mock_calls]


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("status", [404, 403])
def test_owned_database_only_ignores_missing_cleanup_rust(asynchronous, status):
    client = MagicMock()
    error = (
        exceptions.CosmosResourceNotFoundError(status_code=404)
        if status == 404 else exceptions.CosmosHttpResponseError(status_code=403)
    )
    mock_type = AsyncMock if asynchronous else MagicMock
    client.create_database = mock_type()
    client.delete_database = mock_type(side_effect=error)

    async def run_async():
        async with _fixtures.owned_database_async(client, "owned"):
            pass

    def run():
        if asynchronous:
            asyncio.run(run_async())
        else:
            with _fixtures.owned_database(client, "owned"):
                pass

    if status == 404:
        run()
    else:
        with pytest.raises(exceptions.CosmosHttpResponseError) as caught:
            run()
        assert caught.value is error
    client.delete_database.assert_called_once_with("owned")


@pytest.mark.parametrize("phase", ["create", "body"])
def test_async_owned_database_cleans_up_after_cancellation_rust(phase):
    async def run():
        entered = asyncio.Event()
        client = MagicMock()

        async def wait():
            entered.set()
            await asyncio.Event().wait()

        async def create(**kwargs):
            if phase == "create":
                await wait()
            return MagicMock()

        client.create_database = AsyncMock(side_effect=create)
        client.delete_database = AsyncMock()

        async def use():
            async with _fixtures.owned_database_async(client, "owned"):
                await wait()

        task = asyncio.create_task(use())
        try:
            await asyncio.wait_for(entered.wait(), 3)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(task, 3)
            client.delete_database.assert_awaited_once_with("owned")
        finally:
            if not task.done():
                task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    asyncio.run(run())


@pytest.mark.parametrize("failure", [None, "second-create", "second-conflict", "delete", "body-and-delete"])
def test_pair_fixture_drains_all_resources_and_closes_client_rust(monkeypatch, failure):
    monkeypatch.setenv("ACCOUNT_HOST", "https://unused.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unused")
    client = MagicMock()
    factory = MagicMock(return_value=client)
    monkeypatch.setattr(_fixtures, "CosmosClient", factory)
    created = []
    events = []

    def create(*, id, **kwargs):
        created.append(id)
        if len(created) == 2:
            if failure == "second-create":
                raise RuntimeError("creation failed")
            if failure == "second-conflict":
                raise exceptions.CosmosResourceExistsError(status_code=409)
        return MagicMock(id=id)

    def delete(database_id):
        events.append(database_id)
        if failure in ("delete", "body-and-delete"):
            raise RuntimeError("cleanup failed")

    client.create_database.side_effect = create
    client.delete_database.side_effect = delete
    client.close.side_effect = lambda: events.append("close")
    fixture = _fixtures.database_per_backend.__wrapped__()
    make = next(fixture)
    try:
        if failure in ("second-create", "second-conflict"):
            with pytest.raises(RuntimeError if failure == "second-create" else exceptions.CosmosResourceExistsError):
                make(1000)
        else:
            first = make(1000)
            second = make(None)
            assert first["rust"] != first["core-python"]
            assert second["rust"] == second["core-python"]
            assert len(created) == 3
    finally:
        if failure == "body-and-delete":
            with pytest.raises(RuntimeError, match="cleanup failed") as caught:
                fixture.throw(AssertionError("original assertion"))
            chain = []
            error = caught.value
            while error is not None:
                chain.append(str(error))
                error = error.__context__
            assert "original assertion" in chain
        elif failure == "delete":
            with pytest.raises(RuntimeError, match="cleanup failed"):
                next(fixture)
        else:
            with pytest.raises(StopIteration):
                next(fixture)
    expected = set(created[:-1] if failure == "second-conflict" else created)
    assert set(events[:-1]) == expected
    assert events[-1] == "close"
    assert len(events) == len(expected) + 1
    factory.assert_called_once_with("https://unused.invalid", "unused", _backend="rust")


def test_replacement_copies_collect_without_retired_sources_rust():
    script = r'''
import importlib.util
import os
from pathlib import Path
import sys

root = Path.cwd()
blocked = {
    "test_auto_scale", "test_auto_scale_async", "test_crud_database", "test_crud_database_async",
    "test_cosmos_responses", "test_cosmos_responses_async",
    "test_crud_response_payload_on_write_disabled",
    "test_crud_response_payload_on_write_disabled_async", "test_config",
}
paths = {os.path.normcase(str(root / "tests" / (name + ".py"))) for name in blocked}
def guard(event, args):
    if event == "import" and args[0] in blocked:
        raise AssertionError("Imported retired test source: " + args[0])
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        if os.path.normcase(os.path.abspath(os.fsdecode(args[0]))) in paths:
            raise AssertionError("Read retired test source")
sys.addaudithook(guard)
spec = importlib.util.spec_from_file_location("runner", root / "scripts/v5/run_database_throughput_parity.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
targets = [target for path in runner.test_files("replace") for target in runner.test_targets(path, "replace")]
class Counts:
    def pytest_collection_finish(self, session):
        assert len(session.items) == 8
import pytest
raise SystemExit(pytest.main([
    "--noconftest", "--import-mode=importlib", "--collect-only", "-q",
    "-m", "cosmosEmulator", "-p", "no:cacheprovider", *targets,
], plugins=[Counts()]))
'''
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join((str(ROOT), str(ROOT / "tests")))
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("PYTEST_ADDOPTS", None)
    env.pop("COSMOS_PARITY_CAPTURE_OP", None)
    result = subprocess.run(
        [sys.executable, "-c", script], cwd=ROOT, env=env,
        capture_output=True, text=True, timeout=60, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
