# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import pytest
from azure.servicebus import (
    ServiceBusConnectionStringProperties,
    parse_connection_string,
)
from azure.servicebus._common.utils import strip_protocol_from_uri

from devtools_testutils import AzureMgmtRecordedTestCase


class TestServiceBusConnectionStringParser(AzureMgmtRecordedTestCase):
    def test_sb_conn_str_parse_cs(self, **kwargs):
        conn_str = "Endpoint=sb://resourcename.servicebus.windows.net/;SharedAccessKeyName=test;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        parse_result = parse_connection_string(conn_str)
        assert parse_result.endpoint == "sb://resourcename.servicebus.windows.net/"
        assert parse_result.fully_qualified_namespace == "resourcename.servicebus.windows.net"
        assert parse_result.shared_access_key_name == "test"
        assert parse_result.shared_access_key == "THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="

    def test_sb_conn_str_parse_sas_and_shared_key(self, **kwargs):
        conn_str = "Endpoint=sb://resourcename.servicebus.windows.net/;SharedAccessKeyName=test;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;SharedAccessSignature=THISISASASXXXXXXX="
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str)
        assert str(e.value) == "Only one of the SharedAccessKey or SharedAccessSignature must be present."

    def test_sb_parse_malformed_conn_str_no_endpoint(self, **kwargs):
        conn_str = "SharedAccessKeyName=test;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str)
        assert str(e.value) == "Connection string is either blank or malformed."

    def test_sb_parse_malformed_conn_str_no_endpoint_value(self, **kwargs):
        conn_str = "Endpoint=;SharedAccessKeyName=test;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str)
        assert str(e.value) == "Connection string is either blank or malformed."

    def test_sb_parse_malformed_conn_str_no_netloc(self, **kwargs):
        conn_str = (
            "Endpoint=MALFORMED;SharedAccessKeyName=test;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        )
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str)
        assert str(e.value) == "Invalid Endpoint on the Connection String."

    def test_sb_parse_conn_str_sas(self, **kwargs):
        conn_str = "Endpoint=sb://resourcename.servicebus.windows.net/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        parse_result = parse_connection_string(conn_str)
        assert parse_result.endpoint == "sb://resourcename.servicebus.windows.net/"
        assert parse_result.fully_qualified_namespace == "resourcename.servicebus.windows.net"
        assert parse_result.shared_access_signature == "THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        assert parse_result.shared_access_key_name == None

    def test_sb_parse_conn_str_whitespace_trailing_semicolon(self, **kwargs):
        conn_str = "    Endpoint=sb://resourcename.servicebus.windows.net/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;    "
        parse_result = parse_connection_string(conn_str)
        assert parse_result.endpoint == "sb://resourcename.servicebus.windows.net/"
        assert parse_result.fully_qualified_namespace == "resourcename.servicebus.windows.net"
        assert parse_result.shared_access_signature == "THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        assert parse_result.shared_access_key_name == None

    def test_sb_parse_conn_str_sas_trailing_semicolon(self, **kwargs):
        conn_str = "Endpoint=sb://resourcename.servicebus.windows.net/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;"
        parse_result = parse_connection_string(conn_str)
        assert parse_result.endpoint == "sb://resourcename.servicebus.windows.net/"
        assert parse_result.fully_qualified_namespace == "resourcename.servicebus.windows.net"
        assert parse_result.shared_access_signature == "THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        assert parse_result.shared_access_key_name == None

    def test_sb_parse_conn_str_no_keyname(self, **kwargs):
        conn_str = "Endpoint=sb://resourcename.servicebus.windows.net/;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str)
        assert str(e.value) == "Connection string must have both SharedAccessKeyName and SharedAccessKey."

    def test_sb_parse_conn_str_no_key(self, **kwargs):
        conn_str = "Endpoint=sb://resourcename.servicebus.windows.net/;SharedAccessKeyName=Test"
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str)
        assert str(e.value) == "Connection string must have both SharedAccessKeyName and SharedAccessKey."

    def test_sb_parse_conn_str_no_key_or_sas(self, **kwargs):
        conn_str = "Endpoint=sb://resourcename.servicebus.windows.net/"
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str)
        assert str(e.value) == "At least one of the SharedAccessKey or SharedAccessSignature must be present."

    def test_sb_parse_malformed_conn_str_lowercase_endpoint(self, **kwargs):
        conn_str = "endpoint=sb://resourcename.servicebus.windows.net/;SharedAccessKeyName=test;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str)
        assert str(e.value) == "Connection string is either blank or malformed."

    def test_sb_parse_malformed_conn_str_lowercase_sa_key_name(self, **kwargs):
        conn_str = "Endpoint=sb://resourcename.servicebus.windows.net/;sharedaccesskeyname=test;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str)
        assert str(e.value) == "Connection string must have both SharedAccessKeyName and SharedAccessKey."

    def test_sb_parse_malformed_conn_str_lowercase_sa_key(self, **kwargs):
        conn_str = "Endpoint=sb://resourcename.servicebus.windows.net/;SharedAccessKeyName=test;sharedaccesskey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str)
        assert str(e.value) == "Connection string must have both SharedAccessKeyName and SharedAccessKey."

    def test_sb_parse_emulator_string(self, **kwargs):
        conn_str = "Endpoint=sb://localhost;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"
        parse_result = parse_connection_string(conn_str)
        assert parse_result.endpoint == "sb://localhost/"
        assert parse_result.fully_qualified_namespace == "localhost"

        conn_str = "Endpoint=sb://servicebus-emulator;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"
        parse_result = parse_connection_string(conn_str)
        assert parse_result.endpoint == "sb://servicebus-emulator/"
        assert parse_result.fully_qualified_namespace == "servicebus-emulator"

        conn_str = "Endpoint=sb://192.168.y.z;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"
        parse_result = parse_connection_string(conn_str)
        assert parse_result.endpoint == "sb://192.168.y.z/"
        assert parse_result.fully_qualified_namespace == "192.168.y.z"

    def test_strip_protocol_from_uri_normalizes_to_bare_host(self, **kwargs):
        # strip_protocol_from_uri must reduce any accepted namespace form to the
        # bare host - dropping scheme, port, and trailing path - so the value is
        # usable as both the AMQP connection host and the SAS/AAD token audience.
        # Regression test for issue #44034: the ARM/portal-emitted endpoint
        # https://<ns>.servicebus.windows.net:443/ previously kept the ":443/",
        # producing ServiceBusAuthenticationError (amqp:client-error).
        host = "myservicebus.servicebus.windows.net"
        assert strip_protocol_from_uri(host) == host  # bare host (known-good)
        assert strip_protocol_from_uri("sb://" + host) == host  # protocol only
        assert strip_protocol_from_uri("https://" + host) == host
        assert strip_protocol_from_uri("http://" + host) == host
        assert strip_protocol_from_uri("sb://" + host + "/") == host  # trailing slash
        assert strip_protocol_from_uri(host + ":443") == host  # port only (no scheme)
        assert strip_protocol_from_uri(host + ":443/") == host
        assert strip_protocol_from_uri("https://" + host + ":443/") == host  # ARM/portal-emitted form
        assert strip_protocol_from_uri("sb://" + host + ":5671/") == host
