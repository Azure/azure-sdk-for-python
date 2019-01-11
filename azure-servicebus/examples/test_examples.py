#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest


def test_example_create_servicebus_client(live_servicebus_config):

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


def test_sample_queue_send_receive_batch(live_servicebus_config, standard_queue):
    try:
        from examples.example_queue_send_receive_batch import sample_queue_send_receive_batch
    except ImportError:
        pytest.skip("")
    sample_queue_send_receive_batch(live_servicebus_config, standard_queue)


def test_sample_session_send_receive_batch(live_servicebus_config, session_queue):
    try:
        from examples.example_session_send_receive_batch import sample_session_send_receive_batch
    except ImportError:
        pytest.skip("")
    sample_session_send_receive_batch(live_servicebus_config, session_queue)


def test_sample_session_send_receive_with_pool(live_servicebus_config, session_queue):
    try:
        from examples.example_session_send_receive_with_pool import sample_session_send_receive_with_pool
    except ImportError:
        pytest.skip("")
    sample_session_send_receive_with_pool(live_servicebus_config, session_queue)
