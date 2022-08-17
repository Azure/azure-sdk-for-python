# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from os import PathLike, getcwd, path
from typing import Dict, Iterable, Union

from azure.ai.ml._artifacts._artifact_utilities import (
    _check_and_upload_path,
    _get_default_datastore_info,
    _update_metadata,
)
from azure.ai.ml._artifacts._constants import (
    ASSET_PATH_ERROR,
    CHANGED_ASSET_PATH_MSG,
    CHANGED_ASSET_PATH_MSG_NO_PERSONAL_DATA,
)
from azure.ai.ml._ml_exceptions import AssetPathException, ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml._restclient.v2021_10_01_dataplanepreview import (
    AzureMachineLearningWorkspaces as ServiceClient102021Dataplane,
)
from azure.ai.ml._restclient.v2022_02_01_preview.models import ListViewType, ModelVersionData
from azure.ai.ml._restclient.v2022_05_01 import AzureMachineLearningWorkspaces as ServiceClient052022
from azure.ai.ml._scope_dependent_operations import OperationScope, _ScopeDependentOperations
from azure.ai.ml._telemetry import AML_INTERNAL_LOGGER_NAMESPACE, ActivityType, monitor_with_activity
from azure.ai.ml._utils._asset_utils import (
    _archive_or_restore,
    _create_or_update_autoincrement,
    _get_latest,
    _resolve_label_to_asset,
)
from azure.ai.ml._utils._registry_utils import get_asset_body_for_registry_storage, get_sas_uri_for_registry_asset
from azure.ai.ml._utils._storage_utils import get_ds_name_and_path_prefix, get_storage_client
from azure.ai.ml._utils.utils import resolve_short_datastore_url, validate_ml_flow_folder
from azure.ai.ml.entities._assets import Model
from azure.ai.ml.entities._datastore.credentials import AccountKeyCredentials
from azure.ai.ml.operations._datastore_operations import DatastoreOperations

logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE + __name__)
logger.propagate = False
module_logger = logging.getLogger(__name__)


