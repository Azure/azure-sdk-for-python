import pytest
from devtools_testutils import (
    test_proxy,
    add_general_regex_sanitizer,
    add_remove_header_sanitizer,
    add_oauth_response_sanitizer,
    remove_batch_sanitizers,
)

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    # Scrubbing api-version since latest and mindependency versions of azure-schemaregistry will not be the same.
    add_general_regex_sanitizer(regex="(?<=api-version=)[0-9]{4}-[0-9]{2}(-[0-9]{2})?", value="xxxx-xx")
    add_general_regex_sanitizer(regex="(?<=\\/\\/)[a-z-]+(?=\\.servicebus\\.windows\\.net)", value="fake_resource_avro")
    # Accept is not used by the service. Removing from request headers so changes to Accept are not flagged as diffs.
    add_remove_header_sanitizer(headers="Accept")
    add_oauth_response_sanitizer()

    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3493: $..name
    remove_batch_sanitizers(["AZSDK3493"])

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return
