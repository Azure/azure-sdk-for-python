# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import logging
import os
import tempfile
from typing import Any, Optional, Union, Optional

import yaml  # type: ignore[import]

from azure.ai.resources._utils._ai_client_utils import find_config_file_path, get_config_info
from azure.ai.resources._utils._open_ai_utils import build_open_ai_protocol
from azure.ai.resources._utils._str_utils import build_connection_id
from azure.ai.resources.constants._common import DEFAULT_OPEN_AI_CONNECTION_NAME, DEFAULT_CONTENT_SAFETY_CONNECTION_NAME
from azure.ai.resources.entities.mlindex import Index as MLIndexAsset
from azure.ai.resources.operations import ACSOutputConfig, ACSSource, GitSource, IndexDataSource, LocalSource
from azure.ai.ml import MLClient
from azure.ai.ml._restclient.v2023_06_01_preview import AzureMachineLearningWorkspaces as ServiceClient062023Preview
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities._credentials import ManagedIdentityConfiguration, UserIdentityConfiguration
from azure.core.credentials import TokenCredential

from .._restclient._azure_open_ai._client import MachineLearningServicesClient
from .._project_scope import OperationScope
from .._user_agent import USER_AGENT
from azure.ai.resources.operations import (
    AIResourceOperations,
    ConnectionOperations,
    SingleDeploymentOperations,
    MLIndexOperations,
    PFOperations,
    ProjectOperations,
    DataOperations,
    ModelOperations,
    AzureOpenAIDeploymentOperations,
)

from azure.ai.resources._telemetry import get_appinsights_log_handler

