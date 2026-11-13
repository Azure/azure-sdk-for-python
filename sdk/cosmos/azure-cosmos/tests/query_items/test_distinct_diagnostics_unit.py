# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Check DISTINCT failure reports without contacting a Cosmos account."""

import asyncio
from types import SimpleNamespace
import xml.etree.ElementTree as ET

import pytest

from azure.core.exceptions import ServiceResponseError
from azure.cosmos._backend.errors import UnsupportedQueryError
from azure.cosmos.exceptions import CosmosHttpResponseError
from query_items.aio.test_query_async import _QueryConfig
from query_items.sync import test_query as sync_tests

pytest_plugins = ["pytester"]

QUERY = "SELECT distinct c.distinct_field from c"


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def asynchronous(request):
    return request.param


def validate(collection, asynchronous):
    if asynchronous:
        return asyncio.run(_QueryConfig._validate_distinct(collection, QUERY, [1], True, ["distinct_field"]))
    return sync_tests.TestQuery()._validate_distinct(collection, QUERY, [1], True, ["distinct_field"])


def query_rows(values, asynchronous, error=None):
    def rows():
        for value in values:
            yield {"distinct_field": value}
        if error is not None:
            raise error

    async def async_rows():
        for row in rows():
            yield row

    return async_rows() if asynchronous else rows()


@pytest.mark.parametrize(
    "error",
    [
        UnsupportedQueryError("DISTINCT query shape is unsupported"),
        ServiceResponseError("connection closed"),
        CosmosHttpResponseError(status_code=400, message="query rejected"),
        TimeoutError("page deadline expired"),
    ],
)
@pytest.mark.parametrize("during_iteration", [False, True])
def test_distinct_report_starts_with_error_and_preserves_traceback_rust(error, during_iteration, asynchronous):
    calls = []

    def query_items(**kwargs):
        calls.append(kwargs)
        if not during_iteration:
            raise error
        return query_rows([1], asynchronous, error)

    with pytest.raises(pytest.fail.Exception) as caught:
        validate(SimpleNamespace(query_items=query_items), asynchronous)
    message = str(caught.value)
    assert message.startswith(f"DISTINCT query failed: {type(error).__name__}: {error}")
    assert f"Query: {QUERY}\nPartition key: not specified" in message
    assert "Original traceback:\nTraceback" in message
    assert caught.value.pytrace is False
    expected_options = {"query": QUERY}
    if not asynchronous:
        expected_options["enable_cross_partition_query"] = True
    assert calls == [expected_options]


@pytest.mark.parametrize("values", [[1], [2], [1, 1]])
def test_distinct_diagnostics_preserve_result_assertions_rust(values, asynchronous):
    collection = SimpleNamespace(query_items=lambda **kwargs: query_rows(values, asynchronous))
    if values == [1]:
        validate(collection, asynchronous)
    else:
        with pytest.raises(AssertionError):
            validate(collection, asynchronous)


@pytest.mark.parametrize("error", [ValueError("unexpected input"), asyncio.CancelledError()])
def test_distinct_diagnostics_do_not_convert_unrelated_errors_or_cancellation_rust(error, asynchronous):
    def query_items(**kwargs):
        raise error

    with pytest.raises(type(error)) as caught:
        validate(SimpleNamespace(query_items=query_items), asynchronous)
    assert caught.value is error


def test_distinct_junit_contains_error_query_and_original_cause_rust(pytester, asynchronous):
    pytester.makepyfile(test_reporting="""
        import asyncio
        from types import SimpleNamespace
        from azure.cosmos._backend.errors import UnsupportedQueryError
        from query_items.aio.test_query_async import _QueryConfig
        from query_items.sync import test_query as sync_tests

        def test_distinct_failure():
            def rows():
                try:
                    raise RuntimeError("native DISTINCT detail")
                except RuntimeError as cause:
                    raise UnsupportedQueryError("query shape unsupported") from cause
                yield

            async def async_rows():
                for row in rows():
                    yield row

            if ASYNCHRONOUS:
                asyncio.run(_QueryConfig._validate_distinct(
                    SimpleNamespace(query_items=lambda **kwargs: async_rows()),
                    "SELECT distinct c.distinct_field from c", [1], True, ["distinct_field"]
                ))
            else:
                sync_tests.TestQuery()._validate_distinct(
                    SimpleNamespace(query_items=lambda **kwargs: rows()),
                    "SELECT distinct c.distinct_field from c", [1], True, ["distinct_field"]
                )
        """.replace("ASYNCHRONOUS", repr(asynchronous)))
    report = pytester.path / "pytest.xml"
    result = pytester.runpytest_inprocess(
        "--noconftest",
        "-o",
        "addopts=",
        "-p",
        "no:cacheprovider",
        "--junitxml",
        str(report),
        "-o",
        "junit_logging=no",
    )
    result.assert_outcomes(failed=1)
    failure = ET.parse(report).find(".//testcase/failure")
    assert failure is not None
    assert failure.get("message", "").startswith(
        "Failed: DISTINCT query failed: UnsupportedQueryError: query shape unsupported"
    )
    assert f"Query: {QUERY}" in failure.text
    assert "RuntimeError: native DISTINCT detail" in failure.text
    assert "Original traceback:" in failure.text
