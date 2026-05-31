# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
# cspell:ignore JOBID

"""End-to-end tests for cross-partition SELECT VALUE AVG(...) over
partitions whose AVG argument is null or undefined.

The container holds documents under three partition keys:
  pk1 -> every doc has value=100
  pk2 -> value field is absent on every doc
  pk3 -> value field is explicitly null on every doc

Cross-partition AVG must raise ``ValueError`` with the outer
"Unsupported query shape for range-scoped pagination" prefix and the
"SELECT VALUE AVG" callout. Returning any numeric payload is a silent
contract break (the prior single-partition answer leaking through).

A multi-partition precondition (``read_feed_ranges() > 1``) skips the
cross-partition tests on single-partition lanes so they cannot silently
pass without exercising the merge path.

The backend's choice of empty vs ``[null]`` partial for an all-null
partition is not contracted; both shapes must raise the same error.
"""

import os
import re
import unittest
import uuid

import pytest

import test_config
from azure.cosmos import CosmosClient
from azure.cosmos.partition_key import PartitionKey


CONFIG = test_config.TestConfig()
HOST = CONFIG.host
KEY = CONFIG.masterKey
DATABASE_ID = CONFIG.TEST_DATABASE_ID


def _build_lane_suffix() -> str:
    auth_mode = os.getenv("COSMOS_TEST_DATA_AUTH_MODE", "key")
    run_id = (
        os.getenv("SYSTEM_JOBID")
        or os.getenv("BUILD_BUILDID")
        or os.getenv("GITHUB_RUN_ID")
        or os.getenv("TF_BUILD_BUILDID")
        or "local"
    )
    raw = "{}-{}".format(auth_mode, run_id)
    safe = re.sub(r"[^A-Za-z0-9-]", "-", raw).strip("-")
    return safe[:40] if safe else "local"


PARTITION_KEY = CONFIG.TEST_CONTAINER_PARTITION_KEY
# Lane suffix keeps parallel CI runs from colliding on the container name.
CONTAINER_ID = (
    "Query FeedRange AVG-sparse "
    + _build_lane_suffix()
    + " "
    + CONFIG.TEST_MULTI_PARTITION_CONTAINER_ID
)
THROUGHPUT = CONFIG.THROUGHPUT_FOR_5_PARTITIONS

# Three pk values, one per partition shard, with different `value` shapes
# so AVG across the full feed_range combines mixed partials:
#   pk1 -> value=100
#   pk2 -> value field absent
#   pk3 -> value=null
PK_VALUES = ("pk1", "pk2", "pk3")
DOCS_PER_PK = 5


def _seed_docs():
    docs = []
    for _ in range(DOCS_PER_PK):
        docs.append({PARTITION_KEY: "pk1", "id": str(uuid.uuid4()), "value": 100})
    for _ in range(DOCS_PER_PK):
        docs.append({PARTITION_KEY: "pk2", "id": str(uuid.uuid4())})
    for _ in range(DOCS_PER_PK):
        docs.append({PARTITION_KEY: "pk3", "id": str(uuid.uuid4()), "value": None})
    return docs


@pytest.fixture(scope="class", autouse=True)
def setup_and_teardown():
    key_db = CosmosClient(HOST, KEY).get_database_client(DATABASE_ID)
    data_db = test_config.TestConfig.create_data_client().get_database_client(DATABASE_ID)

    key_db.create_container_if_not_exists(
        id=CONTAINER_ID,
        partition_key=PartitionKey(path="/" + PARTITION_KEY, kind="Hash"),
        offer_throughput=THROUGHPUT,
    )
    container = data_db.get_container_client(CONTAINER_ID)
    for doc in _seed_docs():
        container.upsert_item(body=doc)

    yield {"data_db": data_db, "key_db": key_db}

    try:
        key_db.delete_container(CONTAINER_ID)
    except Exception:  # pylint: disable=broad-except
        # Lane-suffixed container name makes leftover containers safe.
        pass


def _get_container(setup_and_teardown):
    return setup_and_teardown["data_db"].get_container_client(CONTAINER_ID)


