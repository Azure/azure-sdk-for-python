import uuid
import pytest
import os
from devtools_testutils import (
    add_uri_regex_sanitizer,
    remove_batch_sanitizers,
    test_proxy,
)


# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
# test_proxy auto-starts the test proxy
# patch_sleep and patch_async_sleep streamline tests by disabling wait times during LRO polling
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy, patch_sleep, patch_async_sleep):
    return


uniquifier_file = os.path.join(os.path.dirname(__file__), "uniquifier.conf")


@pytest.fixture(scope="session", autouse=True)
def create_session_uniquifier():
    if (
        os.environ.get("AZURE_TEST_RUN_LIVE", "false").lower() == "true"  # Don't override uniquifier by default
        and os.environ.get("AZURE_SKIP_LIVE_RECORDING", "false").lower() != "true"
        and os.environ.get("AZURE_TEST_KEEP_UNIQUIFIER", "false").lower() != "true"
    ):
        print("Creating new uniquifier for live test run.")
        uniquifier = uuid.uuid4().hex[:6]
        os.environ["HEALTHDATAAISERVICES_UNIQUIFIER"] = uniquifier
        with open(uniquifier_file, "w") as file:
            file.write(uniquifier)
    else:
        print("Using existing")
        with open(uniquifier_file, "r") as file:
            uniquifier = file.read()
            os.environ["HEALTHDATAAISERVICES_UNIQUIFIER"] = uniquifier


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    # $..name
    # $..id
    # uri sanitization in favor of substitution
    remove_batch_sanitizers(["AZSDK3493", "AZSDK3430", "AZSDK4001"])
    add_uri_regex_sanitizer(regex='continuationToken=[^&"}]*', value="continuationToken=Sanitized")
