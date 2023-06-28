# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import time
from typing import Callable, Dict, Optional, Tuple

from azure.ai.ml._arm_deployments import ArmDeploymentExecutor
from azure.ai.ml._arm_deployments.arm_helper import get_template
from azure.ai.ml._restclient.v2023_04_01_preview import AzureMachineLearningWorkspaces as ServiceClient042023Preview
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    EncryptionKeyVaultUpdateProperties,
    EncryptionUpdateProperties,
    WorkspaceUpdateParameters,
)
from azure.ai.ml.entities._workspace.networking import ManagedNetwork
from azure.ai.ml.constants._workspace import IsolationMode
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope

# from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._utils._workspace_utils import (
    delete_resource_by_arm_id,
    get_deployment_name,
    get_name_for_dependent_resource,
    get_resource_and_group_name,
    get_resource_group_location,
)
from azure.ai.ml._utils._appinsights_utils import get_log_analytics_arm_id
from azure.ai.ml._utils.utils import camel_to_snake, from_iso_duration_format_min_sec
from azure.ai.ml._version import VERSION
from azure.ai.ml.constants import ManagedServiceIdentityType
from azure.ai.ml.constants._common import ArmConstants, LROConfigurations, WorkspaceResourceConstants
from azure.ai.ml.entities import (
    Workspace,
)
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller, PollingMethod

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class WorkspaceOperationsBase:
    """Base class for WorkspaceOperations, can't be instantiated directly."""

    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: ServiceClient042023Preview,
        all_operations: OperationsContainer,
        credentials: Optional[TokenCredential] = None,
        **kwargs: Dict,
    ):
        # ops_logger.update_info(kwargs)
        self._subscription_id = operation_scope.subscription_id
        self._resource_group_name = operation_scope.resource_group_name
        self._default_workspace_name = operation_scope.workspace_name
        self._all_operations = all_operations
        self._operation = service_client.workspaces
        self._credentials = credentials
        self._init_kwargs = kwargs
        self.containerRegistry = "none"

    def get(self, workspace_name: Optional[str] = None, **kwargs: Dict) -> Workspace:
        workspace_name = self._check_workspace_name(workspace_name)
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        obj = self._operation.get(resource_group, workspace_name)
        return Workspace._from_rest_object(obj)

    def begin_create(
        self,
        workspace: Workspace,
        update_dependent_resources: bool = False,
        get_callback: Optional[Callable[[], Workspace]] = None,
        **kwargs: Dict,
    ) -> LROPoller[Workspace]:
        existing_workspace = None
        resource_group = kwargs.get("resource_group") or workspace.resource_group or self._resource_group_name
        try:
            existing_workspace = self.get(workspace.name, resource_group=resource_group)
        except Exception:  # pylint: disable=broad-except
            pass

        # idempotent behavior
        if existing_workspace:
            if workspace.tags.get("createdByToolkit") is not None:
                workspace.tags.pop("createdByToolkit")
            existing_workspace.tags.update(workspace.tags)
            workspace.tags = existing_workspace.tags
            workspace.container_registry = workspace.container_registry or existing_workspace.container_registry
            workspace.application_insights = workspace.application_insights or existing_workspace.application_insights
            workspace.identity = workspace.identity or existing_workspace.identity
            workspace.primary_user_assigned_identity = (
                workspace.primary_user_assigned_identity or existing_workspace.primary_user_assigned_identity
            )
            workspace._feature_store_settings = (
                workspace._feature_store_settings or existing_workspace._feature_store_settings
            )
            return self.begin_update(
                workspace,
                update_dependent_resources=update_dependent_resources,
                **kwargs,
            )
        # add tag in the workspace to indicate which sdk version the workspace is created from
        if workspace.tags is None:
            workspace.tags = {}
        if workspace.tags.get("createdByToolkit") is None:
            workspace.tags["createdByToolkit"] = "sdk-v2-{}".format(VERSION)

        workspace.resource_group = resource_group
        template, param, resources_being_deployed = self._populate_arm_paramaters(workspace, **kwargs)

        arm_submit = ArmDeploymentExecutor(
            credentials=self._credentials,
            resource_group_name=resource_group,
            subscription_id=self._subscription_id,
            deployment_name=get_deployment_name(workspace.name),
        )

        # deploy_resource() blocks for the poller to succeed if wait is True
        poller = arm_submit.deploy_resource(
            template=template,
            resources_being_deployed=resources_being_deployed,
            parameters=param,
            wait=False,
        )

        def callback():
            return get_callback() if get_callback else self.get(workspace.name, resource_group=resource_group)

        return LROPoller(
            self._operation._client,
            None,
            lambda *x, **y: None,
            CustomArmTemplateDeploymentPollingMethod(poller, arm_submit, callback),
        )

    def begin_update(
        self,
        workspace: Workspace,
        *,
        update_dependent_resources: bool = False,
        deserialize_callback: Optional[Callable[[], Workspace]] = None,
        **kwargs: Dict,
    ) -> LROPoller[Workspace]:
        identity = kwargs.get("identity", workspace.identity)
        workspace_name = kwargs.get("workspace_name", workspace.name)
        existing_workspace = self.get(workspace_name, **kwargs)
        if identity:
            identity = identity._to_workspace_rest_object()
            rest_user_assigned_identities = identity.user_assigned_identities
            # add the uai resource_id which needs to be deleted (which is not provided in the list)
            if (
                existing_workspace
                and existing_workspace.identity
                and existing_workspace.identity.user_assigned_identities
            ):
                if rest_user_assigned_identities is None:
                    rest_user_assigned_identities = {}
                for uai in existing_workspace.identity.user_assigned_identities:
                    if uai.resource_id not in rest_user_assigned_identities:
                        rest_user_assigned_identities[uai.resource_id] = None
                identity.user_assigned_identities = rest_user_assigned_identities

        managed_network = kwargs.get("managed_network", workspace.managed_network)
        if isinstance(managed_network, str):
            managed_network = ManagedNetwork(managed_network)._to_rest_object()
        elif isinstance(managed_network, ManagedNetwork):
            managed_network = workspace.managed_network._to_rest_object()

        container_registry = kwargs.get("container_registry", workspace.container_registry)
        # Empty string is for erasing the value of container_registry, None is to be ignored value
        if (
            container_registry is not None
            and container_registry != existing_workspace.container_registry
            and not update_dependent_resources
        ):
            msg = (
                "Updating the workspace-attached Azure Container Registry resource may break lineage of "
                "previous jobs or your ability to rerun earlier jobs in this workspace. "
                "Are you sure you want to perform this operation? "
                "Include the --update_dependent_resources/-u parameter with this request to confirm."
            )
            raise ValidationException(
                message=msg,
                target=ErrorTarget.WORKSPACE,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        application_insights = kwargs.get("application_insights", workspace.application_insights)
        # Empty string is for erasing the value of application_insights, None is to be ignored value
        if (
            application_insights is not None
            and application_insights != existing_workspace.application_insights
            and not update_dependent_resources
        ):
            msg = (
                "Updating the workspace-attached Azure Application Insights resource may break lineage "
                "of deployed inference endpoints this workspace. Are you sure you want to perform this "
                "operation? Include the --update_dependent_resources/-u parameter with this request to confirm."
            )
            raise ValidationException(
                message=msg,
                target=ErrorTarget.WORKSPACE,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )

        feature_store_settings = kwargs.get("feature_store_settings", workspace._feature_store_settings)
        if feature_store_settings:
            feature_store_settings = feature_store_settings._to_rest_object()

        update_param = WorkspaceUpdateParameters(
            tags=kwargs.get("tags", workspace.tags),
            description=kwargs.get("description", workspace.description),
            friendly_name=kwargs.get("display_name", workspace.display_name),
            public_network_access=kwargs.get("public_network_access", workspace.public_network_access),
            image_build_compute=kwargs.get("image_build_compute", workspace.image_build_compute),
            identity=identity,
            primary_user_assigned_identity=kwargs.get(
                "primary_user_assigned_identity", workspace.primary_user_assigned_identity
            ),
            managed_network=managed_network,
            feature_store_settings=feature_store_settings,
        )
        update_param.container_registry = container_registry or None
        update_param.application_insights = application_insights or None

        # Only the key uri property of customer_managed_key can be updated.
        # Check if user is updating CMK key uri, if so, add to update_param
        if workspace.customer_managed_key is not None and workspace.customer_managed_key.key_uri is not None:
            customer_managed_key_uri = workspace.customer_managed_key.key_uri
            update_param.encryption = EncryptionUpdateProperties(
                key_vault_properties=EncryptionKeyVaultUpdateProperties(
                    key_identifier=customer_managed_key_uri,
                )
            )

        resource_group = kwargs.get("resource_group") or workspace.resource_group or self._resource_group_name

        # pylint: disable=unused-argument
        def callback(_, deserialized, args):
            return (
                deserialize_callback(deserialized)
                if deserialize_callback
                else Workspace._from_rest_object(deserialized)
            )

        poller = self._operation.begin_update(resource_group, workspace_name, update_param, polling=True, cls=callback)
        return poller

    def begin_delete(
        self, name: str, *, delete_dependent_resources: bool, permanently_delete: bool = False, **kwargs: Dict
    ) -> LROPoller[None]:
        workspace = self.get(name, **kwargs)
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        if delete_dependent_resources:
            delete_resource_by_arm_id(
                self._credentials,
                self._subscription_id,
                workspace.application_insights,
                ArmConstants.AZURE_MGMT_APPINSIGHT_API_VERSION,
            )
            delete_resource_by_arm_id(
                self._credentials,
                self._subscription_id,
                workspace.storage_account,
                ArmConstants.AZURE_MGMT_STORAGE_API_VERSION,
            )
            delete_resource_by_arm_id(
                self._credentials,
                self._subscription_id,
                workspace.key_vault,
                ArmConstants.AZURE_MGMT_KEYVAULT_API_VERSION,
            )
            delete_resource_by_arm_id(
                self._credentials,
                self._subscription_id,
                workspace.container_registry,
                ArmConstants.AZURE_MGMT_CONTAINER_REG_API_VERSION,
            )
        poller = self._operation.begin_delete(
            resource_group_name=resource_group,
            workspace_name=name,
            force_to_purge=permanently_delete,
            **self._init_kwargs,
        )
        module_logger.info("Delete request initiated for workspace: %s\n", name)
        return poller

    # pylint: disable=too-many-statements,too-many-branches,too-many-locals
    def _populate_arm_paramaters(self, workspace: Workspace, **kwargs: Dict) -> Tuple[dict, dict, dict]:
        resources_being_deployed = {}
        if not workspace.location:
            workspace.location = get_resource_group_location(
                self._credentials, self._subscription_id, workspace.resource_group
            )

        template = get_template(resource_type=ArmConstants.WORKSPACE_BASE)
        param = get_template(resource_type=ArmConstants.WORKSPACE_PARAM)
        _set_val(param["workspaceName"], workspace.name)
        if not workspace.display_name:
            _set_val(param["friendlyName"], workspace.name)
        else:
            _set_val(param["friendlyName"], workspace.display_name)

        if not workspace.description:
            _set_val(param["description"], workspace.name)
        else:
            _set_val(param["description"], workspace.description)
        _set_val(param["location"], workspace.location)

        if not workspace._kind:
            _set_val(param["kind"], "default")
        else:
            _set_val(param["kind"], workspace._kind)

        _set_val(param["resourceGroupName"], workspace.resource_group)

        if workspace.key_vault:
            resource_name, group_name = get_resource_and_group_name(workspace.key_vault)
            _set_val(param["keyVaultName"], resource_name)
            _set_val(param["keyVaultOption"], "existing")
            _set_val(param["keyVaultResourceGroupName"], group_name)
        else:
            key_vault = _generate_key_vault(workspace.name, resources_being_deployed)
            _set_val(param["keyVaultName"], key_vault)
            _set_val(
                param["keyVaultResourceGroupName"],
                workspace.resource_group,
            )

        if workspace.storage_account:
            resource_name, group_name = get_resource_and_group_name(workspace.storage_account)
            _set_val(param["storageAccountName"], resource_name)
            _set_val(param["storageAccountOption"], "existing")
            _set_val(param["storageAccountResourceGroupName"], group_name)
        else:
            storage = _generate_storage(workspace.name, resources_being_deployed)
            _set_val(param["storageAccountName"], storage)
            _set_val(
                param["storageAccountResourceGroupName"],
                workspace.resource_group,
            )

        if workspace.application_insights:
            resource_name, group_name = get_resource_and_group_name(workspace.application_insights)
            _set_val(param["applicationInsightsName"], resource_name)
            _set_val(param["applicationInsightsOption"], "existing")
            _set_val(
                param["applicationInsightsResourceGroupName"],
                group_name,
            )
        else:
            log_analytics = _generate_log_analytics(workspace.name, resources_being_deployed)
            _set_val(param["logAnalyticsName"], log_analytics)
            _set_val(
                param["logAnalyticsArmId"],
                get_log_analytics_arm_id(self._subscription_id, self._resource_group_name, log_analytics),
            )

            app_insights = _generate_app_insights(workspace.name, resources_being_deployed)
            _set_val(param["applicationInsightsName"], app_insights)
            _set_val(
                param["applicationInsightsResourceGroupName"],
                workspace.resource_group,
            )

        if workspace.container_registry:
            resource_name, group_name = get_resource_and_group_name(workspace.container_registry)
            _set_val(param["containerRegistryName"], resource_name)
            _set_val(param["containerRegistryOption"], "existing")
            _set_val(param["containerRegistryResourceGroupName"], group_name)

        if workspace.customer_managed_key:
            _set_val(param["cmk_keyvault"], workspace.customer_managed_key.key_vault)
            _set_val(param["resource_cmk_uri"], workspace.customer_managed_key.key_uri)
            _set_val(
                param["encryption_status"],
                WorkspaceResourceConstants.ENCRYPTION_STATUS_ENABLED,
            )
            _set_val(
                param["encryption_cosmosdb_resourceid"],
                workspace.customer_managed_key.cosmosdb_id,
            )
            _set_val(
                param["encryption_storage_resourceid"],
                workspace.customer_managed_key.storage_id,
            )
            _set_val(
                param["encryption_search_resourceid"],
                workspace.customer_managed_key.search_id,
            )

        if workspace.hbi_workspace:
            _set_val(param["confidential_data"], "true")

        if workspace.public_network_access:
            _set_val(param["publicNetworkAccess"], workspace.public_network_access)

        if workspace.image_build_compute:
            _set_val(param["imageBuildCompute"], workspace.image_build_compute)

        if workspace.tags:
            for key, val in workspace.tags.items():
                param["tagValues"]["value"][key] = val

        identity = None
        if workspace.identity:
            identity = workspace.identity._to_workspace_rest_object()
        else:
            # pylint: disable=protected-access
            identity = IdentityConfiguration(
                type=camel_to_snake(ManagedServiceIdentityType.SYSTEM_ASSIGNED)
            )._to_workspace_rest_object()
        _set_val(param["identity"], identity)

        if workspace.primary_user_assigned_identity:
            _set_val(param["primaryUserAssignedIdentity"], workspace.primary_user_assigned_identity)

        if workspace._feature_store_settings:
            _set_val(
                param["spark_runtime_version"], workspace._feature_store_settings.compute_runtime.spark_runtime_version
            )
            _set_val(
                param["offline_store_connection_name"],
                workspace._feature_store_settings.offline_store_connection_name
                if workspace._feature_store_settings.offline_store_connection_name
                else "",
            )
            _set_val(
                param["online_store_connection_name"],
                workspace._feature_store_settings.online_store_connection_name
                if workspace._feature_store_settings.online_store_connection_name
                else "",
            )

        setup_materialization_store = False
        if workspace._kind and workspace._kind.lower() == "featurestore":
            materialization_identity = kwargs.get("materialization_identity", None)
            offline_store_target = kwargs.get("offline_store_target", None)
            online_store_target = kwargs.get("online_store_target", None)

            setup_materialization_store = (offline_store_target or online_store_target) and materialization_identity

        _set_val(param["setup_materialization_store"], "true" if setup_materialization_store else "false")
        if setup_materialization_store:
            if offline_store_target is not None:
                _set_val(param["offline_store_connection_target"], offline_store_target)
            if online_store_target is not None:
                _set_val(param["online_store_connection_target"], online_store_target)
            _set_val(param["materialization_identity_client_id"], materialization_identity.client_id)
            _set_val(param["materialization_identity_resource_id"], materialization_identity.resource_id)

        managed_network = None
        if workspace.managed_network:
            managed_network = workspace.managed_network._to_rest_object()
        else:
            managed_network = ManagedNetwork(IsolationMode.DISABLED)._to_rest_object()
        _set_val(param["managedNetwork"], managed_network)
        if workspace.enable_data_isolation:
            _set_val(param["enable_data_isolation"], "true")

        resources_being_deployed[workspace.name] = (ArmConstants.WORKSPACE, None)
        return template, param, resources_being_deployed

    def _check_workspace_name(self, name) -> str:
        workspace_name = name or self._default_workspace_name
        if not workspace_name:
            msg = "Please provide a workspace name or use a MLClient with a workspace name set."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.WORKSPACE,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        return workspace_name


def _set_val(key: str, val: str) -> None:
    key["value"] = val


def _generate_key_vault(name: str, resources_being_deployed: dict) -> str:
    # Vault name must only contain alphanumeric characters and dashes and cannot start with a number.
    # Vault name must be between 3-24 alphanumeric characters.
    # The name must begin with a letter, end with a letter or digit, and not contain consecutive hyphens.
    key_vault = get_name_for_dependent_resource(name, "keyvault")
    resources_being_deployed[key_vault] = (ArmConstants.KEY_VAULT, None)
    return key_vault


def _generate_storage(name: str, resources_being_deployed: dict) -> str:
    storage = get_name_for_dependent_resource(name, "storage")
    resources_being_deployed[storage] = (ArmConstants.STORAGE, None)
    return storage


def _generate_log_analytics(name: str, resources_being_deployed: dict) -> str:
    log_analytics = get_name_for_dependent_resource(name, "logalytics")  # cspell:disable-line
    resources_being_deployed[log_analytics] = (
        ArmConstants.LOG_ANALYTICS,
        None,
    )
    return log_analytics


def _generate_app_insights(name: str, resources_being_deployed: dict) -> str:
    # Application name only allows alphanumeric characters, periods, underscores,
    # hyphens and parenthesis and cannot end in a period
    app_insights = get_name_for_dependent_resource(name, "insights")
    resources_being_deployed[app_insights] = (
        ArmConstants.APP_INSIGHTS,
        None,
    )
    return app_insights


class CustomArmTemplateDeploymentPollingMethod(PollingMethod):
    def __init__(self, poller, arm_submit, func) -> None:
        self.poller = poller
        self.arm_submit = arm_submit
        self.func = func
        super().__init__()

    def resource(self):
        error = None
        try:
            while not self.poller.done():
                try:
                    time.sleep(LROConfigurations.SLEEP_TIME)
                    self.arm_submit._check_deployment_status()
                except KeyboardInterrupt as e:
                    self.arm_submit._client.close()
                    error = e
                    raise

            if self.poller._exception is not None:
                error = self.poller._exception
        except Exception as e:  # pylint: disable=broad-except
            error = e
        finally:
            # one last check to make sure all print statements make it
            if not isinstance(error, KeyboardInterrupt):
                self.arm_submit._check_deployment_status()
                total_duration = self.poller.result().properties.duration

        if error is not None:
            error_msg = f"Unable to create resource. \n {error}\n"
            module_logger.error(error_msg)
            raise error
        module_logger.info("Total time : %s\n", from_iso_duration_format_min_sec(total_duration))
        return self.func()

    def initialize(self, *args, **kwargs):
        pass

    def finished(self):
        pass

    def run(self):
        pass

    def status(self):
        pass
