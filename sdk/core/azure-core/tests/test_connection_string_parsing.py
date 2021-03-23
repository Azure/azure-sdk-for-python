import os
import pytest
from azure.core.utils import parse_connection_string

from devtools_testutils import AzureMgmtTestCase

class CoreConnectionStringParserTests(AzureMgmtTestCase):

    def test_parsing_with_case_sensitive_keys_for_sensitive_conn_str(self, **kwargs):
        conn_str = 'Endpoint=XXXXENDPOINTXXXX;SharedAccessKeyName=XXXXPOLICYXXXX;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
        parse_result = parse_connection_string(conn_str, True)
        assert parse_result["Endpoint"] == 'XXXXENDPOINTXXXX'
        assert parse_result["SharedAccessKeyName"] == 'XXXXPOLICYXXXX'
        assert parse_result["SharedAccessKey"] == 'THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
        with pytest.raises(KeyError):
            parse_result["endPoint"]
        with pytest.raises(KeyError):
            parse_result["sharedAccESSkEynAME"]
        with pytest.raises(KeyError):
            parse_result["sharedaccesskey"]

    def test_parsing_with_case_insensitive_keys_for_sensitive_conn_str(self, **kwargs):
        conn_str = 'Endpoint=XXXXENDPOINTXXXX;SharedAccessKeyName=XXXXPOLICYXXXX;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
        parse_result = parse_connection_string(conn_str, False)
        assert parse_result["Endpoint"] == 'XXXXENDPOINTXXXX'
        assert parse_result["endPoint"] == 'XXXXENDPOINTXXXX'
        assert parse_result["SharedAccessKeyName"] == 'XXXXPOLICYXXXX'
        assert parse_result["sharedAccESSkEynAME"] == 'XXXXPOLICYXXXX'
        assert parse_result["SharedAccessKey"] == 'THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
        assert parse_result["sharedaccesskey"] == 'THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='

    def test_parsing_with_case_sensitive_keys_for_insensitive_conn_str(self, **kwargs):
        conn_str = 'enDpoiNT=XXXXENDPOINTXXXX;sharedaccesskeyname=XXXXPOLICYXXXX;SHAREDACCESSKEY=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
        parse_result = parse_connection_string(conn_str, True)
        assert parse_result["enDpoiNT"] == 'XXXXENDPOINTXXXX'
        assert parse_result["sharedaccesskeyname"] == 'XXXXPOLICYXXXX'
        assert parse_result["SHAREDACCESSKEY"] == 'THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
        with pytest.raises(KeyError):
            parse_result["Endpoint"]
        with pytest.raises(KeyError):
            parse_result["SharedAccessKeyName"]
        with pytest.raises(KeyError):
            parse_result["SharedAccessKey"]

    def test_parsing_with_case_insensitive_keys_for_insensitive_conn_str(self, **kwargs):
        conn_str = 'enDpoiNT=XXXXENDPOINTXXXX;sharedaccesskeyname=XXXXPOLICYXXXX;SHAREDACCESSKEY=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
        parse_result = parse_connection_string(conn_str, False)
        assert parse_result["Endpoint"] == 'XXXXENDPOINTXXXX'
        assert parse_result["endPoint"] == 'XXXXENDPOINTXXXX'
        assert parse_result["SharedAccessKeyName"] == 'XXXXPOLICYXXXX'
        assert parse_result["sharedAccESSkEynAME"] == 'XXXXPOLICYXXXX'
        assert parse_result["SharedAccessKey"] == 'THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
        assert parse_result["sharedaccesskey"] == 'THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='

    def test_error_with_duplicate_case_sensitive_keys_for_sensitive_conn_str(self, **kwargs):
        conn_str = 'Endpoint=XXXXENDPOINTXXXX;Endpoint=XXXXENDPOINT2XXXX;SharedAccessKeyName=XXXXPOLICYXXXX;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str, True)
        assert str(e.value) == "Connection string is either blank or malformed."

    def test_success_with_duplicate_case_sensitive_keys_for_sensitive_conn_str(self, **kwargs):
        conn_str = 'enDpoInt=XXXXENDPOINTXXXX;Endpoint=XXXXENDPOINT2XXXX;'
        parse_result = parse_connection_string(conn_str, True)
        assert parse_result["enDpoInt"] == 'XXXXENDPOINTXXXX'
        assert parse_result["Endpoint"] == 'XXXXENDPOINT2XXXX'

    def test_error_with_duplicate_case_insensitive_keys_for_insensitive_conn_str(self, **kwargs):
        conn_str = 'endPoinT=XXXXENDPOINTXXXX;eNdpOint=XXXXENDPOINT2XXXX;sharedaccesskeyname=XXXXPOLICYXXXX;SHAREDACCESSKEY=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
        with pytest.raises(ValueError) as e:
            parse_result = parse_connection_string(conn_str, False)
        assert str(e.value) == "Duplicate key in connection string: endpoint"
    
    def test_error_with_malformed_conn_str(self):
        for conn_str in ["", "foobar", "foo;bar;baz", ";", "foo=;bar=;", "=", "=;=="]:
            with pytest.raises(ValueError) as e:
                parse_result = parse_connection_string(conn_str)
            self.assertEqual(str(e.value), "Connection string is either blank or malformed.")
