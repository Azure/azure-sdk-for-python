# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access
import json
from typing import Any, Dict, Iterable, Optional, Union, Callable, List

from azure.ai.ml._artifacts._artifact_utilities import _check_and_upload_path

# cspell:disable-next-line
from azure.ai.ml._restclient.azure_ai_assets_v2024_04_01.azureaiassetsv20240401 import (
    MachineLearningServicesClient as AzureAiAssetsClient042024,
)

# cspell:disable-next-line
from azure.ai.ml._restclient.azure_ai_assets_v2024_04_01.azureaiassetsv20240401.models import Index as RestIndex
from azure.ai.ml._restclient.v2023_04_01_preview.models import ListViewType
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._asset_utils import _resolve_label_to_asset
from azure.ai.ml._utils._http_utils import HttpPipeline
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._utils.utils import _get_base_urls_from_discovery_service
from azure.ai.ml.constants._common import AzureMLResourceType, WorkspaceDiscoveryUrlKey, AssetTypes
from azure.ai.ml.entities._assets import Index
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException
from azure.ai.ml.operations._datastore_operations import DatastoreOperations
from azure.core.credentials import TokenCredential

from azure.ai.ml.entities import PipelineJob, PipelineJobSettings
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._indexes import (
    AzureAISearchConfig,
    IndexDataSource,
    LocalSource,
    GitSource,
    ModelConfiguration,
)
from azure.ai.ml.entities._indexes.entities.data_index import (
    CitationRegex,
    Data,
    DataIndex,
    Embedding,
    IndexSource,
    IndexStore,
)
from azure.ai.ml.entities._indexes.utils._open_ai_utils import build_open_ai_protocol, build_connection_id
from azure.ai.ml.entities._credentials import ManagedIdentityConfiguration, UserIdentityConfiguration
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.entities._indexes.data_index_func import index_data as index_data_func
from azure.ai.ml._utils._asset_utils import (
    _validate_auto_delete_setting_in_data_output,
    _validate_workspace_managed_datastore,
)

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class IndexOperations(_ScopeDependentOperations):
    """Represents a client for performing operations on index assets.

    You should not instantiate this class directly. Instead, you should create MLClient and use this client via the
    property MLClient.index
    """

    def __init__(
        self,
        *,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        credential: TokenCredential,
        datastore_operations: DatastoreOperations,
        all_operations: OperationsContainer,
        **kwargs: Any,
    ):
        super().__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self._credential = credential
        # Dataplane service clients are lazily created as they are needed
        self.__azure_ai_assets_client: Optional[AzureAiAssetsClient042024] = None
        # Kwargs to propagate to dataplane service clients
        self._service_client_kwargs: Dict[str, Any] = kwargs.pop("_service_client_kwargs", {})
        self._all_operations = all_operations

        self._datastore_operation: DatastoreOperations = datastore_operations
        self._requests_pipeline: HttpPipeline = kwargs.pop("requests_pipeline")

        # Maps a label to a function which given an asset name,
        # returns the asset associated with the label
        self._managed_label_resolver: Dict[str, Callable[[str], Index]] = {"latest": self._get_latest_version}

    @property
    def _azure_ai_assets(self) -> AzureAiAssetsClient042024:
        """Lazily instantiated client for azure ai assets api.

        .. note::

            Property is lazily instantiated since the api's base url depends on the user's workspace, and
            must be fetched remotely.
        """
        if self.__azure_ai_assets_client is None:
            workspace_operations = self._all_operations.all_operations[AzureMLResourceType.WORKSPACE]

            endpoint = _get_base_urls_from_discovery_service(
                workspace_operations, self._operation_scope.workspace_name, self._requests_pipeline
            )[WorkspaceDiscoveryUrlKey.API]

            self.__azure_ai_assets_client = AzureAiAssetsClient042024(
                endpoint=endpoint,
                subscription_id=self._operation_scope.subscription_id,
                resource_group_name=self._operation_scope.resource_group_name,
                workspace_name=self._operation_scope.workspace_name,
                credential=self._credential,
                **self._service_client_kwargs,
            )

        return self.__azure_ai_assets_client

    @monitor_with_activity(ops_logger, "Index.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(self, index: Index, **kwargs) -> Index:
        """Returns created or updated index asset.

        If not already in storage, asset will be uploaded to the workspace's default datastore.

        :param index: Index asset object.
        :type index: Index
        :return: Index asset object.
        :rtype: ~azure.ai.ml.entities.Index
        """

        if not index.name:
            msg = "Must specify a name."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.INDEX,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.MISSING_FIELD,
            )

        if not index.version:
            if not index._auto_increment_version:
                msg = "Must specify a version."
                raise ValidationException(
                    message=msg,
                    target=ErrorTarget.INDEX,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.MISSING_FIELD,
                )

            next_version = self._azure_ai_assets.indexes.get_next_version(index.name).next_version

            if next_version is None:
                msg = "Version not specified, could not automatically increment version. Set a version to resolve."
                raise ValidationException(
                    message=msg,
                    target=ErrorTarget.INDEX,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.SYSTEM_ERROR,
                    error_type=ValidationErrorType.MISSING_FIELD,
                )

            index.version = str(next_version)

        _ = _check_and_upload_path(
            artifact=index,
            asset_operations=self,
            datastore_name=index.datastore,
            artifact_type=ErrorTarget.INDEX,
            show_progress=self._show_progress,
        )

        return Index._from_rest_object(
            self._azure_ai_assets.indexes.create_or_update(
                name=index.name, version=index.version, body=index._to_rest_object(), **kwargs
            )
        )

    @monitor_with_activity(ops_logger, "Index.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, *, version: Optional[str] = None, label: Optional[str] = None, **kwargs) -> Index:
        """Returns information about the specified index asset.

        :param str name: Name of the index asset.
        :keyword Optional[str] version: Version of the index asset. Mutually exclusive with `label`.
        :keyword Optional[str] label: The label of the index asset. Mutually exclusive with  `version`.
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Index cannot be successfully validated.
            Details will be provided in the error message.
        :return: Index asset object.
        :rtype: ~azure.ai.ml.entities.Index
        """
        if version and label:
            msg = "Cannot specify both version and label."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.INDEX,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        if label:
            return _resolve_label_to_asset(self, name, label)

        if not version:
            msg = "Must provide either version or label."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.INDEX,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.MISSING_FIELD,
            )

        index_version_resource = self._azure_ai_assets.indexes.get(name=name, version=version, **kwargs)

        return Index._from_rest_object(index_version_resource)

    def _get_latest_version(self, name: str) -> Index:
        return Index._from_rest_object(self._azure_ai_assets.indexes.get_latest(name))

    @monitor_with_activity(ops_logger, "Index.List", ActivityType.PUBLICAPI)
    def list(
        self, name: Optional[str] = None, *, list_view_type: ListViewType = ListViewType.ACTIVE_ONLY, **kwargs
    ) -> Iterable[Index]:
        """List all Index assets in workspace.

        If an Index is specified by name, list all version of that Index.

        :param name: Name of the model.
        :type name: Optional[str]
        :keyword list_view_type: View type for including/excluding (for example) archived models.
            Defaults to :attr:`ListViewType.ACTIVE_ONLY`.
        :paramtype list_view_type: ListViewType
        :return: An iterator like instance of Index objects
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.ml.entities.Index]
        """

        def cls(rest_indexes: Iterable[RestIndex]) -> List[Index]:
            return [Index._from_rest_object(i) for i in rest_indexes]

        if name is None:
            return self._azure_ai_assets.indexes.list_latest(cls=cls, **kwargs)

        return self._azure_ai_assets.indexes.list(name, list_view_type=list_view_type, cls=cls, **kwargs)

    # pylint: disable=too-many-locals
    def build_index(
        self,
        *,
        ######## required args ##########
        name: str,
        embeddings_model_config: ModelConfiguration,
        ######## chunking information ##########
        data_source_citation_url: Optional[str] = None,
        tokens_per_chunk: Optional[int] = None,
        token_overlap_across_chunks: Optional[int] = None,
        input_glob: Optional[str] = None,
        ######## other generic args ########
        document_path_replacement_regex: Optional[str] = None,
        ######## Azure AI Search index info ########
        index_config: Optional[AzureAISearchConfig] = None,  # todo better name?
        ######## data source info ########
        input_source: Union[IndexDataSource, str],
        input_source_credential: Optional[Union[ManagedIdentityConfiguration, UserIdentityConfiguration]] = None,
    ) -> Union["Index", "Job"]:  # type: ignore[name-defined]
        """Builds an index on the cloud using the Azure AI Resources service.

        :keyword name: The name of the index to be created.
        :paramtype name: str
        :keyword embeddings_model_config: Model config for the embedding model.
        :paramtype embeddings_model_config: ~azure.ai.ml.entities._indexes.ModelConfiguration
        :keyword data_source_citation_url: The URL of the data source.
        :paramtype data_source_citation_url: Optional[str]
        :keyword tokens_per_chunk: The size of chunks to be used for indexing.
        :paramtype tokens_per_chunk: Optional[int]
        :keyword token_overlap_across_chunks: The amount of overlap between chunks.
        :paramtype token_overlap_across_chunks: Optional[int]
        :keyword input_glob: The glob pattern to be used for indexing.
        :paramtype input_glob: Optional[str]
        :keyword document_path_replacement_regex: The regex pattern for replacing document paths.
        :paramtype document_path_replacement_regex: Optional[str]
        :keyword index_config: The configuration for the ACS output.
        :paramtype index_config: Optional[~azure.ai.ml.entities._indexes.AzureAISearchConfig]
        :keyword input_source: The input source for the index.
        :paramtype input_source: Union[~azure.ai.ml.entities._indexes.IndexDataSource, str]
        :keyword input_source_credential: The identity to be used for the index.
        :paramtype input_source_credential: Optional[Union[~azure.ai.ml.entities.ManagedIdentityConfiguration,
            ~azure.ai.ml.entities.UserIdentityConfiguration]]
        :return: If the `source_input` is a GitSource, returns a created DataIndex Job object.
        :rtype: Union[~azure.ai.ml.entities.Index, ~azure.ai.ml.entities.Job]
        :raises ValueError: If the `source_input` is not type ~typing.Str or
            ~azure.ai.ml.entities._indexes.LocalSource.
        """
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
                citation_url_replacement_regex=(
                    CitationRegex(
                        match_pattern=document_path_replacement_regex["match_pattern"],  # type: ignore[index]
                        replacement_pattern=document_path_replacement_regex[
                            "replacement_pattern"  # type: ignore[index]
                        ],
                    )
                    if document_path_replacement_regex
                    else None
                ),
            ),
            embedding=Embedding(
                model=build_open_ai_protocol(
                    model=embeddings_model_config.model_name, deployment=embeddings_model_config.deployment_name
                ),
                connection=build_connection_id(embeddings_model_config.connection_name, self._operation_scope),
            ),
            index=(
                IndexStore(
                    type="acs",
                    connection=build_connection_id(index_config.connection_id, self._operation_scope),
                    name=index_config.index_name,
                )
                if index_config is not None
                else IndexStore(type="faiss")
            ),
            # name is replaced with a unique value each time the job is run
            path=f"azureml://datastores/workspaceblobstore/paths/indexes/{name}/{{name}}",
        )

        if isinstance(input_source, LocalSource):
            data_index.source.input_data = Data(
                type="uri_folder",
                path=input_source.input_data.path,
            )

            return self._create_data_indexing_job(data_index=data_index, identity=input_source_credential)

        if isinstance(input_source, str):
            data_index.source.input_data = Data(
                type="uri_folder",
                path=input_source,
            )

            return self._create_data_indexing_job(data_index=data_index, identity=input_source_credential)

        if isinstance(input_source, GitSource):
            from azure.ai.ml import MLClient

            ml_registry = MLClient(credential=self._credential, registry_name="azureml")
            git_clone_component = ml_registry.components.get("llm_rag_git_clone", label="latest")

            # Clone Git Repo and use as input to index_job
            @pipeline(default_compute="serverless")  # type: ignore[call-overload]
            def git_to_index(
                git_url,
                branch_name="",
                git_connection_id="",
            ):
                git_clone = git_clone_component(git_repository=git_url, branch_name=branch_name)
                git_clone.environment_variables["AZUREML_WORKSPACE_CONNECTION_ID_GIT"] = git_connection_id

                index_job = index_data_func(
                    description=data_index.description,
                    data_index=data_index,
                    input_data_override=git_clone.outputs.output_data,
                    ml_client=MLClient(
                        subscription_id=self._subscription_id,
                        resource_group_name=self._resource_group_name,
                        workspace_name=self._workspace_name,
                        credential=self._credential,
                    ),
                )
                # pylint: disable=no-member
                return index_job.outputs

            git_index_job = git_to_index(
                git_url=input_source.url,
                branch_name=input_source.branch_name,
                git_connection_id=input_source.connection_id,
            )
            # Ensure repo cloned each run to get latest, comment out to have first clone reused.
            git_index_job.settings.force_rerun = True

            # Submit the DataIndex Job
            return self._all_operations.all_operations[AzureMLResourceType.JOB].create_or_update(git_index_job)
        raise ValueError(f"Unsupported input source type {type(input_source)}")

    def _create_data_indexing_job(
        self,
        data_index: DataIndex,
        identity: Optional[Union[ManagedIdentityConfiguration, UserIdentityConfiguration]] = None,
        compute: str = "serverless",
        serverless_instance_type: Optional[str] = None,
        input_data_override: Optional[Input] = None,
        submit_job: bool = True,
        **kwargs,
    ) -> PipelineJob:
        """
        Returns the data import job that is creating the data asset.

        :param data_index: DataIndex object.
        :type data_index: azure.ai.ml.entities._dataindex
        :param identity: Identity configuration for the job.
        :type identity: Optional[Union[ManagedIdentityConfiguration, UserIdentityConfiguration]]
        :param compute: The compute target to use for the job. Default: "serverless".
        :type compute: str
        :param serverless_instance_type: The instance type to use for serverless compute.
        :type serverless_instance_type: Optional[str]
        :param input_data_override: Input data override for the job.
            Used to pipe output of step into DataIndex Job in a pipeline.
        :type input_data_override: Optional[Input]
        :param submit_job: Whether to submit the job to the service. Default: True.
        :type submit_job: bool
        :return: data import job object.
        :rtype: ~azure.ai.ml.entities.PipelineJob.
        """
        # pylint: disable=no-member
        from azure.ai.ml import MLClient

        default_name = "data_index_" + data_index.name if data_index.name is not None else ""
        experiment_name = kwargs.pop("experiment_name", None) or default_name
        data_index.type = AssetTypes.URI_FOLDER

        # avoid specifying auto_delete_setting in job output now
        _validate_auto_delete_setting_in_data_output(data_index.auto_delete_setting)

        # block customer specified path on managed datastore
        data_index.path = _validate_workspace_managed_datastore(data_index.path)

        if "${{name}}" not in str(data_index.path) and "{name}" not in str(data_index.path):
            data_index.path = str(data_index.path).rstrip("/") + "/${{name}}"

        index_job = index_data_func(
            description=data_index.description or kwargs.pop("description", None) or default_name,
            name=data_index.name or kwargs.pop("name", None),
            display_name=kwargs.pop("display_name", None) or default_name,
            experiment_name=experiment_name,
            compute=compute,
            serverless_instance_type=serverless_instance_type,
            data_index=data_index,
            ml_client=MLClient(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                credential=self._credential,
            ),
            identity=identity,
            input_data_override=input_data_override,
            **kwargs,
        )
        index_pipeline = PipelineJob(
            description=index_job.description,
            tags=index_job.tags,
            name=index_job.name,
            display_name=index_job.display_name,
            experiment_name=experiment_name,
            properties=index_job.properties or {},
            settings=PipelineJobSettings(force_rerun=True, default_compute=compute),
            jobs={default_name: index_job},
        )
        index_pipeline.properties["azureml.mlIndexAssetName"] = data_index.name
        index_pipeline.properties["azureml.mlIndexAssetKind"] = data_index.index.type
        index_pipeline.properties["azureml.mlIndexAssetSource"] = kwargs.pop("mlindex_asset_source", "Data Asset")

        if submit_job:
            return self._all_operations.all_operations[AzureMLResourceType.JOB].create_or_update(
                job=index_pipeline, skip_validation=True, **kwargs
            )
        return index_pipeline
