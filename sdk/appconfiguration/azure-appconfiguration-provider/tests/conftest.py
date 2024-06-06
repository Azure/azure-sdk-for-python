import os
from devtools_testutils import (
    add_general_regex_sanitizer,
    add_general_string_sanitizer,
    add_oauth_response_sanitizer,
    set_custom_default_matcher,
    remove_batch_sanitizers,
    add_remove_header_sanitizer,
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
    add_general_string_sanitizer(
        value="https://fake-key-vault.vault.azure.net/",
        target=os.environ.get("APPCONFIGURATION_KEY_VAULT_REFERENCE", "https://fake-key-vault.vault.azure.net/"),
    )

    add_general_regex_sanitizer(value="api-version=1970-01-01", regex="api-version=.+")
    set_custom_default_matcher(ignored_headers="x-ms-content-sha256, Accept", excluded_headers="Content-Length")
    add_remove_header_sanitizer(headers="Sync-Token")
    add_oauth_response_sanitizer()

    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3430: $..id
    #  - AZSDK3447: $.key
    remove_batch_sanitizers(["AZSDK3430", "AZSDK3447"])
