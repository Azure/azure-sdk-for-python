import os
from devtools_testutils import (
    add_general_regex_sanitizer,
    add_general_string_sanitizer,
    add_oauth_response_sanitizer,
)
import pytest

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    add_general_regex_sanitizer(
        value="https://fake-endpoint.azconfig.io",
        regex=os.environ.get("APPCONFIGURATION_ENDPOINT_STRING", "https://fake-endpoint.azconfig.io"),
    )
    add_general_regex_sanitizer(
        value="fake-connection-string",
        regex=os.environ.get("APPCONFIGURATION_CONNECTION_STRING", "fake-connection-string"),
    )
    add_general_regex_sanitizer(
        value="fake-client-id", regex=os.environ.get("APPCONFIGURATION_CLIENT_ID", "fake-client-id")
    )
    add_general_regex_sanitizer(
        value="fake-client-secret", regex=os.environ.get("APPCONFIGURATION_CLIENT_SECRET", "fake-client-secret")
    )
    add_general_regex_sanitizer(
        value="fake-tenant-id", regex=os.environ.get("APPCONFIGURATION_TENANT_ID", "fake-tenant-id")
    )
    add_general_string_sanitizer(
        value="https://fake-key-vault.vault.azure.net/",
        target=os.environ.get("APPCONFIGURATION_KEY_VAULT_REFERENCE", "https://fake-key-vault.vault.azure.net/"),
    )
    add_oauth_response_sanitizer()
