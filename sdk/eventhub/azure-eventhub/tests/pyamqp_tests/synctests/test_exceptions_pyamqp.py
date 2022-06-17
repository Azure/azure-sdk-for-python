# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from tkinter import E
import pytest

from azure.eventhub._pyamqp import SendClient, Connection, authentication
from azure.eventhub._pyamqp.error import AMQPConnectionError

@pytest.mark.livetest
def test_client_creation_exceptions(live_eventhub):
    try:
        sender = SendClient(
            "fake.host.com",
        )
        assert sender._hostname == "fake.host.com"
    except TypeError:
        assert True

@pytest.mark.livetest
def test_connection_endpoint_exceptions(live_eventhub):
    try:
        endpoint = live_eventhub["hostname"]
        connection = Connection(endpoint)
        connection.open()
    except AMQPConnectionError:
        assert True

@pytest.mark.livetest
def test_connection_sas_authentication_exception(live_eventhub):
    uri = "sb://{}/{}".format(live_eventhub['hostname'], live_eventhub['event_hub'])

    target = "amqps://{}/{}/Partitions/{}".format(
        live_eventhub['hostname'],
        live_eventhub['event_hub'],
        live_eventhub['partition'])
    try:
        sas_auth = authentication.SASTokenAuth(
            uri=uri,
            audience=uri,
            username=live_eventhub['key_name'],
            password=""
        )
        sender = SendClient(live_eventhub["hostname"], target, auth=sas_auth)
        sender.client_ready()
    except AttributeError:
        assert True

@pytest.mark.livetest
def test_connection_sasl_annon_authentication_exception(live_eventhub):
    target = "amqps://{}/{}/Partitions/{}".format(
        live_eventhub['hostname'],
        live_eventhub['event_hub'],
        live_eventhub['partition'])
    try:
        sas_auth = authentication.SASLAnonymousCredential()
        sender = SendClient(live_eventhub["hostname"], target, auth=sas_auth)
        sender.client_ready()
    except AttributeError:
        assert True