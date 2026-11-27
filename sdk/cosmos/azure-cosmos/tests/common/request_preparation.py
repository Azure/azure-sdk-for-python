# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Helpers that let tests run the real argument preparation instead of hand-building inputs.

A caller's keyword arguments do not go straight to the code that builds a request. They
first pass through preparation, which rejects arguments that no longer exist, works out
when the operation must finish, and sorts the rest into request values and options. Tests
that skip that step would be checking input that no real customer call ever produces.

These helpers run the real preparation and hand back what it produced, so a test can
supply ordinary keyword arguments and still see what the code under test would see.
"""
from functools import partial

from azure.cosmos._helpers._item_operations import normalize_item_arguments, build_item_request
from azure.cosmos._helpers._client_context import ClientOperationDefaults
from azure.cosmos._helpers._item_prep import prepare_create_item_kwargs


def call_create_item_helper(helper, **kwargs):
    """Call create_item on a helper after running the preparation it expects first.

    Creating an item is the one operation whose preparation has to happen before the
    helper is called: it checks for arguments that were removed from the public method
    and works out the deadline, which the helper then takes as an argument rather than
    computing itself. Calling the helper directly would skip both.
    """
    deadline = prepare_create_item_kwargs(kwargs)
    return helper.create_item(deadline=deadline, **kwargs)


def call_item_helper(helper, op, **kwargs):
    """Call the named operation on a helper, adding the extra step create_item needs.

    Every other operation prepares its own arguments internally, so a plain call is
    already the real path. This lets a test loop over operation names without special
    casing the one that is different.
    """
    if op == "create_item":
        return call_create_item_helper(helper, **kwargs)
    return getattr(helper, op)(**kwargs)


def prepare_item_request(op, *, partition_key_value, container_rid, kwargs=None,
                         no_response_on_write_default=False, compact_utf8=False, **arguments):
    """Run real preparation for one operation and return the finished request.

    The partition key and the container's resource id (container_rid) are supplied by the
    caller rather than looked up, because looking them up would need a real container.
    Everything else -- sorting arguments, rejecting bad ones, deciding the deadline,
    building the request -- is the production code.
    """
    values = dict(kwargs or {})
    values.update(arguments)
    if op == "create_item":
        values.setdefault("enable_automatic_id_generation", True)
    deadline = prepare_create_item_kwargs(values) if op == "create_item" else None
    args, options = normalize_item_arguments(op, values, compact_utf8=compact_utf8, deadline=deadline)
    # Use the given partition key and container id instead of looking them up.
    options["partitionKey"] = partition_key_value
    if container_rid is not None:
        options["containerRID"] = container_rid
    return build_item_request(
        op, args, options,
        ClientOperationDefaults(no_response_on_write_default, compact_utf8),
    )


prepare_create_item_request = partial(prepare_item_request, "create_item")
prepare_read_item_request = partial(prepare_item_request, "read_item")
prepare_delete_item_request = partial(prepare_item_request, "delete_item")
prepare_upsert_item_request = partial(prepare_item_request, "upsert_item")
prepare_replace_item_request = partial(prepare_item_request, "replace_item")
prepare_patch_item_request = partial(prepare_item_request, "patch_item")
