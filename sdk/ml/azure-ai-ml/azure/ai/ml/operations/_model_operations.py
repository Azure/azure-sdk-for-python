# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,no-value-for-parameter,disable=docstring-missing-return,docstring-missing-param,docstring-missing-rtype,ungrouped-imports,line-too-long,too-many-statements

import re
from contextlib import contextmanager
from os import PathLike, path
from typing import Any, Dict, Generator, Iterable, Optional, Union, cast

from marshmallow.exceptions import ValidationError as SchemaValidationError

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
from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2021_10_01_dataplanepreview import (
    AzureMachineLearningWorkspaces as ServiceClient102021Dataplane,
)
from azure.ai.ml._restclient.v2023_08_01_preview import AzureMachineLearningWorkspaces as ServiceClient082023Preview
from azure.ai.ml._restclient.v2023_08_01_preview.models import ListViewType, ModelVersion
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._arm_id_utils import AMLVersionedArmId, is_ARM_id_for_resource
from azure.ai.ml._utils._asset_utils import (
    _archive_or_restore,
    _get_latest,
    _get_next_version_from_container,
    _resolve_label_to_asset,
)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._utils._registry_utils import (
    get_asset_body_for_registry_storage,
    get_registry_client,
    get_sas_uri_for_registry_asset,
    get_storage_details_for_registry_assets,
)
from azure.ai.ml._utils._storage_utils import get_ds_name_and_path_prefix, get_storage_client
from azure.ai.ml._utils.utils import resolve_short_datastore_url, validate_ml_flow_folder, _is_evaluator
from azure.ai.ml.constants._common import ARM_ID_PREFIX, ASSET_ID_FORMAT, REGISTRY_URI_FORMAT, AzureMLResourceType
from azure.ai.ml.entities._assets import Environment, Model, ModelPackage
from azure.ai.ml.entities._assets._artifacts.code import Code
from azure.ai.ml.entities._assets.workspace_asset_reference import WorkspaceAssetReference
from azure.ai.ml.entities._credentials import AccountKeyConfiguration
from azure.ai.ml.exceptions import (
    AssetPathException,
    ErrorCategory,
    ErrorTarget,
    ValidationErrorType,
    ValidationException,
)
from azure.ai.ml.operations._datastore_operations import DatastoreOperations
from azure.core.exceptions import ResourceNotFoundError

from ._operation_orchestrator import OperationOrchestrator

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


