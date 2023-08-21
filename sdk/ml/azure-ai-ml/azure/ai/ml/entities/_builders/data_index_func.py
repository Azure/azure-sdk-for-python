# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access

import json
import re
from typing import Any, Callable, Dict, Optional, Tuple, Union

from azure.ai.ml._schema import DataIndexTypes
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import AssetTypes, LegacyAssetTypes
from azure.ai.ml.constants._component import ComponentSource, DataIndexComponentUri, LLMRAGComponentUri
from azure.ai.ml.data_index import build_model_protocol
from azure.ai.ml.entities import CitationRegex, Data, DataIndex, Embedding, IndexSource, IndexStore
from azure.ai.ml.entities._builders.base_node import pipeline_node_decorator
from azure.ai.ml.entities._component.datatransfer_component import DataTransferCopyComponent
from azure.ai.ml.entities._credentials import ManagedIdentityConfiguration, UserIdentityConfiguration
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.pipeline._component_translatable import ComponentTranslatableMixin
from azure.ai.ml.entities._job.pipeline._io import NodeOutput, PipelineInput
from azure.ai.ml.exceptions import ErrorTarget, ValidationErrorType, ValidationException

from .data_index import DataIngestionNode, _build_data_index

SUPPORTED_INPUTS = [
    LegacyAssetTypes.PATH,
    AssetTypes.URI_FILE,
    AssetTypes.URI_FOLDER,
    AssetTypes.MLTABLE,
]


def _parse_input(input_value):
    component_input, job_input = None, None
    if isinstance(input_value, Input):
        component_input = Input(**input_value._to_dict())
        input_type = input_value.type
        if input_type in SUPPORTED_INPUTS:
            job_input = Input(**input_value._to_dict())
    elif isinstance(input_value, dict):
        # if user provided dict, we try to parse it to Input.
        # for job input, only parse for path type
        input_type = input_value.get("type", None)
        if input_type in SUPPORTED_INPUTS:
            job_input = Input(**input_value)
        component_input = Input(**input_value)
    elif isinstance(input_value, str):
        # Input bindings
        component_input = ComponentTranslatableMixin._to_input_builder_function(input_value)
        job_input = input_value
    elif isinstance(input_value, (PipelineInput, NodeOutput)):
        # datatransfer node can accept PipelineInput/NodeOutput for export task.
        if input_value._data is None or isinstance(input_value._data, Output):
            data = Input(type=input_value.type, mode=input_value.mode)
        else:
            data = input_value._data
        component_input, _ = _parse_input(data)
        job_input = input_value
    else:
        msg = (
            f"Unsupported input type: {type(input_value)}, only Input, dict, str, PipelineInput and NodeOutput are "
            f"supported."
        )
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.JOB,
            error_type=ValidationErrorType.INVALID_VALUE,
        )
    return component_input, job_input


def _parse_output(output_value):
    component_output, job_output = None, None
    if isinstance(output_value, Output):
        component_output = Output(**output_value._to_dict())
        job_output = Output(**output_value._to_dict())
    elif not output_value:
        # output value can be None or empty dictionary
        # None output value will be packed into a JobOutput object with mode = ReadWriteMount & type = UriFolder
        component_output = ComponentTranslatableMixin._to_output(output_value)
        job_output = output_value
    elif isinstance(output_value, dict):  # When output value is a non-empty dictionary
        job_output = Output(**output_value)
        component_output = Output(**output_value)
    elif isinstance(output_value, str):  # When output is passed in from pipeline job yaml
        job_output = output_value
    else:
        msg = f"Unsupported output type: {type(output_value)}, only Output and dict are supported."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.JOB,
            error_type=ValidationErrorType.INVALID_VALUE,
        )
    return component_output, job_output


