import logging
import os
import time

from devtools_testutils import (
    add_general_regex_sanitizer,
    add_general_string_sanitizer,
    add_oauth_response_sanitizer,
    set_custom_default_matcher,
    remove_batch_sanitizers,
    add_remove_header_sanitizer,
    add_uri_string_sanitizer,
    get_credential,
    is_live,
)
import pytest
from azure.appconfiguration import AzureAppConfigurationClient
from azure.core.exceptions import HttpResponseError
from testcase import setup_configs, cleanup_test_resources


_LOGGER = logging.getLogger(__name__)
_RBAC_PROPAGATION_TIMEOUT = 15 * 60 + 5
_MAX_RETRY_DELAY = 30

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method

# Module-level storage for snapshot names created during session setup
snapshot_names = {}


def _wait_for_rbac_propagation(client, timeout=_RBAC_PROPAGATION_TIMEOUT):
    deadline = time.monotonic() + timeout
    retry_delay = 1

    while True:
        try:
            next(client.list_configuration_settings(key_filter="__rbac_readiness_probe__"), None)
            return
        except HttpResponseError as error:
            if error.status_code != 403:
                raise

            remaining_time = deadline - time.monotonic()
            if remaining_time <= 0:
                raise TimeoutError("App Configuration data-plane role assignment did not propagate in time.") from error

            sleep_time = min(retry_delay, remaining_time)
            _LOGGER.info(
                "Waiting %.0f seconds for the App Configuration data-plane role assignment to propagate.",
                sleep_time,
            )
            time.sleep(sleep_time)
            retry_delay = min(retry_delay * 2, _MAX_RETRY_DELAY)


@pytest.fixture(scope="session", autouse=True)
def wait_for_data_plane_access():
    if not is_live():
        return

    endpoint = os.environ.get("APPCONFIGURATION_ENDPOINT_STRING")
    if not endpoint:
        pytest.fail("APPCONFIGURATION_ENDPOINT_STRING must be set when running live tests.")

    client = AzureAppConfigurationClient(endpoint, get_credential())
    try:
        _wait_for_rbac_propagation(client)
    finally:
        client.close()


@pytest.fixture(scope="session", autouse=True)
def setup_app_config_keys(wait_for_data_plane_access):
    """Pre-populate App Configuration with test keys and snapshots once per session (live mode only)."""
    del wait_for_data_plane_access

    if not is_live():
        yield
        return

    endpoint = os.environ.get("APPCONFIGURATION_ENDPOINT_STRING")
    if not endpoint:
        yield
        return

    credential = get_credential()
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
    # Register the longer URL2 sanitizer FIRST to prevent URL1's sanitizer from partially matching within URL2
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


@pytest.fixture(autouse=True)
def no_startup_backoff(request, monkeypatch):
    """Skip startup backoff delays in all tests except those testing backoff directly."""
    if request.fspath.basename == "test_startup_retry.py":  # cspell:ignore fspath
        return
    monkeypatch.setattr(
        "azure.appconfiguration.provider._azureappconfigurationprovider.get_startup_backoff",
        lambda *args, **kwargs: (0, False),
    )
