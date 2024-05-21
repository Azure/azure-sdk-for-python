# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access
# pylint: disable=no-member
# pylint: disable=unused-argument

import json
import re
from typing import Any, Dict, Optional, Union

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import AssetTypes, LegacyAssetTypes
from azure.ai.ml.entities import PipelineJob
from azure.ai.ml.entities._builders.base_node import pipeline_node_decorator
from azure.ai.ml.entities._credentials import ManagedIdentityConfiguration, UserIdentityConfiguration
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.pipeline._io import PipelineInput
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException
from azure.ai.ml.constants._common import DataIndexTypes
from azure.ai.ml.constants._component import LLMRAGComponentUri
from azure.ai.ml.entities._indexes.entities.data_index import DataIndex

SUPPORTED_INPUTS = [
    LegacyAssetTypes.PATH,
    AssetTypes.URI_FILE,
    AssetTypes.URI_FOLDER,
    AssetTypes.MLTABLE,
]


def _build_data_index(io_dict: Union[Dict, DataIndex]):
    if io_dict is None:
        return io_dict
    if isinstance(io_dict, DataIndex):
        component_io = io_dict
    else:
        if isinstance(io_dict, dict):
            component_io = DataIndex(**io_dict)
        else:
            msg = "data_index only support dict and DataIndex"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.DATA,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

    return component_io


@experimental
@pipeline_node_decorator
def index_data(
    *,
    data_index: DataIndex,
    description: Optional[str] = None,
    tags: Optional[Dict] = None,
    name: Optional[str] = None,
    display_name: Optional[str] = None,
    experiment_name: Optional[str] = None,
    compute: Optional[str] = None,
    serverless_instance_type: Optional[str] = None,
    ml_client: Optional[Any] = None,
    identity: Optional[Union[ManagedIdentityConfiguration, UserIdentityConfiguration]] = None,
    input_data_override: Optional[Input] = None,
    **kwargs,
) -> PipelineJob:
    """
    Create a PipelineJob object which can be used inside dsl.pipeline.

    :keywork data_index: The data index configuration.
    :type data_index: DataIndex
    :keyword description: Description of the job.
    :type description: str
    :keyword tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :keyword display_name: Display name of the job.
    :type display_name: str
    :keyword experiment_name: Name of the experiment the job will be created under.
    :type experiment_name: str
    :keyword compute: The compute resource the job runs on.
    :type compute: str
    :keyword serverless_instance_type: The instance type to use for serverless compute.
    :type serverless_instance_type: Optional[str]
    :keyword ml_client: The ml client to use for the job.
    :type ml_client: Any
    :keyword identity: Identity configuration for the job.
    :type identity: Optional[Union[ManagedIdentityConfiguration, UserIdentityConfiguration]]
    :keyword input_data_override: Input data override for the job.
        Used to pipe output of step into DataIndex Job in a pipeline.
    :type input_data_override: Optional[Input]
    :return: A PipelineJob object.
    :rtype: ~azure.ai.ml.entities.PipelineJob.
    """
    data_index = _build_data_index(data_index)

    if data_index.index.type == DataIndexTypes.FAISS:
        configured_component = data_index_faiss(
            ml_client,
            data_index,
            description,
            tags,
            name,
            display_name,
            experiment_name,
            compute,
            serverless_instance_type,
            identity,
            input_data_override,
        )
    elif data_index.index.type in (DataIndexTypes.ACS, DataIndexTypes.PINECONE):
        if kwargs.get("incremental_update", False):
            configured_component = data_index_incremental_update_hosted(
                ml_client,
                data_index,
                description,
                tags,
                name,
                display_name,
                experiment_name,
                compute,
                serverless_instance_type,
                identity,
                input_data_override,
            )
        else:
            configured_component = data_index_hosted(
                ml_client,
                data_index,
                description,
                tags,
                name,
                display_name,
                experiment_name,
                compute,
                serverless_instance_type,
                identity,
                input_data_override,
            )
    else:
        raise ValueError(f"Unsupported index type: {data_index.index.type}")

    configured_component.properties["azureml.mlIndexAssetName"] = data_index.name
    configured_component.properties["azureml.mlIndexAssetKind"] = data_index.index.type
    configured_component.properties["azureml.mlIndexAssetSource"] = "Data Asset"

    return configured_component


