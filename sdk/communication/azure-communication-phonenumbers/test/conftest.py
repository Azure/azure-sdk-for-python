import os
import pytest
from devtools_testutils import add_general_regex_sanitizer, add_general_string_sanitizer, test_proxy

@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    add_general_regex_sanitizer(regex="^(.*?)\.communication.azure.com", value="https://sanitized.communication.azure.com")