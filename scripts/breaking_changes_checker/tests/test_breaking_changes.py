#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import json
import jsondiff
from .. import BreakingChangesTracker
from .. import RUN_BREAKING_CHANGES_PACKAGES


EXPECTED = [
    "(RemoveOrRenameInstanceAttribute): The model or publicly exposed class 'azure.storage.queue.Metrics' had its instance variable 'retention_policy' deleted or renamed in the current version",
    "(RemoveOrRenameInstanceAttribute): The client 'azure.storage.queue.QueueClient' had its instance variable 'queue_name' deleted or renamed in the current version",
    "(ChangedParameterType): The class 'azure.storage.queue.QueueClient' method 'from_queue_url' had its parameter 'credential' changed from 'positional_or_keyword' to 'keyword_only' in the current version",
    "(AddedPositionalParam): The 'azure.storage.queue.QueueClient method 'get_queue_access_policy' had a 'positional_or_keyword' parameter 'queue_name' inserted in the current version",
    "(RemoveOrRenamePositionalParam): The 'azure.storage.queue.QueueClient method 'set_queue_access_policy' had its 'positional_or_keyword' parameter 'signed_identifiers' deleted or renamed in the current version",
    "(ChangedParameterDefaultValue): The class 'azure.storage.queue.QueueClient' method 'set_queue_metadata' had its parameter 'metadata' default value changed from 'None' to ''",
    "(RemoveOrRenameModelMethod): The 'azure.storage.queue.QueueSasPermissions' method 'from_string' was deleted or renamed in the current version",
    "(RemoveOrRenameClientMethod): The 'azure.storage.queue.QueueServiceClient' client method 'get_service_properties' was deleted or renamed in the current version",
    "(RemoveOrRenameEnumValue): The 'azure.storage.queue.StorageErrorCode' enum had its value 'queue_not_found' deleted or renamed in the current version",
    "(RemoveOrRenameModel): The model or publicly exposed class 'azure.storage.queue.QueueMessage' was deleted or renamed in the current version",
    "(ChangedParameterType): The class 'azure.storage.queue.aio.QueueClient' method 'from_queue_url' had its parameter 'credential' changed from 'positional_or_keyword' to 'keyword_only' in the current version",
    "(RemovedParameterDefaultValue): The class 'azure.storage.queue.aio.QueueClient' method 'update_message' had default value 'None' removed from its parameter 'pop_receipt' in the current version",
    "(ChangedFunctionType): The class 'azure.storage.queue.aio.QueueServiceClient' method 'get_service_stats' changed from 'asynchronous' to 'synchronous' in the current version.",
    "(ChangedParameterDefaultValue): The publicly exposed function 'azure.storage.queue.generate_queue_sas' had its parameter 'permission' default value changed from 'None' to ''",
    "(ChangedParameterType): The function 'azure.storage.queue.generate_queue_sas' had its parameter 'ip' changed from 'positional_or_keyword' to 'keyword_only' in the current version",
    "(AddedPositionalParam): The function 'azure.storage.queue.generate_queue_sas' had a 'positional_or_keyword' parameter 'conn_str' inserted in the current version",
    "(RemoveOrRenamePositionalParam): The function 'azure.storage.queue.generate_queue_sas' had its 'positional_or_keyword' parameter 'account_name' deleted or renamed in the current version",
    "(RemoveOrRenameModuleLevelFunction): The publicly exposed function 'azure.storage.queue.generate_account_sas' was deleted or renamed in the current version",
    "(ChangedParameterOrdering): The class 'azure.storage.queue.QueueClient' method 'from_connection_string' had its parameters re-ordered from '['conn_str', 'queue_name', 'credential', 'kwargs']' to '['queue_name', 'conn_str', 'credential', 'kwargs']' in the current version",
    "(ChangedParameterOrdering): The publicly exposed function 'azure.storage.queue.generate_queue_sas' had its parameters re-ordered from '['account_name', 'queue_name', 'account_key', 'permission', 'expiry', 'start', 'policy_id', 'ip', 'kwargs']' to '['conn_str', 'queue_name', 'account_key', 'permission', 'expiry', 'start', 'policy_id', 'ip', 'kwargs']' in the current version",
    "(ChangedParameterOrdering): The class 'azure.storage.queue.aio.QueueClient' method 'from_connection_string' had its parameters re-ordered from '['conn_str', 'queue_name', 'credential', 'kwargs']' to '['queue_name', 'conn_str', 'credential', 'kwargs']' in the current version"
]


def test_all_checkers():
    with open(os.path.join(os.path.dirname(__file__), "test_stable.json"), "r") as fd:
        stable = json.load(fd)
    with open(os.path.join(os.path.dirname(__file__), "test_current.json"), "r") as fd:
        current = json.load(fd)
    diff = jsondiff.diff(stable, current)

    bc = BreakingChangesTracker(stable, current, diff, "azure-storage-queue")
    bc.run_checks()

    assert len(bc.breaking_changes) == len(EXPECTED)
    for message in bc.breaking_changes:
        assert message in EXPECTED


def test_ignore_checks():
    with open(os.path.join(os.path.dirname(__file__), "test_stable.json"), "r") as fd:
        stable = json.load(fd)
    with open(os.path.join(os.path.dirname(__file__), "test_current.json"), "r") as fd:
        current = json.load(fd)
    diff = jsondiff.diff(stable, current)

    ignore = {
        "azure-storage-queue": [
            ("ChangedParameterOrdering", "azure.storage.queue.aio", "QueueClient", "from_connection_string"),
            ("ChangedParameterOrdering", "azure.storage.queue", "generate_queue_sas")
        ]
    }

    bc = BreakingChangesTracker(stable, current, diff, "azure-storage-queue", ignore=ignore)
    bc.run_checks()

    assert len(bc.breaking_changes)+2 == len(EXPECTED)
    for message in bc.breaking_changes:
        assert message in EXPECTED[:-2]
