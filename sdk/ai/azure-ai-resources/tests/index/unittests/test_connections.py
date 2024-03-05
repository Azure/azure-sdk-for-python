import logging
import os
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.ai.resources._index._mlindex import MLIndex
from azure.ai.resources._index._utils.connections import get_connection_credential

logger = logging.getLogger(__name__)


def test_connection_credential(test_data_dir: Path):
    environment_mlindex = (test_data_dir / "mlindex_connections").resolve()
    logger.info(environment_mlindex)

    index = MLIndex(str(environment_mlindex))

    os.environ["ACS-PROD-KEY"] = "key1"
    cred = get_connection_credential(index.index_config)
    assert isinstance(cred, AzureKeyCredential)
    assert cred.key == "key1"

    os.environ["CUSTOM-OPENAI-API-KEY"] = "key2"
    cred = get_connection_credential(index.embeddings_config)
    assert isinstance(cred, AzureKeyCredential)
    assert cred.key == "key2"