def _require_multi_partition(container) -> None:
    """Skip the test if the container has only one physical partition.

    The cross-partition AVG raise only happens on the second merge call.
    On a one-partition lane that call never happens, so the test would
    pass without exercising the bug.
    """
    feed_range_count = len(list(container.read_feed_ranges()))
    if feed_range_count <= 1:
        pytest.skip(
            "Cross-partition AVG contract requires >1 physical partition; "
            "container reports {} feed range(s).".format(feed_range_count)
        )


def _full_hash_range_feed_range():
    # A feed_range covering every physical partition of the container.
    full_range = test_config.create_range(
        range_min="",
        range_max="FF",
        is_min_inclusive=True,
        is_max_inclusive=False,
    )
    return test_config.create_feed_range_in_dict(full_range)


@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADQuery
class TestQueryFeedRangeAvgSparse:

    AVG_QUERY = 'SELECT VALUE AVG(c["value"]) FROM c'

    def _assert_avg_value_error(self, excinfo) -> None:
        """Assert the full AVG raise contract end-to-end.

        Outer message must include the range-scoped pagination prefix
        and the "SELECT VALUE AVG" callout. ``__cause__`` must chain
        the inner merge ``ValueError`` with its original text intact
        so callers can match on the inner message without parsing the
        outer rephrased one.
        """
        outer_message = str(excinfo.value)
        assert "Unsupported query shape for range-scoped pagination" in outer_message, (
            "Unexpected outer ValueError message: {!r}".format(outer_message)
        )
        assert "SELECT VALUE AVG" in outer_message, (
            "Outer message must mention SELECT VALUE AVG: {!r}".format(outer_message)
        )

        cause = excinfo.value.__cause__
        assert isinstance(cause, ValueError), (
            "Outer ValueError must chain the inner merge ValueError via "
            "`raise ... from`; got __cause__={!r}".format(cause)
        )
        inner_message = str(cause)
        assert "VALUE AVG aggregate merge across partitions is not supported client-side." in inner_message, (
            "Inner __cause__ must preserve the original merge error text; "
            "got {!r}".format(inner_message)
        )

    def test_avg_full_feed_range_with_null_and_missing_partitions(self, setup_and_teardown):
        """AVG over the full feed_range with mixed numeric, null, and
        missing value fields MUST raise ``ValueError``."""
        container = _get_container(setup_and_teardown)
        _require_multi_partition(container)
        feed_range = _full_hash_range_feed_range()

        with pytest.raises(ValueError) as excinfo:
            list(container.query_items(
                query=self.AVG_QUERY, feed_range=feed_range,
            ))
        self._assert_avg_value_error(excinfo)

    def test_avg_full_feed_range_with_explicit_null_only_filter(self, setup_and_teardown):
        """AVG over rows where value is explicitly null, across the full
        feed_range, MUST raise ``ValueError``."""
        container = _get_container(setup_and_teardown)
        _require_multi_partition(container)
        feed_range = _full_hash_range_feed_range()
        query = 'SELECT VALUE AVG(c["value"]) FROM c WHERE IS_NULL(c["value"])'

        with pytest.raises(ValueError) as excinfo:
            list(container.query_items(
                query=query, feed_range=feed_range,
            ))
        self._assert_avg_value_error(excinfo)

    def test_avg_full_feed_range_with_missing_field_argument(self, setup_and_teardown):
        """AVG over a field that is undefined in every row across every
        partition MUST raise ``ValueError``."""
        container = _get_container(setup_and_teardown)
        _require_multi_partition(container)
        feed_range = _full_hash_range_feed_range()
        query = 'SELECT VALUE AVG(c["never_seeded"]) FROM c'

        with pytest.raises(ValueError) as excinfo:
            list(container.query_items(
                query=query, feed_range=feed_range,
            ))
        self._assert_avg_value_error(excinfo)

    def test_avg_single_partition_with_null_values_still_succeeds(self, setup_and_teardown):
        # Single-partition AVG must not raise. The raise is keyed on
        # the cross-partition merge step, not on AVG-of-nulls semantics.
        container = _get_container(setup_and_teardown)
        feed_range = container.feed_range_from_partition_key("pk3")

        items = list(container.query_items(
            query=self.AVG_QUERY, feed_range=feed_range,
        ))
        assert len(items) <= 1, (
            "Single-partition AVG must not produce >1 rows; got {!r}".format(items)
        )


if __name__ == "__main__":
    unittest.main()

