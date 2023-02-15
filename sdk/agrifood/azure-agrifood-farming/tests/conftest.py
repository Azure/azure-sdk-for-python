import pytest
from devtools_testutils import set_custom_default_matcher

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    set_custom_default_matcher(ignored_headers="Accept-Encoding")
    return