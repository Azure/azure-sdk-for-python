import sys
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
        assert parse_result["endpoint"] == 'XXXXENDPOINTXXXX'
        assert parse_result["sharedaccesskeyname"] == 'XXXXPOLICYXXXX'
        assert parse_result["sharedaccesskey"] == 'THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='

    def test_parsing_with_case_insensitive_keys_for_insensitive_conn_str(self, **kwargs):
        conn_str = 'enDpoiNT=XXXXENDPOINTXXXX;sharedaccesskeyname=XXXXPOLICYXXXX;SHAREDACCESSKEY=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
        parse_result = parse_connection_string(conn_str, False)
        assert parse_result["endpoint"] == 'XXXXENDPOINTXXXX'
        assert parse_result["sharedaccesskeyname"] == 'XXXXPOLICYXXXX'
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

    def test_case_insensitive_clear_method(self):
        conn_str = 'enDpoiNT=XXXXENDPOINTXXXX;sharedaccesskeyname=XXXXPOLICYXXXX;SHAREDACCESSKEY=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
        parse_result = parse_connection_string(conn_str, False)
        parse_result.clear()
        assert len(parse_result) == 0

    def test_case_insensitive_copy_method(self):
        conn_str = 'enDpoiNT=XXXXENDPOINTXXXX;sharedaccesskeyname=XXXXPOLICYXXXX;SHAREDACCESSKEY=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
        parse_result = parse_connection_string(conn_str, False)
        copied = parse_result.copy()
        assert copied == parse_result
    
    def test_case_insensitive_get_method(self):
        conn_str = 'Endpoint=XXXXENDPOINTXXXX;SharedAccessKeyName=XXXXPOLICYXXXX;SharedAccessKey=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
        parse_result = parse_connection_string(conn_str, False)
        assert parse_result.get("sharedaccesskeyname") == 'XXXXPOLICYXXXX'
        assert parse_result.get("sharedaccesskey") == 'THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
        assert parse_result.get("accesskey") is None
        assert parse_result.get("accesskey", "XXothertestkeyXX=") == "XXothertestkeyXX="

    def test_case_insensitive_keys_method(self):
        conn_str = 'enDpoiNT=XXXXENDPOINTXXXX;sharedaccesskeyname=XXXXPOLICYXXXX;SHAREDACCESSKEY=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
        parse_result = parse_connection_string(conn_str, False)
        keys = parse_result.keys()
        assert len(keys) == 3
        assert "endpoint" in keys
    
    def test_case_insensitive_pop_method(self):
        conn_str = 'enDpoiNT=XXXXENDPOINTXXXX;sharedaccesskeyname=XXXXPOLICYXXXX;SHAREDACCESSKEY=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
        parse_result = parse_connection_string(conn_str, False)
        endpoint = parse_result.pop("endpoint")
        sharedaccesskey = parse_result.pop("sharedaccesskey")
        assert len(parse_result) == 1
        assert endpoint == "XXXXENDPOINTXXXX"
        assert sharedaccesskey == "THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="

    def test_case_insensitive_update_with_insensitive_method(self):
        conn_str = 'enDpoiNT=XXXXENDPOINTXXXX;sharedaccesskeyname=XXXXPOLICYXXXX;SHAREDACCESSKEY=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
        conn_str2 = 'hostName=XXXXENDPOINTXXXX;ACCessKEy=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;'
        parse_result_insensitive = parse_connection_string(conn_str, False)
        parse_result_insensitive2 = parse_connection_string(conn_str2, False)

        parse_result_insensitive.update(parse_result_insensitive2)
        assert len(parse_result_insensitive) == 5
        assert parse_result_insensitive["hostname"] == "XXXXENDPOINTXXXX"
        assert parse_result_insensitive["accesskey"] == "THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX="

        # check that update replace duplicate case insensitive keys
        conn_str_duplicate_key = "endpoint=XXXXENDPOINT2XXXX;ACCessKEy=TestKey"
        parse_result_insensitive_dupe = parse_connection_string(conn_str_duplicate_key, False)
        parse_result_insensitive.update(parse_result_insensitive_dupe)
        assert parse_result_insensitive_dupe["endpoint"] == "XXXXENDPOINT2XXXX"
        assert parse_result_insensitive_dupe["accesskey"] == "TestKey" 
        assert len(parse_result_insensitive) == 5

    def test_case_sensitive_update_with_insensitive_method(self):
        conn_str = 'enDpoiNT=XXXXENDPOINTXXXX;sharedaccesskeyname=XXXXPOLICYXXXX;SHAREDACCESSKEY=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
        conn_str2 = 'hostName=XXXXENDPOINTXXXX;ACCessKEy=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;'
        parse_result_insensitive = parse_connection_string(conn_str, False)
        parse_result_sensitive = parse_connection_string(conn_str2, True)

        parse_result_sensitive.update(parse_result_insensitive)
        assert len(parse_result_sensitive) == 5
        assert parse_result_sensitive["hostName"] == "XXXXENDPOINTXXXX"
        with pytest.raises(KeyError):
            parse_result_sensitive["hostname"]

    def test_case_insensitive_values_method(self):
        conn_str = 'enDpoiNT=XXXXENDPOINTXXXX;sharedaccesskeyname=XXXXPOLICYXXXX;SHAREDACCESSKEY=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
        parse_result = parse_connection_string(conn_str, False)
        values = parse_result.values()
        assert len(values) == 3