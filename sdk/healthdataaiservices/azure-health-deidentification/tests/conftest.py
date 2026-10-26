import uuid
import pytest
import os
from devtools_testutils import (
    add_uri_regex_sanitizer,
    remove_batch_sanitizers,
    set_custom_default_matcher,
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
    is_live = os.environ.get("AZURE_TEST_RUN_LIVE", "false").lower() == "true"
    skip_recording = os.environ.get("AZURE_SKIP_LIVE_RECORDING", "false").lower() == "true"
    keep_uniquifier = os.environ.get("AZURE_TEST_KEEP_UNIQUIFIER", "false").lower() == "true"
    if is_live and not keep_uniquifier:
        # Every live run gets fresh job names so reused resources or parallel matrix legs can't collide.
        uniquifier = uuid.uuid4().hex[:6]
        print(f"Creating new uniquifier for live test run: {uniquifier}")
        os.environ["HEALTHDATAAISERVICES_UNIQUIFIER"] = uniquifier
        if not skip_recording:
            # Persist only when recording so playback replays the job names in the new recordings.
            with open(uniquifier_file, "w") as file:
                file.write(uniquifier)
    else:
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
    # Regenerated delete_job no longer sends "Accept: application/json" for its 204 response; existing
    # recordings still contain it.
    set_custom_default_matcher(excluded_headers="Accept")