def _parse_inputs_outputs(io_dict: Dict, parse_func: Callable) -> Tuple[Dict, Dict]:
    component_io_dict, job_io_dict = {}, {}
    if io_dict:
        for key, val in io_dict.items():
            component_io, job_io = parse_func(val)
            component_io_dict[key] = component_io
            job_io_dict[key] = job_io
    return component_io_dict, job_io_dict


@experimental
@pipeline_node_decorator
def index_data(
    *,
    data_index: DataIndex,
    description: Optional[str] = None,
    tags: Optional[Dict] = None,
    display_name: Optional[str] = None,
    experiment_name: Optional[str] = None,
    compute: Optional[str] = None,
    serverless_instance_type: Optional[str] = None,
    ml_client: Optional[Any] = None,
    identity: Optional[Union[ManagedIdentityConfiguration, UserIdentityConfiguration]] = None,
    **kwargs,
) -> DataIngestionNode:
    """Create a DataTransferImport object which can be used inside dsl.pipeline.

    # :keyword name: The name of the index asset.
    # :type name: str
    # :param source: The source data to be indexed.
    # :type source: IndexSource
    # :param embedding: The embedding model to use when processing source data chunks.
    # :type embedding: Embedding
    # :param index: The destination index to write processed data to.
    # :type index: IndexStore
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
    :return: A DataTransferImport object.
    :rtype: ~azure.ai.ml.entities._job.pipeline._component_translatable.DataTransferImport
    """
    data_index = _build_data_index(data_index)

    # TODO: Handle Faiss
    configured_component = data_index_acs(ml_client, data_index, compute, serverless_instance_type, identity)

    return configured_component


