import logging
from pathlib import Path
import pytest
from typing import List
from azure.identity import AzureCliCredential, DefaultAzureCredential, InteractiveBrowserCredential

from azure.ai.generative import AIClient

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    from index.conftest import index_pytest_addoption

    parser.addoption("--subscription-id", default="b17253fa-f327-42d6-9686-f3e553e24763",
                     help="Subscription id of Azure AI Project used for testing.")
    parser.addoption("--resource-group", default="hanchi-test",
                     help="Resource group name of Azure AI Project used for testing.")
    parser.addoption("--project_name-name", default="hwep",
                     help="Name of Azure AI Project used for testing.")
    parser.addoption("--workspace-config-path", default="./config.json",
                     help="Path to workspace config file.")

    index_pytest_addoption(parser)


def pytest_generate_tests(metafunc):
    from index.conftest import pytest_generate_tests as index_generate_tests

    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test 'fixturenames'.
    args = ["subscription_id", "resource_group", "project_name", "workspace_config_path"]
    args.extend(index_generate_tests())
    parameterize_metafunc(metafunc, args)


def parameterize_metafunc(metafunc, param_names: List[str]):
    for param_name in param_names:
        if hasattr(metafunc.config.option, param_name):
            param_value = getattr(metafunc.config.option, param_name)
        else:
            param_value = None
        if param_name in metafunc.fixturenames:
            metafunc.parametrize(param_name, [param_value], scope="session")


@pytest.fixture(scope="session")
def azure_credentials():
    try:
        credential = AzureCliCredential(process_timeout=60)
        # Check if given credential can get token successfully.
        credential.get_token("https://management.azure.com/.default")
    except Exception:
        try:
            credential = DefaultAzureCredential(process_timeout=60)
            # Check if given credential can get token successfully.
            credential.get_token("https://management.azure.com/.default")
        except Exception:
            credential = InteractiveBrowserCredential()

    return credential


@pytest.fixture(scope="session")
def ai_client(azure_credentials, subscription_id, resource_group, project_name, workspace_config_path):
    if workspace_config_path is not None and len(workspace_config_path) > 0:
        logger.info(
            f"🔃 Loading Project details from config file: {workspace_config_path}.")
        try:
            return AIClient.from_config(credential=azure_credentials, path=workspace_config_path)
        except Exception as e:
            logger.warning(
                f"Failed to load Project details from config file: {workspace_config_path}: {e}")

    ai_client = AIClient(
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        project_name=project_name,
        credential=azure_credentials
    )
    logger.info(f"🔃 Using AIClient: {ai_client}")
    return ai_client


@pytest.fixture(scope="session")
def ml_client(ai_client):
    return ai_client._ml_client


@pytest.fixture()
def test_dir():
    test_dir = Path(__file__).parent
    logger.info(f"test directory is {test_dir}")
    return test_dir
