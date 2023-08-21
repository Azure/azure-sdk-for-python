import logging
from pathlib import Path

import pytest

from azure.ai.ml import load_data
from azure.ai.ml.data_index import index_data
from azure.ai.ml.entities import CitationRegex, Data, DataIndex, Embedding, IndexSource, IndexStore

# Stops noisy warning logs from urllib3 before test-proxy starts serving
connectionpool_logger = logging.getLogger("urllib3.connectionpool")
connectionpool_logger.setLevel(logging.CRITICAL)

unittests_folder = Path(__file__).parent


@pytest.mark.unittest
@pytest.mark.data_index_test
class TestDataIndex:
    def test_data_index_uri_to_acs_aoai(self):
        data_index1 = load_data(source=str(unittests_folder / "../../test_configs/data_index/data_index_aoai_acs.yaml"))
        data_index2 = DataIndex(
            name="azure_docs_ml_aoai",
            type="uri_folder",
            path="azureml://datastores/workspaceblobstore/paths/{name}",
            source=IndexSource(
                input_data=Data(
                    type="uri_folder",
                    path=str(unittests_folder / "../test_data")
                    # path = "https://github.com/MicrosoftDocs/azure-docs.git"
                ),
                # input_glob = "articles/machine-learning/**/*",
                chunk_size=1024,
                chunk_overlap=0,
                citation_url="https://learn.microsoft.com/en-us/azure",
                citation_url_replacement_regex=CitationRegex(
                    match_pattern="(.*)/articles/(.*)(\\.[^.]+)$", replacement_pattern="\\1/\\2"
                ),
            ),
            embedding=Embedding(
                model="azure_open_ai://deployment/text-embedding-ada-002/model/text-embedding-ada-002",
                connection="azureml:azureml-rag-aoai-v2",
                cache_path="azureml://datastores/workspaceblobstore/paths/embeddings_cache/azure_docs_ml_aoai",
            ),
            index=IndexStore(
                type="acs",
                connection="azureml:azureml-rag-acs-v2",
                name="azure_docs_ml_aoai",
            ),
        )

        assert isinstance(data_index1, DataIndex)
        assert isinstance(data_index2, DataIndex)
        assert data_index1.name == data_index2.name
        assert data_index1.type == data_index2.type
        assert data_index1.path == data_index2.path

        assert isinstance(data_index1.source, IndexSource)
        assert isinstance(data_index2.source, IndexSource)
        assert data_index1.source.input_data.type == data_index2.source.input_data.type
        assert data_index1.source.input_data.path == data_index2.source.input_data.path
        assert data_index1.source.input_glob == data_index2.source.input_glob
        assert data_index1.source.chunk_size == data_index2.source.chunk_size
        assert data_index1.source.chunk_overlap == data_index2.source.chunk_overlap
        assert data_index1.source.citation_url == data_index2.source.citation_url
        assert (
            data_index1.source.citation_url_replacement_regex.match_pattern
            == data_index2.source.citation_url_replacement_regex.match_pattern
        )
        assert (
            data_index1.source.citation_url_replacement_regex.replacement_pattern
            == data_index2.source.citation_url_replacement_regex.replacement_pattern
        )

        assert isinstance(data_index1.embedding, Embedding)
        assert isinstance(data_index2.embedding, Embedding)
        assert data_index1.embedding.model == data_index2.embedding.model
        assert data_index1.embedding.connection == data_index2.embedding.connection
        assert data_index1.embedding.cache_path == data_index2.embedding.cache_path

        assert isinstance(data_index1.index, IndexStore)
        assert isinstance(data_index2.index, IndexStore)
        assert data_index1.index.type == data_index2.index.type
        assert data_index1.index.connection == data_index2.index.connection
        assert data_index1.index.name == data_index2.index.name

    def test_data_index_uri_to_acs_aoai_pipeline(self):
        from azure.ai.ml import MLClient
        from azure.identity import DefaultAzureCredential

        data_index = load_data(source=str(unittests_folder / "../../test_configs/data_index/data_index_aoai_acs.yaml"))
        index_job = index_data(
            data_index=DataIndex(
                source=IndexSource(
                    input_data=Data(
                        type="uri_folder",
                        path=str(unittests_folder / "../test_data")
                        # path = "https://github.com/MicrosoftDocs/azure-docs.git"
                    ),
                    # input_glob = "articles/machine-learning/**/*",
                    chunk_size=1024,
                    chunk_overlap=0,
                    citation_url="https://learn.microsoft.com/en-us/azure",
                    citation_url_replacement_regex=CitationRegex(
                        match_pattern="(.*)/articles/(.*)(\\.[^.]+)$", replacement_pattern="\\1/\\2"
                    ),
                ),
                embedding=Embedding(
                    model="azure_open_ai://deployment/text-embedding-ada-002/model/text-embedding-ada-002",
                    connection="azureml:azureml-rag-aoai-v2",
                    cache_path="azureml://datastores/workspaceblobstore/paths/embeddings_cache/azure_docs_ml_aoai",
                ),
                index=IndexStore(
                    type="acs",
                    connection="azureml:azureml-rag-acs-v2",
                    name="azure_docs_ml_aoai",
                ),
                name="azure_docs_ml_aoai",
                path="azureml://datastores/workspaceblobstore/paths/{name}",
            ),
            ml_client=MLClient.from_config(
                credential=DefaultAzureCredential(), path=str(unittests_folder / "../workspace.json")
            ),
        )

        assert isinstance(data_index, DataIndex)
        print(f'{vars(index_job.outputs["mlindex_asset_uri"])}')
        assert data_index.path == index_job.outputs["mlindex_asset_uri"].path
        assert data_index.name == index_job.outputs["mlindex_asset_uri"].name
