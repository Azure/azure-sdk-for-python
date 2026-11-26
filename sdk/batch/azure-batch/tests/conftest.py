import pytest
from devtools_testutils import (
    test_proxy,
    set_custom_default_matcher,
    remove_batch_sanitizers,
    add_uri_regex_sanitizer,
)


@pytest.fixture(autouse=True)
def add_sanitizers(test_proxy):
    #  Remove the following body key sanitizer:
    #  - AZSDK3430: $..id
    #  - AZSDK3493: $..name
    remove_batch_sanitizers(["AZSDK3430", "AZSDK3493"])
    # Existing accounts may be outside the default region used by playback preparers.
    add_uri_regex_sanitizer(
        regex=r"https://[^/.]+\.[^/.]+\.batch\.azure\.com",
        value="https://Sanitized.eastus2.batch.azure.com",
    )


# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    set_custom_default_matcher(ignored_headers="Accept, ocp-date, client-request-id", excluded_headers="Connection")
    return
