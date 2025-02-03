import os
import pytest
from azure.communication.phonenumbers._shared.utils import parse_connection_str
from devtools_testutils import (
    add_body_key_sanitizer,
    add_general_string_sanitizer,
    add_general_regex_sanitizer,
    add_header_regex_sanitizer,
    test_proxy,
    remove_batch_sanitizers,
)


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    fake_connection_str = "endpoint=https://sanitized.communication.azure.com/;accesskey=fake=="

    client_id = os.getenv("AZURE_CLIENT_ID", "sanitized")
    client_secret = os.getenv("AZURE_CLIENT_SECRET", "sanitized")
    tenant_id = os.getenv("AZURE_TENANT_ID", "sanitized")
    connection_str = os.getenv("COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING", fake_connection_str)
    dynamic_connection_str = os.getenv("COMMUNICATION_LIVETEST_DYNAMIC_CONNECTION_STRING", fake_connection_str)
    endpoint, *_, access_key = parse_connection_str(connection_str)
    dynamic_endpoint, *_, dynamic_access_key = parse_connection_str(dynamic_connection_str)

    add_general_string_sanitizer(target=client_id, value="sanitized")
    add_general_string_sanitizer(target=client_secret, value="sanitized")
    add_general_string_sanitizer(target=tenant_id, value="sanitized")
    add_general_string_sanitizer(target=connection_str, value=fake_connection_str)
    add_general_string_sanitizer(target=endpoint, value="sanitized.communication.azure.com")
    add_general_string_sanitizer(target=access_key, value="fake==")

    add_general_string_sanitizer(target=dynamic_connection_str, value=fake_connection_str)
    add_general_string_sanitizer(target=dynamic_endpoint, value="sanitized.communication.azure.com")
    add_general_string_sanitizer(target=dynamic_access_key, value="fake==")

    add_body_key_sanitizer(json_path="id", value="sanitized")
    add_body_key_sanitizer(json_path="phoneNumber", value="sanitized")
    add_body_key_sanitizer(json_path="phoneNumbers[*].id", value="sanitized")
    add_body_key_sanitizer(json_path="phoneNumbers[*].phoneNumber", value="sanitized")

    add_general_regex_sanitizer(regex=r"-[0-9a-fA-F]{32}\.[0-9a-zA-Z\.]*(\.com|\.net|\.test)", value=".sanitized.com")

    add_general_regex_sanitizer(regex=r"(?:(?:%2B)|\+)\d{10,15}", value="sanitized")

    add_general_regex_sanitizer(regex=r"phoneNumbers/[%2B\d]{10,15}", value="phoneNumbers/sanitized")

    add_header_regex_sanitizer(key="P3P", value="sanitized")
    add_header_regex_sanitizer(key="Set-Cookie", value="sanitized")
    add_header_regex_sanitizer(key="Date", value="sanitized")
    add_header_regex_sanitizer(key="Cookie", value="sanitized")
    add_header_regex_sanitizer(key="client-request-id", value="sanitized")
    add_header_regex_sanitizer(key="MS-CV", value="sanitized")
    add_header_regex_sanitizer(key="X-Azure-Ref", value="sanitized")
    add_header_regex_sanitizer(key="x-ms-content-sha256", value="sanitized")
    add_header_regex_sanitizer(key="x-ms-client-request-id", value="sanitized")
    add_header_regex_sanitizer(key="x-ms-date", value="sanitized")
    add_header_regex_sanitizer(key="x-ms-ests-server", value="sanitized")
    add_header_regex_sanitizer(key="x-ms-request-id", value="sanitized")
    add_header_regex_sanitizer(key="Content-Security-Policy-Report-Only", value="sanitized")

    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3493: $..name
    #  - AZSDK2003: Location
    remove_batch_sanitizers(["AZSDK3493", "AZSDK2003"])
