#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest


def test_example_create_servicebus_client():

# Create a new service bus client using SAS credentials
# [START create_servicebus_client]
    import os
    from azure.servicebus import ServiceBusClient

    namespace = os.environ['SERVICE_BUS_HOSTNAME']
    shared_access_policy = os.environ['SERVICE_BUS_SAS_POLICY']
    shared_access_key = os.environ['SERVICE_BUS_SAS_KEY']

    client = ServiceBusClient(
        service_namespace=namespace,
        shared_access_key_name=shared_access_policy,
        shared_access_key_value=shared_access_key)

# [END create_servicebus_client]

