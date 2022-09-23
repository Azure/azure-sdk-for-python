import os
from devtools_testutils import (
    test_proxy,
    add_general_regex_sanitizer
)
import pytest

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    add_general_regex_sanitizer(value="https://fake-endpoint.azconfig.io",
                                regex=os.environ.get('APPCONFIGURATION_ENDPOINT_STRING'))
    add_general_regex_sanitizer(value="fake-connection-string",
                                regex=os.environ.get('APPCONFIGURATION_CONNECTION_STRING'))
    add_general_regex_sanitizer(
        value="fake-client-id", regex=os.environ.get('APPCONFIGURATION_CLIENT_ID'))
    add_general_regex_sanitizer(
        value="fake-client-secret", regex=os.environ.get('APPCONFIGURATION_CLIENT_SECRET'))
    add_general_regex_sanitizer(
        value="fake-tenant-id", regex=os.environ.get('APPCONFIGURATION_TENANT_ID'))
