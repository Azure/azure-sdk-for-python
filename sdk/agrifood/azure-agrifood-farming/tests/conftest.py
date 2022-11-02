import pytest
from devtools_testutils import test_proxy, add_general_string_sanitizer

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return