# pylint: disable=too-many-statements
def data_index_incremental_update_hosted(
    ml_client: Any,
    data_index: DataIndex,
    description: Optional[str] = None,
    tags: Optional[Dict] = None,
    name: Optional[str] = None,
    display_name: Optional[str] = None,
    experiment_name: Optional[str] = None,
    compute: Optional[str] = None,
    serverless_instance_type: Optional[str] = None,
    identity: Optional[Union[ManagedIdentityConfiguration, UserIdentityConfiguration]] = None,
    input_data_override: Optional[Input] = None,
):
    from azure.ai.ml.entities._indexes.utils import build_model_protocol, pipeline

    crack_and_chunk_and_embed_component = get_component_obj(
        ml_client, LLMRAGComponentUri.LLM_RAG_CRACK_AND_CHUNK_AND_EMBED
    )

    if data_index.index.type == DataIndexTypes.ACS:
        update_index_component = get_component_obj(ml_client, LLMRAGComponentUri.LLM_RAG_UPDATE_ACS_INDEX)
    elif data_index.index.type == DataIndexTypes.PINECONE:
        update_index_component = get_component_obj(ml_client, LLMRAGComponentUri.LLM_RAG_UPDATE_PINECONE_INDEX)
    else:
        raise ValueError(f"Unsupported hosted index type: {data_index.index.type}")

    register_mlindex_asset_component = get_component_obj(ml_client, LLMRAGComponentUri.LLM_RAG_REGISTER_MLINDEX_ASSET)

    @pipeline(  # type: ignore [call-overload]
        name=name if name else f"data_index_incremental_update_{data_index.index.type}",
        description=description,
        tags=tags,
        display_name=(
            display_name if display_name else f"LLM - Data to {data_index.index.type.upper()} (Incremental Update)"
        ),
        experiment_name=experiment_name,
        compute=compute,
        get_component=True,
    )
    def data_index_pipeline(
        input_data: Input,
        embeddings_model: str,
        index_config: str,
        index_connection_id: str,
        chunk_size: int = 768,
        chunk_overlap: int = 0,
        input_glob: str = "**/*",
        citation_url: Optional[str] = None,
        citation_replacement_regex: Optional[str] = None,
        aoai_connection_id: Optional[str] = None,
        embeddings_container: Optional[Input] = None,
    ):
        """
        Generate embeddings for a `input_data` source and
        push them into a hosted index (such as Azure Cognitive Search and Pinecone).

        :param input_data: The input data to be indexed.
        :type input_data: Input
        :param embeddings_model: The embedding model to use when processing source data chunks.
        :type embeddings_model: str
        :param index_config: The configuration for the hosted index.
        :type index_config: str
        :param index_connection_id: The connection ID for the hosted index.
        :type index_connection_id: str
        :param chunk_size: The size of the chunks to break the input data into.
        :type chunk_size: int
        :param chunk_overlap: The number of tokens to overlap between chunks.
        :type chunk_overlap: int
        :param input_glob: The glob pattern to use when searching for input data.
        :type input_glob: str
        :param citation_url: The URL to use when generating citations for the input data.
        :type citation_url: str
        :param citation_replacement_regex: The regex to use when generating citations for the input data.
        :type citation_replacement_regex: str
        :param aoai_connection_id: The connection ID for the Azure Open AI service.
        :type aoai_connection_id: str
        :param embeddings_container: The container to use when caching embeddings.
        :type embeddings_container: Input
        :return: The URI of the generated Azure Cognitive Search index.
        :rtype: str.
        """
        crack_and_chunk_and_embed = crack_and_chunk_and_embed_component(
            input_data=input_data,
            input_glob=input_glob,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            citation_url=citation_url,
            citation_replacement_regex=citation_replacement_regex,
            embeddings_container=embeddings_container,
            embeddings_model=embeddings_model,
            embeddings_connection_id=aoai_connection_id,
        )
        if compute is None or compute == "serverless":
            use_automatic_compute(crack_and_chunk_and_embed, instance_type=serverless_instance_type)
        if optional_pipeline_input_provided(embeddings_container):  # type: ignore [arg-type]
            crack_and_chunk_and_embed.outputs.embeddings = Output(
                type="uri_folder", path=f"{embeddings_container.path}/{{name}}"  # type: ignore [union-attr]
            )
        if identity:
            crack_and_chunk_and_embed.identity = identity

        if data_index.index.type == DataIndexTypes.ACS:
            update_index = update_index_component(
                embeddings=crack_and_chunk_and_embed.outputs.embeddings, acs_config=index_config
            )
            update_index.environment_variables["AZUREML_WORKSPACE_CONNECTION_ID_ACS"] = index_connection_id
        elif data_index.index.type == DataIndexTypes.PINECONE:
            update_index = update_index_component(
                embeddings=crack_and_chunk_and_embed.outputs.embeddings, pinecone_config=index_config
            )
            update_index.environment_variables["AZUREML_WORKSPACE_CONNECTION_ID_PINECONE"] = index_connection_id
        else:
            raise ValueError(f"Unsupported hosted index type: {data_index.index.type}")
        if compute is None or compute == "serverless":
            use_automatic_compute(update_index, instance_type=serverless_instance_type)
        if identity:
            update_index.identity = identity

        register_mlindex_asset = register_mlindex_asset_component(
            storage_uri=update_index.outputs.index,
            asset_name=data_index.name,
        )
        if compute is None or compute == "serverless":
            use_automatic_compute(register_mlindex_asset, instance_type=serverless_instance_type)
        if identity:
            register_mlindex_asset.identity = identity
        return {
            "mlindex_asset_uri": update_index.outputs.index,
            "mlindex_asset_id": register_mlindex_asset.outputs.asset_id,
        }

    if input_data_override is not None:
        input_data = input_data_override
    else:
        input_data = Input(
            type=data_index.source.input_data.type, path=data_index.source.input_data.path  # type: ignore [arg-type]
        )

    index_config = {
        "index_name": data_index.index.name if data_index.index.name is not None else data_index.name,
        "full_sync": True,
    }
    if data_index.index.config is not None:
        index_config.update(data_index.index.config)

    component = data_index_pipeline(
        input_data=input_data,
        input_glob=data_index.source.input_glob,  # type: ignore [arg-type]
        chunk_size=data_index.source.chunk_size,  # type: ignore [arg-type]
        chunk_overlap=data_index.source.chunk_overlap,  # type: ignore [arg-type]
        citation_url=data_index.source.citation_url,
        citation_replacement_regex=(
            json.dumps(data_index.source.citation_url_replacement_regex._to_dict())
            if data_index.source.citation_url_replacement_regex
            else None
        ),
        embeddings_model=build_model_protocol(data_index.embedding.model),
        aoai_connection_id=_resolve_connection_id(ml_client, data_index.embedding.connection),
        embeddings_container=(
            Input(type=AssetTypes.URI_FOLDER, path=data_index.embedding.cache_path)
            if data_index.embedding.cache_path
            else None
        ),
        index_config=json.dumps(index_config),
        index_connection_id=_resolve_connection_id(ml_client, data_index.index.connection),  # type: ignore [arg-type]
    )
    # Hack until full Component classes are implemented that can annotate the optional parameters properly
    component.inputs["input_glob"]._meta.optional = True
    component.inputs["chunk_size"]._meta.optional = True
    component.inputs["chunk_overlap"]._meta.optional = True
    component.inputs["citation_url"]._meta.optional = True
    component.inputs["citation_replacement_regex"]._meta.optional = True
    component.inputs["aoai_connection_id"]._meta.optional = True
    component.inputs["embeddings_container"]._meta.optional = True

    if data_index.path:
        component.outputs.mlindex_asset_uri = Output(  # type: ignore [attr-defined]
            type=AssetTypes.URI_FOLDER, path=data_index.path  # type: ignore [arg-type]
        )

    return component