def data_index_acs(
    ml_client: Any,
    data_index: DataIndex,
    compute: Optional[str] = None,
    serverless_instance_type: str = "Standard_E8s_v3",
    identity: Optional[Union[ManagedIdentityConfiguration, UserIdentityConfiguration]] = None,
):
    from azure.ai.ml.dsl import pipeline

    # validate_deployments_component = get_component_obj(ml_client, LLMRAGComponentUri.LLM_RAG_VALIDATE_DEPLOYMENTS)
    crack_and_chunk_component = get_component_obj(ml_client, LLMRAGComponentUri.LLM_RAG_CRACK_AND_CHUNK)
    generate_embeddings_component = get_component_obj(ml_client, LLMRAGComponentUri.LLM_RAG_GENERATE_EMBEDDINGS)
    update_acs_index_component = get_component_obj(ml_client, LLMRAGComponentUri.LLM_RAG_UPDATE_ACS_INDEX)
    register_mlindex_asset_component = get_component_obj(ml_client, LLMRAGComponentUri.LLM_RAG_REGISTER_MLINDEX_ASSET)

    @pipeline(get_component=True)
    def data_index_acs(
        input_data: Input,
        embeddings_model: str,
        acs_config: str,
        acs_connection_id: str,
        chunk_size: int = 1024,
        data_source_glob: str = None,
        data_source_url: str = None,
        document_path_replacement_regex: str = None,
        aoai_connection_id: str = None,
        embeddings_container: Input = None,
    ):
        """Pipeline to generate embeddings for a `input_data` source and push them into an Azure Cognitive Search index."""
        crack_and_chunk = crack_and_chunk_component(
            input_data=input_data,
            input_glob=data_source_glob,
            chunk_size=chunk_size,
            data_source_url=data_source_url,
            document_path_replacement_regex=document_path_replacement_regex,
        )
        use_automatic_compute(crack_and_chunk, instance_type=serverless_instance_type)
        if identity:
            print(f"identity: {identity}")
            crack_and_chunk.identity = identity

        generate_embeddings = generate_embeddings_component(
            chunks_source=crack_and_chunk.outputs.output_chunks,
            embeddings_container=embeddings_container,
            embeddings_model=embeddings_model,
        )
        use_automatic_compute(generate_embeddings, instance_type=serverless_instance_type)
        if optional_pipeline_input_provided(aoai_connection_id):
            generate_embeddings.environment_variables["AZUREML_WORKSPACE_CONNECTION_ID_AOAI"] = aoai_connection_id
        if optional_pipeline_input_provided(embeddings_container):
            generate_embeddings.outputs.embeddings = Output(
                type="uri_folder", path=f"{embeddings_container.path}/{{name}}"
            )
        if identity:
            generate_embeddings.identity = identity

        update_acs_index = update_acs_index_component(
            embeddings=generate_embeddings.outputs.embeddings, acs_config=acs_config
        )
        use_automatic_compute(update_acs_index, instance_type=serverless_instance_type)
        update_acs_index.environment_variables["AZUREML_WORKSPACE_CONNECTION_ID_ACS"] = acs_connection_id

        if identity:
            update_acs_index.identity = identity

        register_mlindex_asset = register_mlindex_asset_component(
            storage_uri=update_acs_index.outputs.index,
            asset_name=data_index.name,
        )
        use_automatic_compute(register_mlindex_asset, instance_type=serverless_instance_type)
        if identity:
            register_mlindex_asset.identity = identity
        return {
            "mlindex_asset_uri": update_acs_index.outputs.index,
            "mlindex_asset_id": register_mlindex_asset.outputs.asset_id,
        }

    component = data_index_acs(
        input_data=Input(type=data_index.source.input_data.type, path=data_index.source.input_data.path),
        embeddings_model=build_model_protocol(data_index.embedding.model),
        acs_config=json.dumps(
            {"index_name": data_index.index.name if data_index.index.name is not None else data_index.name}
        ),
        acs_connection_id=resolve_connection_id(ml_client, data_index.index.connection),
        chunk_size=data_index.source.chunk_size,
        data_source_glob=data_index.source.input_glob,
        data_source_url=data_index.source.citation_url,
        document_path_replacement_regex=json.dumps(data_index.source.citation_url_replacement_regex._to_dict())
        if data_index.source.citation_url_replacement_regex
        else None,
        aoai_connection_id=resolve_connection_id(ml_client, data_index.embedding.connection),
        embeddings_container=Input(type=AssetTypes.URI_FOLDER, path=data_index.embedding.cache_path),
    )
    if data_index.path:
        component.outputs.mlindex_asset_uri = Output(type=AssetTypes.URI_FOLDER, path=data_index.path)

    component.outputs.mlindex_asset_uri.name = data_index.name
    return component


def optional_pipeline_input_provided(input: Optional[PipelineInput]):
    """Checks if optional pipeline inputs are provided."""
    return input is not None and input._data is not None


def use_automatic_compute(component, instance_count=1, instance_type="Standard_E8s_v3"):
    """Configure input `component` to use automatic compute with `instance_count` and `instance_type`.

    This avoids the need to provision a compute cluster to run the component.
    """
    component.set_resources(
        instance_count=instance_count,
        instance_type=instance_type,
        properties={"compute_specification": {"automatic": True}},
    )
    return component


def get_component_obj(ml_client, component_uri):
    from azure.ai.ml import MLClient

    matches = re.match(
        r"azureml://registries/(?P<registry_name>.*)/components/(?P<component_name>.*)/(?P<identifier_type>.*)/(?P<identifier_name>.*)",
        component_uri,
    )
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


def resolve_connection_id(ml_client, connection_uri: str) -> str:
    short_form = re.match(r"azureml:(?P<connection_name>[^/]*)", connection_uri)
    if short_form:
        connection_name = short_form.group("connection_name")
    else:
        # TODO: Handle long form connection sub/rg/ws, ideally reuse logic implemented by connections code.
        long_form = re.match(r"azureml://.*/connections/(?P<connection_name>[^/]*)", connection_uri)
        if long_form:
            connection_name = long_form.group("connection_name")
        else:
            connection_name = connection_uri

    connection = ml_client.connections.get(connection_name)
    return connection.id
