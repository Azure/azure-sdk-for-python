import pytest
from devtools_testutils import (
    add_oauth_response_sanitizer,
    add_remove_header_sanitizer,
)


# autouse=True will trigger this fixture on each pytest run
# test_proxy auto-starts the test proxy
# patch_sleep and patch_async_sleep remove wait times during polling
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy, patch_sleep, patch_async_sleep):
    add_remove_header_sanitizer(headers="Ocp-Apim-Subscription-Key,Authorization")
    add_oauth_response_sanitizer()
    return
