# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline checks of resolved container-id option/header helpers.

These helpers are used where Python already has a resolved id. The tests
check precedence and mutation rules; they do not establish that every
Rust item request carries this header or test service-side enforcement.
"""
from copy import deepcopy
import inspect
import pytest

from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._helpers._request_settings import stamp_container_rid
from azure.cosmos._helpers._request_item import build_read_item_request

RID_HEADER = "x-ms-cosmos-intended-collection-rid"


@pytest.mark.parametrize("existing", [None, "", "customer-rid"])
def test_stamp_preserves_existing_option_even_when_falsey(existing):
    """A value the customer already set is never replaced, even when it is empty.

    All three existing values are left alone: a real id, an empty string, and
    ``None``. The last two are the trap -- code that checks whether a value is
    truthy would treat both as "nothing there" and overwrite them.

    That matters because a customer setting the id explicitly is deliberately
    overriding the client, and an empty value may be their way of saying "send
    no id at all". Neighboring options are untouched too.
    """
    options = {Constants.ContainerRID: existing, "other": "untouched"}
    assert stamp_container_rid(options, "resolved-rid") is None
    assert options == {Constants.ContainerRID: existing, "other": "untouched"}


def test_stamp_takes_resolved_value_without_lookup_callback():
    """The helper is handed an already-resolved id; it never looks one up itself.

    Its only two arguments are the options and the id. If it instead took a
    callback, it could trigger a metadata request from deep inside request
    building, at a point where the caller has no say over timeouts or retries.

    Calling it a second time with a different id changes nothing, because the
    first call already set the value and it does not overwrite. The first
    resolution wins for the life of the request.
    """
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
    """When the client has resolved an id, it wins over anything in the options, and
    the caller's options are never edited.

    The id can arrive from three places: the resolved value passed in, an option,
    or a header the customer set. Whenever a resolved value is passed it is used
    and the others are ignored, because it is the only one the client knows is
    current -- and that holds even when it is an empty string, which is treated
    as a real answer rather than as nothing. Only when no resolved value is
    passed at all does the call fall back to whatever the options carried.

    Two of the cases are the same two sources in opposite order, and they produce
    different results, so which of the two wins depends on the order the keys
    were added. That only applies in the fallback case.

    In every case the option spelling never leaks out as a request header, and
    the caller's options, nested headers included, come back unchanged.
    """
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
    """Compare option dictionaries for the two synthetic metadata-resolution cases.

    Matching these local dictionaries does not verify a transmitted header.
    """
    cache = {"_rid": "cached-rid"} if cached else {}
    if not cache:
        cache.update({"_rid": "refreshed-rid"})
    legacy_options = {Constants.ContainerRID: cache["_rid"]}
    options = {}
    stamp_container_rid(options, cache["_rid"])
    assert options == legacy_options
