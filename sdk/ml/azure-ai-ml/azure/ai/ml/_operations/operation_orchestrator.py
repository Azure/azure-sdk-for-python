# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from os import PathLike
from typing import Any, Optional, Tuple, Union
from azure.core.exceptions import ResourceNotFoundError

from azure.ai.ml._artifacts._artifact_utilities import _check_and_upload_path, _check_and_upload_env_build_context
from azure.ai.ml._utils._exception_utils import EmptyDirectoryError
from azure.ai.ml.entities._assets import Code, Model, Dataset, Environment, Data
from azure.ai.ml.entities._assets.asset import Asset
from azure.ai.ml.entities import Component
from azure.ai.ml._utils._arm_id_utils import (
    AMLNamedArmId,
    AMLVersionedArmId,
    is_ARM_id_for_resource,
    parse_prefixed_name_version,
    parse_name_label,
    get_arm_id_with_version,
    is_registry_id_for_resource,
)
from azure.ai.ml._utils._storage_utils import AzureMLDatastorePathUri
from azure.ai.ml._utils._asset_utils import _resolve_label_to_asset
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope
from azure.ai.ml.constants import (
    AZUREML_RESOURCE_PROVIDER,
    NAMED_RESOURCE_ID_FORMAT,
    VERSIONED_RESOURCE_ID_FORMAT,
    VERSIONED_RESOURCE_NAME,
    AzureMLResourceType,
    FILE_PREFIX,
    FOLDER_PREFIX,
    ARM_ID_PREFIX,
    HTTPS_PREFIX,
    MLFLOW_URI_REGEX_FORMAT,
    JOB_URI_REGEX_FORMAT,
)
from azure.ai.ml._restclient.v2021_10_01.models import UriReference
import re
from azure.ai.ml._ml_exceptions import AssetException, ModelException, ErrorCategory, ErrorTarget, ValidationException

module_logger = logging.getLogger(__name__)


