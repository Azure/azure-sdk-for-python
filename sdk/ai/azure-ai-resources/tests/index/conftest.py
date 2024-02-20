import logging
import uuid
from pathlib import Path
from typing import List

import pytest
from azure.ai.resources._index._utils.connections import connection_to_credential, get_metadata_from_connection

logger = logging.getLogger(__name__)


# def pytest_addoption(parser):
#     from remote.conftest import remote_pytest_addoption

#     parser.addoption("--subscription-id", default="79a1ba0c-35bb-436b-bff2-3074d5ff1f89", help="Subscription id of Azure ML Workspace used for testing.")
#     parser.addoption("--resource-group", default="azureml-rag-ci", help="Resource group name of Azure ML Workspace used for testing.")
#     parser.addoption("--workspace-name", default="azureml-rag-eastus", help="Name of Azure ML Workspace used for testing.")
#     parser.addoption("--workspace-config-path", default=None, help="Path to workspace config file.")
#     parser.addoption("--git-connection-name", default="msdata-Vienna-AmlRunbook")
#     parser.addoption("--aoai-connection-name", default="prod-azureml-rag")
#     parser.addoption("--acs-connection-name", default="azureml-rag-acs-v2")
#     parser.addoption("--doc-intel-connection-name", default="azureml-rag-documentintelligence")
#     parser.addoption("--keep-acs-index", action="store_true", default=False)
#     parser.addoption("--acs-index-name", default=None)
#     parser.addoption("--pinecone-connection-name", default="azureml-rag-pinecone-dev")
#     parser.addoption("--keep-pinecone-index", action="store_true", default=False)
#     parser.addoption("--pinecone-index-name", default=None)
#     parser.addoption("--milvus-connection-name", default="datdo-milvus-dev")
#     parser.addoption("--keep-milvus-collection", action="store_true", default=False)
#     parser.addoption("--milvus-collection-name", default=None)
#     parser.addoption("--cosmos-namespace", default=None)
#     parser.addoption("--cosmos-connection-name", default="azureml-rag-cosmos-mongo-dev")
#     parser.addoption("--keep-cosmos-collection", action="store_true", default=False)
#     parser.addoption("--vision-acs-connection", default="vision-acs-connection")
#     parser.addoption("--florence-connection", default="florence-connection")
    
#     remote_pytest_addoption(parser)

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