# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
import re
from os import PathLike
from typing import Any, Optional, Tuple, Union

from typing_extensions import Protocol

from azure.ai.ml._artifacts._artifact_utilities import _check_and_upload_env_build_context, _check_and_upload_path
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)
from azure.ai.ml._utils._arm_id_utils import (
    AMLLabelledArmId,
    AMLNamedArmId,
    AMLVersionedArmId,
    get_arm_id_with_version,
    is_ARM_id_for_resource,
    is_registry_id_for_resource,
    is_singularity_full_name_for_resource,
    is_singularity_id_for_resource,
    is_singularity_short_name_for_resource,
    parse_name_label,
    parse_prefixed_name_version,
)
from azure.ai.ml._utils._asset_utils import _resolve_label_to_asset, get_storage_info_for_non_registry_asset
from azure.ai.ml._utils._storage_utils import AzureMLDatastorePathUri
from azure.ai.ml.constants._common import (
    ARM_ID_PREFIX,
    AZUREML_RESOURCE_PROVIDER,
    CURATED_ENV_PREFIX,
    DEFAULT_LABEL_NAME,
    FILE_PREFIX,
    FOLDER_PREFIX,
    HTTPS_PREFIX,
    JOB_URI_REGEX_FORMAT,
    LABELLED_RESOURCE_ID_FORMAT,
    LABELLED_RESOURCE_NAME,
    MLFLOW_URI_REGEX_FORMAT,
    NAMED_RESOURCE_ID_FORMAT,
    REGISTRY_VERSION_PATTERN,
    SINGULARITY_FULL_NAME_REGEX_FORMAT,
    SINGULARITY_ID_FORMAT,
    SINGULARITY_SHORT_NAME_REGEX_FORMAT,
    VERSIONED_RESOURCE_ID_FORMAT,
    VERSIONED_RESOURCE_NAME,
    AzureMLResourceType,
)
from azure.ai.ml.entities import Component
from azure.ai.ml.entities._assets import Code, Data, Environment, Model
from azure.ai.ml.entities._assets.asset import Asset
from azure.ai.ml.exceptions import (
    AssetException,
    EmptyDirectoryError,
    ErrorCategory,
    ErrorTarget,
    MlException,
    ModelException,
    ValidationErrorType,
    ValidationException,
)
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

module_logger = logging.getLogger(__name__)


