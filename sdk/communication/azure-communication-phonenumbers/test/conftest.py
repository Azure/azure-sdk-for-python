import os
import pytest
from azure.communication.phonenumbers._shared.utils import parse_connection_str
from devtools_testutils import (
    add_body_key_sanitizer,
    add_general_string_sanitizer,
    add_general_regex_sanitizer,
    test_proxy
)


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    fake_connection_str = "endpoint=https://sanitized.communication.azure.com/;accesskey=fake=="

    client_id = os.getenv("AZURE_CLIENT_ID", "sanitized")
    client_secret = os.getenv("AZURE_CLIENT_SECRET", "sanitized")
    tenant_id = os.getenv("AZURE_TENANT_ID", "sanitized")
    connection_str = os.getenv("COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING",
                               fake_connection_str)
    endpoint, *_, access_key = parse_connection_str(connection_str)

    add_general_string_sanitizer(target=client_id, value="sanitized")
    add_general_string_sanitizer(target=client_secret, value="sanitized")
    add_general_string_sanitizer(target=tenant_id, value="sanitized")
    add_general_string_sanitizer(
        target=connection_str, value=fake_connection_str)
    add_general_string_sanitizer(
        target=endpoint, value="sanitized.communication.azure.com")
    add_general_string_sanitizer(target=access_key, value="fake==")

    add_body_key_sanitizer(json_path="id", value="sanitized")
    add_body_key_sanitizer(json_path="phoneNumber", value="sanitized")
    add_body_key_sanitizer(json_path="phoneNumbers[*].id", value="sanitized")
    add_body_key_sanitizer(
        json_path="phoneNumbers[*].phoneNumber", value="sanitized")

    add_general_regex_sanitizer(regex=r"[%2B\d]{10,15}", value="sanitized")

    add_general_regex_sanitizer(
        regex=r"phoneNumbers/[%2B\d]{10,15}", value="phoneNumbers/sanitized")
