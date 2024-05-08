# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Callable, Dict, Iterable, List, Optional

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
from azure.ai.ml.constants._common import AzureMLResourceType, WorkspaceDiscoveryUrlKey
from azure.ai.ml.entities._assets import Index
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException
from azure.ai.ml.operations._datastore_operations import DatastoreOperations
from azure.core.credentials import TokenCredential

# pylint: disable=protected-access


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
