import pytest
from devtools_testutils import add_general_regex_sanitizer, test_proxy, add_oauth_response_sanitizer

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    add_general_regex_sanitizer(regex="(?<=\\/\\/)[a-z-]+(?=\\.servicebus\\.windows\\.net)", value="fake_resource")
    add_oauth_response_sanitizer()

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return
