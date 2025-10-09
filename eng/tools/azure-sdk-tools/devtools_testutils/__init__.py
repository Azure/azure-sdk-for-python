from .mgmt_testcase import AzureMgmtPreparer
from .mgmt_recorded_testcase import AzureMgmtRecordedTestCase
from .azure_recorded_testcase import AzureRecordedTestCase, get_credential
from .azure_testcase import is_live, get_region_override
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

# cSpell:disable
from .envvariable_loader import EnvironmentVariableLoader
from .exceptions import AzureTestError, ReservedResourceNameError
from .proxy_fixtures import environment_variables, recorded_test, variable_recorder
from .proxy_startup import start_test_proxy, stop_test_proxy, test_proxy
from .proxy_testcase import recorded_by_proxy
from .sanitizers import (
    add_api_version_transform,
    add_batch_sanitizers,
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
    remove_batch_sanitizers,
    PemCertificate,
    Sanitizer,
    set_bodiless_matcher,
    set_custom_default_matcher,
    set_default_function_settings,
    set_default_session_settings,
    set_function_recording_options,
    set_headerless_matcher,
    set_session_recording_options,
)
from .cert import create_combined_bundle
from .helpers import ResponseCallback, RetryCounter, is_live_and_not_recording, trim_kwargs_from_test_function
from .fake_credentials import FakeTokenCredential

PowerShellPreparer = EnvironmentVariableLoader  # Backward compat

__all__ = [
    "add_api_version_transform",
    "add_batch_sanitizers",
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
    "get_credential",
    "remove_batch_sanitizers",
    "AzureMgmtPreparer",
    "AzureMgmtRecordedTestCase",
    "AzureRecordedTestCase",
    "AzureTestError",
    "FakeResource",
    "ReservedResourceNameError",
    "ResourceGroupPreparer",
    "Sanitizer",
    "StorageAccountPreparer",
    "BlobAccountPreparer",
    "CachedStorageAccountPreparer",
    "FakeStorageAccount",
    "is_live",
    "get_region_override",
    "RandomNameResourceGroupPreparer",
    "CachedResourceGroupPreparer",
    "PemCertificate",
    "PowerShellPreparer",
    "EnvironmentVariableLoader",
    "environment_variables",
    "recorded_by_proxy",
    "recorded_test",
    "test_proxy",
    "trim_kwargs_from_test_function",
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
    "is_live_and_not_recording",
]
