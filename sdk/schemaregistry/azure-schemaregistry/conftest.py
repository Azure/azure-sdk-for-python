import pytest
from devtools_testutils import (
    test_proxy,
    add_general_regex_sanitizer,
    add_oauth_response_sanitizer,
    remove_batch_sanitizers,
)


# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    add_general_regex_sanitizer(
        regex="(?<=\\/\\/)[a-z-]+_avro(?=\\.servicebus\\.windows\\.net)", value="fake_resource_avro"
    )
    add_general_regex_sanitizer(
        regex="(?<=\\/\\/)[a-z-]+_json(?=\\.servicebus\\.windows\\.net)", value="fake_resource_json"
    )
    add_general_regex_sanitizer(
        regex="(?<=\\/\\/)[a-z-]+_custom(?=\\.servicebus\\.windows\\.net)", value="fake_resource_custom"
    )
    add_general_regex_sanitizer(
        regex="(?<=\\/\\/)[a-z-]+_protobuf(?=\\.servicebus\\.windows\\.net)", value="fake_resource_protobuf"
    )
    add_oauth_response_sanitizer()

    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3493: $..name
    remove_batch_sanitizers(["AZSDK3493"])


# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return