@experimental
class AIClient:
    """A client class to interact with Azure AI services.

    Use this client to manage Azure AI resources such as MLIndexes, jobs, models, and so on.

    :param credential: The credential object.
    :type credential: ~azure.core.credentials.TokenCredential
    :param subscription_id: The Azure subscription ID.
    :type subscription_id: str
    :param resource_group_name: The name of the resource group.
    :type resource_group_name: str
    :param ai_resource_name: The name of the AI resource.
    :type ai_resource_name: Optional[str]
    :param project_name: The name of the AI project.
    :type project_name: Optional[str]
    """
    def __init__(
        self,
        credential: TokenCredential,
        subscription_id: str,
        resource_group_name: str,  # Consider changing to a team name
        ai_resource_name: Optional[str] = None,
        project_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:

        self._add_user_agent(kwargs)

        properties = {
            "subscription_id": subscription_id,
            "resource_group_name": resource_group_name,
        }
        if ai_resource_name:
            properties.update({"ai_resource_name": ai_resource_name})
        if project_name:
            properties.update({"project_name": project_name})
            
        team_name = kwargs.get("team_name")
        if team_name:
            properties.update({"team_name": team_name})

        user_agent = USER_AGENT

        app_insights_handler = get_appinsights_log_handler(
            user_agent,
            **{"properties": properties},
        )
        app_insights_handler_kwargs = {"app_insights_handler": app_insights_handler}

        self._scope = OperationScope(
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            ai_resource_name=ai_resource_name,
            project_name=project_name,
        )

        self._credential = credential
        self._ml_client = MLClient(
            credential=credential,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=project_name,
            **kwargs,
        )

        if project_name:
            ai_resource_name = ai_resource_name or self._ml_client.workspaces.get(project_name).workspace_hub.split("/")[-1]

        # Client scoped to the AI Resource for operations that need AI resource-scoping
        # instead of project scoping.
        self._ai_resource_ml_client = MLClient(
            credential=credential,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=ai_resource_name,
            **kwargs,
        )

        self._service_client_06_2023_preview = ServiceClient062023Preview(
            credential=self._credential,
            subscription_id=subscription_id,
            # base_url=base_url, # TODO does this still need to be set?
            **kwargs,
        )

        ai_services_client = MachineLearningServicesClient(
            self._credential,
            api_version="2023-08-01-preview",
            subscription_id=subscription_id
        )
        # TODO remove restclient dependency once v2 SDK supports lean filtering
        self._projects = ProjectOperations(
            resource_group_name=resource_group_name,
            service_client=self._service_client_06_2023_preview,
            ml_client=self._ml_client,
            **app_insights_handler_kwargs,
        )
        # TODO add scoping to allow connections to:
        # - Create project-scoped connections
        # For now, connections are AI resource-scoped.
        self._connections = ConnectionOperations(resource_ml_client=self._ai_resource_ml_client, project_ml_client=self._ml_client, **app_insights_handler_kwargs)
        self._mlindexes = MLIndexOperations(self._ml_client, **app_insights_handler_kwargs)
        self._ai_resources = AIResourceOperations(self._ml_client, **app_insights_handler_kwargs)
        self._single_deployments = SingleDeploymentOperations(self._ml_client, self._connections, **app_insights_handler_kwargs)
        self._azure_open_ai_deployments = AzureOpenAIDeploymentOperations(self._ml_client, ai_services_client)
        self._data = DataOperations(self._ml_client)
        self._models = ModelOperations(self._ml_client)
        # self._pf = PFOperations(self._ml_client, self._scope)

    @classmethod
    def from_config(
        cls,
        credential: TokenCredential,
        *,
        path: Optional[Union[os.PathLike, str]] = None,
        file_name=None,
        **kwargs,
    ) -> "AIClient":
        """Returns a client from an existing Azure AI project using a file configuration.

        To get the required details, you can go to the Project Overview page in AI Foundry.
        
        You can save a project's details in a JSON configuration file using this format:

        .. code-block:: json

            {
                "subscription_id": "<subscription_id>",
                "resource_group": "<resource_group_name>",
                "project_name": "<project_name>",
            }

        This method provides a simple way to reuse the same project across multiple Python notebooks or projects
        without retyping the project details.

        :param credential: The credential object.
        :type credential: ~azure.core.credentials.TokenCredential
        :keyword path: The path to the configuration file or starting directory to search for the configuration file
            within. Defaults to None, indicating the current directory will be used.
        :paramtype path: Optional[Union[os.PathLike, str]]
        :keyword file_name: The configuration file name to search for when path is a directory path. Defaults to
            "config.json".
        :paramtype file_name: Optional[str]
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if "config.json", or file_name if overridden,
            cannot be found in directory. Details will be provided in the error message.
        :returns: The client for an existing Azure AI project.
        :rtype: ~azure.ai.resources.client.AIClient
        """
        config_file_path = find_config_file_path(path, file_name)
        config_info = get_config_info(config_file_path)
        return AIClient(
            credential=credential,
            subscription_id=config_info["subscription_id"],
            resource_group_name=config_info["resource_group_name"],
            project_name=config_info["project_name"],
        )

    @property
    def ai_resources(self) -> AIResourceOperations:
        """A collection of AI resource-related operations.

        :return: A class containing AI resource-related operations.
        :rtype: ~azure.ai.resources.operations.AIResourceOperations
        """
        return self._ai_resources

    @property
    def projects(self) -> ProjectOperations:
        """A collection of project-related operations.

        :return: A class containing project-related operations.
        :rtype: ~azure.ai.resources.operations.ProjectOperations
        """
        return self._projects

    @property
    def connections(self) -> ConnectionOperations:
        """A collection of connection-related operations.

        .. note::
            Unlike other operation handles, the connections handle
            is scoped to the AIClient's AI Resource, and not the project.
            SDK support for project-scoped connections does not exist yet.

        :return: A class containing connection-related operations.
        :rtype: ~azure.ai.resources.operations.ConnectionsOperations
        """
        return self._connections

    @property
    def indexes(self) -> MLIndexOperations:
        """A collection of ML index-related operations.

        :return: A class containing ML index-related operations.
        :rtype: ~azure.ai.resources.operations.MLIndexOperations
        """
        return self._mlindexes

    # @property
    # def pf(self) -> PFOperations:
    #     """A collection of PF operation-related operations.

    #     :return: PF Operation operations
    #     :rtype: PFOperations
    #     """
    #     return self._pf

    @property
    def data(self) -> DataOperations:
        """A collection of data-related operations.

        :return: A class containing data-related operations.
        :rtype: ~azure.ai.resources.operations.DataOperations
        """
        return self._data

    @property
    def single_deployments(self) -> SingleDeploymentOperations:
        """A collection of single deployment-related operations.

        :return: A class containing single deployment-related operations.
        :rtype: ~azure.ai.resources.operations.SingleDeploymentOperations
        """
        return self._single_deployments

    @property
    def azure_open_ai_deployments(self) -> AzureOpenAIDeploymentOperations:
        """A collection of Azure OpenAI deployment-related operations.

        :return: Azure OpenAI deployment operations
        :rtype: ~azure.ai.resources.operations.AzureOpenAIDeploymentOperations
        """
        return self._azure_open_ai_deployments

    @property
    def models(self) -> ModelOperations:
        """A collection of model-related operations.

        :return: A class containing model-related operations.
        :rtype: ~azure.ai.resources.operations.ModelOperations
        """
        return self._models

    @property
    def subscription_id(self) -> str:
        """ The subscription ID the AIClient is associated with.

        :return: The subscription ID the AIClient is associated with.
        :rtype: str
        """
        return self._scope.subscription_id

    @property
    def resource_group_name(self) -> str:
        """The name of the resource group that the AIClient is associated with.

        :return: The name of the resource group that the AIClient is associated with.
        :rtype: str
        """
        return self._scope.resource_group_name

    @property
    def project_name(self) -> Optional[str]:
        """The workspace where workspace-dependent operations will be executed.

        :return: The name of the workspace where workspace-dependent operations will be executed.
        :rtype: Optional[str]
        """
        return self._scope.project_name
    
    @property
    def ai_resource_name(self) -> Optional[str]:
        """The name of the AI Resource where resource-dependent operations will be executed.

        :return: The name of the AI Resource where resource-dependent operations will be executed.
        :rtype: Optional[str]
        """
        return self._scope.ai_resource_name

    @property
    def tracking_uri(self) -> str:
        """The MLFlow tracking uri of the project.
        
        :return: The MLFlow tracking uri of the project.
        :rtype: str
        """
        project = self.projects._service_client.workspaces.get(
            self._scope.resource_group_name, self._scope.project_name, api_version="2023-04-01-preview"
        )
        return project.ml_flow_tracking_uri

    def build_index_on_cloud(
        self,
        *,
        ######## required args ##########
        output_index_name: str,
        vector_store: str,
        ######## chunking information ##########
        data_source_url: Optional[str] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        input_glob: Optional[str] = None,
        max_sample_files: Optional[int] = None,
        chunk_prepend_summary: Optional[bool] = None,
        ######## other generic args ########
        document_path_replacement_regex: Optional[str] = None,
        embeddings_model: str ="text-embedding-ada-002",
        aoai_connection_id: str = DEFAULT_OPEN_AI_CONNECTION_NAME,
        ######## ACS index info ########
        acs_config: Optional[ACSOutputConfig] = None,  # todo better name?
        ######## data source info ########
        input_source: Union[IndexDataSource, str],
        identity: Optional[Union[ManagedIdentityConfiguration, UserIdentityConfiguration]] = None,
        _dry_run: bool = False,
    ) -> Union["MLIndex", "Job"]:  # type: ignore[name-defined]
        """Builds an index on the cloud using the Azure AI Resources service.
        
        :param output_index_name: The name of the index to be created.
        :type output_index_name: str
        :param vector_store: The name of the vector store to be used for the index.
        :type vector_store: str
        :param data_source_url: The URL of the data source.
        :type data_source_url: Optional[str]
        :param chunk_size: The size of chunks to be used for indexing.
        :type chunk_size: Optional[int]
        :param chunk_overlap: The amount of overlap between chunks.
        :type chunk_overlap: Optional[int]
        :param input_glob: The glob pattern to be used for indexing.
        :type input_glob: Optional[str]
        :param max_sample_files: The maximum number of sample files to be used for indexing.
        :type max_sample_files: Optional[int]
        :param chunk_prepend_summary: Whether to prepend a summary to each chunk.
        :type chunk_prepend_summary: Optional[bool]
        :param document_path_replacement_regex: The regex pattern for replacing document paths.
        :type document_path_replacement_regex: Optional[str]
        :param embeddings_model: The model to be used for embeddings. Defaults to "text-embedding-ada-002".
        :type embeddings_model: str
        :param aoai_connection_id: The ID of the Azure Open AI connection to be used. Defaults to 
            ~azure.ai.resources.constants._common.DEFAULT_OPEN_AI_CONNECTION_NAME.
        :type aoai_connection_id: str
        :param acs_config: The configuration for the ACS output.
        :type acs_config: Optional[~azure.ai.resources.operations.ACSOutputConfig]
        :param input_source: The input source for the index.
        :type input_source: Union[~azure.ai.resources.operations.IndexDataSource, str]
        :param identity: The identity to be used for the index.
        :type identity: Optional[Union[~azure.ai.ml.entities.ManagedIdentityConfiguration,
            ~azure.ai.ml.entities.UserIdentityConfiguration]]
        :param _dry_run: Whether to run the operation as a dry run. Defaults to False.
        :type _dry_run: bool
        :return: If the `source_input` is an ACSSource, returns an MLIndex object.
            If the `source_input` is a GitSource, returns a created DataIndex Job object.
        :rtype: Union[~azure.ai.resources.entities.MLIndex, ~azure.ai.ml.entities.Job]
        :raises ValueError: If the `source_input` is not type ~typing.Str or
            ~azure.ai.resources.operations.LocalSource.
        """
        from azure.ai.resources._index._dataindex.data_index import index_data
        from azure.ai.resources._index._dataindex.entities import (
            CitationRegex,
            Data,
            DataIndex,
            Embedding,
            IndexSource,
            IndexStore,
        )
        from azure.ai.resources._index._embeddings import EmbeddingsContainer
        if isinstance(input_source, ACSSource):
            from azure.ai.resources._index._utils.connections import get_connection_by_id_v2, get_target_from_connection

            # Construct MLIndex object
            mlindex_config = {}
            connection_args = {"connection_type": "workspace_connection", "connection": {"id": aoai_connection_id}}
            mlindex_config["embeddings"] = EmbeddingsContainer.from_uri(  # type: ignore[attr-defined]
                build_open_ai_protocol(embeddings_model), **connection_args
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
                    # "url": input_source., # TODO: Add to ACSSource
                    # "filename": input_source., # TODO: Add to ACSSource
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

                mlindex = MLIndexAsset(name=output_index_name, path=temp_dir)
                # Register it
                return self.indexes.create_or_update(mlindex)

        if document_path_replacement_regex:
            document_path_replacement_regex = json.loads(document_path_replacement_regex)
        data_index = DataIndex(
            name=output_index_name,
            source=IndexSource(
                input_data=Data(
                    type="uri_folder",
                    path=".",
                ),
                input_glob=input_glob,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                citation_url=data_source_url,
                citation_url_replacement_regex=CitationRegex(
                    match_pattern=document_path_replacement_regex["match_pattern"],  # type: ignore[index]
                    replacement_pattern=document_path_replacement_regex["replacement_pattern"], # type: ignore[index]
                )
                if document_path_replacement_regex
                else None,
            ),
            embedding=Embedding(
                model=build_open_ai_protocol(embeddings_model),
                connection=build_connection_id(aoai_connection_id, self._scope),
            ),
            index=IndexStore(
                type="acs",
                connection=build_connection_id(acs_config.acs_connection_id, self._scope),
                name=acs_config.acs_index_name,
            )
            if acs_config is not None
            else IndexStore(type="faiss"),
            # name is replaced with a unique value each time the job is run
            path=f"azureml://datastores/workspaceblobstore/paths/indexes/{output_index_name}/{{name}}",
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
            return self._ml_client.jobs.create_or_update(git_index_job, identity=identity)

        if isinstance(input_source, LocalSource):
            data_index.source.input_data = Data(
                type="uri_folder",
                path=input_source.input_data.path,
            )

            return self._ml_client.data.index_data(data_index=data_index, identity=identity)
        elif isinstance(input_source, str):
            data_index.source.input_data = Data(
                type="uri_folder",
                path=input_source,
            )

            return self._ml_client.data.index_data(data_index=data_index, identity=identity)
        else:
            raise ValueError(f"Unsupported input source type {type(input_source)}")

    def get_default_aoai_connection(self) -> "azure.ai.resources.entities.AzureOpenAIConnection":  # type: ignore[name-defined]
        """Retrieves the default Azure Open AI connection associated with this AIClient's project,
        creating it if it does not already exist.

        :return: An Azure OpenAI Connection associated to the project
        :rtype: ~azure.ai.resources.entities.AzureOpenAIConnection
        """
        return self._connections.get(DEFAULT_OPEN_AI_CONNECTION_NAME)
    
    def get_default_content_safety_connection(self) -> "azure.ai.resources.entities.AzureAIServiceConnection":  # type: ignore[name-defined]
        """Retrieves a default Azure AI Service connection associated with this AIClient's project,
        creating it if the connection does not already exist.
        This particular AI Service connection is linked to an Azure Content Safety service.

        :return: An Azure AI Service Connection associated to the project that is linked to an Azure
            Content Safety service.
        :rtype: ~azure.ai.resources.entities.AzureAIServiceConnection
        """
        return self._connections.get(DEFAULT_CONTENT_SAFETY_CONNECTION_NAME)

    def _add_user_agent(self, kwargs) -> None:
        """Add user agent to kwargs or update existing user agent to contain SDK user agent."""
        user_agent = kwargs.pop("user_agent", None)
        user_agent = f"{user_agent} {USER_AGENT}" if user_agent else USER_AGENT
        kwargs.setdefault("user_agent", user_agent)
