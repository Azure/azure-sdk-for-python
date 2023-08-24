import logging
from pathlib import Path

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient, load_data
from azure.ai.ml.data_index import index_data
from azure.ai.ml.entities import CitationRegex, Data, DataIndex, Embedding, IndexSource, IndexStore, PipelineJob

# Stops noisy warning logs from urllib3 before test-proxy starts serving
connectionpool_logger = logging.getLogger("urllib3.connectionpool")
connectionpool_logger.setLevel(logging.CRITICAL)

e2etests_folder = Path(__file__).parent


@pytest.mark.timeout(600)
@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test", "mock_code_hash", "mock_set_headers_with_user_aml_token")
@pytest.mark.data_index_test
class TestDataIndex(AzureRecordedTestCase):
    # Please set ML_TENANT_ID in your environment variables when recording this test.
    # It will to help sanitize RequestBody.Studio.endpoint for job creation request.
    def test_data_index(self, client: MLClient) -> None:
        data_index = DataIndex(
            name="azure_docs_ml_aoai",
            type="uri_folder",
            path="azureml://datastores/workspaceblobstore/paths/{name}",
            source=IndexSource(
                input_data=Data(
                    type="uri_folder",
                    path=str(e2etests_folder.parent / "test_data")
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
        pipeline_job: PipelineJob = client.data.index_data(data_index)

        key = "data_index_" + data_index.name
        assert key in pipeline_job.jobs

        job = pipeline_job.jobs[key]
        assert isinstance(data_index, DataIndex)
        assert data_index.name == job.outputs["mlindex_asset_uri"].name
        assert data_index.path == job.outputs["mlindex_asset_uri"].path

    def test_data_index_uri_to_acs_aoai_pipeline(self, client: MLClient) -> None:
        data_index = load_data(source=str(e2etests_folder / "../../test_configs/data_index/data_index_aoai_acs.yaml"))
        index_job = index_data(
            data_index=DataIndex(
                source=IndexSource(
                    input_data=Data(
                        type="uri_folder",
                        path=str(e2etests_folder.parent / "test_data")
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
                    cache_path="azureml://datastores/workspaceblobstore/paths/embeddings_cache/docs_ml_aoai",
                ),
                index=IndexStore(
                    type="acs",
                    connection="azureml:azureml-rag-acs-v2",
                    name="docs_ml_aoai",
                ),
                name="docs_ml_aoai",
                path="azureml://datastores/workspaceblobstore/paths/{name}",
            ),
            ml_client=client,
        )

        assert isinstance(data_index, DataIndex)
        assert data_index.path == index_job.outputs["mlindex_asset_uri"].path
        assert data_index.name == index_job.outputs["mlindex_asset_uri"].name