def data_index_faiss(
    ml_client: Any,
    data_index: DataIndex,
    description: Optional[str] = None,
    tags: Optional[Dict] = None,
    name: Optional[str] = None,
    display_name: Optional[str] = None,
    experiment_name: Optional[str] = None,
    compute: Optional[str] = None,
    serverless_instance_type: Optional[str] = None,
    identity: Optional[Union[ManagedIdentityConfiguration, UserIdentityConfiguration]] = None,
    input_data_override: Optional[Input] = None,
):
    from azure.ai.ml.entities._indexes.utils import build_model_protocol, pipeline

    crack_and_chunk_component = get_component_obj(ml_client, LLMRAGComponentUri.LLM_RAG_CRACK_AND_CHUNK)
    generate_embeddings_component = get_component_obj(ml_client, LLMRAGComponentUri.LLM_RAG_GENERATE_EMBEDDINGS)
    create_faiss_index_component = get_component_obj(ml_client, LLMRAGComponentUri.LLM_RAG_CREATE_FAISS_INDEX)
    register_mlindex_asset_component = get_component_obj(ml_client, LLMRAGComponentUri.LLM_RAG_REGISTER_MLINDEX_ASSET)

    @pipeline(  # type: ignore [call-overload]
        name=name if name else "data_index_faiss",
        description=description,
        tags=tags,
        display_name=display_name if display_name else "LLM - Data to Faiss",
        experiment_name=experiment_name,
        compute=compute,
        get_component=True,
    )
    def data_index_faiss_pipeline(
        input_data: Input,
        embeddings_model: str,
        chunk_size: int = 1024,
        data_source_glob: str = None,  # type: ignore [assignment]
        data_source_url: str = None,  # type: ignore [assignment]
        document_path_replacement_regex: str = None,  # type: ignore [assignment]
        aoai_connection_id: str = None,  # type: ignore [assignment]
        embeddings_container: Input = None,  # type: ignore [assignment]
    ):
        """
        Generate embeddings for a `input_data` source and create a Faiss index from them.

        :param input_data: The input data to be indexed.
        :type input_data: Input
        :param embeddings_model: The embedding model to use when processing source data chunks.
        :type embeddings_model: str
        :param chunk_size: The size of the chunks to break the input data into.
        :type chunk_size: int
        :param data_source_glob: The glob pattern to use when searching for input data.
        :type data_source_glob: str
        :param data_source_url: The URL to use when generating citations for the input data.
        :type data_source_url: str
        :param document_path_replacement_regex: The regex to use when generating citations for the input data.
        :type document_path_replacement_regex: str
        :param aoai_connection_id: The connection ID for the Azure Open AI service.
        :type aoai_connection_id: str
        :param embeddings_container: The container to use when caching embeddings.
        :type embeddings_container: Input
        :return: The URI of the generated Faiss index.
        :rtype: str.
        """
        crack_and_chunk = crack_and_chunk_component(
            input_data=input_data,
            input_glob=data_source_glob,
            chunk_size=chunk_size,
            data_source_url=data_source_url,
            document_path_replacement_regex=document_path_replacement_regex,
        )
        if compute is None or compute == "serverless":
            use_automatic_compute(crack_and_chunk, instance_type=serverless_instance_type)
        if identity:
            crack_and_chunk.identity = identity

        generate_embeddings = generate_embeddings_component(
            chunks_source=crack_and_chunk.outputs.output_chunks,
            embeddings_container=embeddings_container,
            embeddings_model=embeddings_model,
        )
        if compute is None or compute == "serverless":
            use_automatic_compute(generate_embeddings, instance_type=serverless_instance_type)
        if optional_pipeline_input_provided(aoai_connection_id):  # type: ignore [arg-type]
            generate_embeddings.environment_variables["AZUREML_WORKSPACE_CONNECTION_ID_AOAI"] = aoai_connection_id
        if optional_pipeline_input_provided(embeddings_container):  # type: ignore [arg-type]
            generate_embeddings.outputs.embeddings = Output(
                type="uri_folder", path=f"{embeddings_container.path}/{{name}}"
            )
        if identity:
            generate_embeddings.identity = identity

        create_faiss_index = create_faiss_index_component(embeddings=generate_embeddings.outputs.embeddings)
        if compute is None or compute == "serverless":
            use_automatic_compute(create_faiss_index, instance_type=serverless_instance_type)
        if identity:
            create_faiss_index.identity = identity

        register_mlindex_asset = register_mlindex_asset_component(
            storage_uri=create_faiss_index.outputs.index,
            asset_name=data_index.name,
        )
        if compute is None or compute == "serverless":
            use_automatic_compute(register_mlindex_asset, instance_type=serverless_instance_type)
        if identity:
            register_mlindex_asset.identity = identity
        return {
            "mlindex_asset_uri": create_faiss_index.outputs.index,
            "mlindex_asset_id": register_mlindex_asset.outputs.asset_id,
        }

    if input_data_override is not None:
        input_data = input_data_override
    else:
        input_data = Input(
            type=data_index.source.input_data.type, path=data_index.source.input_data.path  # type: ignore [arg-type]
        )

    component = data_index_faiss_pipeline(
        input_data=input_data,
        embeddings_model=build_model_protocol(data_index.embedding.model),
        chunk_size=data_index.source.chunk_size,  # type: ignore [arg-type]
        data_source_glob=data_index.source.input_glob,  # type: ignore [arg-type]
        data_source_url=data_index.source.citation_url,  # type: ignore [arg-type]
        document_path_replacement_regex=(
            json.dumps(data_index.source.citation_url_replacement_regex._to_dict())  # type: ignore [arg-type]
            if data_index.source.citation_url_replacement_regex
            else None
        ),
        aoai_connection_id=_resolve_connection_id(
            ml_client, data_index.embedding.connection
        ),  # type: ignore [arg-type]
        embeddings_container=(
            Input(type=AssetTypes.URI_FOLDER, path=data_index.embedding.cache_path)  # type: ignore [arg-type]
            if data_index.embedding.cache_path
            else None
        ),
    )
    # Hack until full Component classes are implemented that can annotate the optional parameters properly
    component.inputs["data_source_glob"]._meta.optional = True
    component.inputs["data_source_url"]._meta.optional = True
    component.inputs["document_path_replacement_regex"]._meta.optional = True
    component.inputs["aoai_connection_id"]._meta.optional = True
    component.inputs["embeddings_container"]._meta.optional = True
    if data_index.path:
        component.outputs.mlindex_asset_uri = Output(
            type=AssetTypes.URI_FOLDER, path=data_index.path  # type: ignore [arg-type]
        )

    return component


