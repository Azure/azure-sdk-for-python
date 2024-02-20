from datetime import datetime
import logging
import uuid
from pathlib import Path
from typing import List

import pytest
from azure.ai.resources._index._utils.connections import connection_to_credential, get_metadata_from_connection

logger = logging.getLogger(__name__)


def remote_pytest_addoption(parser):
    parser.addoption(
        "--experiment-name",
        default=f"dev-rag-e2e-{datetime.utcnow().month:02}{datetime.utcnow().day:02}",
        help="Name of experiment to run all tests under, defaults to <alias>rag-e2e-<month><day>.",
    )
    # TODO: Run `az ad signed-in-user show`, parse as json, use `userPrincipalName` via r'(.*)@microsoft.com' as alias.
    parser.addoption("--stream-run-output", action="store_true", default=False)
    parser.addoption("--dump-components-path", default=None)
    parser.addoption(
        "--component-source",
        default="dev",
        help="Local dev components are used by default, use 'registry:<registry_name>' to use components from a registry, use 'file://<path>' to use components from a local path (typically azureml-assets).",
    )

def pytest_addoption(parser):
    parser.addoption("--subscription-id", default="79a1ba0c-35bb-436b-bff2-3074d5ff1f89", help="Subscription id of Azure ML Workspace used for testing.")
    parser.addoption("--resource-group", default="azureml-rag-ci", help="Resource group name of Azure ML Workspace used for testing.")
    parser.addoption("--workspace-name", default="azureml-rag-eastus", help="Name of Azure ML Workspace used for testing.")
    parser.addoption("--workspace-config-path", default=None, help="Path to workspace config file.")
    parser.addoption("--git-connection-name", default="msdata-Vienna-AmlRunbook")
    parser.addoption("--aoai-connection-name", default="prod-azureml-rag")
    parser.addoption("--acs-connection-name", default="azureml-rag-acs-v2")
    parser.addoption("--doc-intel-connection-name", default="azureml-rag-documentintelligence")
    parser.addoption("--keep-acs-index", action="store_true", default=False)
    parser.addoption("--acs-index-name", default=None)
    parser.addoption("--pinecone-connection-name", default="azureml-rag-pinecone-dev")
    parser.addoption("--keep-pinecone-index", action="store_true", default=False)
    parser.addoption("--pinecone-index-name", default=None)
    parser.addoption("--milvus-connection-name", default="datdo-milvus-dev")
    parser.addoption("--keep-milvus-collection", action="store_true", default=False)
    parser.addoption("--milvus-collection-name", default=None)
    parser.addoption("--cosmos-namespace", default=None)
    parser.addoption("--cosmos-connection-name", default="azureml-rag-cosmos-mongo-dev")
    parser.addoption("--keep-cosmos-collection", action="store_true", default=False)
    parser.addoption("--vision-acs-connection", default="vision-acs-connection")
    parser.addoption("--florence-connection", default="florence-connection")
    parser.addoption("--embeddings-model", default="azure_open_ai://deployment/text-embedding-ada-002/model/text-embedding-ada-002", help="The embedding model deployed for testing.")

    remote_pytest_addoption(parser)

def pytest_generate_tests(metafunc):

    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test 'fixturenames'.
    args = ["subscription_id", "resource_group", "workspace_name", "workspace_config_path",
            "git_connection_name", "aoai_connection_name", "acs_connection_name",
            "doc_intel_connection_name", "keep_acs_index", "acs_index_name",
            "pinecone_connection_name", "keep_pinecone_index", "pinecone_index_name",
            "milvus_connection_name", "keep_milvus_collection", "milvus_collection_name",
            "cosmos_namespace", "cosmos_connection_name", "keep_cosmos_collection",
            "vision_acs_connection", "florence_connection", "embeddings_model", 
            "experiment_name", "stream_run_output", "dump_components_path", "component_source"]
    parameterize_metafunc(metafunc, args)

def parameterize_metafunc(metafunc, param_names: List[str]):
    for param_name in param_names:
        if hasattr(metafunc.config.option, param_name):
            param_value = getattr(metafunc.config.option, param_name)
        else:
            param_value = None
        if param_name in metafunc.fixturenames:
            metafunc.parametrize(param_name, [param_value], scope="session")

@pytest.fixture()
def test_dir():
    test_dir = Path(__file__).parent
    logger.info(f"test directory is {test_dir}")
    return test_dir


@pytest.fixture()
def test_data_dir(test_dir):
    test_data_dir = test_dir / "data"
    logger.info(f"test data directory is {test_data_dir}")
    return test_data_dir

# TODO: Update to use WorkspaceConnections and MLClients
@pytest.fixture(scope="session")
def free_tier_acs_connection(azureml_workspace_v1) -> dict:
    """
    Retrieve ACS connection information.

    To register a new connection use azure.ai.ml.MLClient.connections.create
    or AI/ML Workspace UI.
    """
    from azure.ai.resources._index._utils.connections import get_connection_by_name_v2

    return get_connection_by_name_v2(azureml_workspace_v1, "free-teir-eastus")

@pytest.fixture(scope="session")
def azureml_workspace_v1(subscription_id, resource_group, workspace_name, workspace_config_path):
    from azureml.core import Workspace
    from azureml.core.authentication import AzureCliAuthentication

    if workspace_config_path is not None and len(workspace_config_path) > 0:
        logger.info(
            f"🔃 Loading workspace from config file: {workspace_config_path}.")
        return Workspace.from_config(path=workspace_config_path)

    logger.info(f"🔃 Using AzureML workspace: {workspace_name}")
    return Workspace(subscription_id, resource_group, workspace_name, auth=AzureCliAuthentication())

# TODO: Update to use WorkspaceConnections and MLClients
@pytest.fixture(scope="session")
def acs_connection(azureml_workspace_v1, acs_connection_name) -> dict:
    """
    Retrieve ACS connection information.

    To register a new connection use azure.ai.ml.MLClient.connections.create
    or AI/ML Workspace UI.
    """
    from azure.ai.resources._index._utils.connections import get_connection_by_name_v2

    return get_connection_by_name_v2(azureml_workspace_v1, acs_connection_name)