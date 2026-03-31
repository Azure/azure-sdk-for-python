import os
from devtools_testutils import (
    add_general_regex_sanitizer,
    add_general_string_sanitizer,
    add_oauth_response_sanitizer,
    set_custom_default_matcher,
    remove_batch_sanitizers,
    add_remove_header_sanitizer,
    add_uri_string_sanitizer,
    is_live,
)
import pytest
from azure.appconfiguration import AzureAppConfigurationClient
from azure.identity import DefaultAzureCredential
from testcase import setup_configs, cleanup_test_resources

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method

# Module-level storage for snapshot names created during session setup
snapshot_names = {}


@pytest.fixture(scope="session", autouse=True)
def setup_app_config_keys():
    """Pre-populate App Configuration with test keys and snapshots once per session (live mode only)."""
    if not is_live():
        yield
        return

    endpoint = os.environ.get("APPCONFIGURATION_ENDPOINT_STRING")
    if not endpoint:
        yield
        return

    credential = DefaultAzureCredential()
    client = AzureAppConfigurationClient(endpoint, credential)
    keyvault_secret_url = os.environ.get("APPCONFIGURATION_KEY_VAULT_REFERENCE")
    keyvault_secret_url2 = os.environ.get("APPCONFIGURATION_KEY_VAULT_REFERENCE2")
    snap_name, ff_snap_name = setup_configs(client, keyvault_secret_url, keyvault_secret_url2)

    snapshot_names["snapshot"] = snap_name
    snapshot_names["ff_snapshot"] = ff_snap_name

    yield

    cleanup_test_resources(client, snapshot_names=[snap_name, ff_snap_name])


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    add_general_regex_sanitizer(
        value="https://sanitized.azconfig.io",
        regex=os.environ.get("APPCONFIGURATION_ENDPOINT_STRING", "https://sanitized.azconfig.io"),
    )
    add_general_regex_sanitizer(
        value="sanitized",
        regex=os.environ.get("APPCONFIGURATION_CONNECTION_STRING", "https://sanitized.azconfig.io"),
    )
    add_uri_string_sanitizer()
    add_general_string_sanitizer(
        value="https://sanitized.vault.azure.net/secrets/fake-secret/",
        target=os.environ.get(
            "APPCONFIGURATION_KEY_VAULT_REFERENCE", "https://sanitized.vault.azure.net/secrets/fake-secret/"
        ),
    )
    add_remove_header_sanitizer(headers="Correlation-Context")

    add_general_regex_sanitizer(value="api-version=1970-01-01", regex="api-version=.+")
    set_custom_default_matcher(ignored_headers="x-ms-content-sha256, Accept", excluded_headers="Content-Length")
    add_remove_header_sanitizer(headers="Sync-Token")
    add_oauth_response_sanitizer()

    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3430: $..id
    #  - AZSDK3447: $.key
    remove_batch_sanitizers(["AZSDK3430", "AZSDK3447"])
