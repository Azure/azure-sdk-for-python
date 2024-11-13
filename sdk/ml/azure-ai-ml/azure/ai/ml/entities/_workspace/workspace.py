# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes

from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Dict, List, Optional, Tuple, Type, Union

from azure.ai.ml._restclient.v2024_07_01_preview.models import (
    FeatureStoreSettings as RestFeatureStoreSettings,
    ManagedNetworkSettings as RestManagedNetwork,
    ManagedServiceIdentity as RestManagedServiceIdentity,
    ServerlessComputeSettings as RestServerlessComputeSettings,
    Workspace as RestWorkspace,
)
from azure.ai.ml._schema.workspace.workspace import WorkspaceSchema
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.constants._common import (
    BASE_PATH_CONTEXT_KEY,
    PARAMS_OVERRIDE_KEY,
    CommonYamlFields,
    WorkspaceKind,
    WorkspaceResourceConstants,
)
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._util import find_field_in_override, load_from_dict
from azure.ai.ml.entities._workspace.serverless_compute import ServerlessComputeSettings
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from .customer_managed_key import CustomerManagedKey
from .feature_store_settings import FeatureStoreSettings
from .networking import ManagedNetwork


class Workspace(Resource):
    """Azure ML workspace.

    :param name: Name of the workspace.
    :type name: str
    :param description: Description of the workspace.
    :type description: str
    :param tags: Tags of the workspace.
    :type tags: dict
    :param display_name: Display name for the workspace. This is non-unique within the resource group.
    :type display_name: str
    :param location: The location to create the workspace in.
        If not specified, the same location as the resource group will be used.
    :type location: str
    :param resource_group: Name of resource group to create the workspace in.
    :type resource_group: str
    :param hbi_workspace: Whether the customer data is of high business impact (HBI),
        containing sensitive business information.
        For more information, see
        https://docs.microsoft.com/azure/machine-learning/concept-data-encryption#encryption-at-rest.
    :type hbi_workspace: bool
    :param storage_account: The resource ID of an existing storage account to use instead of creating a new one.
    :type storage_account: str
    :param container_registry: The resource ID of an existing container registry
        to use instead of creating a new one.
    :type container_registry: str
    :param key_vault: The resource ID of an existing key vault to use instead of creating a new one.
    :type key_vault: str
    :param application_insights: The resource ID of an existing application insights
        to use instead of creating a new one.
    :type application_insights: str
    :param customer_managed_key: Key vault details for encrypting data with customer-managed keys.
        If not specified, Microsoft-managed keys will be used by default.
    :type customer_managed_key: ~azure.ai.ml.entities.CustomerManagedKey
    :param image_build_compute: The name of the compute target to use for building environment
        Docker images with the container registry is behind a VNet.
    :type image_build_compute: str
    :param public_network_access: Whether to allow public endpoint connectivity
        when a workspace is private link enabled.
    :type public_network_access: str
    :param identity: workspace's Managed Identity (user assigned, or system assigned)
    :type identity: ~azure.ai.ml.entities.IdentityConfiguration
    :param primary_user_assigned_identity: The workspace's primary user assigned identity
    :type primary_user_assigned_identity: str
    :param managed_network: workspace's Managed Network configuration
    :type managed_network: ~azure.ai.ml.entities.ManagedNetwork
    :param system_datastores_auth_mode: The authentication mode for system datastores.
    :type system_datastores_auth_mode: str
    :param enable_data_isolation: A flag to determine if workspace has data isolation enabled.
        The flag can only be set at the creation phase, it can't be updated.
    :type enable_data_isolation: bool
    :param allow_roleassignment_on_rg: Determine whether allow workspace role assignment on resource group level.
    :type allow_roleassignment_on_rg: Optional[bool]
    :param serverless_compute: The serverless compute settings for the workspace.
    :type: ~azure.ai.ml.entities.ServerlessComputeSettings
    :param workspace_hub: Deprecated resource ID of an existing workspace hub to help create project workspace.
        Use the Project class instead now.
    :type workspace_hub: Optional[str]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict

    .. literalinclude:: ../samples/ml_samples_workspace.py
            :start-after: [START workspace]
            :end-before: [END workspace]
            :language: python
            :dedent: 8
            :caption: Creating a Workspace object.
    """

    def __init__(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        display_name: Optional[str] = None,
        location: Optional[str] = None,
        resource_group: Optional[str] = None,
        hbi_workspace: bool = False,
        storage_account: Optional[str] = None,
        container_registry: Optional[str] = None,
        key_vault: Optional[str] = None,
        application_insights: Optional[str] = None,
        customer_managed_key: Optional[CustomerManagedKey] = None,
        image_build_compute: Optional[str] = None,
        public_network_access: Optional[str] = None,
        identity: Optional[IdentityConfiguration] = None,
        primary_user_assigned_identity: Optional[str] = None,
        managed_network: Optional[ManagedNetwork] = None,
        system_datastores_auth_mode: Optional[str] = None,
        enable_data_isolation: bool = False,
        allow_roleassignment_on_rg: Optional[bool] = None,
        hub_id: Optional[str] = None,  # Hidden input, surfaced by Project
        workspace_hub: Optional[str] = None,  # Deprecated input maintained for backwards compat.
        serverless_compute: Optional[ServerlessComputeSettings] = None,
        **kwargs: Any,
    ):
        # Workspaces have subclasses that are differentiated by the 'kind' field in the REST API.
        # Now that this value is occasionally surfaced (for sub-class YAML specifications)
        # We've switched to using 'type' in the SDK for consistency's sake with other polymorphic classes.
        # That said, the code below but quietly supports 'kind' as an input
        # to maintain backwards compatibility with internal systems that I suspect still use 'kind' somewhere.
        # 'type' takes precedence over 'kind' if they're both set, and this defaults to a normal workspace's type
        # if nothing is set.
        self._kind = kwargs.pop("kind", None)
        if self._kind is None:
            self._kind = WorkspaceKind.DEFAULT

        self.print_as_yaml = True
        self._discovery_url: Optional[str] = kwargs.pop("discovery_url", None)
        self._mlflow_tracking_uri: Optional[str] = kwargs.pop("mlflow_tracking_uri", None)
        self._workspace_id = kwargs.pop("workspace_id", None)
        self._feature_store_settings: Optional[FeatureStoreSettings] = kwargs.pop("feature_store_settings", None)
        super().__init__(name=name, description=description, tags=tags, **kwargs)

        self.display_name = display_name
        self.location = location
        self.resource_group = resource_group
        self.hbi_workspace = hbi_workspace
        self.storage_account = storage_account
        self.container_registry = container_registry
        self.key_vault = key_vault
        self.application_insights = application_insights
        self.customer_managed_key = customer_managed_key
        self.image_build_compute = image_build_compute
        self.public_network_access = public_network_access
        self.identity = identity
        self.primary_user_assigned_identity = primary_user_assigned_identity
        self.managed_network = managed_network
        self.system_datastores_auth_mode = system_datastores_auth_mode
        self.enable_data_isolation = enable_data_isolation
        self.allow_roleassignment_on_rg = allow_roleassignment_on_rg
        if workspace_hub and not hub_id:
            hub_id = workspace_hub
        self.__hub_id = hub_id
        # Overwrite kind if hub_id is provided. Technically not needed anymore,
        # but kept for backwards if people try to just use a normal workspace like
        # a project.
        if hub_id:
            self._kind = WorkspaceKind.PROJECT
        self.serverless_compute: Optional[ServerlessComputeSettings] = serverless_compute

    @property
    def discovery_url(self) -> Optional[str]:
        """Backend service base URLs for the workspace.

        :return: Backend service URLs of the workspace
        :rtype: str
        """
        return self._discovery_url

    # Exists to appease tox's mypy rules.
    @property
    def _hub_id(self) -> Optional[str]:
        """The UID of the hub parent of the project. This is an internal property
        that's surfaced by the Project sub-class, but exists here for backwards-compatibility
        reasons.

        :return: Resource ID of the parent hub.
        :rtype: str
        """
        return self.__hub_id

    # Exists to appease tox's mypy rules.
    @_hub_id.setter
    def _hub_id(self, value: str):
        """Set the hub of the project. This is an internal property
        that's surfaced by the Project sub-class, but exists here for backwards-compatibility
        reasons.


        :param value: The hub id to assign to the project.
            Note: cannot be reassigned after creation.
        :type value: str
        """
        if not value:
            return
        self.__hub_id = value

    @property
    def mlflow_tracking_uri(self) -> Optional[str]:
        """MLflow tracking uri for the workspace.

        :return: Returns mlflow tracking uri of the workspace.
        :rtype: str
        """
        return self._mlflow_tracking_uri

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs: Any) -> None:
        """Dump the workspace spec into a file in yaml format.

        :param dest: The destination to receive this workspace's spec.
            Must be either a path to a local file, or an already-open file stream.
            If dest is a file path, a new file will be created,
            and an exception is raised if the file exists.
            If dest is an open file, the file will be written to directly,
            and an exception will be raised if the file is not writable.
        :type dest: Union[PathLike, str, IO[AnyStr]]
        """
        path = kwargs.pop("path", None)
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, path=path, **kwargs)

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        res: dict = self._get_schema_class()(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res

    @classmethod
    def _resolve_sub_cls_and_kind(
        cls, data: Dict, params_override: Optional[List[Dict]] = None
    ) -> Tuple[Type["Workspace"], str]:
        """Given a workspace data dictionary, determine the appropriate workspace class and type string.
        Allows for easier polymorphism between the workspace class and its children.
        Adapted from similar code in the Job class.

        :param data: A dictionary of values describing the workspace.
        :type data: Dict
        :param params_override: Override values from alternative sources (ex: CLI input).
        :type params_override: Optional[List[Dict]]
        :return: A tuple containing the workspace class and type string.
        :rtype: Tuple[Type["Workspace"], str]
        """
        from azure.ai.ml.entities import Hub, Project

        workspace_class: Optional[Type["Workspace"]] = None
        type_in_override = find_field_in_override(CommonYamlFields.KIND, params_override)
        type_str = type_in_override or data.get(CommonYamlFields.KIND, WorkspaceKind.DEFAULT)
        if type_str is not None:
            type_str = type_str.lower()
        if type_str == WorkspaceKind.HUB:
            workspace_class = Hub
        elif type_str == WorkspaceKind.PROJECT:
            workspace_class = Project
        elif type_str == WorkspaceKind.DEFAULT:
            workspace_class = Workspace
        else:
            msg = f"Unsupported workspace type: {type_str}."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.WORKSPACE,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
        return workspace_class, type_str

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "Workspace":
        # This _load function is polymorphic and can return child classes.
        # It was adapted from the Job class's similar function.
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        workspace_class, type_str = cls._resolve_sub_cls_and_kind(data, params_override)
        schema_type = workspace_class._get_schema_class()  # pylint: disable=protected-access
        loaded_schema = load_from_dict(
            schema_type,
            data=data,
            context=context,
            additional_message=f"If you are trying to configure a workspace that is not of type {type_str},"
            f" please specify the correct job type in the 'type' property.",
            **kwargs,
        )
        result = workspace_class(**loaded_schema)
        if yaml_path:
            result._source_path = yaml_path  # pylint: disable=protected-access
        return result

    @classmethod
    def _from_rest_object(
        cls, rest_obj: RestWorkspace, v2_service_context: Optional[object] = None
    ) -> Optional["Workspace"]:

        if not rest_obj:
            return None
        customer_managed_key = (
            CustomerManagedKey(
                key_vault=rest_obj.encryption.key_vault_properties.key_vault_arm_id,
                key_uri=rest_obj.encryption.key_vault_properties.key_identifier,
            )
            if rest_obj.encryption
            and rest_obj.encryption.status == WorkspaceResourceConstants.ENCRYPTION_STATUS_ENABLED
            else None
        )

        # TODO: Remove attribute check once Oct API version is out
        mlflow_tracking_uri = None

        if hasattr(rest_obj, "ml_flow_tracking_uri"):
            try:
                if v2_service_context:
                    # v2_service_context is required (not None) in get_mlflow_tracking_uri_v2
                    from azureml.mlflow import get_mlflow_tracking_uri_v2

                    mlflow_tracking_uri = get_mlflow_tracking_uri_v2(rest_obj, v2_service_context)
                else:
                    mlflow_tracking_uri = rest_obj.ml_flow_tracking_uri
            except ImportError:
                mlflow_tracking_uri = rest_obj.ml_flow_tracking_uri
                error_msg = (
                    "azureml.mlflow could not be imported. "
                    "Please ensure that latest 'azureml-mlflow' has been installed in the current python environment"
                )
                print(error_msg)
                # warnings.warn(error_msg, UserWarning)

        # TODO: Remove once Online Endpoints updates API version to at least 2023-08-01
        allow_roleassignment_on_rg = None
        if hasattr(rest_obj, "allow_role_assignment_on_rg"):
            allow_roleassignment_on_rg = rest_obj.allow_role_assignment_on_rg
        system_datastores_auth_mode = None
        if hasattr(rest_obj, "system_datastores_auth_mode"):
            system_datastores_auth_mode = rest_obj.system_datastores_auth_mode

        # TODO: remove this once it is included in API response
        managed_network = None
        if hasattr(rest_obj, "managed_network"):
            if rest_obj.managed_network and isinstance(rest_obj.managed_network, RestManagedNetwork):
                managed_network = ManagedNetwork._from_rest_object(  # pylint: disable=protected-access
                    rest_obj.managed_network
                )

        armid_parts = str(rest_obj.id).split("/")
        group = None if len(armid_parts) < 4 else armid_parts[4]
        identity = None
        if rest_obj.identity and isinstance(rest_obj.identity, RestManagedServiceIdentity):
            identity = IdentityConfiguration._from_workspace_rest_object(  # pylint: disable=protected-access
                rest_obj.identity
            )
        feature_store_settings = None
        if rest_obj.feature_store_settings and isinstance(rest_obj.feature_store_settings, RestFeatureStoreSettings):
            feature_store_settings = FeatureStoreSettings._from_rest_object(  # pylint: disable=protected-access
                rest_obj.feature_store_settings
            )
        serverless_compute = None
        # TODO: Remove attribute check once serverless_compute_settings is in API response contract
        if hasattr(rest_obj, "serverless_compute_settings"):
            if rest_obj.serverless_compute_settings and isinstance(
                rest_obj.serverless_compute_settings, RestServerlessComputeSettings
            ):
                serverless_compute = ServerlessComputeSettings._from_rest_object(  # pylint: disable=protected-access
                    rest_obj.serverless_compute_settings
                )

        return cls(
            name=rest_obj.name,
            id=rest_obj.id,
            description=rest_obj.description,
            kind=rest_obj.kind.lower() if rest_obj.kind else None,
            tags=rest_obj.tags,
            location=rest_obj.location,
            resource_group=group,
            display_name=rest_obj.friendly_name,
            discovery_url=rest_obj.discovery_url,
            hbi_workspace=rest_obj.hbi_workspace,
            storage_account=rest_obj.storage_account,
            container_registry=rest_obj.container_registry,
            key_vault=rest_obj.key_vault,
            application_insights=rest_obj.application_insights,
            customer_managed_key=customer_managed_key,
            image_build_compute=rest_obj.image_build_compute,
            public_network_access=rest_obj.public_network_access,
            mlflow_tracking_uri=mlflow_tracking_uri,
            identity=identity,
            primary_user_assigned_identity=rest_obj.primary_user_assigned_identity,
            managed_network=managed_network,
            system_datastores_auth_mode=system_datastores_auth_mode,
            feature_store_settings=feature_store_settings,
            enable_data_isolation=rest_obj.enable_data_isolation,
            allow_roleassignment_on_rg=allow_roleassignment_on_rg,
            hub_id=rest_obj.hub_resource_id,
            workspace_id=rest_obj.workspace_id,
            serverless_compute=serverless_compute,
        )

    def _to_rest_object(self) -> RestWorkspace:
        """Note: Unlike most entities, the create operation for workspaces does NOTE use this function,
        and instead relies on its own internal conversion process to produce a valid ARM template.

        :return: The REST API object-equivalent of this workspace.
        :rtype: RestWorkspace
        """
        feature_store_settings = None
        if self._feature_store_settings:
            feature_store_settings = self._feature_store_settings._to_rest_object()  # pylint: disable=protected-access

        serverless_compute_settings = None
        if self.serverless_compute:
            serverless_compute_settings = self.serverless_compute._to_rest_object()  # pylint: disable=protected-access
        return RestWorkspace(
            name=self.name,
            identity=(
                self.identity._to_workspace_rest_object() if self.identity else None  # pylint: disable=protected-access
            ),
            location=self.location,
            tags=self.tags,
            description=self.description,
            kind=self._kind,
            friendly_name=self.display_name,
            key_vault=self.key_vault,
            application_insights=self.application_insights,
            container_registry=self.container_registry,
            storage_account=self.storage_account,
            discovery_url=self.discovery_url,
            hbi_workspace=self.hbi_workspace,
            image_build_compute=self.image_build_compute,
            public_network_access=self.public_network_access,
            primary_user_assigned_identity=self.primary_user_assigned_identity,
            managed_network=(
                self.managed_network._to_rest_object()  # pylint: disable=protected-access
                if self.managed_network
                else None
            ),  # pylint: disable=protected-access
            system_datastores_auth_mode=self.system_datastores_auth_mode,
            feature_store_settings=feature_store_settings,
            enable_data_isolation=self.enable_data_isolation,
            allow_role_assignment_on_rg=self.allow_roleassignment_on_rg,  # diff due to swagger restclient casing diff
            hub_resource_id=self._hub_id,
            serverless_compute_settings=serverless_compute_settings,
        )

    # Helper for sub-class polymorphism. Needs to be overwritten by child classes
    # If they don't want to redefine things like _to_dict.
    @classmethod
    def _get_schema_class(cls) -> Type[WorkspaceSchema]:
        return WorkspaceSchema