class OperationOrchestrator(object):
    def __init__(
        self,
        operation_container: OperationsContainer,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
    ):
        self._operation_container = operation_container
        self._operation_scope = operation_scope
        self._operation_config = operation_config

    @property
    def _datastore_operation(self) -> _ScopeDependentOperations:
        return self._operation_container.all_operations[AzureMLResourceType.DATASTORE]

    @property
    def _code_assets(self) -> _ScopeDependentOperations:
        return self._operation_container.all_operations[AzureMLResourceType.CODE]

    @property
    def _model(self) -> _ScopeDependentOperations:
        return self._operation_container.all_operations[AzureMLResourceType.MODEL]

    @property
    def _environments(self) -> _ScopeDependentOperations:
        return self._operation_container.all_operations[AzureMLResourceType.ENVIRONMENT]

    @property
    def _data(self) -> _ScopeDependentOperations:
        return self._operation_container.all_operations[AzureMLResourceType.DATA]

    @property
    def _component(self) -> _ScopeDependentOperations:
        return self._operation_container.all_operations[AzureMLResourceType.COMPONENT]

    @property
    def _virtual_cluster(self) -> _ScopeDependentOperations:
        return self._operation_container.all_operations[AzureMLResourceType.VIRTUALCLUSTER]

    def get_asset_arm_id(
        self,
        asset: Optional[Union[str, Asset]],
        azureml_type: str,
        register_asset: bool = True,
        sub_workspace_resource: bool = True,
    ) -> Optional[Union[str, Asset]]:
        """This method converts AzureML Id to ARM Id. Or if the given asset is entity object, it tries to
        register/upload the asset based on register_asset and azureml_type.

        :param asset: The asset to resolve/register. It can be a ARM id or a entity's object.
        :type asset: Optional[Union[str, Asset]]
        :param azureml_type: The AzureML resource type. Defined in AzureMLResourceType.
        :type azureml_type: str
        :param register_asset: Indicates if the asset should be registered, defaults to True.
        :type register_asset: Optional[bool]
        :param sub_workspace_resource:
        :type sub_workspace_resource: Optional[bool]
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if asset's ID cannot be converted
            or asset cannot be successfully registered.
        :return: The ARM Id or entity object
        :rtype: Optional[Union[str, ~azure.ai.ml.entities.Asset]]
        """
        # pylint: disable=too-many-return-statements, too-many-branches
        if (
            asset is None
            or is_ARM_id_for_resource(asset, azureml_type, sub_workspace_resource)
            or is_registry_id_for_resource(asset)
            or is_singularity_id_for_resource(asset)
        ):
            return asset
        if is_singularity_full_name_for_resource(asset):
            return self._get_singularity_arm_id_from_full_name(str(asset))
        if is_singularity_short_name_for_resource(asset):
            return self._get_singularity_arm_id_from_short_name(str(asset))
        if isinstance(asset, str):
            if azureml_type in AzureMLResourceType.NAMED_TYPES:
                return NAMED_RESOURCE_ID_FORMAT.format(
                    self._operation_scope.subscription_id,
                    self._operation_scope.resource_group_name,
                    AZUREML_RESOURCE_PROVIDER,
                    self._operation_scope.workspace_name,
                    azureml_type,
                    asset,
                )
            if azureml_type in AzureMLResourceType.VERSIONED_TYPES:
                # Short form of curated env will be expanded on the backend side.
                # CLI strips off azureml: in the schema, appending it back as required by backend
                if azureml_type == AzureMLResourceType.ENVIRONMENT:
                    azureml_prefix = "azureml:"
                    # return the same value if resolved result is passed in
                    _asset = asset[len(azureml_prefix) :] if asset.startswith(azureml_prefix) else asset
                    if _asset.startswith(CURATED_ENV_PREFIX) or re.match(
                        REGISTRY_VERSION_PATTERN, f"{azureml_prefix}{_asset}"
                    ):
                        return f"{azureml_prefix}{_asset}"

                name, label = parse_name_label(asset)
                # TODO: remove this condition after label is fully supported for all versioned resources
                if label == DEFAULT_LABEL_NAME and azureml_type == AzureMLResourceType.COMPONENT:
                    return LABELLED_RESOURCE_ID_FORMAT.format(
                        self._operation_scope.subscription_id,
                        self._operation_scope.resource_group_name,
                        AZUREML_RESOURCE_PROVIDER,
                        self._operation_scope.workspace_name,
                        azureml_type,
                        name,
                        label,
                    )
                name, version = self._resolve_name_version_from_name_label(asset, azureml_type)
                if not version:
                    name, version = parse_prefixed_name_version(asset)

                if not version:
                    msg = (
                        "Failed to extract version when parsing asset {} of type {} as arm id. "
                        "Version must be provided."
                    )
                    raise ValidationException(
                        message=msg.format(asset, azureml_type),
                        target=ErrorTarget.ASSET,
                        no_personal_data_message=msg.format("", azureml_type),
                        error_category=ErrorCategory.USER_ERROR,
                        error_type=ValidationErrorType.MISSING_FIELD,
                    )
                if self._operation_scope.registry_name:
                    # Short form for env not supported with registry flow except when it's a curated env.
                    # Adding a graceful error message for the scenario
                    if not asset.startswith(CURATED_ENV_PREFIX):
                        msg = (
                            "Use fully qualified name to reference custom environments "
                            "when creating assets in registry. "
                            "The syntax for fully qualified names is "
                            "azureml://registries/azureml/environments/{{env-name}}/versions/{{version}}"
                        )
                        raise ValidationException(
                            message=msg.format(asset, azureml_type),
                            target=ErrorTarget.ASSET,
                            no_personal_data_message=msg.format("", azureml_type),
                            error_category=ErrorCategory.USER_ERROR,
                            error_type=ValidationErrorType.INVALID_VALUE,
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
            msg = "Unsupported azureml type {} for asset: {}"
            raise ValidationException(
                message=msg.format(azureml_type, asset),
                target=ErrorTarget.ASSET,
                no_personal_data_message=msg.format(azureml_type, ""),
                error_type=ValidationErrorType.INVALID_VALUE,
            )
        if isinstance(asset, Asset):
            try:
                result: Any = None
                # TODO: once the asset redesign is finished, this logic can be replaced with unified API
                if azureml_type == AzureMLResourceType.CODE and isinstance(asset, Code):
                    result = self._get_code_asset_arm_id(asset, register_asset=register_asset)
                elif azureml_type == AzureMLResourceType.ENVIRONMENT and isinstance(asset, Environment):
                    result = self._get_environment_arm_id(asset, register_asset=register_asset)
                elif azureml_type == AzureMLResourceType.MODEL and isinstance(asset, Model):
                    result = self._get_model_arm_id(asset, register_asset=register_asset)
                elif azureml_type == AzureMLResourceType.DATA and isinstance(asset, Data):
                    result = self._get_data_arm_id(asset, register_asset=register_asset)
                elif azureml_type == AzureMLResourceType.COMPONENT and isinstance(asset, Component):
                    result = self._get_component_arm_id(asset)
                else:
                    msg = "Unsupported azureml type {} for asset: {}"
                    raise ValidationException(
                        message=msg.format(azureml_type, asset),
                        target=ErrorTarget.ASSET,
                        no_personal_data_message=msg.format(azureml_type, ""),
                        error_category=ErrorCategory.USER_ERROR,
                        error_type=ValidationErrorType.INVALID_VALUE,
                    )
            except EmptyDirectoryError as e:
                msg = f"Error creating {azureml_type} asset : {e.message}"
                raise AssetException(
                    message=msg.format(azureml_type, e.message),
                    target=ErrorTarget.ASSET,
                    no_personal_data_message=msg.format(azureml_type, ""),
                    error=e,
                    error_category=ErrorCategory.SYSTEM_ERROR,
                ) from e
            return result
        msg = f"Error creating {azureml_type} asset: must be type Optional[Union[str, Asset]]"
        raise ValidationException(
            message=msg,
            target=ErrorTarget.ASSET,
            no_personal_data_message=msg,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.INVALID_VALUE,
        )

    def _get_code_asset_arm_id(self, code_asset: Code, register_asset: bool = True) -> Union[Code, str]:
        try:
            self._validate_datastore_name(code_asset.path)
            if register_asset:
                code_asset = self._code_assets.create_or_update(code_asset)  # type: ignore[attr-defined]
                return str(code_asset.id)
            sas_info = get_storage_info_for_non_registry_asset(
                service_client=self._code_assets._service_client,  # type: ignore[attr-defined]
                workspace_name=self._operation_scope.workspace_name,
                name=code_asset.name,
                version=code_asset.version,
                resource_group=self._operation_scope.resource_group_name,
            )
            uploaded_code_asset, _ = _check_and_upload_path(
                artifact=code_asset,
                asset_operations=self._code_assets,  # type: ignore[arg-type]
                artifact_type=ErrorTarget.CODE,
                show_progress=self._operation_config.show_progress,
                sas_uri=sas_info["sas_uri"],
                blob_uri=sas_info["blob_uri"],
            )
            uploaded_code_asset._id = get_arm_id_with_version(
                self._operation_scope,
                AzureMLResourceType.CODE,
                code_asset.name,
                code_asset.version,
            )
            return uploaded_code_asset
        except (MlException, HttpResponseError) as e:
            raise e
        except Exception as e:
            raise AssetException(
                message=f"Error with code: {e}",
                target=ErrorTarget.ASSET,
                no_personal_data_message="Error getting code asset",
                error=e,
                error_category=ErrorCategory.SYSTEM_ERROR,
            ) from e

    def _get_environment_arm_id(self, environment: Environment, register_asset: bool = True) -> Union[str, Environment]:
        if register_asset:
            if environment.id:
                return environment.id
            env_response = self._environments.create_or_update(environment)  # type: ignore[attr-defined]
            return env_response.id
        environment = _check_and_upload_env_build_context(
            environment=environment,
            operations=self._environments,  # type: ignore[arg-type]
            show_progress=self._operation_config.show_progress,
        )
        environment._id = get_arm_id_with_version(
            self._operation_scope,
            AzureMLResourceType.ENVIRONMENT,
            environment.name,
            environment.version,
        )
        return environment

    def _get_model_arm_id(self, model: Model, register_asset: bool = True) -> Union[str, Model]:
        try:
            self._validate_datastore_name(model.path)

            if register_asset:
                if model.id:
                    return model.id
                return self._model.create_or_update(model).id  # type: ignore[attr-defined]
            uploaded_model, _ = _check_and_upload_path(
                artifact=model,
                asset_operations=self._model,  # type: ignore[arg-type]
                artifact_type=ErrorTarget.MODEL,
                show_progress=self._operation_config.show_progress,
            )
            uploaded_model._id = get_arm_id_with_version(
                self._operation_scope,
                AzureMLResourceType.MODEL,
                model.name,
                model.version,
            )
            return uploaded_model
        except (MlException, HttpResponseError) as e:
            raise e
        except Exception as e:
            raise ModelException(
                message=f"Error with model: {e}",
                target=ErrorTarget.MODEL,
                no_personal_data_message="Error getting model",
                error=e,
                error_category=ErrorCategory.SYSTEM_ERROR,
            ) from e

    def _get_data_arm_id(self, data_asset: Data, register_asset: bool = True) -> Union[str, Data]:
        self._validate_datastore_name(data_asset.path)

        if register_asset:
            return self._data.create_or_update(data_asset).id  # type: ignore[attr-defined]
        data_asset, _ = _check_and_upload_path(
            artifact=data_asset,
            asset_operations=self._data,  # type: ignore[arg-type]
            artifact_type=ErrorTarget.DATA,
            show_progress=self._operation_config.show_progress,
        )
        return data_asset

    def _get_component_arm_id(self, component: Component) -> str:
        """Gets the component ARM ID.

        :param component: The component
        :type component: Component
        :return: The component id
        :rtype: str
        """

        # If component arm id is already resolved, return the id otherwise get arm id via remote call.
        # Register the component if necessary, and FILL BACK the arm id to component to reduce remote call.
        if not component.id:
            component._id = self._component.create_or_update(  # type: ignore[attr-defined]
                component, is_anonymous=True, show_progress=self._operation_config.show_progress
            ).id
        return str(component.id)

    def _get_singularity_arm_id_from_full_name(self, singularity: str) -> str:
        match = re.match(SINGULARITY_FULL_NAME_REGEX_FORMAT, singularity)
        subscription_id = match.group("subscription_id") if match is not None else ""
        resource_group_name = match.group("resource_group_name") if match is not None else ""
        vc_name = match.group("name") if match is not None else ""
        arm_id = SINGULARITY_ID_FORMAT.format(subscription_id, resource_group_name, vc_name)
        vc = self._virtual_cluster.get(arm_id)  # type: ignore[attr-defined]
        return str(vc["id"])

    def _get_singularity_arm_id_from_short_name(self, singularity: str) -> str:
        match = re.match(SINGULARITY_SHORT_NAME_REGEX_FORMAT, singularity)
        vc_name = match.group("name") if match is not None else ""
        # below list operation can be time-consuming, may need an optimization on this
        match_vcs = [vc for vc in self._virtual_cluster.list() if vc["name"] == vc_name]  # type: ignore[attr-defined]
        num_match_vc = len(match_vcs)
        if num_match_vc != 1:
            if num_match_vc == 0:
                msg = "The virtual cluster {} could not be found."
            else:
                msg = "More than one match virtual clusters {} found."
            raise ValidationException(
                message=msg.format(vc_name),
                no_personal_data_message=msg.format(""),
                target=ErrorTarget.COMPUTE,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
        return str(match_vcs[0]["id"])

    def _resolve_name_version_from_name_label(self, aml_id: str, azureml_type: str) -> Tuple[str, Optional[str]]:
        """Given an AzureML id of the form name@label, resolves the label to the actual ID.

        :param aml_id: AzureML id of the form name@label
        :type aml_id: str
        :param azureml_type: The AzureML resource type. Defined in AzureMLResourceType.
        :type azureml_type: str
        :return: Returns tuple (name, version) on success, (name@label, None) if resolution fails
        :rtype: Tuple[str, Optional[str]]
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
            _resolve_label_to_asset(
                self._operation_container.all_operations[azureml_type],
                name,
                label=label,
            ).version,
        )

    # pylint: disable=unused-argument
    def resolve_azureml_id(self, arm_id: Optional[str] = None, **kwargs: Any) -> Optional[str]:
        """This function converts ARM id to name or name:version AzureML id. It parses the ARM id and matches the
        subscription Id, resource group name and workspace_name.

        TODO: It is debatable whether this method should be in operation_orchestrator.

        :param arm_id: entity's ARM id, defaults to None
        :type arm_id: str
        :return: AzureML id
        :rtype: str
        """

        if arm_id:
            if not isinstance(arm_id, str):
                msg = "arm_id cannot be resolved: str expected but got {}".format(type(arm_id))  # type: ignore
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.GENERAL,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )
            try:
                arm_id_obj = AMLVersionedArmId(arm_id)
                if arm_id_obj.is_registry_id:
                    return arm_id
                if self._match(arm_id_obj):
                    return str(VERSIONED_RESOURCE_NAME.format(arm_id_obj.asset_name, arm_id_obj.asset_version))
            except ValidationException:
                pass  # fall back to named arm id
            try:
                arm_id_obj = AMLLabelledArmId(arm_id)
                if self._match(arm_id_obj):
                    return str(LABELLED_RESOURCE_NAME.format(arm_id_obj.asset_name, arm_id_obj.asset_label))
            except ValidationException:
                pass  # fall back to named arm id
            try:
                arm_id_obj = AMLNamedArmId(arm_id)
                if self._match(arm_id_obj):
                    return str(arm_id_obj.asset_name)
            except ValidationException:
                pass  # fall back to be not a ARM_id
        return arm_id

    def _match(self, id_: Any) -> bool:
        return bool(
            (
                id_.subscription_id == self._operation_scope.subscription_id
                and id_.resource_group_name == self._operation_scope.resource_group_name
                and id_.workspace_name == self._operation_scope.workspace_name
            )
        )

    def _validate_datastore_name(self, datastore_uri: Optional[Union[str, PathLike]]) -> None:
        if datastore_uri:
            try:
                if isinstance(datastore_uri, str):
                    if datastore_uri.startswith(FILE_PREFIX):
                        datastore_uri = datastore_uri[len(FILE_PREFIX) :]
                    elif datastore_uri.startswith(FOLDER_PREFIX):
                        datastore_uri = datastore_uri[len(FOLDER_PREFIX) :]
                elif isinstance(datastore_uri, PathLike):
                    return

                if datastore_uri.startswith(HTTPS_PREFIX) and datastore_uri.count("/") == 7:
                    # only long-form (i.e. "https://x.blob.core.windows.net/datastore/LocalUpload/guid/x/x")
                    # format includes datastore
                    datastore_name = datastore_uri.split("/")[3]
                elif datastore_uri.startswith(ARM_ID_PREFIX) and not (
                    re.match(MLFLOW_URI_REGEX_FORMAT, datastore_uri) or re.match(JOB_URI_REGEX_FORMAT, datastore_uri)
                ):
                    datastore_name = AzureMLDatastorePathUri(datastore_uri).datastore
                else:
                    # local path
                    return

                if datastore_name.startswith(ARM_ID_PREFIX):
                    datastore_name = datastore_name[len(ARM_ID_PREFIX) :]

                self._datastore_operation.get(datastore_name)  # type: ignore[attr-defined]
            except ResourceNotFoundError as e:
                msg = "The datastore {} could not be found in this workspace."
                raise ValidationException(
                    message=msg.format(datastore_name),
                    target=ErrorTarget.DATASTORE,
                    no_personal_data_message=msg.format(""),
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.RESOURCE_NOT_FOUND,
                ) from e


class _AssetResolver(Protocol):
    """Describes the type of a function used by operation classes like :py:class:`JobOperations` and
    :py:class:`ComponentOperations` to resolve Assets

    .. see-also:: methods :py:method:`OperationOrchestrator.get_asset_arm_id`,
            :py:method:`OperationOrchestrator.resolve_azureml_id`

    """

    def __call__(
        self,
        asset: Optional[Union[str, Asset]],
        azureml_type: str,
        register_asset: bool = True,
        sub_workspace_resource: bool = True,
    ) -> Optional[Union[str, Asset]]:
        """Resolver function

        :param asset: The asset to resolve/register. It can be a ARM id or a entity's object.
        :type asset: Optional[Union[str, Asset]]
        :param azureml_type: The AzureML resource type. Defined in AzureMLResourceType.
        :type azureml_type: str
        :param register_asset: Indicates if the asset should be registered, defaults to True.
        :type register_asset: Optional[bool]
        :param sub_workspace_resource:
        :type sub_workspace_resource: Optional[bool]
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if asset's ID cannot be converted
            or asset cannot be successfully registered.
        :return: The ARM Id or entity object
        :rtype: Optional[Union[str, ~azure.ai.ml.entities.Asset]]
        """
