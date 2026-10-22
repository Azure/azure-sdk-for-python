# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import pytest
from azure.eventhub import (
    EventHubConnectionStringProperties,
    parse_connection_string,
)
from azure.eventhub._client_base import _parse_conn_str


class TestEventHubConnectionStringParser:

    def test_eh_conn_str_parse_cs(self, **kwargs):
        conn_str = "Endpoint=sb://eh-namespace.servicebus.windows.net/;SharedAccessKeyName=test-policy;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        parse_result = parse_connection_string(conn_str)
        assert parse_result.endpoint == "sb://eh-namespace.servicebus.windows.net/"
        assert parse_result.fully_qualified_namespace == "eh-namespace.servicebus.windows.net"
        assert parse_result.shared_access_key_name == "test-policy"
        assert parse_result.shared_access_key == "THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="

    def test_eh_conn_str_parse_with_entity_path(self, **kwargs):
        conn_str = "Endpoint=sb://eh-namespace.servicebus.windows.net/;SharedAccessKeyName=test-policy;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;EntityPath=eventhub-name"
        parse_result = parse_connection_string(conn_str)
        assert parse_result.endpoint == "sb://eh-namespace.servicebus.windows.net/"
        assert parse_result.fully_qualified_namespace == "eh-namespace.servicebus.windows.net"
        assert parse_result.shared_access_key_name == "test-policy"
        assert parse_result.shared_access_key == "THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        assert parse_result.eventhub_name == "eventhub-name"

    def test_eh_conn_str_parse_sas_and_shared_key(self, **kwargs):
        conn_str = "Endpoint=sb://eh-namespace.servicebus.windows.net/;SharedAccessKeyName=test-policy;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;SharedAccessSignature=THISISASASXXXXXXX="
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str)
        assert str(e.value) == "Only one of the SharedAccessKey or SharedAccessSignature must be present."

    def test_eh_parse_malformed_conn_str_no_endpoint(self, **kwargs):
        conn_str = "SharedAccessKeyName=test-policy;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str)
        assert str(e.value) == "Connection string is either blank or malformed."

    def test_eh_parse_malformed_conn_str_no_endpoint_value(self, **kwargs):
        conn_str = "Endpoint=;SharedAccessKeyName=test;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str)
        assert str(e.value) == "Connection string is either blank or malformed."

    def test_eh_parse_malformed_conn_str_no_netloc(self, **kwargs):
        conn_str = "Endpoint=MALFORMED;SharedAccessKeyName=test-policy;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str)
        assert str(e.value) == "Invalid Endpoint on the Connection String."

    def test_eh_parse_conn_str_sas(self, **kwargs):
        conn_str = "Endpoint=sb://eh-namespace.servicebus.windows.net/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        parse_result = parse_connection_string(conn_str)
        assert parse_result.endpoint == "sb://eh-namespace.servicebus.windows.net/"
        assert parse_result.fully_qualified_namespace == "eh-namespace.servicebus.windows.net"
        assert parse_result.shared_access_signature == "THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        assert parse_result.shared_access_key_name == None

    def test_eh_parse_conn_str_whitespace_trailing_semicolon(self, **kwargs):
        conn_str = "    Endpoint=sb://resourcename.servicebus.windows.net/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;    "
        parse_result = parse_connection_string(conn_str)
        assert parse_result.endpoint == "sb://resourcename.servicebus.windows.net/"
        assert parse_result.fully_qualified_namespace == "resourcename.servicebus.windows.net"
        assert parse_result.shared_access_signature == "THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        assert parse_result.shared_access_key_name == None

    def test_eh_parse_conn_str_sas_trailing_semicolon(self, **kwargs):
        conn_str = "Endpoint=sb://resourcename.servicebus.windows.net/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;"
        parse_result = parse_connection_string(conn_str)
        assert parse_result.endpoint == "sb://resourcename.servicebus.windows.net/"
        assert parse_result.fully_qualified_namespace == "resourcename.servicebus.windows.net"
        assert parse_result.shared_access_signature == "THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        assert parse_result.shared_access_key_name == None

    def test_eh_parse_conn_str_no_keyname(self, **kwargs):
        conn_str = "Endpoint=sb://eh-namespace.servicebus.windows.net/;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str)
        assert "Invalid connection string" in str(e.value)

    def test_eh_parse_conn_str_no_key(self, **kwargs):
        conn_str = "Endpoint=sb://eh-namespace.servicebus.windows.net/;SharedAccessKeyName=test-policy"
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str)
        assert "Invalid connection string" in str(e.value)

    def test_eh_parse_conn_str_no_key_or_sas(self, **kwargs):
        conn_str = "Endpoint=sb://resourcename.servicebus.windows.net/"
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str)
        assert str(e.value) == "At least one of the SharedAccessKey or SharedAccessSignature must be present."

    def test_eh_parse_malformed_conn_str_lowercase_endpoint(self, **kwargs):
        conn_str = "endpoint=sb://resourcename.servicebus.windows.net/;SharedAccessKeyName=test;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str)
        assert str(e.value) == "Connection string is either blank or malformed."

    def test_eh_parse_malformed_conn_str_lowercase_sa_key_name(self, **kwargs):
        conn_str = "Endpoint=sb://resourcename.servicebus.windows.net/;sharedaccesskeyname=test;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str)
        assert "Invalid connection string" in str(e.value)

    def test_eh_parse_malformed_conn_str_lowercase_sa_key_name(self, **kwargs):
        conn_str = "Endpoint=sb://resourcename.servicebus.windows.net/;SharedAccessKeyName=test;sharedaccesskey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str)
        assert "Invalid connection string" in str(e.value)

    def test_eh_emulator_slug_parse_localhost(self, **kwargs):
        conn_str = "Endpoint=sb://localhost:6065;SharedAccessKeyName=test-policy;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;UseDevelopmentEmulator=true"
        fully_qualified_namespace, policy, key, entity, signature, expiry, emulator = _parse_conn_str(conn_str)
        assert fully_qualified_namespace == "localhost:6065"
        assert emulator == True

    def test_eh_emulator_slug_parse_ipv6(self, **kwargs):
        conn_str = "Endpoint=sb://::1;SharedAccessKeyName=test-policy;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;UseDevelopmentEmulator=true"
        fully_qualified_namespace, policy, key, entity, signature, expiry, emulator = _parse_conn_str(conn_str)
        assert fully_qualified_namespace == "::1"
        assert emulator == True
