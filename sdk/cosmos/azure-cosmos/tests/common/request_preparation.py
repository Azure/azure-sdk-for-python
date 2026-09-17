# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Test entrypoints exercising real argument preparation before pure item builders."""
from functools import partial

from azure.cosmos._helpers.item_helper import normalize_item_arguments, build_item_request
from azure.cosmos._helpers._item_context import ItemClientDefaults
from azure.cosmos._helpers._item_prep import prepare_create_item_kwargs


def call_create_item_helper(helper, **kwargs):
    deadline = prepare_create_item_kwargs(kwargs)
    return helper.create_item(deadline=deadline, **kwargs)


def call_item_helper(helper, op, **kwargs):
    if op == "create_item":
        return call_create_item_helper(helper, **kwargs)
    return getattr(helper, op)(**kwargs)


def prepare_item_request(op, *, partition_key_value, container_rid, kwargs=None,
                         no_response_on_write_default=False, compact_utf8=False, **arguments):
    values = dict(kwargs or {})
    values.update(arguments)
    if op == "create_item":
        values.setdefault("enable_automatic_id_generation", True)
    deadline = prepare_create_item_kwargs(values) if op == "create_item" else None
    args, options = normalize_item_arguments(op, values, compact_utf8=compact_utf8, deadline=deadline)
    # These fixtures exercise explicit wire options, not metadata resolution.
    options["partitionKey"] = partition_key_value
    if container_rid is not None:
        options["containerRID"] = container_rid
    return build_item_request(
        op, args, options,
        ItemClientDefaults(no_response_on_write_default, compact_utf8),
    )


prepare_create_item_request = partial(prepare_item_request, "create_item")
prepare_read_item_request = partial(prepare_item_request, "read_item")
prepare_delete_item_request = partial(prepare_item_request, "delete_item")
prepare_upsert_item_request = partial(prepare_item_request, "upsert_item")
prepare_replace_item_request = partial(prepare_item_request, "replace_item")
prepare_patch_item_request = partial(prepare_item_request, "patch_item")
