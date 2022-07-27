# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import pytest

from azure.eventhub._pyamqp import SendClient, Connection, authentication
from azure.eventhub._pyamqp.error import AMQPConnectionError

def test_client_creation_exceptions():
    with pytest.raises(TypeError):
        sender = SendClient(
            "fake.host.com",
        )
        assert sender._remote_address == "fake.host.com"

def test_connection_endpoint_exceptions():
    with pytest.raises(AMQPConnectionError):
        endpoint = "fake.host.com"
        connection = Connection(endpoint)
        connection.open()

def test_connection_sas_authentication_exception():
    uri = "sb://{}/{}".format("fake.host.come", "fake_eh")

    target = "amqps://{}/{}/Partitions/{}".format(
        "fake.host.com",
        "fake_eh",
        "0")
    sas_auth = authentication.SASTokenAuth(
        uri=uri,
        audience=uri,
        username="key",
        password=""
    )
    with pytest.raises(AttributeError):
        sender = SendClient("fake.host.com", target, auth=sas_auth)
        sender.client_ready()
    
def test_connection_sasl_annon_authentication_exception():
    target = "amqps://{}/{}/Partitions/{}".format(
        "fake.host.com",
        "fake_eh",
        "0")

    sas_auth = authentication.SASLAnonymousCredential()
    with pytest.raises(AttributeError):
        sender = SendClient("fake.host.com", target, auth=sas_auth)
        sender.client_ready()