# pylint: disable=too-many-instance-attributes
class ModelOperations(_ScopeDependentOperations):
    """ModelOperations.

    You should not instantiate this class directly. Instead, you should create an MLClient instance that instantiates it
    for you and attaches it as an attribute.

    :param operation_scope: Scope variables for the operations classes of an MLClient object.
    :type operation_scope: ~azure.ai.ml._scope_dependent_operations.OperationScope
    :param operation_config: Common configuration for operations classes of an MLClient object.
    :type operation_config: ~azure.ai.ml._scope_dependent_operations.OperationConfig
    :param service_client: Service client to allow end users to operate on Azure Machine Learning Workspace
        resources (ServiceClient082023Preview or ServiceClient102021Dataplane).
    :type service_client: typing.Union[
        azure.ai.ml._restclient.v2023_04_01_preview._azure_machine_learning_workspaces.AzureMachineLearningWorkspaces,
        azure.ai.ml._restclient.v2021_10_01_dataplanepreview._azure_machine_learning_workspaces.
        AzureMachineLearningWorkspaces]
    :param datastore_operations: Represents a client for performing operations on Datastores.
    :type datastore_operations: ~azure.ai.ml.operations._datastore_operations.DatastoreOperations
    :param all_operations: All operations classes of an MLClient object.
    :type all_operations: ~azure.ai.ml._scope_dependent_operations.OperationsContainer
    """

    _IS_EVALUATOR = "__is_evaluator"

    # pylint: disable=unused-argument
    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: Union[ServiceClient082023Preview, ServiceClient102021Dataplane],
        datastore_operations: DatastoreOperations,
        all_operations: Optional[OperationsContainer] = None,
        **kwargs,
    ):
        super(ModelOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self._model_versions_operation = service_client.model_versions
        self._model_container_operation = service_client.model_containers
        self._service_client = service_client
        self._datastore_operation = datastore_operations
        self._all_operations = all_operations
        self._control_plane_client: Any = kwargs.get("control_plane_client", None)
        self._workspace_rg = kwargs.pop("workspace_rg", None)
        self._workspace_sub = kwargs.pop("workspace_sub", None)
        self._registry_reference = kwargs.pop("registry_reference", None)

        # Maps a label to a function which given an asset name,
        # returns the asset associated with the label
        self._managed_label_resolver = {"latest": self._get_latest_version}
        self.__is_evaluator = kwargs.pop(ModelOperations._IS_EVALUATOR, False)

    @monitor_with_activity(ops_logger, "Model.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(  # type: ignore
        self, model: Union[Model, WorkspaceAssetReference]
    ) -> Model:  # TODO: Are we going to implement job_name?
        """Returns created or updated model asset.

        :param model: Model asset object.
        :type model: ~azure.ai.ml.entities.Model
        :raises ~azure.ai.ml.exceptions.AssetPathException: Raised when the Model artifact path is
            already linked to another asset
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Model cannot be successfully validated.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.EmptyDirectoryError: Raised if local path provided points to an empty directory.
        :return: Model asset object.
        :rtype: ~azure.ai.ml.entities.Model
        """
        # Check if we have the model with the same name and it is an
        # evaluator. In this aces raise the exception do not create the model.
        if not self.__is_evaluator and _is_evaluator(model.properties):
            msg = (
                "Unable to create the evaluator using ModelOperations. To create "
                "evaluator, please use EvaluatorOperations by calling "
                "ml_client.evaluators.create_or_update(model) instead."
            )
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.MODEL,
                error_category=ErrorCategory.USER_ERROR,
            )
        if model.name is not None:
            model_properties = self._get_model_properties(model.name)
            if model_properties is not None and _is_evaluator(model_properties) != _is_evaluator(model.properties):
                if _is_evaluator(model.properties):
                    msg = (
                        f"Unable to create the model with name {model.name} "
                        "because this version of model was marked as promptflow evaluator, but the previous "
                        "version is a regular model. "
                        "Please change the model name and try again."
                    )
                else:
                    msg = (
                        f"Unable to create the model with name {model.name} "
                        "because previous version of model was marked as promptflow evaluator, but this "
                        "version is a regular model. "
                        "Please change the model name and try again."
                    )
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.MODEL,
                    error_category=ErrorCategory.USER_ERROR,
                )
        try:
            name = model.name
            if not model.version and model._auto_increment_version:
                model.version = _get_next_version_from_container(
                    name=model.name,
                    container_operation=self._model_container_operation,
                    resource_group_name=self._operation_scope.resource_group_name,
                    workspace_name=self._workspace_name,
                    registry_name=self._registry_name,
                )

            version = model.version

            sas_uri = None

            if self._registry_name:
                # Case of copy model to registry
                if isinstance(model, WorkspaceAssetReference):
                    # verify that model is not already in registry
                    try:
                        self._model_versions_operation.get(
                            name=model.name,
                            version=model.version,
                            resource_group_name=self._resource_group_name,
                            registry_name=self._registry_name,
                        )
                    except Exception as err:  # pylint: disable=W0718
                        if isinstance(err, ResourceNotFoundError):
                            pass
                        else:
                            raise err
                    else:
                        msg = "A model with this name and version already exists in registry"
                        raise ValidationException(
                            message=msg,
                            no_personal_data_message=msg,
                            target=ErrorTarget.MODEL,
                            error_category=ErrorCategory.USER_ERROR,
                        )

                    model_rest = model._to_rest_object()
                    result = self._service_client.resource_management_asset_reference.begin_import_method(
                        resource_group_name=self._resource_group_name,
                        registry_name=self._registry_name,
                        body=model_rest,
                    ).result()

                    if not result:
                        model_rest_obj = self._get(name=str(model.name), version=model.version)
                        return Model._from_rest_object(model_rest_obj)

                sas_uri = get_sas_uri_for_registry_asset(
                    service_client=self._service_client,
                    name=model.name,
                    version=model.version,
                    resource_group=self._resource_group_name,
                    registry=self._registry_name,
                    body=get_asset_body_for_registry_storage(self._registry_name, "models", model.name, model.version),
                )

            model, indicator_file = _check_and_upload_path(  # type: ignore[type-var]
                artifact=model,
                asset_operations=self,
                sas_uri=sas_uri,
                artifact_type=ErrorTarget.MODEL,
                show_progress=self._show_progress,
            )

            model.path = resolve_short_datastore_url(model.path, self._operation_scope)  # type: ignore
            validate_ml_flow_folder(model.path, model.type)  # type: ignore
            model_version_resource = model._to_rest_object()
            auto_increment_version = model._auto_increment_version
            try:
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
                    result = self._get(name=str(model.name), version=model.version)

            except Exception as e:  # pylint: disable=W0718
                # service side raises an exception if we attempt to update an existing asset's path
                if str(e) == ASSET_PATH_ERROR:
                    raise AssetPathException(
                        message=CHANGED_ASSET_PATH_MSG,
                        target=ErrorTarget.MODEL,
                        no_personal_data_message=CHANGED_ASSET_PATH_MSG_NO_PERSONAL_DATA,
                        error_category=ErrorCategory.USER_ERROR,
                    ) from e
                raise e

            model = Model._from_rest_object(result)
            if auto_increment_version and indicator_file:
                datastore_info = _get_default_datastore_info(self._datastore_operation)
                _update_metadata(model.name, model.version, indicator_file, datastore_info)  # update version in storage

            return model
        except Exception as ex:  # pylint: disable=W0718
            if isinstance(ex, SchemaValidationError):
                log_and_raise_error(ex)
            else:
                raise ex

    def _get(self, name: str, version: Optional[str] = None) -> ModelVersion:  # name:latest
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

        return (
            self._model_container_operation.get(name=name, registry_name=self._registry_name, **self._scope_kwargs)
            if self._registry_name
            else self._model_container_operation.get(
                name=name, workspace_name=self._workspace_name, **self._scope_kwargs
            )
        )

    @monitor_with_activity(ops_logger, "Model.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, version: Optional[str] = None, label: Optional[str] = None) -> Model:
        """Returns information about the specified model asset.

        :param name: Name of the model.
        :type name: str
        :param version: Version of the model.
        :type version: str
        :param label: Label of the model. (mutually exclusive with version)
        :type label: str
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Model cannot be successfully validated.
            Details will be provided in the error message.
        :return: Model asset object.
        :rtype: ~azure.ai.ml.entities.Model
        """
        if version and label:
            msg = "Cannot specify both version and label."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.MODEL,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
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
                error_type=ValidationErrorType.MISSING_FIELD,
            )
        # TODO: We should consider adding an exception trigger for internal_model=None
        model_version_resource = self._get(name, version)

        return Model._from_rest_object(model_version_resource)

    @monitor_with_activity(ops_logger, "Model.Download", ActivityType.PUBLICAPI)
    def download(self, name: str, version: str, download_path: Union[PathLike, str] = ".") -> None:
        """Download files related to a model.

        :param name: Name of the model.
        :type name: str
        :param version: Version of the model.
        :type version: str
        :param download_path: Local path as download destination, defaults to current working directory of the current
            user. Contents will be overwritten.
        :type download_path: Union[PathLike, str]
        :raises ResourceNotFoundError: if can't find a model matching provided name.
        """

        model_uri = self.get(name=name, version=version).path
        ds_name, path_prefix = get_ds_name_and_path_prefix(model_uri, self._registry_name)
        if self._registry_name:
            sas_uri, auth_type = get_storage_details_for_registry_assets(
                service_client=self._service_client,
                asset_name=name,
                asset_version=version,
                reg_name=self._registry_name,
                asset_type=AzureMLResourceType.MODEL,
                rg_name=self._resource_group_name,
                uri=model_uri,
            )
            if auth_type == "SAS":
                storage_client = get_storage_client(credential=None, storage_account=None, account_url=sas_uri)
            else:
                parts = sas_uri.split("/")
                storage_account = parts[2].split(".")[0]
                container_name = parts[3]
                storage_client = get_storage_client(
                    credential=None,
                    storage_account=storage_account,
                    container_name=container_name,
                )

        else:
            ds = self._datastore_operation.get(ds_name, include_secrets=True)
            acc_name = ds.account_name

            if isinstance(ds.credentials, AccountKeyConfiguration):
                credential = ds.credentials.account_key
            else:
                try:
                    credential = ds.credentials.sas_token
                except Exception as e:  # pylint: disable=W0718
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
        module_logger.info("Downloading the model %s at %s\n", path_prefix, path_file)
        storage_client.download(starts_with=path_prefix, destination=path_file)

    @monitor_with_activity(ops_logger, "Model.Archive", ActivityType.PUBLICAPI)
    def archive(
        self,
        name: str,
        version: Optional[str] = None,
        label: Optional[str] = None,
        **kwargs: Any,
    ) -> None:  # pylint:disable=unused-argument
        """Archive a model asset.

        :param name: Name of model asset.
        :type name: str
        :param version: Version of model asset.
        :type version: str
        :param label: Label of the model asset. (mutually exclusive with version)
        :type label: str

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_misc.py
                :start-after: [START model_operations_archive]
                :end-before: [END model_operations_archive]
                :language: python
                :dedent: 8
                :caption: Archive a model.
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

    @monitor_with_activity(ops_logger, "Model.Restore", ActivityType.PUBLICAPI)
    def restore(
        self,
        name: str,
        version: Optional[str] = None,
        label: Optional[str] = None,
        **kwargs: Any,
    ) -> None:  # pylint:disable=unused-argument
        """Restore an archived model asset.

        :param name: Name of model asset.
        :type name: str
        :param version: Version of model asset.
        :type version: str
        :param label: Label of the model asset. (mutually exclusive with version)
        :type label: str

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_misc.py
                :start-after: [START model_operations_restore]
                :end-before: [END model_operations_restore]
                :language: python
                :dedent: 8
                :caption: Restore an archived model.
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

    @monitor_with_activity(ops_logger, "Model.List", ActivityType.PUBLICAPI)
    def list(
        self,
        name: Optional[str] = None,
        stage: Optional[str] = None,
        *,
        list_view_type: ListViewType = ListViewType.ACTIVE_ONLY,
    ) -> Iterable[Model]:
        """List all model assets in workspace.

        :param name: Name of the model.
        :type name: Optional[str]
        :param stage: The Model stage
        :type stage: Optional[str]
        :keyword list_view_type: View type for including/excluding (for example) archived models.
            Defaults to :attr:`ListViewType.ACTIVE_ONLY`.
        :paramtype list_view_type: ListViewType
        :return: An iterator like instance of Model objects
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.ml.entities.Model]
        """
        if name:
            return cast(
                Iterable[Model],
                (
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
                        stage=stage,
                        **self._scope_kwargs,
                    )
                ),
            )

        return cast(
            Iterable[Model],
            (
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
            ),
        )

    @monitor_with_activity(ops_logger, "Model.Share", ActivityType.PUBLICAPI)
    @experimental
    def share(
        self, name: str, version: str, *, share_with_name: str, share_with_version: str, registry_name: str
    ) -> Model:
        """Share a model asset from workspace to registry.

        :param name: Name of model asset.
        :type name: str
        :param version: Version of model asset.
        :type version: str
        :keyword share_with_name: Name of model asset to share with.
        :paramtype share_with_name: str
        :keyword share_with_version: Version of model asset to share with.
        :paramtype share_with_version: str
        :keyword registry_name: Name of the destination registry.
        :paramtype registry_name: str
        :return: Model asset object.
        :rtype: ~azure.ai.ml.entities.Model
        """

        #  Get workspace info to get workspace GUID
        workspace = self._service_client.workspaces.get(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
        )
        workspace_guid = workspace.workspace_id
        workspace_location = workspace.location

        # Get model asset ID
        asset_id = ASSET_ID_FORMAT.format(
            workspace_location,
            workspace_guid,
            AzureMLResourceType.MODEL,
            name,
            version,
        )

        model_ref = WorkspaceAssetReference(
            name=share_with_name if share_with_name else name,
            version=share_with_version if share_with_version else version,
            asset_id=asset_id,
        )

        with self._set_registry_client(registry_name):
            return self.create_or_update(model_ref)

    def _get_latest_version(self, name: str) -> Model:
        """Returns the latest version of the asset with the given name.

        Latest is defined as the most recently created, not the most recently updated.
        """
        result = _get_latest(
            name,
            self._model_versions_operation,
            self._resource_group_name,
            self._workspace_name,
            self._registry_name,
        )
        return Model._from_rest_object(result)

    @contextmanager
    def _set_registry_client(self, registry_name: str) -> Generator:
        """Sets the registry client for the model operations.

        :param registry_name: Name of the registry.
        :type registry_name: str
        """
        rg_ = self._operation_scope._resource_group_name
        sub_ = self._operation_scope._subscription_id
        registry_ = self._operation_scope.registry_name
        client_ = self._service_client
        model_versions_operation_ = self._model_versions_operation

        try:
            _client, _rg, _sub = get_registry_client(self._service_client._config.credential, registry_name)
            self._operation_scope.registry_name = registry_name
            self._operation_scope._resource_group_name = _rg
            self._operation_scope._subscription_id = _sub
            self._service_client = _client
            self._model_versions_operation = _client.model_versions
            yield
        finally:
            self._operation_scope.registry_name = registry_
            self._operation_scope._resource_group_name = rg_
            self._operation_scope._subscription_id = sub_
            self._service_client = client_
            self._model_versions_operation = model_versions_operation_

    @experimental
    @monitor_with_activity(ops_logger, "Model.Package", ActivityType.PUBLICAPI)
    def package(self, name: str, version: str, package_request: ModelPackage, **kwargs: Any) -> Environment:
        """Package a model asset

        :param name: Name of model asset.
        :type name: str
        :param version: Version of model asset.
        :type version: str
        :param package_request: Model package request.
        :type package_request: ~azure.ai.ml.entities.ModelPackage
        :return: Environment object
        :rtype: ~azure.ai.ml.entities.Environment
        """

        is_deployment_flow = kwargs.pop("skip_to_rest", False)
        if not is_deployment_flow:
            orchestrators = OperationOrchestrator(
                operation_container=self._all_operations,  # type: ignore[arg-type]
                operation_scope=self._operation_scope,
                operation_config=self._operation_config,
            )

            # Create a code asset if code is not already an ARM ID
            if hasattr(package_request.inferencing_server, "code_configuration"):
                if package_request.inferencing_server.code_configuration and not is_ARM_id_for_resource(
                    package_request.inferencing_server.code_configuration.code,
                    AzureMLResourceType.CODE,
                ):
                    if package_request.inferencing_server.code_configuration.code.startswith(ARM_ID_PREFIX):
                        package_request.inferencing_server.code_configuration.code = orchestrators.get_asset_arm_id(
                            package_request.inferencing_server.code_configuration.code[len(ARM_ID_PREFIX) :],
                            azureml_type=AzureMLResourceType.CODE,
                        )
                    else:
                        package_request.inferencing_server.code_configuration.code = orchestrators.get_asset_arm_id(
                            Code(
                                base_path=package_request._base_path,
                                path=package_request.inferencing_server.code_configuration.code,
                            ),
                            azureml_type=AzureMLResourceType.CODE,
                        )
                if package_request.inferencing_server.code_configuration and hasattr(
                    package_request.inferencing_server.code_configuration, "code"
                ):
                    package_request.inferencing_server.code_configuration.code = (
                        "azureml:/" + package_request.inferencing_server.code_configuration.code
                    )

            if package_request.base_environment_source and hasattr(
                package_request.base_environment_source, "resource_id"
            ):
                if not package_request.base_environment_source.resource_id.startswith(REGISTRY_URI_FORMAT):
                    package_request.base_environment_source.resource_id = orchestrators.get_asset_arm_id(
                        package_request.base_environment_source.resource_id,
                        azureml_type=AzureMLResourceType.ENVIRONMENT,
                    )

                package_request.base_environment_source.resource_id = (
                    "azureml:/" + package_request.base_environment_source.resource_id
                    if not package_request.base_environment_source.resource_id.startswith(ARM_ID_PREFIX)
                    else package_request.base_environment_source.resource_id
                )

            # create ARM id for the target environment
            if self._operation_scope._workspace_location and self._operation_scope._workspace_id:
                package_request.target_environment_id = f"azureml://locations/{self._operation_scope._workspace_location}/workspaces/{self._operation_scope._workspace_id}/environments/{package_request.target_environment_id}"
            else:
                if self._all_operations is not None:
                    ws: Any = self._all_operations.all_operations.get("workspaces")
                    ws_details = ws.get(self._workspace_name)
                    workspace_location, workspace_id = (
                        ws_details.location,
                        ws_details._workspace_id,
                    )
                    package_request.target_environment_id = f"azureml://locations/{workspace_location}/workspaces/{workspace_id}/environments/{package_request.target_environment_id}"

            if package_request.environment_version is not None:
                package_request.target_environment_id = (
                    package_request.target_environment_id + f"/versions/{package_request.environment_version}"
                )
            package_request = package_request._to_rest_object()

        if self._registry_reference:
            package_request.target_environment_id = f"azureml://locations/{self._operation_scope._workspace_location}/workspaces/{self._operation_scope._workspace_id}/environments/{package_request.target_environment_id}"
        package_out = (
            self._model_versions_operation.begin_package(
                name=name,
                version=version,
                registry_name=self._registry_name if self._registry_name else self._registry_reference,
                body=package_request,
                **self._scope_kwargs,
            ).result()
            if self._registry_name or self._registry_reference
            else self._model_versions_operation.begin_package(
                name=name,
                version=version,
                workspace_name=self._workspace_name,
                body=package_request,
                **self._scope_kwargs,
            ).result()
        )
        if is_deployment_flow:  # No need to go through the schema, as this is for deployment notification only
            return package_out
        if hasattr(package_out, "target_environment_id"):
            environment_id = package_out.target_environment_id
        else:
            environment_id = package_out.additional_properties["targetEnvironmentId"]

        pattern = r"azureml://locations/(\w+)/workspaces/([\w-]+)/environments/([\w.-]+)/versions/(\d+)"
        parsed_id: Any = re.search(pattern, environment_id)

        if parsed_id:
            environment_name = parsed_id.group(3)
            environment_version = parsed_id.group(4)
        else:
            parsed_id = AMLVersionedArmId(environment_id)
            environment_name = parsed_id.asset_name
            environment_version = parsed_id.asset_version

        module_logger.info("\nPackage Created")
        if package_out is not None and package_out.__class__.__name__ == "PackageResponse":
            if self._registry_name:
                current_rg = self._scope_kwargs.pop("resource_group_name", None)
                self._scope_kwargs["resource_group_name"] = self._workspace_rg
                self._control_plane_client._config.subscription_id = self._workspace_sub
                env_out = self._control_plane_client.environment_versions.get(
                    name=environment_name,
                    version=environment_version,
                    workspace_name=self._workspace_name,
                    **self._scope_kwargs,
                )
                package_out = Environment._from_rest_object(env_out)
                self._scope_kwargs["resource_group_name"] = current_rg
            else:
                if self._all_operations is not None:
                    environment_operation = self._all_operations.all_operations[AzureMLResourceType.ENVIRONMENT]
                    package_out = environment_operation.get(name=environment_name, version=environment_version)

        return package_out

    def _get_model_properties(
        self, name: str, version: Optional[str] = None, label: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Return the model properties if the model with this name exists.

        :param name: Model name.
        :type name: str
        :param version: Model version.
        :type version: Optional[str]
        :param label: model label.
        :type label: Optional[str]
        :return: Model properties, if the model exists, or None.
        """
        try:
            if version or label:
                return self.get(name, version, label).properties
            return self._get_latest_version(name).properties
        except (ResourceNotFoundError, ValidationException):
            return None