class ModelOperations(_ScopeDependentOperations):
    """ModelOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: Union[ServiceClient052022, ServiceClient102021Dataplane],
        datastore_operations: DatastoreOperations,
        **kwargs: Dict,
    ):
        super(ModelOperations, self).__init__(operation_scope)
        if "app_insights_handler" in kwargs:
            logger.addHandler(kwargs.pop("app_insights_handler"))
        self._model_versions_operation = service_client.model_versions
        self._model_container_operation = service_client.model_containers
        self._service_client = service_client
        self._datastore_operation = datastore_operations

        # Maps a label to a function which given an asset name,
        # returns the asset associated with the label
        self._managed_label_resolver = {"latest": self._get_latest_version}

    @monitor_with_activity(logger, "Model.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(self, model: Model) -> Model:  # TODO: Are we going to implement job_name?
        name = model.name
        if not model.version and self._registry_name:
            raise Exception("Model version is required for registry")
        version = model.version

        sas_uri = None

        if self._registry_name:
            sas_uri = get_sas_uri_for_registry_asset(
                service_client=self._service_client,
                name=model.name,
                version=model.version,
                resource_group=self._resource_group_name,
                registry=self._registry_name,
                body=get_asset_body_for_registry_storage(self._registry_name, "models", model.name, model.version),
            )
            if not sas_uri:
                module_logger.debug(f"Getting the existing asset name: {model.name}, version: {model.version}")
                return self.get(name=model.name, version=model.version)

        model, indicator_file = _check_and_upload_path(artifact=model, asset_operations=self, sas_uri=sas_uri)

        model.path = resolve_short_datastore_url(model.path, self._operation_scope)
        validate_ml_flow_folder(model.path, model.type)
        model_version_resource = model._to_rest_object()
        auto_increment_version = model._auto_increment_version
        try:
            if auto_increment_version:
                result = _create_or_update_autoincrement(
                    name=model.name,
                    body=model_version_resource,
                    version_operation=self._model_versions_operation,
                    container_operation=self._model_container_operation,
                    workspace_name=self._workspace_name,
                    **self._scope_kwargs,
                )
            else:
                result = (
                    self._model_versions_operation.begin_create_or_update(
                        name=name,
                        version=version,
                        body=model_version_resource,
                        registry_name=self._registry_name,
                        **self._scope_kwargs,
                    ).result()
                    if self._registry_name
                    else self._model_versions_operation.create_or_update(
                        name=name,
                        version=version,
                        body=model_version_resource,
                        workspace_name=self._workspace_name,
                        **self._scope_kwargs,
                    )
                )

            if not result and self._registry_name:
                result = self._get(name=model.name, version=model.version)

        except Exception as e:
            # service side raises an exception if we attempt to update an existing asset's path
            if str(e) == ASSET_PATH_ERROR:
                raise AssetPathException(
                    message=CHANGED_ASSET_PATH_MSG,
                    target=ErrorTarget.MODEL,
                    no_personal_data_message=CHANGED_ASSET_PATH_MSG_NO_PERSONAL_DATA,
                    error_category=ErrorCategory.USER_ERROR,
                )
            else:
                raise e

        model = Model._from_rest_object(result)
        if auto_increment_version and indicator_file:
            datastore_info = _get_default_datastore_info(self._datastore_operation)
            _update_metadata(model.name, model.version, indicator_file, datastore_info)  # update version in storage

        return model

    def _get(self, name: str, version: str = None) -> ModelVersionData:  # name:latest
        if version:
            return (
                self._model_versions_operation.get(
                    name=name,
                    version=version,
                    registry_name=self._registry_name,
                    **self._scope_kwargs,
                )
                if self._registry_name
                else self._model_versions_operation.get(
                    name=name,
                    version=version,
                    workspace_name=self._workspace_name,
                    **self._scope_kwargs,
                )
            )
        else:
            return (
                self._model_container_operation.get(name=name, registry_name=self._registry_name, **self._scope_kwargs)
                if self._registry_name
                else self._model_container_operation.get(
                    name=name, workspace_name=self._workspace_name, **self._scope_kwargs
                )
            )

    @monitor_with_activity(logger, "Model.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, version: str = None, label: str = None) -> Model:
        """Returns information about the specified model asset.

        :param name: Name of the model.
        :type name: str
        :param version: Version of the model.
        :type version: str
        :param label: Label of the model. (mutually exclusive with version)
        :type label: str
        """
        if version and label:
            msg = "Cannot specify both version and label."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.MODEL,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )

        if label:
            return _resolve_label_to_asset(self, name, label)

        if not version:
            msg = "Must provide either version or label"
            raise ValidationException(
                message=msg,
                target=ErrorTarget.MODEL,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        # TODO: We should consider adding an exception trigger for internal_model=None
        model_version_resource = self._get(name, version)

        return Model._from_rest_object(model_version_resource)

    @monitor_with_activity(logger, "Model.Download", ActivityType.PUBLICAPI)
    def download(self, name: str, version: str, download_path: Union[PathLike, str] = getcwd()) -> None:
        """Download files related to a model.

        :param str name: Name of the model.
        :param str version: Version of the model.
        :param Union[PathLike, str] download_path: Local path as download destination, defaults to current working directory of the current user. Contents will be overwritten.
        :raise: ResourceNotFoundError if can't find a model matching provided name.
        """
        model_uri = self.get(name=name, version=version).path
        ds_name, path_prefix = get_ds_name_and_path_prefix(model_uri)
        ds = self._datastore_operation.get(ds_name, include_secrets=True)
        acc_name = ds.account_name

        if isinstance(ds.credentials, AccountKeyCredentials):
            credential = ds.credentials.account_key
        else:
            try:
                credential = ds.credentials.sas_token
            except Exception as e:
                if not hasattr(ds.credentials, "sas_token"):
                    credential = self._datastore_operation._credential
                else:
                    raise e

        container = ds.container_name
        datastore_type = ds.type

        storage_client = get_storage_client(
            credential=credential,
            container_name=container,
            storage_account=acc_name,
            storage_type=datastore_type,
        )

        path_file = "{}{}{}".format(download_path, path.sep, name)
        is_directory = storage_client.exists(f"{path_prefix.rstrip('/')}/")
        if is_directory:
            path_file = path.join(path_file, path.basename(path_prefix.rstrip("/")))
        module_logger.info(f"Downloading the model {path_prefix} at {path_file}\n")
        storage_client.download(starts_with=path_prefix, destination=path_file)

    @monitor_with_activity(logger, "Model.Archive", ActivityType.PUBLICAPI)
    def archive(self, name: str, version: str = None, label: str = None) -> None:
        """Archive a model asset.

        :param name: Name of model asset.
        :type name: str
        :param version: Version of model asset.
        :type version: str
        :param label: Label of the model asset. (mutually exclusive with version)
        :type label: str
        """
        _archive_or_restore(
            asset_operations=self,
            version_operation=self._model_versions_operation,
            container_operation=self._model_container_operation,
            is_archived=True,
            name=name,
            version=version,
            label=label,
        )

    @monitor_with_activity(logger, "Model.Restore", ActivityType.PUBLICAPI)
    def restore(self, name: str, version: str = None, label: str = None) -> None:
        """Restore an archived model asset.

        :param name: Name of model asset.
        :type name: str
        :param version: Version of model asset.
        :type version: str
        :param label: Label of the model asset. (mutually exclusive with version)
        :type label: str
        """
        _archive_or_restore(
            asset_operations=self,
            version_operation=self._model_versions_operation,
            container_operation=self._model_container_operation,
            is_archived=False,
            name=name,
            version=version,
            label=label,
        )

    @monitor_with_activity(logger, "Model.List", ActivityType.PUBLICAPI)
    def list(
        self,
        name: str = None,
        *,
        list_view_type: ListViewType = ListViewType.ACTIVE_ONLY,
    ) -> Iterable[Model]:
        """List all model assets in workspace.

        :param name: Name of the model.
        :type name: Optional[str]
        :param list_view_type: View type for including/excluding (for example) archived models. Default: ACTIVE_ONLY.
        :type list_view_type: Optional[ListViewType]
        :return: An iterator like instance of Model objects
        :rtype: ~azure.core.paging.ItemPaged[Model]
        """
        if name:
            return (
                self._model_versions_operation.list(
                    name=name,
                    registry_name=self._registry_name,
                    cls=lambda objs: [Model._from_rest_object(obj) for obj in objs],
                    **self._scope_kwargs,
                )
                if self._registry_name
                else self._model_versions_operation.list(
                    name=name,
                    workspace_name=self._workspace_name,
                    cls=lambda objs: [Model._from_rest_object(obj) for obj in objs],
                    list_view_type=list_view_type,
                    **self._scope_kwargs,
                )
            )
        else:
            return (
                self._model_container_operation.list(
                    registry_name=self._registry_name,
                    cls=lambda objs: [Model._from_container_rest_object(obj) for obj in objs],
                    list_view_type=list_view_type,
                    **self._scope_kwargs,
                )
                if self._registry_name
                else self._model_container_operation.list(
                    workspace_name=self._workspace_name,
                    cls=lambda objs: [Model._from_container_rest_object(obj) for obj in objs],
                    list_view_type=list_view_type,
                    **self._scope_kwargs,
                )
            )

    def _get_latest_version(self, name: str) -> Model:
        """Returns the latest version of the asset with the given name.

        Latest is defined as the most recently created, not the most
        recently updated.
        """
        result = _get_latest(
            name,
            self._model_versions_operation,
            self._resource_group_name,
            self._workspace_name,
        )
        return Model._from_rest_object(result)
