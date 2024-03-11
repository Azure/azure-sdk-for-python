import pytest
from devtools_testutils import test_proxy, add_header_regex_sanitizer, add_general_regex_sanitizer
import os

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return


from devtools_testutils import add_header_regex_sanitizer


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    add_header_regex_sanitizer(key="client-request-id", value="match_all")
    tenant_id = os.environ.get("AZURE_TENANT_ID", "00000000-0000-0000-0000-000000000000")
    client_id = os.environ.get("AZURE_CLIENT_ID", "00000000-0000-0000-0000-000000000000")
    client_secret = os.environ.get("AZURE_CLIENT_SECRET", "00000000-0000-0000-0000-000000000000")
    subscription_id = os.environ.get("SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=tenant_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=client_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=client_secret, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=subscription_id, value="00000000-0000-0000-0000-000000000000")
    add_header_regex_sanitizer(key="Cookie", value="cookie;")

    # add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")
    # add_body_key_sanitizer(json_path="$..access_token", value="access_token")
