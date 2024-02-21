import base64
import json
import logging
import uuid
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest
from azure.search.documents.indexes import SearchIndexClient
from azure.ai.generative.index._embeddings import EmbeddingsContainer
from azure.ai.generative.index._mlindex import MLIndex
from azure.ai.generative.index._tasks.update_acs import create_index_from_raw_embeddings, search_client_from_config

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingConfig:
    embedding_uri: str
    embedding_connection: str


@pytest.fixture()
def test_acs_no_embeddings(acs_connection, acs_index_name):
    from azure.core.credentials import AzureKeyCredential
    test_acs_config = {
        "endpoint": acs_connection.target,
        "index_name": acs_index_name if acs_index_name is not None else f"azureml-rag-test-{uuid.uuid4()}",
        "api_version": "2021-04-30-Preview",
        "credential": AzureKeyCredential(acs_connection.credentials.key),
        "connection_args": {
            "connection_type": "workspace_connection",
            "connection": {
                "id": acs_connection.id,
            },
        },
        "push_embeddings": "False"
    }
    yield test_acs_config

    logger.info(f"Deleting index: {test_acs_config['index_name']}")
    index_client = SearchIndexClient(endpoint=acs_connection.target, credential=test_acs_config["credential"], api_version=test_acs_config["api_version"])
    index_client.delete_index(test_acs_config["index_name"])


@pytest.fixture(scope="session")
def test_acs_embeddings(acs_connection, keep_acs_index, acs_index_name):
    from azure.core.credentials import AzureKeyCredential
    test_acs_config = {
        "endpoint": acs_connection.target,
        "index_name": acs_index_name if acs_index_name is not None else f"azureml-rag-test-{uuid.uuid4()}",
        "api_version": "2023-07-01-preview",
        "credential": AzureKeyCredential(acs_connection.credentials.key),
        "connection_args": {
            "connection_type": "workspace_connection",
            "connection": {
                "id": acs_connection.id,
            },
        }
    }
    yield test_acs_config

    if keep_acs_index:
        logger.info(f"Keeping index: {test_acs_config['index_name']}")
    else:
        logger.info(f"Deleting index: {test_acs_config['index_name']}")
        index_client = SearchIndexClient(endpoint=acs_connection.target, credential=test_acs_config["credential"], api_version=test_acs_config["api_version"])
        index_client.delete_index(test_acs_config["index_name"])


# TODO: Test index fixture is same for both configs, can't run both at once until fixed.
@pytest.mark.parametrize("embedding_config", [
    #EmbeddingConfig("azure_open_ai://deployment/text-embedding-ada-002/model/text-embedding-ada-002", "aoai_connection"),
    EmbeddingConfig("hugging_face://model/sentence-transformers/all-mpnet-base-v2", None)
])
def test_update_acs_embeddings(test_data_dir: Path, test_acs_embeddings, embedding_config):
    run_acs_update(test_acs_embeddings, test_data_dir, embedding_config)


# TODO: fix acs no embeddings test
# def test_update_acs_no_embeddings(test_data_dir: Path, test_acs_no_embeddings):
#     run_acs_update(test_acs_no_embeddings, test_data_dir)


def run_acs_update(test_acs_config, test_data_dir, embedding_config=None):
    embedding_kind = "none"
    if embedding_config:
        embedding_kind = embedding_config.embedding_uri.split("://")[0]
    embeddings_container = (test_data_dir / "embedded_documents" / embedding_kind).resolve()
    logger.info(embeddings_container)

    acs_index_dir =  test_data_dir / "acs_mlindex"

    emb = EmbeddingsContainer.load("first_run", str(embeddings_container))
    # TODO: Support override aoai_connection on EmbeddingsContainer

    create_index_from_raw_embeddings(emb, test_acs_config, connection=test_acs_config["connection_args"], output_path=str(acs_index_dir))

    search_client = search_client_from_config(test_acs_config, credential=test_acs_config["credential"])

    # Query ACS Index to confirm contents
    # use_semantic_captions = False
    exclude_category = None
    filter = f"category ne '{exclude_category}'" if exclude_category else None
    top = 20

    logger.info(f"Searching for top {top} results in index: {test_acs_config['index_name']}")
    results = search_client.search(
        "*",
        filter=filter,
        top=top,
        # query_type=QueryType.SEMANTIC,
        # query_language="en-us",
        # query_speller="lexicon",
        # semantic_configuration_name="default",
        # query_caption="extractive|highlight-false" if use_semantic_captions else None
    )

    emb = EmbeddingsContainer.load("first_run", str(embeddings_container))

    for i, result in enumerate(results):
        logger.debug(f"Result {i}: {result}")
        doc_id = base64.urlsafe_b64decode(result["id"].encode("utf8")).decode("utf-8")
        assert doc_id in emb._document_embeddings
        assert emb._document_embeddings[doc_id].get_data() == result["content"]
        assert json.dumps(emb._document_embeddings[doc_id].metadata) == result["meta_json_string"]
        if test_acs_config.get("push_embeddings", "True") != "False":
            assert np.isclose(emb._document_embeddings[doc_id].get_embeddings(), result[f"contentVector"]).all()

    # Test MLIndex
   # if test_acs_config.get("push_embeddings") != "False":
    logger.info(acs_index_dir)

    mlindex = MLIndex(str(acs_index_dir))

    assert mlindex.index_config["kind"] == "acs"
    assert mlindex.embeddings_config["kind"] == embedding_kind.lstrip("azure_")

    langchain_retriever = mlindex.as_langchain_retriever()
    logger.info(f"{type(langchain_retriever) = }")

    docs = langchain_retriever.get_relevant_documents("e2e multinode classify")
    logger.info(json.dumps([{"content": doc.page_content, "metadata": doc.metadata} for doc in docs], indent=2))
    assert len(docs) == 8
    assert docs[0].metadata["source"]["filename"] == "tutorials_README.md"


@pytest.fixture(scope="session")
def test_free_acs_embeddings(free_tier_acs_connection, keep_acs_index, acs_index_name):
    from azure.core.credentials import AzureKeyCredential
    test_acs_config = {
        "endpoint": free_tier_acs_connection.target,
        "index_name": acs_index_name if acs_index_name is not None else f"azureml-rag-test-{uuid.uuid4()}",
        "api_version": "2023-07-01-preview",
        "credential": AzureKeyCredential(free_tier_acs_connection.credentials.key),
        "connection_args": {
            "connection_type": "workspace_connection",
            "connection": {
                "id": free_tier_acs_connection.id,
            },
        }
    }
    yield test_acs_config

    if keep_acs_index:
        logger.info(f"Keeping index: {test_acs_config['index_name']}")
    else:
        logger.info(f"Deleting index: {test_acs_config['index_name']}")
        index_client = SearchIndexClient(endpoint=free_tier_acs_connection.target, credential=test_acs_config["credential"], api_version=test_acs_config["api_version"])
        index_client.delete_index(test_acs_config["index_name"])


@pytest.mark.parametrize("embedding_config", [
    EmbeddingConfig("azure_open_ai://deployment/text-embedding-ada-002/model/text-embedding-ada-002", "aoai_connection")
    # EmbeddingConfig("hugging_face://model/sentence-transformers/all-mpnet-base-v2", None)
])
def test_free_tier_acs(test_data_dir, test_free_acs_embeddings, embedding_config):
    run_acs_update(test_free_acs_embeddings, test_data_dir, embedding_config)
