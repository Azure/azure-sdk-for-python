import uuid
import pytest
import os
from devtools_testutils import (
    add_body_key_sanitizer,
    add_general_string_sanitizer,
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
        os.environ.get("AZURE_TEST_RUN_LIVE", "false").lower()
        == "true"  # Don't override uniquifier by default
        and os.environ.get("AZURE_SKIP_LIVE_RECORDING", "false").lower() != "true"
    ):
        uniquifier = uuid.uuid4().hex[:6]
        os.environ["HEALTHDATAAISERVICES_UNIQUIFIER"] = uniquifier
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
    account_name = os.environ.get(
        "HEALTHDATAAISERVICES_STORAGE_ACCOUNT_NAME", "Not Found."
    )
    container_name = os.environ.get(
        "HEALTHDATAAISERVICES_STORAGE_CONTAINER_NAME", "Not Found."
    )
    add_body_key_sanitizer(
        json_path="..location",
        value=f"https://{account_name}.blob.core.windows.net:443/{container_name}",
    )
