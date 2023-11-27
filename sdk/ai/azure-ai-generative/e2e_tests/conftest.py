from azure.ai.resources.client import AIClient
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import AzureCliCredential, DefaultAzureCredential, InteractiveBrowserCredential
import logging
from pathlib import Path
import pytest
from typing import List
import uuid

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    from index.conftest import index_pytest_addoption

    parser.addoption("--subscription-id", default="79a1ba0c-35bb-436b-bff2-3074d5ff1f89",
                     help="Subscription id of Azure ML Workspace used for testing.")
    parser.addoption("--resource-group", default="azureml-rag-ci",
                     help="Resource group name of Azure ML Workspace used for testing.")
    parser.addoption("--project-name", default="azureml-rag-eastus",
                     help="Name of Azure ML Workspace used for testing.")
    parser.addoption("--workspace-config-path", default=None,
                     help="Path to workspace config file.")

    parser.addoption("--git-connection-name", default="msdata-Vienna-AmlRunbook")
    parser.addoption("--aoai-connection-name", default="azureml-rag-aoai")
    parser.addoption("--acs-connection-name", default="azureml-rag-acs")
    parser.addoption("--doc-intel-connection-name", default="azureml-rag-documentintelligence")
    parser.addoption("--keep-acs-index", action="store_true", default=False)
    parser.addoption("--acs-index-name", default=None)
    # parser.addoption("--pinecone-connection-name", default="azureml-rag-pinecone-dev")
    # parser.addoption("--keep-pinecone-index", action="store_true", default=False)
    # parser.addoption("--pinecone-index-name", default=None)
    # parser.addoption('--logging-verbosity', default='info',
    #                  help='Sets logging verbosity for test session.')

    index_pytest_addoption(parser)


def pytest_generate_tests(metafunc):
    from index.conftest import pytest_generate_tests as index_generate_tests

    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test 'fixturenames'.
    args = ["subscription_id", "resource_group", "project_name", "workspace_config_path",
            "git_connection_name", "aoai_connection_name", "acs_connection_name",
            "doc_intel_connection_name", "keep_acs_index", "acs_index_name",
            "pinecone_connection_name", "keep_pinecone_index", "pinecone_index_name"]

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
        ai_resource_name = project_name,
        project_name=project_name,
        credential=azure_credentials
    )
    logger.info(f"🔃 Using AIClient: {ai_client}")
    return ai_client


@pytest.fixture(scope="session")
def aoai_connection(ai_client, aoai_connection_name):
    """
    Retieve AOAI connection information.
    """
    try:
        return ai_client.connections.get(aoai_connection_name)
    except ResourceNotFoundError:
        error = f"AOAI connection {aoai_connection_name} not found, create a new connection via UI or code (find this message in code)."
        logger.error(error)
        raise ValueError(error)


@pytest.fixture(scope="session")
def acs_connection(ai_client, acs_connection_name):
    """
    Retrieve ACS connection information.

    To register a new connection use azure.ai.ml.MLClient.connections.create
    or AI/ML Workspace UI.
    """
    try:
        return ai_client.connections.get(acs_connection_name)
    except ResourceNotFoundError:
        error = f"Azure Search connection {acs_connection_name} not found, create a new connection via UI or code (find this message in code)."
        logger.error(error)
        raise ValueError(error)


@pytest.fixture(scope="session")
def document_intelligence_connection(ai_client, document_intelligence_connection_name):
    """Retrieve ACS connection information."""
    try:
        return ai_client.connections.get(document_intelligence_connection_name)
    except ResourceNotFoundError:
        error = f"Custom connection {document_intelligence_connection_name} not found, create a new connection via UI or code (find this message in code)."
        logger.error(error)
        raise ValueError(error)


@pytest.fixture(scope="session")
def free_tier_acs_connection(ai_client) -> dict:
    """
    Retrieve ACS connection information.

    To register a new connection use azure.ai.ml.MLClient.connections.create
    or AI/ML Workspace UI.
    """
    return ai_client.connections.get("free-teir-eastus")


@pytest.fixture(scope="session")
def acs_temp_index(acs_connection, keep_acs_index, acs_index_name):
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient

    index_name = acs_index_name if acs_index_name is not None else f"azure-ai-generative-test-{uuid.uuid4()}"

    yield index_name

    if keep_acs_index:
        logger.info(f"Keeping index: {index_name}")
    else:
        logger.info(f"Deleting index: {index_name}")
        index_client = SearchIndexClient(
            endpoint=acs_connection.target,
            credential=AzureKeyCredential(acs_connection.credentials.key)
        )
        index_client.delete_index(index_name)


@pytest.fixture(scope="session")
def pinecone_temp_index(pinecone_connection, keep_pinecone_index, pinecone_index_name):
    import pinecone

    index_name = pinecone_index_name if pinecone_index_name is not None else f"rag-{uuid.uuid4()}"

    yield index_name

    # Note: If using the Starter Plan which only allows having one index, make sure to delete index afterwards (this is by default).
    if keep_pinecone_index:
        logger.info(f"Keeping index: {index_name}")
    else:
        logger.info(f"Deleting index: {index_name}")
        pinecone.init(api_key=pinecone_connection["properties"]["credentials"]["keys"]["api_key"], environment=pinecone_connection["properties"]["metadata"]["environment"])
        pinecone.delete_index(index_name)