# pylint: disable=too-many-statements
def data_index_hosted(
    ml_client: Any,
    data_index: DataIndex,
    description: Optional[str] = None,
    tags: Optional[Dict] = None,
    name: Optional[str] = None,
    display_name: Optional[str] = None,
    experiment_name: Optional[str] = None,
    compute: Optional[str] = None,
    serverless_instance_type: Optional[str] = None,
    identity: Optional[Union[ManagedIdentityConfiguration, UserIdentityConfiguration]] = None,
    input_data_override: Optional[Input] = None,
):
    from azure.ai.ml.entities._indexes.utils import build_model_protocol, pipeline

    crack_and_chunk_component = get_component_obj(ml_client, LLMRAGComponentUri.LLM_RAG_CRACK_AND_CHUNK)
    generate_embeddings_component = get_component_obj(ml_client, LLMRAGComponentUri.LLM_RAG_GENERATE_EMBEDDINGS)

    if data_index.index.type == DataIndexTypes.ACS:
        update_index_component = get_component_obj(ml_client, LLMRAGComponentUri.LLM_RAG_UPDATE_ACS_INDEX)
    elif data_index.index.type == DataIndexTypes.PINECONE:
        update_index_component = get_component_obj(ml_client, LLMRAGComponentUri.LLM_RAG_UPDATE_PINECONE_INDEX)
    else:
        raise ValueError(f"Unsupported hosted index type: {data_index.index.type}")

    register_mlindex_asset_component = get_component_obj(ml_client, LLMRAGComponentUri.LLM_RAG_REGISTER_MLINDEX_ASSET)

    @pipeline(  # type: ignore [call-overload]
        name=name if name else f"data_index_{data_index.index.type}",
        description=description,
        tags=tags,
        display_name=display_name if display_name else f"LLM - Data to {data_index.index.type.upper()}",
        experiment_name=experiment_name,
        compute=compute,
        get_component=True,
    )
    def data_index_pipeline(
        input_data: Input,
        embeddings_model: str,
        index_config: str,
        index_connection_id: str,
        chunk_size: int = 1024,
        data_source_glob: str = None,  # type: ignore [assignment]
        data_source_url: str = None,  # type: ignore [assignment]
        document_path_replacement_regex: str = None,  # type: ignore [assignment]
        aoai_connection_id: str = None,  # type: ignore [assignment]
        embeddings_container: Input = None,  # type: ignore [assignment]
    ):
        """
        Generate embeddings for a `input_data` source
        and push them into a hosted index (such as Azure Cognitive Search and Pinecone).

        :param input_data: The input data to be indexed.
        :type input_data: Input
        :param embeddings_model: The embedding model to use when processing source data chunks.
        :type embeddings_model: str
        :param index_config: The configuration for the hosted index.
        :type index_config: str
        :param index_connection_id: The connection ID for the hosted index.
        :type index_connection_id: str
        :param chunk_size: The size of the chunks to break the input data into.
        :type chunk_size: int
        :param data_source_glob: The glob pattern to use when searching for input data.
        :type data_source_glob: str
        :param data_source_url: The URL to use when generating citations for the input data.
        :type data_source_url: str
        :param document_path_replacement_regex: The regex to use when generating citations for the input data.
        :type document_path_replacement_regex: str
        :param aoai_connection_id: The connection ID for the Azure Open AI service.
        :type aoai_connection_id: str
        :param embeddings_container: The container to use when caching embeddings.
        :type embeddings_container: Input
        :return: The URI of the generated Azure Cognitive Search index.
        :rtype: str.
        """
        crack_and_chunk = crack_and_chunk_component(
            input_data=input_data,
            input_glob=data_source_glob,
            chunk_size=chunk_size,
            data_source_url=data_source_url,
            document_path_replacement_regex=document_path_replacement_regex,
        )
        if compute is None or compute == "serverless":
            use_automatic_compute(crack_and_chunk, instance_type=serverless_instance_type)
        if identity:
            crack_and_chunk.identity = identity

        generate_embeddings = generate_embeddings_component(
            chunks_source=crack_and_chunk.outputs.output_chunks,
            embeddings_container=embeddings_container,
            embeddings_model=embeddings_model,
        )
        if compute is None or compute == "serverless":
            use_automatic_compute(generate_embeddings, instance_type=serverless_instance_type)
        if optional_pipeline_input_provided(aoai_connection_id):  # type: ignore [arg-type]
            generate_embeddings.environment_variables["AZUREML_WORKSPACE_CONNECTION_ID_AOAI"] = aoai_connection_id
        if optional_pipeline_input_provided(embeddings_container):  # type: ignore [arg-type]
            generate_embeddings.outputs.embeddings = Output(
                type="uri_folder", path=f"{embeddings_container.path}/{{name}}"
            )
        if identity:
            generate_embeddings.identity = identity

        if data_index.index.type == DataIndexTypes.ACS:
            update_index = update_index_component(
                embeddings=generate_embeddings.outputs.embeddings, acs_config=index_config
            )
            update_index.environment_variables["AZUREML_WORKSPACE_CONNECTION_ID_ACS"] = index_connection_id
        elif data_index.index.type == DataIndexTypes.PINECONE:
            update_index = update_index_component(
                embeddings=generate_embeddings.outputs.embeddings, pinecone_config=index_config
            )
            update_index.environment_variables["AZUREML_WORKSPACE_CONNECTION_ID_PINECONE"] = index_connection_id
        else:
            raise ValueError(f"Unsupported hosted index type: {data_index.index.type}")
        if compute is None or compute == "serverless":
            use_automatic_compute(update_index, instance_type=serverless_instance_type)
        if identity:
            update_index.identity = identity

        register_mlindex_asset = register_mlindex_asset_component(
            storage_uri=update_index.outputs.index,
            asset_name=data_index.name,
        )
        if compute is None or compute == "serverless":
            use_automatic_compute(register_mlindex_asset, instance_type=serverless_instance_type)
        if identity:
            register_mlindex_asset.identity = identity
        return {
            "mlindex_asset_uri": update_index.outputs.index,
            "mlindex_asset_id": register_mlindex_asset.outputs.asset_id,
        }

    if input_data_override is not None:
        input_data = input_data_override
    else:
        input_data = Input(
            type=data_index.source.input_data.type, path=data_index.source.input_data.path  # type: ignore [arg-type]
        )

    index_config = {
        "index_name": data_index.index.name if data_index.index.name is not None else data_index.name,
    }
    if data_index.index.config is not None:
        index_config.update(data_index.index.config)

    component = data_index_pipeline(
        input_data=input_data,
        embeddings_model=build_model_protocol(data_index.embedding.model),
        index_config=json.dumps(index_config),
        index_connection_id=_resolve_connection_id(ml_client, data_index.index.connection),  # type: ignore [arg-type]
        chunk_size=data_index.source.chunk_size,  # type: ignore [arg-type]
        data_source_glob=data_index.source.input_glob,  # type: ignore [arg-type]
        data_source_url=data_index.source.citation_url,  # type: ignore [arg-type]
        document_path_replacement_regex=(
            json.dumps(data_index.source.citation_url_replacement_regex._to_dict())  # type: ignore [arg-type]
            if data_index.source.citation_url_replacement_regex
            else None
        ),
        aoai_connection_id=_resolve_connection_id(
            ml_client, data_index.embedding.connection  # type: ignore [arg-type]
        ),
        embeddings_container=(
            Input(type=AssetTypes.URI_FOLDER, path=data_index.embedding.cache_path)  # type: ignore [arg-type]
            if data_index.embedding.cache_path
            else None
        ),
    )
    # Hack until full Component classes are implemented that can annotate the optional parameters properly
    component.inputs["data_source_glob"]._meta.optional = True
    component.inputs["data_source_url"]._meta.optional = True
    component.inputs["document_path_replacement_regex"]._meta.optional = True
    component.inputs["aoai_connection_id"]._meta.optional = True
    component.inputs["embeddings_container"]._meta.optional = True

    if data_index.path:
        component.outputs.mlindex_asset_uri = Output(
            type=AssetTypes.URI_FOLDER, path=data_index.path  # type: ignore [arg-type]
        )

    return component


