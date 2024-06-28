# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
from typing import Dict, Optional, Union

import yaml  # type: ignore[import]
from packaging import version

from azure.ai.resources._utils._open_ai_utils import build_open_ai_protocol
from azure.ai.resources.entities.mlindex import Index
from azure.ai.resources.operations._acs_output_config import ACSOutputConfig
from azure.ai.resources.operations._index_data_source import ACSSource, LocalSource


def build_index(  # pylint: disable=too-many-locals, too-many-statements
    *,
    output_index_name: str,
    vector_store: str,
    index_input_config: Union[ACSSource, LocalSource],
    acs_config: ACSOutputConfig,  # todo better name?
    embeddings_model: str,
    aoai_connection_id: Optional[str] = None,
    data_source_url: Optional[str] = None,
    chunk_size: int = 1024,
    chunk_overlap: int = 0,
    input_glob: str = "**/*",
    max_sample_files: Optional[int] = None,
    chunk_prepend_summary: Optional[bool] = None,
    document_path_replacement_regex: Optional[Dict[str, str]] = None,
    embeddings_cache_path: Optional[str] = None,
) -> Index:
    """
    Generates embeddings locally and stores Index reference in memory

    :keyword output_index_name: The name of the output index.
    :paramtype output_index_name: str
    :keyword vector_store: The vector store to be indexed.
    :paramtype vector_store: str
    :keyword index_input_config: The configuration for input data source.
    :paramtype index_input_config: Union[ACSSource, LocalSource]
    :keyword acs_config: The configuration for Azure Cognitive Search output.
    :paramtype acs_config: ACSOutputConfig
    :keyword embeddings_model: The embeddings model to use.
    :paramtype embeddings_model: str
    :keyword aoai_connection_id: The ID of AOAI connection.
    :paramtype aoai_connection_id: Optional[str]
    :keyword data_source_url: The URL of the data source.
    :paramtype data_source_url: Optional[str]
    :keyword chunk_size: The size of each chunk.
    :paramtype chunk_size: int
    :keyword chunk_overlap: The overlap between chunks.
    :paramtype chunk_overlap: int
    :keyword input_glob: The input glob pattern.
    :paramtype input_glob: str
    :keyword max_sample_files: The maximum number of sample files.
    :paramtype max_sample_files: Optional[int]
    :keyword chunk_prepend_summary: Whether to prepend summary to each chunk.
    :paramtype chunk_prepend_summary: Optional[bool]
    :keyword document_path_replacement_regex: The regex for document path replacement.
    :paramtype document_path_replacement_regex: Optional[Dict[str, str]]
    :keyword embeddings_cache_path: The path to embeddings cache.
    :paramtype embeddings_cache_path: Optional[str]
    :return: The built index.
    :rtype: Index
    """
    try:
        from azure.ai.generative.index._documents import DocumentChunksIterator, split_documents
        from azure.ai.generative.index._embeddings import EmbeddingsContainer
        from azure.ai.generative.index._tasks.update_acs import create_index_from_raw_embeddings
        from azure.ai.generative.index._utils.logging import disable_mlflow
        from azure.ai.resources._index._utils.connections import get_connection_by_id_v2
    except ImportError as e:
        print(
            "In order to use build_index to build an Index locally, you must have azure-ai-generative[index] installed"
        )
        raise e

    disable_mlflow()
    embeddings_model = build_open_ai_protocol(embeddings_model)

    if vector_store == "azure_cognitive_search" and isinstance(index_input_config, ACSSource):
        return _create_mlindex_from_existing_acs(
            output_index_name=output_index_name,
            # TODO: Fix Bug 2818331
            embedding_model=embeddings_model,  # type: ignore[no-redef,arg-type]
            aoai_connection=aoai_connection_id,
            acs_config=index_input_config,
        )
    embeddings_cache_path = str(Path(embeddings_cache_path) if embeddings_cache_path else Path.cwd())
    save_path = str(Path(embeddings_cache_path) / f"{output_index_name}-mlindex")
    splitter_args = {"chunk_size": chunk_size, "chunk_overlap": chunk_overlap, "use_rcts": True}
    if max_sample_files is not None:
        splitter_args["max_sample_files"] = max_sample_files
    if chunk_prepend_summary is not None:
        splitter_args["chunk_preprend_summary"] = chunk_prepend_summary

    chunked_docs = DocumentChunksIterator(
        files_source=index_input_config.input_data.path,
        glob=input_glob,
        base_url=data_source_url,
        document_path_replacement_regex=document_path_replacement_regex,
        chunked_document_processors=[
            lambda docs: split_documents(
                docs,
                splitter_args=splitter_args,
            )
        ],
    )

    connection_args = {}
    if "open_ai" in embeddings_model:
        import os

        if aoai_connection_id:
            aoai_connection = get_connection_by_id_v2(aoai_connection_id)
            connection_args = {
                "connection_type": "workspace_connection",
                "connection": {"id": aoai_connection_id},
                "endpoint": aoai_connection["properties"]["target"],
            }
        else:
            import openai

            api_key = "OPENAI_API_KEY"
            api_base = "OPENAI_API_BASE"
            if version.parse(openai.version.VERSION) >= version.parse("1.0.0"):
                api_key = "AZURE_OPENAI_KEY"
                api_base = "AZURE_OPENAI_ENDPOINT"
            connection_args = {
                "connection_type": "environment",
                "connection": {"key": api_key},
                "endpoint": os.getenv(api_base),
            }
    embedder = EmbeddingsContainer.from_uri(
        uri=embeddings_model,
        **connection_args,
    )

    embeddings = embedder.embed(chunked_docs)

    if vector_store.lower() == "faiss":
        embeddings.write_as_faiss_mlindex(save_path)
        mlindex_properties = {
            "azureml.mlIndexAssetKind": "faiss",
            "azureml.mlIndexAsset": "true",
            "azureml.mlIndexAssetSource": "AzureML Data",
            "azureml.mlIndexAssetPipelineRunId": "Local",
        }
    if vector_store.lower() == "azure_cognitive_search":
        acs_args = {
            "index_name": acs_config.acs_index_name,
        }
        if not acs_config.acs_connection_id:
            import os

            acs_args = {
                **acs_args,
                **{
                    "endpoint": os.getenv("AZURE_AI_SEARCH_ENDPOINT")
                    if "AZURE_AI_SEARCH_ENDPOINT" in os.environ
                    else os.getenv("AZURE_COGNITIVE_SEARCH_TARGET"),
                    "api_version": "2023-07-01-preview",
                },
            }
            connection_args = {"connection_type": "environment", "connection": {"key": "AZURE_AI_SEARCH_KEY"}}
        else:
            acs_connection = get_connection_by_id_v2(acs_config.acs_connection_id)
            acs_args = {
                **acs_args,
                **{
                    "endpoint": acs_connection["properties"]["target"],
                    "api_version": acs_connection["properties"]
                    .get("metadata", {})
                    .get("apiVersion", "2023-07-01-preview"),
                },
            }
            connection_args = {
                "connection_type": "workspace_connection",
                "connection": {"id": acs_config.acs_connection_id},
            }

        create_index_from_raw_embeddings(
            emb=embedder,
            acs_config=acs_args,
            connection=connection_args,
            output_path=save_path,
        )
        mlindex_properties = {
            "azureml.mlIndexAssetKind": "acs",
            "azureml.mlIndexAsset": "true",
            "azureml.mlIndexAssetSource": "AzureML Data",
            "azureml.mlIndexAssetPipelineRunId": "Local",
        }

    return Index(
        name=output_index_name,
        path=save_path,
        properties=mlindex_properties,
    )


