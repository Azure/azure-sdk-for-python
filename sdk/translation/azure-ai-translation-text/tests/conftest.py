import pytest
from devtools_testutils import test_proxy, add_remove_header_sanitizer, remove_batch_sanitizers

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
# def start_proxy(test_proxy):
#   return


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    add_remove_header_sanitizer(headers="Ocp-Apim-Subscription-Key")

    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3430: $..id
    #  - AZSDK3424: $..to
    remove_batch_sanitizers(["AZSDK3430", "AZSDK3424"])
