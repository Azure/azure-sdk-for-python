import pytest
from devtools_testutils import (
    test_proxy,
    add_remove_header_sanitizer
)

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
#def start_proxy(test_proxy):
 #   return

@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    add_remove_header_sanitizer(headers="Ocp-Apim-Subscription-Key")