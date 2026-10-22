import pytest
from devtools_testutils import EnvironmentVariableLoader

# Environment variable keys
ENV_ENDPOINT = "AUTHORING_ENDPOINT"
ENV_KEY = "AUTHORING_KEY"

@pytest.fixture(scope="session")
def authoring_endpoint(environment_variables: EnvironmentVariableLoader) -> str:
    """Endpoint for Authoring tests."""
    return environment_variables.get(ENV_ENDPOINT)

@pytest.fixture(scope="session")
def authoring_key(environment_variables: EnvironmentVariableLoader) -> str:
    """API key for Authoring tests."""
    return environment_variables.get(ENV_KEY)

# autouse=True will trigger this fixture on each pytest run
# test_proxy auto-starts the test proxy
# patch_sleep and patch_async_sleep remove wait times during polling
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy, patch_sleep, patch_async_sleep):
    return