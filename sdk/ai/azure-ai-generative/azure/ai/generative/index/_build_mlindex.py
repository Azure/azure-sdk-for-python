# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
from typing import Union

import yaml

from azure.ai.resources.entities.mlindex import Index
from azure.ai.resources.operations._index_data_source import ACSSource, LocalSource
from azure.ai.resources.operations._acs_output_config import ACSOutputConfig
from azure.ai.resources._utils._open_ai_utils import build_open_ai_protocol


def build_index(
    *,
    ######## required args ##########
    output_index_name: str,
    vector_store: str,
    ######## embedding model information ##########
    embeddings_model: str = None,
    aoai_connection_id: str = None,
    ######## chunking information ##########
    data_source_url: str = None,
    chunk_size: int = 1024,
    chunk_overlap: int = 0,
    input_glob: str = "**/*",
    max_sample_files: int = None,
    chunk_prepend_summary: bool = None,
    document_path_replacement_regex: str = None,
    embeddings_cache_path: str = None,
    ######## data source info ########
    index_input_config: Union[ACSSource, LocalSource] = None,
    acs_config: ACSOutputConfig = None,  # todo better name?
) -> Index:

    """Generates embeddings locally and stores Index reference in memory
    """
    try:
        from azure.ai.generative.index._documents import DocumentChunksIterator, split_documents
        from azure.ai.generative.index._embeddings import EmbeddingsContainer
        from azure.ai.generative.index._tasks.update_acs import create_index_from_raw_embeddings
        from azure.ai.generative.index._utils.connections import get_connection_by_id_v2
        from azure.ai.generative.index._utils.logging import disable_mlflow
    except ImportError as e:
        print("In order to use build_index to build an Index locally, you must have azure-ai-generative[index] installed")
        raise e

    disable_mlflow()
    embeddings_model = build_open_ai_protocol(embeddings_model)

    if vector_store == "azure_cognitive_search" and isinstance(index_input_config, ACSSource):
        return _create_mlindex_from_existing_acs(
            output_index_name=output_index_name,
            embedding_model=embeddings_model,
            aoai_connection=aoai_connection_id,
            acs_config=index_input_config,
        )
    embeddings_cache_path = Path(embeddings_cache_path) if embeddings_cache_path else Path.cwd()
    save_path = embeddings_cache_path/f"{output_index_name}-mlindex"
    splitter_args= {
        'chunk_size': chunk_size,
        'chunk_overlap': chunk_overlap,
    }
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
                "endpoint": aoai_connection["properties"]["target"]
            }
        else:
            connection_args = {
                "connection_type": "environment",
                "connection": {"key": "OPENAI_API_KEY"},
                "endpoint": os.getenv("OPENAI_API_BASE"),
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
                    "endpoint": os.getenv("AZURE_AI_SEARCH_ENDPOINT") if "AZURE_AI_SEARCH_ENDPOINT" in os.environ else os.getenv("AZURE_COGNITIVE_SEARCH_TARGET"),
                    "api_version": "2023-07-01-preview",
                }
            }
            connection_args = {
                "connection_type": "environment",
                "connection": {"key": "AZURE_AI_SEARCH_KEY"}
            }
        else:
            acs_connection = get_connection_by_id_v2(acs_config.acs_connection_id)
            acs_args = {
                **acs_args,
                **{
                    "endpoint": acs_connection["properties"]["target"],
                    "api_version": acs_connection['properties'].get('metadata', {}).get('apiVersion', "2023-07-01-preview")
                }
            }
            connection_args = {
                "connection_type": "workspace_connection",
                "connection": {"id": acs_config.acs_connection_id}
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
    aoai_connection: str,
    acs_config: ACSSource,
) -> Index:
    try:
        from azure.ai.generative.index._embeddings import EmbeddingsContainer
        from azure.ai.generative.index._utils.connections import get_connection_by_id_v2
    except ImportError as e:
        print("In order to use build_index to build an Index locally, you must have azure-ai-generative[index] installed")
        raise e
    mlindex_config = {}
    connection_info = {}
    if not acs_config.acs_connection_id:
        import os
        connection_info = {
            "endpoint": os.getenv("AZURE_AI_SEARCH_ENDPOINT") if "AZURE_AI_SEARCH_ENDPOINT" in os.environ else os.getenv("AZURE_COGNITIVE_SEARCH_TARGET"),
            "connection_type": "environment",
            "connection": {"key": "AZURE_AI_SEARCH_KEY"}
        }
    else:
        acs_connection = get_connection_by_id_v2(acs_config.acs_connection_id)
        connection_info = {
            "endpoint": acs_connection["properties"]["target"],
            "connection_type": "workspace_connection",
            "connection": {
                "id": acs_config.acs_connection_id,
            }
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
        **connection_info
    }

    if acs_config.acs_title_key:
        mlindex_config["index"]["field_mapping"]["title"] = acs_config.acs_title_key
    if acs_config.acs_metadata_key:
        mlindex_config["index"]["field_mapping"]["metadata"] = acs_config.acs_metadata_key

    if not aoai_connection:
        import openai
        model_connection_args = {
            "key": openai.api_key,
        }
    else:
        model_connection_args = {
            "connection_type": "workspace_connection",
            "connection": {"id": aoai_connection}
        }

    embedding = EmbeddingsContainer.from_uri(embedding_model, **model_connection_args)
    mlindex_config["embeddings"] = embedding.get_metadata()

    path = Path.cwd() / f"import-acs-{acs_config.acs_index_name}-mlindex"

    path.mkdir(exist_ok=True)
    with open(path / "MLIndex", "w") as f:
        yaml.dump(mlindex_config, f)

    return Index(
        name=output_index_name,
        path=path,
        properties={
            "azureml.mlIndexAssetKind": "acs",
            "azureml.mlIndexAsset": "true",
            "azureml.mlIndexAssetPipelineRunId": "Local",
        }
    )
