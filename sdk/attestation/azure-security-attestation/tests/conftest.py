import pytest
from devtools_testutils import add_general_string_sanitizer,test_proxy, add_oauth_response_sanitizer

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    add_general_string_sanitizer(target="sharedwus", value="fakeresource")
    add_general_string_sanitizer(target="policies/SgxEnclave:reset", value="policies/Tpm:reset")
    add_general_string_sanitizer(target="policies/OpenEnclave:reset", value="policies/Tpm:reset")
    add_general_string_sanitizer(target="policies/SgxEnclave", value="policies/Tpm")
    add_general_string_sanitizer(target="policies/OpenEnclave", value="policies/Tpm")
    add_oauth_response_sanitizer()
    return
 