class OperationOrchestrator(object):
    def __init__(self, operation_container: OperationsContainer, operation_scope: OperationScope):
        self._operation_container = operation_container
        self._operation_scope = operation_scope

    @property
    def _datastore_operation(self):
        return self._operation_container.all_operations[AzureMLResourceType.DATASTORE]

    @property
    def _code_assets(self):
        return self._operation_container.all_operations[AzureMLResourceType.CODE]

    @property
    def _model(self):
        return self._operation_container.all_operations[AzureMLResourceType.MODEL]

    @property
    def _dataset(self):
        return self._operation_container.all_operations[AzureMLResourceType.DATASET]

    @property
    def _environments(self):
        return self._operation_container.all_operations[AzureMLResourceType.ENVIRONMENT]

    @property
    def _data(self):
        return self._operation_container.all_operations[AzureMLResourceType.DATA]

    @property
    def _component(self):
        return self._operation_container.all_operations[AzureMLResourceType.COMPONENT]

    def get_asset_arm_id(
        self,
        asset: Optional[Union[str, Asset]],
        azureml_type: str,
        register_asset: bool = True,
        sub_workspace_resource: bool = True,
    ) -> Optional[Union[str, Asset]]:
        """This method converts AzureML Id to ARM Id. Or if the given asset is entity object, it tries to register/upload the asset based on register_asset and aszureml_type.

        :param asset: The asset to resolve/register. It can be a ARM id or a entity's object.
        :type asset: Optional[Union[str, Asset]]
        :param azureml_type: The AzureML resource type. Defined in AzureMLResourceType.
        :type azureml_type: str
        :param register_asset: flag to register the asset, defaults to True
        :type register_asset: bool, optional
        :param sub_workspace_resource:
        :type sub_workspace_resource: bool, optional
        :param arm_id_cache_dict: a dict to cache the arm id of input asset
        :type arm_id_cache_dict: Dict[str, str], optional
        :return: The ARM Id or entity object
        :rtype: Union[str, Asset], optional
        """
        if (
            asset is None
            or is_ARM_id_for_resource(asset, azureml_type, sub_workspace_resource)
            or is_registry_id_for_resource(asset)
        ):
            return asset
        elif isinstance(asset, str):
            if azureml_type in AzureMLResourceType.NAMED_TYPES:
                return NAMED_RESOURCE_ID_FORMAT.format(
                    self._operation_scope.subscription_id,
                    self._operation_scope.resource_group_name,
                    AZUREML_RESOURCE_PROVIDER,
                    self._operation_scope.workspace_name,
                    azureml_type,
                    asset,
                )
            elif azureml_type in AzureMLResourceType.VERSIONED_TYPES:
                name, version = self._resolve_name_version_from_name_label(asset, azureml_type)
                if not version:
                    name, version = parse_prefixed_name_version(asset)

                if not version:
                    msg = "Failed to extract version when parsing asset {} of type {} as arm id. Version must be provided."
                    raise ValidationException(
                        message=msg.format(asset, azureml_type),
                        target=ErrorTarget.ASSET,
                        no_personal_data_message=msg.format("", azureml_type),
                        error_category=ErrorCategory.USER_ERROR,
                    )
                return VERSIONED_RESOURCE_ID_FORMAT.format(
                    self._operation_scope.subscription_id,
                    self._operation_scope.resource_group_name,
                    AZUREML_RESOURCE_PROVIDER,
                    self._operation_scope.workspace_name,
                    azureml_type,
                    name,
                    version,
                )
            else:
                msg = "Unsupported azureml type {} for asset: {}"
                raise ValidationException(
                    message=msg.format(azureml_type, asset),
                    target=ErrorTarget.ASSET,
                    no_personal_data_message=msg.format(azureml_type, ""),
                )
        elif isinstance(asset, Asset):
            try:
                # TODO: once the asset redesign is finished, this logic can be replaced with unified API
                if azureml_type == AzureMLResourceType.CODE and isinstance(asset, Code):
                    result = self._get_code_asset_arm_id(asset, register_asset=register_asset)
                elif azureml_type == AzureMLResourceType.ENVIRONMENT and isinstance(asset, Environment):
                    result = self._get_environment_arm_id(asset, register_asset=register_asset)
                elif azureml_type == AzureMLResourceType.MODEL and isinstance(asset, Model):
                    result = self._get_model_arm_id(asset, register_asset=register_asset)
                elif azureml_type == AzureMLResourceType.DATA and isinstance(asset, Data):
                    result = self._get_data_arm_id(asset, register_asset=register_asset)
                elif azureml_type == AzureMLResourceType.DATASET and isinstance(asset, Dataset):
                    result = self._get_dataset_arm_id(asset, register_asset=register_asset)
                elif azureml_type == AzureMLResourceType.COMPONENT and isinstance(asset, Component):
                    result = self._get_component_arm_id(asset)
                else:
                    msg = "Unsupported azureml type {} for asset: {}"
                    raise ValidationException(
                        message=msg.format(azureml_type, asset),
                        target=ErrorTarget.ASSET,
                        no_personal_data_message=msg.format(azureml_type, ""),
                        error_category=ErrorCategory.USER_ERROR,
                    )
            except EmptyDirectoryError as e:
                msg = f"Error creating {azureml_type} asset : {e.message}"
                raise AssetException(
                    message=msg.format(azureml_type, e.message),
                    target=ErrorTarget.ASSET,
                    no_personal_data_message=msg.format(azureml_type, ""),
                    error=e,
                )
            return result
        else:
            msg = f"Error creating {azureml_type} asset: must be Optional[Union[str, Asset]]"
            raise ValidationException(
                message=msg,
                target=ErrorTarget.ASSET,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )

    def _get_code_asset_arm_id(self, code_asset: Code, register_asset: bool = True) -> Union[Code, str]:
        try:
            self._validate_datastore_name(code_asset.path)
            if register_asset:
                code_asset = self._code_assets.create_or_update(code_asset)
                return code_asset.id
            else:
                uploaded_code_asset, _ = _check_and_upload_path(artifact=code_asset, asset_operations=self._code_assets)
                uploaded_code_asset._id = get_arm_id_with_version(
                    self._operation_scope, AzureMLResourceType.CODE, code_asset.name, code_asset.version
                )
                return uploaded_code_asset
        except Exception as e:
            raise AssetException(
                message=f"Error with code: {e}",
                target=ErrorTarget.ASSET,
                no_personal_data_message="Error getting code asset",
                error=e,
            )

    def _get_environment_arm_id(self, environment: Environment, register_asset: bool = True) -> Union[str, Environment]:
        if register_asset:
            env_response = self._environments.create_or_update(environment)
            return env_response.id
        else:
            environment = _check_and_upload_env_build_context(environment=environment, operations=self._environments)
            environment._id = get_arm_id_with_version(
                self._operation_scope, AzureMLResourceType.ENVIRONMENT, environment.name, environment.version
            )
            return environment

    def _get_model_arm_id(self, model: Model, register_asset: bool = True) -> Union[str, Model]:
        try:
            self._validate_datastore_name(model.path)

            if register_asset:
                return self._model.create_or_update(model).id
            else:
                uploaded_model, _ = _check_and_upload_path(artifact=model, asset_operations=self._model)
                uploaded_model._id = get_arm_id_with_version(
                    self._operation_scope, AzureMLResourceType.MODEL, model.name, model.version
                )
                return uploaded_model
        except Exception as e:
            raise ModelException(
                message=f"Error with model: {e}",
                target=ErrorTarget.MODEL,
                no_personal_data_message="Error getting model",
                error=e,
            )

    def _get_dataset_arm_id(self, data_asset: Dataset, register_asset: bool = True) -> Union[str, Dataset]:
        for path in data_asset.paths:
            self._validate_datastore_name(path)

        if register_asset:
            return self._dataset.create_or_update(data_asset).id
        else:
            data_asset, _ = _check_and_upload_path(artifact=data_asset, asset_operations=self._dataset)
            return data_asset

    def _get_data_arm_id(self, data_asset: Data, register_asset: bool = True) -> Union[str, Data]:
        self._validate_datastore_name(data_asset.path)

        if register_asset:
            return self._data.create_or_update(data_asset).id
        else:
            data_asset, _ = _check_and_upload_path(artifact=data_asset, asset_operations=self._data)
            return data_asset

    def _get_component_arm_id(self, component: Component) -> str:
        """If component arm id is already resolved, return the id
        Or get arm id via remote call, register the component if necessary,
        and FILL BACK the arm id to component to reduce remote call"""
        if not component.id:
            component._id = self._component.create_or_update(component, is_anonymous=True).id
        return component.id

    def _resolve_name_version_from_name_label(self, aml_id: str, azureml_type: str) -> Tuple[str, Optional[str]]:
        """Given an AzureML id of the form name@label, resolves the label to the actual ID

        :param aml_id: AzureML id of the form name@label
        :type aml_id: str
        :param azureml_type: The AzureML resource type. Defined in AzureMLResourceType.
        :type azureml_type: str
        :returns: Returns tuple (name, version) on success, (name@label, None) if resolution fails
        """
        name, label = parse_name_label(aml_id)
        if (
            azureml_type not in AzureMLResourceType.VERSIONED_TYPES
            or azureml_type == AzureMLResourceType.CODE
            or not label
        ):
            return aml_id, None

        return (
            name,
            _resolve_label_to_asset(self._operation_container.all_operations[azureml_type], name, label=label).version,
        )

    def resolve_azureml_id(self, arm_id: str = None, **kwargs) -> str:
        """Thie function converts ARM id to name or name:version AzureML id. It parses the ARM id and matches the
        subscription Id, resource group name and worksapce_name.

        TODO: It is detable whether this method should be in operation_orchestrator.

        :param arm_id: entity's ARM id, defaults to None
        :type arm_id: str, optional
        :return: AzureML id
        :rtype: str
        """

        if arm_id:
            if not isinstance(arm_id, str):
                msg = "arm_id to be resolved: str expected but get {}".format(type(arm_id))
                raise ValidationException(message=msg, no_personal_data_message=msg, target=ErrorTarget.GENERAL)
            try:
                arm_id_obj = AMLVersionedArmId(arm_id)
                if arm_id_obj.is_registry_id:
                    return arm_id
                if self._match(arm_id_obj):
                    return VERSIONED_RESOURCE_NAME.format(arm_id_obj.asset_name, arm_id_obj.asset_version)
            except ValidationException:
                pass  # fall back to named arm id
            try:
                arm_id_obj = AMLNamedArmId(arm_id)
                if self._match(arm_id_obj):
                    return arm_id_obj.asset_name
            except ValidationException:
                pass  # fall back to be not a ARM_id
        return arm_id

    def _match(self, id: Any) -> bool:
        return (
            id.subscription_id == self._operation_scope.subscription_id
            and id.resource_group_name == self._operation_scope.resource_group_name
            and id.workspace_name == self._operation_scope.workspace_name
        )

    def _validate_datastore_name(self, datastore_uri: Optional[Union[UriReference, str, PathLike]]) -> None:
        if datastore_uri:
            try:
                if isinstance(datastore_uri, UriReference):
                    if datastore_uri.file:
                        datastore_uri = datastore_uri.file
                    else:
                        datastore_uri = datastore_uri.folder
                elif isinstance(datastore_uri, str):
                    if datastore_uri.startswith(FILE_PREFIX):
                        datastore_uri = datastore_uri[len(FILE_PREFIX) :]
                    elif datastore_uri.startswith(FOLDER_PREFIX):
                        datastore_uri = datastore_uri[len(FOLDER_PREFIX) :]
                elif isinstance(datastore_uri, PathLike):
                    return

                if (
                    datastore_uri.startswith(HTTPS_PREFIX) and datastore_uri.count("/") == 7
                ):  # only long-form (i.e. "https://x.blob.core.windows.net/datastore/LocalUpload/guid/x/x") format includes datastore
                    datastore_name = datastore_uri.split("/")[3]
                elif datastore_uri.startswith(ARM_ID_PREFIX) and not (
                    re.match(MLFLOW_URI_REGEX_FORMAT, datastore_uri) or re.match(JOB_URI_REGEX_FORMAT, datastore_uri)
                ):
                    datastore_name = AzureMLDatastorePathUri(datastore_uri).datastore
                else:
                    # local path
                    return

                if datastore_name.startswith(ARM_ID_PREFIX):
                    datastore_name[len(ARM_ID_PREFIX) :]

                self._datastore_operation.get(datastore_name)
            except ResourceNotFoundError:
                msg = "The datastore {} could not be found in this workspace."
                raise ValidationException(
                    message=msg.format(datastore_name),
                    target=ErrorTarget.DATASTORE,
                    no_personal_data_message=msg.format(""),
                    error_category=ErrorCategory.USER_ERROR,
                )
