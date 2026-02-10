import pytest
from devtools_testutils import EnvironmentVariableLoader

# Environment variable keys
ENV_ENDPOINT = "TEXT_ANALYSIS_ENDPOINT"
ENV_KEY = "TEXT_ANALYSIS_KEY"


@pytest.fixture(scope="session")
def text_analysis_endpoint(environment_variables: EnvironmentVariableLoader) -> str:
    """Endpoint for Text Analysis tests."""
    return environment_variables.get(ENV_ENDPOINT)


@pytest.fixture(scope="session")
def text_analysis_key(environment_variables: EnvironmentVariableLoader) -> str:
    """API key for Text Analysis tests."""
    return environment_variables.get(ENV_KEY)


# autouse=True will trigger this fixture on each pytest run
# test_proxy auto-starts the test proxy
# patch_sleep and patch_async_sleep remove wait times during polling
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy, patch_sleep, patch_async_sleep):
    return
