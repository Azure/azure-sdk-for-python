# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pytest
import time
from azure.identity import EnvironmentCredential, DefaultAzureCredential
from azure.eventhub import EventHubProducerClient, EventHubSharedKeyCredential
from azure.eventhub._client_base import EventHubSASTokenCredential
from azure.core.credentials import AzureSasCredential, AzureNamedKeyCredential

@pytest.mark.livetest
def test_mgmt_call_conn_str(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str)
    client._start_producer("0",60)

@pytest.mark.livetest
def test_mgmt_call_default_azure_credential(live_eventhub):
    credential = DefaultAzureCredential()
    client = EventHubProducerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=credential,
                                             user_agent='customized information')
    client._start_producer("0",60)

@pytest.mark.livetest
def test_mgmt_call_credential(live_eventhub):
    credential = EnvironmentCredential()
    client = EventHubProducerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=credential,
                                             user_agent='customized information')
    client._start_producer("0",60)

@pytest.mark.livetest
def test_mgmt_call_sas(live_eventhub):
    hostname = live_eventhub["hostname"]
    credential = EventHubSharedKeyCredential(live_eventhub['key_name'], live_eventhub['access_key'])
    auth_uri = "sb://{}/{}".format(hostname, live_eventhub['event_hub'])
    token = credential.get_token(auth_uri).token
    client = EventHubProducerClient(fully_qualified_namespace=hostname,
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=EventHubSASTokenCredential(token, time.time() + 3000))
    client._start_producer("0",60)
    assert True

@pytest.mark.livetest
def test_mgmt_call_sas_credential(live_eventhub):
    hostname = live_eventhub["hostname"]
    credential = EventHubSharedKeyCredential(live_eventhub['key_name'], live_eventhub['access_key'])
    auth_uri = "sb://{}/{}".format(hostname, live_eventhub['event_hub'])
    token = credential.get_token(auth_uri).token.decode()
    client = EventHubProducerClient(fully_qualified_namespace=hostname,
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=AzureSasCredential(token))
    client._start_producer("0",60)
    assert True

@pytest.mark.livetest
def test_mgmt_call_azure_named_key_credential(live_eventhub):
    credential = AzureNamedKeyCredential(live_eventhub['key_name'], live_eventhub['access_key'])
    client = EventHubProducerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=credential)

    client._start_producer("0",60)
    assert True