def _create_mlindex_from_existing_acs(
    output_index_name: str,
    embedding_model: str,
    aoai_connection: Optional[str],
    acs_config: ACSSource,
) -> Index:
    try:
        from azure.ai.generative.index._embeddings import EmbeddingsContainer
        from azure.ai.resources._index._utils.connections import get_connection_by_id_v2
    except ImportError as e:
        print(
            "In order to use build_index to build an Index locally, you must have azure-ai-generative[index] installed"
        )
        raise e
    mlindex_config = {}
    connection_info = {}
    if not acs_config.acs_connection_id:
        import os

        connection_info = {
            "endpoint": os.getenv("AZURE_AI_SEARCH_ENDPOINT")
            if "AZURE_AI_SEARCH_ENDPOINT" in os.environ
            else os.getenv("AZURE_COGNITIVE_SEARCH_TARGET"),
            "connection_type": "environment",
            "connection": {"key": "AZURE_AI_SEARCH_KEY"},
        }
    else:
        acs_connection = get_connection_by_id_v2(acs_config.acs_connection_id)
        connection_info = {
            "endpoint": acs_connection["properties"]["target"],
            "connection_type": "workspace_connection",
            "connection": {
                "id": acs_config.acs_connection_id,
            },
        }
    mlindex_config["index"] = {
        "kind": "acs",
        "engine": "azure-sdk",
        "index": acs_config.acs_index_name,
        "api_version": "2023-07-01-preview",
        "field_mapping": {
            "content": acs_config.acs_content_key,
            "embedding": acs_config.acs_embedding_key,
        },
        **connection_info,
    }

    if acs_config.acs_title_key:
        mlindex_config["index"]["field_mapping"]["title"] = acs_config.acs_title_key
    if acs_config.acs_metadata_key:
        mlindex_config["index"]["field_mapping"]["metadata"] = acs_config.acs_metadata_key

    model_connection_args: Dict[str, Optional[Union[str, Dict]]]
    if not aoai_connection:
        import openai

        model_connection_args = {
            "key": openai.api_key,
        }
    else:
        model_connection_args = {"connection_type": "workspace_connection", "connection": {"id": aoai_connection}}

    embedding = EmbeddingsContainer.from_uri(embedding_model, credential=None, **model_connection_args)
    mlindex_config["embeddings"] = embedding.get_metadata()

    path = Path.cwd() / f"import-acs-{acs_config.acs_index_name}-mlindex"

    path.mkdir(exist_ok=True)
    with open(path / "MLIndex", "w", encoding="utf-8") as f:
        yaml.dump(mlindex_config, f)

    return Index(
        name=output_index_name,
        path=path,
        properties={
            "azureml.mlIndexAssetKind": "acs",
            "azureml.mlIndexAsset": "true",
            "azureml.mlIndexAssetPipelineRunId": "Local",
        },
    )
