import logging
import pytest

from azure.ai.ml import load_data
from azure.ai.resources._index._dataindex.entities import CitationRegex, Data, DataIndex, Embedding, IndexSource, IndexStore

logger = logging.getLogger(__name__)


def test_dataindex_config_load(test_data_dir):
    data_index1 = load_data(source=test_data_dir / "dataindex" / "local_docs_to_acs_mlindex.yaml")
    data_index2 = DataIndex(
        name="mlindex_docs_aoai_acs",
        type="uri_folder",
        path="azureml://datastores/workspaceblobstore/paths/indexes/mlindex_docs_aoai_acs/{name}",
        source=IndexSource(
            input_data=Data(
                type="uri_folder",
                path=str(test_data_dir / "dataindex" / "documents")
            ),
            chunk_size=200,
            citation_url="https://github.com/Azure/azureml-examples/tree/main/sdk/python/generative-ai/rag/refresh",
            citation_url_replacement_regex=CitationRegex(
                match_pattern="(.*)/articles/(.*)(\\.[^.]+)$", replacement_pattern="\\1/\\2"
            ),
        ),
        embedding=Embedding(
            model="azure_open_ai://deployment/text-embedding-ada-002/model/text-embedding-ada-002",
            connection="azureml-rag-oai",
            cache_path="azureml://datastores/workspaceblobstore/paths/embeddings_cache/mlindex_docs_aoai_acs",
        ),
        index=IndexStore(
            type="acs",
            connection="azureml:azureml-rag-acs",
            name="mlindex_docs_aoai",
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