def optional_pipeline_input_provided(input: Optional[PipelineInput]):
    """
    Checks if optional pipeline inputs are provided.

    :param input: The pipeline input to check.
    :type input: Optional[PipelineInput]
    :return: True if the input is not None and has a value, False otherwise.
    :rtype: bool.
    """
    return input is not None and input._data is not None


def use_automatic_compute(component, instance_count=1, instance_type=None):
    """
    Configure input `component` to use automatic compute with `instance_count` and `instance_type`.

    This avoids the need to provision a compute cluster to run the component.
    :param component: The component to configure.
    :type component: Any
    :param instance_count: The number of instances to use.
    :type instance_count: int
    :param instance_type: The type of instance to use.
    :type instance_type: str
    :return: The configured component.
    :rtype: Any.
    """
    component.set_resources(
        instance_count=instance_count,
        instance_type=instance_type,
        properties={"compute_specification": {"automatic": True}},
    )
    return component


def get_component_obj(ml_client, component_uri):
    from azure.ai.ml import MLClient

    if not isinstance(component_uri, str):
        # Assume Component object
        return component_uri

    matches = re.match(
        r"azureml://registries/(?P<registry_name>.*)/components/(?P<component_name>.*)"
        r"/(?P<identifier_type>.*)/(?P<identifier_name>.*)",
        component_uri,
    )
    if matches is None:
        from azure.ai.ml import load_component

        # Assume local path to component
        return load_component(source=component_uri)

    registry_name = matches.group("registry_name")
    registry_client = MLClient(
        subscription_id=ml_client.subscription_id,
        resource_group_name=ml_client.resource_group_name,
        credential=ml_client._credential,
        registry_name=registry_name,
    )
    component_obj = registry_client.components.get(
        matches.group("component_name"),
        **{matches.group("identifier_type").rstrip("s"): matches.group("identifier_name")},
    )
    return component_obj


def _resolve_connection_id(ml_client, connection: Optional[str] = None) -> Optional[str]:
    if connection is None:
        return None

    if isinstance(connection, str):
        from azure.ai.ml._utils._arm_id_utils import AMLNamedArmId

        connection_name = AMLNamedArmId(connection).asset_name

        connection = ml_client.connections.get(connection_name)
        if connection is None:
            return None
    return connection.id  # type: ignore [attr-defined]
