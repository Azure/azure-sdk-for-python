# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import json
import os
import tempfile
from typing import Any, Dict, Iterable, Optional, Union, cast

import yaml

from azure.ai.ml._restclient.v2023_08_01_preview import AzureMachineLearningWorkspaces as ServiceClient022023Preview
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope, _ScopeDependentOperations
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._logger_utils import OpsLogger

from azure.ai.ml.entities._indexes.entities.mlindex import Index as MLIndexAsset
from azure.ai.ml.entities._indexes.utils._open_ai_utils import build_open_ai_protocol, build_connection_id
from azure.ai.ml.entities._indexes import (
    AzureAISearchConfig,
    IndexDataSource,
    AISearchSource,
    LocalSource,
    GitSource,
    ModelConfiguration,
)
from azure.ai.ml.entities._credentials import ManagedIdentityConfiguration, UserIdentityConfiguration

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class IndexOperations(_ScopeDependentOperations):
    """IndexOperations.

    This class should not be instantiated directly. Instead, use the `compute` attribute of an MLClient object.

    :param operation_scope: Scope variables for the operations classes of an MLClient object.
    :type operation_scope: ~azure.ai.ml._scope_dependent_operations.OperationScope
    :param operation_config: Common configuration for operations classes of an MLClient object.
    :type operation_config: ~azure.ai.ml._scope_dependent_operations.OperationConfig
    :param service_client: Service client to allow end users to operate on Azure Machine Learning
        Workspace resources.
    :type service_client: ~azure.ai.ml._restclient.v2023_02_01_preview.AzureMachineLearningWorkspaces
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: ServiceClient022023Preview,
        **kwargs: Dict,
    ) -> None:
        super(IndexOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self._operation = service_client.compute
        self._workspace_operations = service_client.workspaces
        self._vmsize_operations = service_client.virtual_machine_sizes
        self._usage_operations = service_client.usages
        self._init_kwargs = kwargs

    def build_index(
        self,
        *,
        ######## required args ##########
        name: str,
        vector_store: str,
        embeddings_model_config: ModelConfiguration,
        ######## chunking information ##########
        data_source_citation_url: Optional[str] = None,
        tokens_per_chunk: Optional[int] = None,
        token_overlap_across_chunks: Optional[int] = None,
        input_glob: Optional[str] = None,
        ######## other generic args ########
        document_path_replacement_regex: Optional[str] = None,
        ######## ACS index info ########
        index_config: Optional[AzureAISearchConfig] = None,  # todo better name?
        ######## data source info ########
        input_source: Union[IndexDataSource, str],
        input_source_credential: Optional[Union[ManagedIdentityConfiguration, UserIdentityConfiguration]] = None,
        _dry_run: bool = False,
    ) -> Union["MLIndex", "Job"]:  # type: ignore[name-defined]
        """Builds an index on the cloud using the Azure AI Resources service.
        
        :param name: The name of the index to be created.
        :type name: str
        :param vector_store: The name of the vector store to be used for the index.
        :type vector_store: str
        :param data_source_citation_url: The URL of the data source.
        :type data_source_citation_url: Optional[str]
        :param tokens_per_chunk: The size of chunks to be used for indexing.
        :type tokens_per_chunk: Optional[int]
        :param token_overlap_across_chunks: The amount of overlap between chunks.
        :type token_overlap_across_chunks: Optional[int]
        :param input_glob: The glob pattern to be used for indexing.
        :type input_glob: Optional[str]
        :param max_sample_files: The maximum number of sample files to be used for indexing.
        :type max_sample_files: Optional[int]
        :param chunk_prepend_summary: Whether to prepend a summary to each chunk.
        :type chunk_prepend_summary: Optional[bool]
        :param document_path_replacement_regex: The regex pattern for replacing document paths.
        :type document_path_replacement_regex: Optional[str]
        :param embeddings_model_config: The configuration for the embedding model.
        :type embeddings_model_config: Optional[~azure.ai.ml.entities._indexes.ModelConfiguration]
        :param index_config: The configuration for the ACS output.
        :type index_config: Optional[~azure.ai.ml.entities._indexes.AzureAISearchConfig]
        :param input_source: The input source for the index.
        :type input_source: Union[~azure.ai.ml.entities._indexes.IndexDataSource, str]
        :param input_source_credential: The identity to be used for the index.
        :type input_source_credential: Optional[Union[~azure.ai.ml.entities.ManagedIdentityConfiguration,
            ~azure.ai.ml.entities.UserIdentityConfiguration]]
        :param _dry_run: Whether to run the operation as a dry run. Defaults to False.
        :type _dry_run: bool
        :return: If the `source_input` is an AISearchSource, returns an MLIndex object.
            If the `source_input` is a GitSource, returns a created DataIndex Job object.
        :rtype: Union[~azure.ai.ml.entities._indexes.MLIndex, ~azure.ai.ml.entities.Job]
        :raises ValueError: If the `source_input` is not type ~typing.Str or
            ~azure.ai.ml.entities._indexes.LocalSource.
        """
        from azure.ai.ml.entities._indexes.dataindex.data_index import index_data
        from azure.ai.ml.entities._indexes.dataindex.entities import (
            CitationRegex,
            Data,
            DataIndex,
            Embedding,
            IndexSource,
            IndexStore,
        )
        from azure.ai.ml.entities._indexes.embeddings import EmbeddingsContainer

        if not embeddings_model_config.model_name:
            raise ValueError("Please specify embeddings_model_config.model_name")

        if isinstance(input_source, AISearchSource):
            from azure.ai.ml.entities._indexes.utils.connections import get_connection_by_id_v2, get_target_from_connection

            # Construct MLIndex object
            mlindex_config = {}
            connection_args = {
                "connection_type": "workspace_connection", 
                "connection": {"id": build_connection_id(embeddings_model_config.deployment_name, self._scope)}
            }
            mlindex_config["embeddings"] = EmbeddingsContainer.from_uri(  # type: ignore[attr-defined]
                build_open_ai_protocol(embeddings_model_config.model_name), **connection_args
            ).get_metadata()  # Bug 2922096
            mlindex_config["index"] = {
                "kind": "acs",
                "connection_type": "workspace_connection",
                "connection": {"id": input_source.acs_connection_id},
                "index": input_source.acs_index_name,
                "endpoint": get_target_from_connection(
                    get_connection_by_id_v2(input_source.acs_connection_id, credential=self._ml_client._credential)
                ),
                "engine": "azure-sdk",
                "field_mapping": {
                    "content": input_source.acs_content_key,
                    # "url": input_source., # TODO: Add to AISearchSource
                    # "filename": input_source., # TODO: Add to AISearchSource
                    "title": input_source.acs_title_key,
                    "metadata": input_source.acs_metadata_key,
                },
            }
            if input_source.acs_embedding_key is not None:
                mlindex_config["index"]["embedding"] = input_source.acs_embedding_key

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file = os.path.join(temp_dir, "MLIndex")
                with open(temp_file, "w") as f:
                    yaml.dump(mlindex_config, f)

                mlindex = MLIndexAsset(name=name, path=temp_dir)
                # Register it
                return self.indexes.create_or_update(mlindex)

        if document_path_replacement_regex:
            document_path_replacement_regex = json.loads(document_path_replacement_regex)
        data_index = DataIndex(
            name=name,
            source=IndexSource(
                input_data=Data(
                    type="uri_folder",
                    path=".",
                ),
                input_glob=input_glob,
                chunk_size=tokens_per_chunk,
                chunk_overlap=token_overlap_across_chunks,
                citation_url=data_source_citation_url,
                citation_url_replacement_regex=CitationRegex(
                    match_pattern=document_path_replacement_regex["match_pattern"],  # type: ignore[index]
                    replacement_pattern=document_path_replacement_regex["replacement_pattern"], # type: ignore[index]
                )
                if document_path_replacement_regex
                else None,
            ),
            embedding=Embedding(
                model=build_open_ai_protocol(embeddings_model_config.model_name),
                connection=build_connection_id(embeddings_model_config.deployment_name, self._scope),
            ),
            index=IndexStore(
                type="acs",
                connection=build_connection_id(index_config.acs_connection_id, self._scope),
                name=index_config.acs_index_name,
            )
            if index_config is not None
            else IndexStore(type="faiss"),
            # name is replaced with a unique value each time the job is run
            path=f"azureml://datastores/workspaceblobstore/paths/indexes/{name}/{{name}}",
        )

        if isinstance(input_source, GitSource):
            from azure.ai.ml.dsl import pipeline

            ml_registry = MLClient(credential=self._ml_client._credential, registry_name="azureml")
            git_clone_component = ml_registry.components.get("llm_rag_git_clone", label="latest")

            # Clone Git Repo and use as input to index_job
            @pipeline(default_compute="serverless")
            def git_to_index(
                git_url,
                branch_name="",
                git_connection_id="",
            ):
                git_clone = git_clone_component(git_repository=git_url, branch_name=branch_name)
                git_clone.environment_variables["AZUREML_WORKSPACE_CONNECTION_ID_GIT"] = git_connection_id

                index_job = index_data(
                    description=data_index.description,
                    data_index=data_index,
                    input_data_override=git_clone.outputs.output_data,
                    ml_client=self._ml_client,
                )

                return index_job.outputs

            git_index_job = git_to_index(
                git_url=input_source.git_url,
                branch_name=input_source.git_branch_name,
                git_connection_id=input_source.git_connection_id,
            )
            # Ensure repo cloned each run to get latest, comment out to have first clone reused.
            git_index_job.settings.force_rerun = True

            # Submit the DataIndex Job
            return self._ml_client.jobs.create_or_update(git_index_job, identity=input_source_credential)

        if isinstance(input_source, LocalSource):
            data_index.source.input_data = Data(
                type="uri_folder",
                path=input_source.input_data.path,
            )

            return self._ml_client.data.index_data(data_index=data_index, identity=input_source_credential)
        elif isinstance(input_source, str):
            data_index.source.input_data = Data(
                type="uri_folder",
                path=input_source,
            )

            return self._ml_client.data.index_data(data_index=data_index, identity=input_source_credential)
        else:
            raise ValueError(f"Unsupported input source type {type(input_source)}")
