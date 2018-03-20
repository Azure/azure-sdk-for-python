# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import logging
import uuid
from azure.eventprocessorhost import EventHubConfig


class MockCredentials:

    storage_account = "mockstorageaccount"
    storage_key = "bW9ja3Bhc3N3b3Jk"
    lease_container = "leases"

    sb_name = "pythonsb"
    eh_name = "pythoneh"
    eh_policy = "pythonpolicy"
    eh_key = "bW9ja3Bhc3N3b3Jk"

    eh_address = EventHubConfig(
        MockCredentials.sb_name,
        MockCredentials.eh_name,
        MockCredentials.eh_policy,
        MockCredentials.eh_key)
