# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Fault one get-or-create step while forwarding every request to the real binding."""

import os
from contextlib import contextmanager

import pytest

from azure.cosmos import PartitionKey
from config.clients import create_fault_setup_client
from fault_injection._container_create import (
    CREATE_FAULT_CASES,
    assert_stored_container,
)
from fault_injection._query_resume import set_rule

GET_OR_CREATE_FAULT_CASES = [
    pytest.param(
        phase,
        existing,
        *case.values,
        id=f"{phase}-{'existing' if existing else 'missing'}-{case.id}",
    )
    for phase, existing in (("read", False), ("read", True), ("create", False))
    for case in CREATE_FAULT_CASES
    if phase == "create"
    or case.values[0] == "throttle"
    or (case.values[0] == "timeout" and case.values[3])
]


def prepare_target(database_id, container_id, existing):
    if existing:
        with create_fault_setup_client(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"]
        ) as setup:
            setup.get_database_client(database_id).create_container(
                container_id, PartitionKey("/pk"), default_ttl=90
            )
    return assert_stored_container(database_id, container_id, exists=existing)


def capture_workflow_calls(
    monkeypatch, client, handle, rule_id, phase, *, asynchronous=False
):
    """Arm All only around the chosen binding operation, never setup or the other step."""
    original = client._adapter.execute
    calls = []

    @contextmanager
    def observe(prepared, deadline):
        calls.append((prepared.op, deadline))
        armed = prepared.op == f"{phase}_container"
        if armed:
            set_rule(handle, rule_id, True)
        try:
            yield
        finally:
            if armed:
                set_rule(handle, rule_id, False)

    def execute(prepared, *, deadline=None):
        with observe(prepared, deadline):
            return original(prepared, deadline=deadline)

    async def execute_async(prepared, *, deadline=None):
        with observe(prepared, deadline):
            return await original(prepared, deadline=deadline)

    monkeypatch.setattr(
        client._adapter, "execute", execute_async if asynchronous else execute
    )
    return calls


def assert_workflow_calls(
    calls, before, after, *, phase, existing, fault, inject, hit_limit
):
    read_failed = (
        phase == "read" and inject and (fault != "throttle" or hit_limit is None)
    )
    expected = ["read_container"]
    if not existing and not read_failed:
        expected.append("create_container")
    assert [operation for operation, _ in calls] == expected
    assert after - before == len(expected), "Wrong native binding operation count"
    assert calls[0][1] is not None
    assert all(deadline == calls[0][1] for _, deadline in calls)
