import pytest
from devtools_testutils import remove_batch_sanitizers, test_proxy

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
# test_proxy auto-starts the test proxy
# patch_sleep and patch_async_sleep streamline tests by disabling wait times during LRO polling
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy, patch_sleep, patch_async_sleep):
    return

@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    ...
    #  Remove the following body key sanitizer: AZSDK3430: $..id
    remove_batch_sanitizers(["AZSDK3430"])
