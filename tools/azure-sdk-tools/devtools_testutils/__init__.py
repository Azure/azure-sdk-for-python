from .mgmt_testcase import AzureMgmtTestCase, AzureMgmtPreparer
from .mgmt_recorded_testcase import AzureMgmtRecordedTestCase
from .azure_recorded_testcase import AzureRecordedTestCase
from .azure_testcase import AzureTestCase, is_live, get_region_override
from .resource_testcase import (
    FakeResource,
    ResourceGroupPreparer,
    RandomNameResourceGroupPreparer,
    CachedResourceGroupPreparer,
)
from .storage_testcase import (
    FakeStorageAccount,
    StorageAccountPreparer,
    BlobAccountPreparer,
    CachedStorageAccountPreparer,
)
from .keyvault_preparer import KeyVaultPreparer
# cSpell:disable
from .envvariable_loader import EnvironmentVariableLoader
PowerShellPreparer = EnvironmentVariableLoader  # Backward compat
from .proxy_fixtures import environment_variables, recorded_test, variable_recorder
from .proxy_startup import start_test_proxy, stop_test_proxy, test_proxy
from .proxy_testcase import recorded_by_proxy
from .sanitizers import (
    add_api_version_transform,
    add_body_key_sanitizer,
    add_body_regex_sanitizer,
    add_body_string_sanitizer,
    add_client_id_transform,
    add_continuation_sanitizer,
    add_general_regex_sanitizer,
    add_general_string_sanitizer,
    add_header_regex_sanitizer,
    add_header_string_sanitizer,
    add_header_transform,
    add_oauth_response_sanitizer,
    add_remove_header_sanitizer,
    add_storage_request_id_transform,
    add_uri_regex_sanitizer,
    add_uri_string_sanitizer,
    add_uri_subscription_id_sanitizer,
    PemCertificate,
    set_bodiless_matcher,
    set_custom_default_matcher,
    set_default_function_settings,
    set_default_session_settings,
    set_function_recording_options,
    set_headerless_matcher,
    set_session_recording_options,
)
from .cert import create_combined_bundle
from .helpers import ResponseCallback, RetryCounter, is_live_and_not_recording
from .fake_credentials import FakeTokenCredential

__all__ = [
    "add_api_version_transform",
    "add_body_key_sanitizer",
    "add_body_regex_sanitizer",
    "add_body_string_sanitizer",
    "add_client_id_transform",
    "add_continuation_sanitizer",
    "add_general_regex_sanitizer",
    "add_general_string_sanitizer",
    "add_header_regex_sanitizer",
    "add_header_string_sanitizer",
    "add_header_transform",
    "add_oauth_response_sanitizer",
    "add_remove_header_sanitizer",
    "add_storage_request_id_transform",
    "add_uri_regex_sanitizer",
    "add_uri_string_sanitizer",
    "add_uri_subscription_id_sanitizer",
    "AzureMgmtTestCase",
    "AzureMgmtPreparer",
    "AzureMgmtRecordedTestCase",
    "AzureRecordedTestCase",
    "FakeResource",
    "ResourceGroupPreparer",
    "StorageAccountPreparer",
    "BlobAccountPreparer",
    "CachedStorageAccountPreparer",
    "FakeStorageAccount",
    "AzureTestCase",
    "is_live",
    "get_region_override",
    "KeyVaultPreparer",
    "RandomNameResourceGroupPreparer",
    "CachedResourceGroupPreparer",
    "PemCertificate",
    "PowerShellPreparer",
    "EnvironmentVariableLoader",
    "environment_variables",
    "recorded_by_proxy",
    "recorded_test",
    "test_proxy",
    "set_bodiless_matcher",
    "set_custom_default_matcher",
    "set_default_function_settings",
    "set_default_session_settings",
    "set_function_recording_options",
    "set_headerless_matcher",
    "set_session_recording_options",
    "start_test_proxy",
    "stop_test_proxy",
    "variable_recorder",
    "ResponseCallback",
    "RetryCounter",
    "FakeTokenCredential",
    "create_combined_bundle",
    "is_live_and_not_recording"
]
