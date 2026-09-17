# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Direct resolved RID stamping and end-to-end header precedence, without I/O."""
from copy import deepcopy
import inspect
import pytest

from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers._request_settings import stamp_container_rid
from azure.cosmos._helpers._request_item import build_read_item_request

RID_HEADER = "x-ms-cosmos-intended-collection-rid"


@pytest.mark.parametrize("existing", [None, "", "customer-rid"])
def test_stamp_preserves_existing_option_even_when_falsey(existing):
    options = {Constants.ContainerRID: existing, "other": "untouched"}
    assert stamp_container_rid(options, "resolved-rid") is None
    assert options == {Constants.ContainerRID: existing, "other": "untouched"}


def test_stamp_takes_resolved_value_without_lookup_callback():
    assert tuple(inspect.signature(stamp_container_rid).parameters) == ("options", "container_rid")
    options = {"other": "untouched"}
    stamp_container_rid(options, "resolved-rid")
    stamp_container_rid(options, "later-rid")
    assert options == {"other": "untouched", Constants.ContainerRID: "resolved-rid"}


@pytest.mark.parametrize("resolved", [None, "", "resolved-rid"])
@pytest.mark.parametrize("options,expected", [
    ({"containerRID": "option"}, "option"),
    ({"initialHeaders": {RID_HEADER: "customer"}}, "customer"),
    ({"containerRID": "option", "initialHeaders": {RID_HEADER: "customer"}}, "customer"),
    ({"initialHeaders": {RID_HEADER: "customer"}, "containerRID": "option"}, "option"),
    ({RID_HEADER: "wire", "containerRID": "option"}, "option"),
])
def test_resolved_canonical_rid_wins_without_mutating_customer_options(resolved, options, expected):
    before = deepcopy(options)
    request = build_read_item_request(
        container_link="dbs/d/colls/c", item_id="item", partition_key_value="p",
        container_rid=resolved, request_options=options,
    )
    actual = request.settings.resource.container_rid
    if actual is None:
        actual = request.headers[RID_HEADER]
    else:
        assert RID_HEADER not in request.headers
    assert actual == (expected if resolved is None else resolved)
    assert "containerRID" not in request.headers
    assert options == before


@pytest.mark.parametrize("cached", [True, False])
def test_direct_stamp_matches_legacy_after_metadata_resolution(cached):
    cache = {"_rid": "cached-rid"} if cached else {}
    if not cache:
        cache.update({"_rid": "refreshed-rid"})
    legacy_options = {Constants.ContainerRID: cache["_rid"]}
    options = {}
    stamp_container_rid(options, cache["_rid"])
    assert options == legacy_options
