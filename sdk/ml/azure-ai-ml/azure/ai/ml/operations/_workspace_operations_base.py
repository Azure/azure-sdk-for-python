# pylint: disable=too-many-lines
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import time
from abc import ABC
from typing import Any, Callable, Dict, MutableMapping, Optional, Tuple

from azure.ai.ml._arm_deployments import ArmDeploymentExecutor
from azure.ai.ml._arm_deployments.arm_helper import get_template
from azure.ai.ml._restclient.v2024_07_01_preview import AzureMachineLearningWorkspaces as ServiceClient072024Preview
from azure.ai.ml._restclient.v2024_07_01_preview.models import (
    EncryptionKeyVaultUpdateProperties,
    EncryptionUpdateProperties,
    WorkspaceUpdateParameters,
)
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope
from azure.ai.ml._utils._appinsights_utils import get_log_analytics_arm_id

# from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._utils._workspace_utils import (
    delete_resource_by_arm_id,
    get_deployment_name,
    get_generic_arm_resource_by_arm_id,
    get_name_for_dependent_resource,
    get_resource_and_group_name,
    get_resource_group_location,
    get_sub_id_resource_and_group_name,
)
from azure.ai.ml._utils.utils import camel_to_snake, from_iso_duration_format_min_sec
from azure.ai.ml._version import VERSION
from azure.ai.ml.constants import ManagedServiceIdentityType
from azure.ai.ml.constants._common import (
    WORKSPACE_PATCH_REJECTED_KEYS,
    ArmConstants,
    LROConfigurations,
    WorkspaceKind,
    WorkspaceResourceConstants,
)
from azure.ai.ml.constants._workspace import IsolationMode, OutboundRuleCategory
from azure.ai.ml.entities import Hub, Project, Workspace
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.ai.ml.entities._workspace._ai_workspaces._constants import ENDPOINT_AI_SERVICE_KIND
from azure.ai.ml.entities._workspace.networking import ManagedNetwork
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller, PollingMethod

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class WorkspaceOperationsBase(ABC):
    """Base class for WorkspaceOperations, can't be instantiated directly."""

    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: ServiceClient072024Preview,
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

    def get(self, workspace_name: Optional[str] = None, **kwargs: Any) -> Optional[Workspace]:
        """Get a Workspace by name.

        :param workspace_name: Name of the workspace.
        :type workspace_name: str
        :return: The workspace with the provided name.
        :rtype: ~azure.ai.ml.entities.Workspace
        """
        workspace_name = self._check_workspace_name(workspace_name)
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        obj = self._operation.get(resource_group, workspace_name)
        v2_service_context = {}

        v2_service_context["subscription_id"] = self._subscription_id
        v2_service_context["workspace_name"] = workspace_name
        v2_service_context["resource_group_name"] = resource_group
        v2_service_context["auth"] = self._credentials  # type: ignore

        from urllib.parse import urlparse

        if obj is not None and obj.ml_flow_tracking_uri:
            parsed_url = urlparse(obj.ml_flow_tracking_uri)
            host_url = "https://{}".format(parsed_url.netloc)
            v2_service_context["host_url"] = host_url
        else:
            v2_service_context["host_url"] = ""

        # host_url=service_context._get_mlflow_url(),
        # cloud=_get_cloud_or_default(
        #     service_context.get_auth()._cloud_type.name
        if obj is not None and obj.kind is not None and obj.kind.lower() == WorkspaceKind.HUB:
            return Hub._from_rest_object(obj, v2_service_context)
        if obj is not None and obj.kind is not None and obj.kind.lower() == WorkspaceKind.PROJECT:
            return Project._from_rest_object(obj, v2_service_context)
        return Workspace._from_rest_object(obj, v2_service_context)

    def begin_create(
        self,
        workspace: Workspace,
        update_dependent_resources: bool = False,
        get_callback: Optional[Callable[[], Workspace]] = None,
        **kwargs: Any,
    ) -> LROPoller[Workspace]:
        """Create a new Azure Machine Learning Workspace.

        Returns the workspace if already exists.

        :param workspace: Workspace definition.
        :type workspace: ~azure.ai.ml.entities.Workspace
        :param update_dependent_resources: Whether to update dependent resources, defaults to False.
        :type update_dependent_resources: boolean
        :param get_callback: A callable function to call at the end of operation.
        :type get_callback: Optional[Callable[[], ~azure.ai.ml.entities.Workspace]]
        :return: An instance of LROPoller that returns a Workspace.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.Workspace]
        :raises ~azure.ai.ml.ValidationException: Raised if workspace is Project workspace and user
        specifies any of the following in workspace object: storage_account, container_registry, key_vault,
        public_network_access, managed_network, customer_managed_key, system_datastores_auth_mode.
        """
        existing_workspace = None
        resource_group = kwargs.get("resource_group") or workspace.resource_group or self._resource_group_name
        endpoint_resource_id = kwargs.pop("endpoint_resource_id", "")
        endpoint_kind = kwargs.pop("endpoint_kind", ENDPOINT_AI_SERVICE_KIND)

        try:
            existing_workspace = self.get(workspace.name, resource_group=resource_group)
        except Exception:  # pylint: disable=W0718
            pass

        # idempotent behavior
        if existing_workspace:
            if workspace.tags is not None and workspace.tags.get("createdByToolkit") is not None:
                workspace.tags.pop("createdByToolkit")
            if existing_workspace.tags is not None:
                existing_workspace.tags.update(workspace.tags)  # type: ignore
            workspace.tags = existing_workspace.tags
            # TODO do we want projects to do this?
            if workspace._kind != WorkspaceKind.PROJECT:
                workspace.container_registry = workspace.container_registry or existing_workspace.container_registry
                workspace.application_insights = (
                    workspace.application_insights or existing_workspace.application_insights
                )
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
        (
            template,
            param,
            resources_being_deployed,
        ) = self._populate_arm_parameters(
            workspace,
            endpoint_resource_id=endpoint_resource_id,
            endpoint_kind=endpoint_kind,
            **kwargs,
        )
        # check if create with workspace hub request is valid
        if workspace._kind == WorkspaceKind.PROJECT:
            if not all(
                x is None
                for x in [
                    workspace.storage_account,
                    workspace.container_registry,
                    workspace.key_vault,
                ]
            ):
                msg = (
                    "To create a project workspace with a workspace hub, please only specify name, description, "
                    + "display_name, location, application insight and identity"
                )
                raise ValidationException(
                    message=msg,
                    target=ErrorTarget.WORKSPACE,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.USER_ERROR,
                )

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

        def callback() -> Optional[Workspace]:
            """Callback to be called after completion

            :return: Result of calling appropriate callback.
            :rtype: Any
            """
            return get_callback() if get_callback else self.get(workspace.name, resource_group=resource_group)

        real_callback = callback
        injected_callback = kwargs.get("cls", None)
        if injected_callback:
            # pylint: disable=function-redefined
            def real_callback() -> Any:
                """Callback to be called after completion

                :return: Result of calling appropriate callback.
                :rtype: Any
                """
                return injected_callback(callback())

        return LROPoller(
            self._operation._client,
            None,
            lambda *x, **y: None,
            CustomArmTemplateDeploymentPollingMethod(poller, arm_submit, real_callback),
        )

    # pylint: disable=too-many-statements,too-many-locals
    def begin_update(
        self,
        workspace: Workspace,
        *,
        update_dependent_resources: bool = False,
        deserialize_callback: Optional[Callable] = None,
        **kwargs: Any,
    ) -> LROPoller[Workspace]:
        """Updates a Azure Machine Learning Workspace.

        :param workspace: Workspace resource.
        :type workspace: ~azure.ai.ml.entities.Workspace
        :keyword update_dependent_resources: Whether to update dependent resources, defaults to False.
        :paramtype update_dependent_resources: boolean
        :keyword deserialize_callback: A callable function to call at the end of operation.
        :paramtype deserialize_callback: Optional[Callable[[], ~azure.ai.ml.entities.Workspace]]
        :return: An instance of LROPoller that returns a Workspace.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.Workspace]
        :raises ~azure.ai.ml.ValidationException: Raised if updating container_registry for a workspace
        and update_dependent_resources is not True.
        :raises ~azure.ai.ml.ValidationException: Raised if updating application_insights for a workspace
        and update_dependent_resources is not True.
        """
        identity = kwargs.get("identity", workspace.identity)
        workspace_name = kwargs.get("workspace_name", workspace.name)
        resource_group = kwargs.get("resource_group") or workspace.resource_group or self._resource_group_name
        existing_workspace: Any = self.get(workspace_name, **kwargs)
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
            managed_network = ManagedNetwork(isolation_mode=managed_network)._to_rest_object()
        elif isinstance(managed_network, ManagedNetwork):
            if managed_network.outbound_rules is not None:
                # drop recommended and required rules from the update request since it would result in bad request
                managed_network.outbound_rules = [
                    rule
                    for rule in managed_network.outbound_rules
                    if rule.category not in (OutboundRuleCategory.REQUIRED, OutboundRuleCategory.RECOMMENDED)
                ]
            managed_network = managed_network._to_rest_object()

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
                "Include the update_dependent_resources argument in SDK or the "
                "--update-dependent-resources/-u parameter in CLI with this request to confirm."
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
                "operation? "
                "Include the update_dependent_resources argument in SDK or the "
                "--update-dependent-resources/-u parameter in CLI with this request to confirm."
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

        serverless_compute_settings = kwargs.get("serverless_compute", workspace.serverless_compute)
        if serverless_compute_settings:
            serverless_compute_settings = (
                serverless_compute_settings._to_rest_object()
            )  # pylint: disable=protected-access

        update_param = WorkspaceUpdateParameters(
            tags=kwargs.get("tags", workspace.tags),
            description=kwargs.get("description", workspace.description),
            friendly_name=kwargs.get("display_name", workspace.display_name),
            public_network_access=kwargs.get("public_network_access", workspace.public_network_access),
            system_datastores_auth_mode=kwargs.get(
                "system_datastores_auth_mode", workspace.system_datastores_auth_mode
            ),
            allow_role_assignment_on_rg=kwargs.get(
                "allow_roleassignment_on_rg", workspace.allow_roleassignment_on_rg
            ),  # diff due to swagger restclient casing diff
            image_build_compute=kwargs.get("image_build_compute", workspace.image_build_compute),
            identity=identity,
            primary_user_assigned_identity=kwargs.get(
                "primary_user_assigned_identity", workspace.primary_user_assigned_identity
            ),
            managed_network=managed_network,
            feature_store_settings=feature_store_settings,
        )
        if serverless_compute_settings:
            update_param.serverless_compute_settings = serverless_compute_settings
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

        update_role_assignment = (
            kwargs.get("update_workspace_role_assignment", None)
            or kwargs.get("update_offline_store_role_assignment", None)
            or kwargs.get("update_online_store_role_assignment", None)
        )
        grant_materialization_permissions = kwargs.get("grant_materialization_permissions", None)

        # Remove deprecated keys from older workspaces that might still have them before we try to update.
        if workspace.tags is not None:
            for bad_key in WORKSPACE_PATCH_REJECTED_KEYS:
                _ = workspace.tags.pop(bad_key, None)

        # pylint: disable=unused-argument, docstring-missing-param
        def callback(_: Any, deserialized: Any, args: Any) -> Workspace:
            """Callback to be called after completion

            :return: Workspace deserialized.
            :rtype: ~azure.ai.ml.entities.Workspace
            """
            if (
                workspace._kind
                and workspace._kind.lower() == "featurestore"
                and update_role_assignment
                and grant_materialization_permissions
            ):
                module_logger.info("updating feature store materialization identity role assignments..")
                template, param, resources_being_deployed = self._populate_feature_store_role_assignment_parameters(
                    workspace, resource_group=resource_group, location=existing_workspace.location, **kwargs
                )

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

                poller.result()
            return (
                deserialize_callback(deserialized)
                if deserialize_callback
                else Workspace._from_rest_object(deserialized)
            )

        real_callback = callback
        injected_callback = kwargs.get("cls", None)
        if injected_callback:
            # pylint: disable=function-redefined, docstring-missing-param
            def real_callback(_: Any, deserialized: Any, args: Any) -> Any:
                """Callback to be called after completion

                :return: Result of calling appropriate callback.
                :rtype: Any
                """
                return injected_callback(callback(_, deserialized, args))

        poller = self._operation.begin_update(
            resource_group, workspace_name, update_param, polling=True, cls=real_callback
        )
        return poller

    def begin_delete(
        self, name: str, *, delete_dependent_resources: bool, permanently_delete: bool = False, **kwargs: Any
    ) -> LROPoller[None]:
        """Delete a Workspace.

        :param name: Name of the Workspace
        :type name: str
        :keyword delete_dependent_resources: Whether to delete resources associated with the Workspace,
            i.e., container registry, storage account, key vault, application insights, log analytics.
            The default is False. Set to True to delete these resources.
        :paramtype delete_dependent_resources: bool
        :keyword permanently_delete: Workspaces are soft-deleted by default to allow recovery of workspace data.
            Set this flag to true to override the soft-delete behavior and permanently delete your workspace.
        :paramtype permanently_delete: bool
        :return: A poller to track the operation status.
        :rtype: ~azure.core.polling.LROPoller[None]
        """
        workspace: Any = self.get(name, **kwargs)
        resource_group = kwargs.get("resource_group") or self._resource_group_name

        # prevent dependent resource delete for lean workspace, only delete appinsight and associated log analytics
        if workspace._kind == WorkspaceKind.PROJECT and delete_dependent_resources:
            app_insights = get_generic_arm_resource_by_arm_id(
                self._credentials,
                self._subscription_id,
                workspace.application_insights,
                ArmConstants.AZURE_MGMT_APPINSIGHT_API_VERSION,
            )
            if app_insights is not None and "WorkspaceResourceId" in app_insights.properties:
                delete_resource_by_arm_id(
                    self._credentials,
                    self._subscription_id,
                    app_insights.properties["WorkspaceResourceId"],
                    ArmConstants.AZURE_MGMT_LOGANALYTICS_API_VERSION,
                )
            delete_resource_by_arm_id(
                self._credentials,
                self._subscription_id,
                workspace.application_insights,
                ArmConstants.AZURE_MGMT_APPINSIGHT_API_VERSION,
            )
        elif delete_dependent_resources:
            app_insights = get_generic_arm_resource_by_arm_id(
                self._credentials,
                self._subscription_id,
                workspace.application_insights,
                ArmConstants.AZURE_MGMT_APPINSIGHT_API_VERSION,
            )
            if app_insights is not None and "WorkspaceResourceId" in app_insights.properties:
                delete_resource_by_arm_id(
                    self._credentials,
                    self._subscription_id,
                    app_insights.properties["WorkspaceResourceId"],
                    ArmConstants.AZURE_MGMT_LOGANALYTICS_API_VERSION,
                )
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
    def _populate_arm_parameters(self, workspace: Workspace, **kwargs: Any) -> Tuple[dict, dict, dict]:
        """Populates ARM template parameters for use to deploy a workspace resource.

        :param workspace: Workspace resource.
        :type workspace: ~azure.ai.ml.entities.Workspace
        :return: A tuple of three dicts: an ARM template, ARM template parameters, resources_being_deployed.
        :rtype: Tuple[dict, dict, dict]
        """
        resources_being_deployed: Dict = {}
        if not workspace.location:
            workspace.location = get_resource_group_location(
                self._credentials, self._subscription_id, workspace.resource_group
            )
        template = get_template(resource_type=ArmConstants.WORKSPACE_BASE)
        param = get_template(resource_type=ArmConstants.WORKSPACE_PARAM)
        if workspace._kind == WorkspaceKind.PROJECT:
            template = get_template(resource_type=ArmConstants.WORKSPACE_PROJECT)
        endpoint_resource_id = kwargs.get("endpoint_resource_id") or ""
        endpoint_kind = kwargs.get("endpoint_kind") or ENDPOINT_AI_SERVICE_KIND
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
            subscription_id, resource_name, group_name = get_sub_id_resource_and_group_name(workspace.storage_account)
            _set_val(param["storageAccountName"], resource_name)
            _set_val(param["storageAccountOption"], "existing")
            _set_val(param["storageAccountResourceGroupName"], group_name)
            _set_val(param["storageAccountSubscriptionId"], subscription_id)
        else:
            storage = _generate_storage(workspace.name, resources_being_deployed)
            _set_val(param["storageAccountName"], storage)
            _set_val(
                param["storageAccountResourceGroupName"],
                workspace.resource_group,
            )
            _set_val(
                param["storageAccountSubscriptionId"],
                self._subscription_id,
            )

        if workspace.application_insights:
            resource_name, group_name = get_resource_and_group_name(workspace.application_insights)
            _set_val(param["applicationInsightsName"], resource_name)
            _set_val(param["applicationInsightsOption"], "existing")
            _set_val(
                param["applicationInsightsResourceGroupName"],
                group_name,
            )
        elif workspace._kind and workspace._kind.lower() in {WorkspaceKind.HUB, WorkspaceKind.PROJECT}:
            _set_val(param["applicationInsightsOption"], "none")
            # Set empty values because arm templates whine over unset values.
            _set_val(param["applicationInsightsName"], "ignoredButCantBeEmpty")
            _set_val(
                param["applicationInsightsResourceGroupName"],
                "ignoredButCantBeEmpty",
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
            _set_val(param["associatedResourcePNA"], workspace.public_network_access)

        if workspace.system_datastores_auth_mode:
            _set_val(param["systemDatastoresAuthMode"], workspace.system_datastores_auth_mode)

        if workspace.allow_roleassignment_on_rg is False:
            _set_val(param["allowRoleAssignmentOnRG"], "false")

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
            if workspace._feature_store_settings.offline_store_connection_name:
                _set_val(
                    param["offline_store_connection_name"],
                    workspace._feature_store_settings.offline_store_connection_name,
                )
            if workspace._feature_store_settings.online_store_connection_name:
                _set_val(
                    param["online_store_connection_name"],
                    workspace._feature_store_settings.online_store_connection_name,
                )

        if workspace._kind and workspace._kind.lower() == "featurestore":
            materialization_identity = kwargs.get("materialization_identity", None)
            offline_store_target = kwargs.get("offline_store_target", None)
            online_store_target = kwargs.get("online_store_target", None)

            from azure.ai.ml._utils._arm_id_utils import AzureResourceId, AzureStorageContainerResourceId

            # set workspace storage account access auth type to identity-based
            _set_val(param["systemDatastoresAuthMode"], "identity")

            if offline_store_target:
                arm_id = AzureStorageContainerResourceId(offline_store_target)
                _set_val(param["offlineStoreStorageAccountOption"], "existing")
                _set_val(param["offline_store_container_name"], arm_id.container)
                _set_val(param["offline_store_storage_account_name"], arm_id.storage_account)
                _set_val(param["offline_store_resource_group_name"], arm_id.resource_group_name)
                _set_val(param["offline_store_subscription_id"], arm_id.subscription_id)
            else:
                _set_val(param["offlineStoreStorageAccountOption"], "new")
                _set_val(
                    param["offline_store_container_name"],
                    _generate_storage_container(workspace.name, resources_being_deployed),
                )
                if not workspace.storage_account:
                    _set_val(param["offline_store_storage_account_name"], param["storageAccountName"]["value"])
                else:
                    _set_val(
                        param["offline_store_storage_account_name"],
                        _generate_storage(workspace.name, resources_being_deployed),
                    )
                _set_val(param["offline_store_resource_group_name"], workspace.resource_group)
                _set_val(param["offline_store_subscription_id"], self._subscription_id)

            if online_store_target:
                arm_id = AzureResourceId(online_store_target)
                _set_val(param["online_store_resource_id"], online_store_target)
                _set_val(param["online_store_resource_group_name"], arm_id.resource_group_name)
                _set_val(param["online_store_subscription_id"], arm_id.subscription_id)

            if materialization_identity:
                arm_id = AzureResourceId(materialization_identity.resource_id)
                _set_val(param["materializationIdentityOption"], "existing")
                _set_val(param["materialization_identity_name"], arm_id.asset_name)
                _set_val(param["materialization_identity_resource_group_name"], arm_id.resource_group_name)
                _set_val(param["materialization_identity_subscription_id"], arm_id.subscription_id)
            else:
                _set_val(param["materializationIdentityOption"], "new")
                _set_val(
                    param["materialization_identity_name"],
                    _generate_materialization_identity(workspace, self._subscription_id, resources_being_deployed),
                )
                _set_val(param["materialization_identity_resource_group_name"], workspace.resource_group)
                _set_val(param["materialization_identity_subscription_id"], self._subscription_id)

            if not kwargs.get("grant_materialization_permissions", None):
                _set_val(param["grant_materialization_permissions"], "false")

        managed_network = None
        if workspace.managed_network:
            managed_network = workspace.managed_network._to_rest_object()
            if workspace.managed_network.isolation_mode in [
                IsolationMode.ALLOW_INTERNET_OUTBOUND,
                IsolationMode.ALLOW_ONLY_APPROVED_OUTBOUND,
            ]:
                _set_val(param["associatedResourcePNA"], "Disabled")
        else:
            managed_network = ManagedNetwork(isolation_mode=IsolationMode.DISABLED)._to_rest_object()
        _set_obj_val(param["managedNetwork"], managed_network)
        if workspace.enable_data_isolation:
            _set_val(param["enable_data_isolation"], "true")

        if workspace._kind and workspace._kind.lower() == WorkspaceKind.HUB:
            _set_obj_val(param["workspace_hub_config"], workspace._hub_values_to_rest_object())  # type: ignore
            # A user-supplied resource ID (either AOAI or AI Services or null)
            # endpoint_kind differentiates between a 'Bring a legacy AOAI resource hub' and 'any other kind of hub'
            # The former doesn't create non-AOAI endpoints, and is set below if the user provided a byo AOAI
            # resource ID. The latter case is the default and not shown here.
            if endpoint_resource_id != "":
                _set_val(param["endpoint_resource_id"], endpoint_resource_id)
                _set_val(param["endpoint_kind"], endpoint_kind)

        # Lean related param
        if (
            hasattr(workspace, "_kind")
            and workspace._kind is not None
            and workspace._kind.lower() == WorkspaceKind.PROJECT
        ):
            if hasattr(workspace, "_hub_id"):
                _set_val(param["workspace_hub"], workspace._hub_id)

        # Serverless compute related param
        serverless_compute = workspace.serverless_compute if workspace.serverless_compute else None
        if serverless_compute:
            _set_obj_val(param["serverless_compute_settings"], serverless_compute._to_rest_object())

        resources_being_deployed[workspace.name] = (ArmConstants.WORKSPACE, None)
        return template, param, resources_being_deployed

    def _populate_feature_store_role_assignment_parameters(
        self, workspace: Workspace, **kwargs: Any
    ) -> Tuple[dict, dict, dict]:
        """Populates ARM template parameters for use to update feature store materialization identity role assignments.

        :param workspace: Workspace resource.
        :type workspace: ~azure.ai.ml.entities.Workspace
        :return: A tuple of three dicts: an ARM template, ARM template parameters, resources_being_deployed.
        :rtype: Tuple[dict, dict, dict]
        """
        resources_being_deployed = {}
        template = get_template(resource_type=ArmConstants.FEATURE_STORE_ROLE_ASSIGNMENTS)
        param = get_template(resource_type=ArmConstants.FEATURE_STORE_ROLE_ASSIGNMENTS_PARAM)

        materialization_identity_id = kwargs.get("materialization_identity_id", None)
        if materialization_identity_id:
            _set_val(param["materialization_identity_resource_id"], materialization_identity_id)

        _set_val(param["workspace_name"], workspace.name)
        resource_group = kwargs.get("resource_group", workspace.resource_group)
        _set_val(param["resource_group_name"], resource_group)
        location = kwargs.get("location", workspace.location)
        _set_val(param["location"], location)

        update_workspace_role_assignment = kwargs.get("update_workspace_role_assignment", None)
        if update_workspace_role_assignment:
            _set_val(param["update_workspace_role_assignment"], "true")
        update_offline_store_role_assignment = kwargs.get("update_offline_store_role_assignment", None)
        if update_offline_store_role_assignment:
            _set_val(param["update_offline_store_role_assignment"], "true")
        update_online_store_role_assignment = kwargs.get("update_online_store_role_assignment", None)
        if update_online_store_role_assignment:
            _set_val(param["update_online_store_role_assignment"], "true")

        offline_store_target = kwargs.get("offline_store_target", None)
        online_store_target = kwargs.get("online_store_target", None)

        from azure.ai.ml._utils._arm_id_utils import AzureResourceId

        if offline_store_target:
            arm_id = AzureResourceId(offline_store_target)
            _set_val(param["offline_store_target"], offline_store_target)
            _set_val(param["offline_store_resource_group_name"], arm_id.resource_group_name)
            _set_val(param["offline_store_subscription_id"], arm_id.subscription_id)

        if online_store_target:
            arm_id = AzureResourceId(online_store_target)
            _set_val(param["online_store_target"], online_store_target)
            _set_val(param["online_store_resource_group_name"], arm_id.resource_group_name)
            _set_val(param["online_store_subscription_id"], arm_id.subscription_id)

        resources_being_deployed[materialization_identity_id] = (ArmConstants.USER_ASSIGNED_IDENTITIES, None)
        return template, param, resources_being_deployed

    def _check_workspace_name(self, name: Optional[str]) -> str:
        """Validates that a workspace name exists.

        :param name: Name for a workspace resource.
        :type name: str
        :return: No Return.
        :rtype: None
        :raises ~azure.ai.ml.ValidationException: Raised if updating nothing is specified for name and
        MLClient does not have workspace name set.
        """
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


def _set_val(dict: dict, val: Optional[str]) -> None:
    """Sets the value of a reference in parameters dict to a certain value.

    :param dict: Dict for a certain parameter.
    :type dict: dict
    :param val: The value to set for "value" in the passed in dict.
    :type val: str
    :return: No Return.
    :rtype: None
    """
    dict["value"] = val


def _set_obj_val(dict: dict, val: Any) -> None:
    """Serializes a JSON string into the parameters dict.

    :param dict: Parameters dict.
    :type dict: dict
    :param val: The obj to serialize.
    :type val: Any type. Must have `.serialize() -> MutableMapping[str, Any]` method.
    :return: No Return.
    :rtype: None
    """
    from copy import deepcopy

    json: MutableMapping[str, Any] = val.serialize()
    dict["value"] = deepcopy(json)


def _generate_key_vault(name: Optional[str], resources_being_deployed: dict) -> str:
    """Generates a name for a key vault resource to be created with workspace based on workspace name,
    sets name and type in resources_being_deployed.

    :param name: The name for the related workspace.
    :type name: str
    :param resources_being_deployed: Dict for resources being deployed.
    :type resources_being_deployed: dict
    :return: String for name of key vault.
    :rtype: str
    """
    # Vault name must only contain alphanumeric characters and dashes and cannot start with a number.
    # Vault name must be between 3-24 alphanumeric characters.
    # The name must begin with a letter, end with a letter or digit, and not contain consecutive hyphens.
    key_vault = get_name_for_dependent_resource(name, "keyvault")
    resources_being_deployed[key_vault] = (ArmConstants.KEY_VAULT, None)
    return str(key_vault)


def _generate_storage(name: Optional[str], resources_being_deployed: dict) -> str:
    """Generates a name for a storage account resource to be created with workspace based on workspace name,
    sets name and type in resources_being_deployed.

    :param name: The name for the related workspace.
    :type name: str
    :param resources_being_deployed: Dict for resources being deployed.
    :type resources_being_deployed: dict
    :return: String for name of storage account.
    :rtype: str
    """
    storage = get_name_for_dependent_resource(name, "storage")
    resources_being_deployed[storage] = (ArmConstants.STORAGE, None)
    return str(storage)


def _generate_storage_container(name: Optional[str], resources_being_deployed: dict) -> str:
    """Generates a name for a storage container resource to be created with workspace based on workspace name,
    sets name and type in resources_being_deployed.

    :param name: The name for the related workspace.
    :type name: str
    :param resources_being_deployed: Dict for resources being deployed.
    :type resources_being_deployed: dict
    :return: String for name of storage container
    :rtype: str
    """
    storage_container = get_name_for_dependent_resource(name, "container")
    resources_being_deployed[storage_container] = (ArmConstants.STORAGE_CONTAINER, None)
    return str(storage_container)


def _generate_log_analytics(name: Optional[str], resources_being_deployed: dict) -> str:
    """Generates a name for a log analytics resource to be created with workspace based on workspace name,
    sets name and type in resources_being_deployed.

    :param name: The name for the related workspace.
    :type name: str
    :param resources_being_deployed: Dict for resources being deployed.
    :type resources_being_deployed: dict
    :return: String for name of log analytics.
    :rtype: str
    """
    log_analytics = get_name_for_dependent_resource(name, "logalytics")  # cspell:disable-line
    resources_being_deployed[log_analytics] = (
        ArmConstants.LOG_ANALYTICS,
        None,
    )
    return str(log_analytics)


def _generate_app_insights(name: Optional[str], resources_being_deployed: dict) -> str:
    """Generates a name for an application insights resource to be created with workspace based on workspace name,
    sets name and type in resources_being_deployed.

    :param name: The name for the related workspace.
    :type name: str
    :param resources_being_deployed: Dict for resources being deployed.
    :type resources_being_deployed: dict
    :return: String for name of app insights.
    :rtype: str
    """
    # Application name only allows alphanumeric characters, periods, underscores,
    # hyphens and parenthesis and cannot end in a period
    app_insights = get_name_for_dependent_resource(name, "insights")
    resources_being_deployed[app_insights] = (
        ArmConstants.APP_INSIGHTS,
        None,
    )
    return str(app_insights)


def _generate_container_registry(name: Optional[str], resources_being_deployed: dict) -> str:
    """Generates a name for a container registry resource to be created with workspace based on workspace name,
    sets name and type in resources_being_deployed.

    :param name: The name for the related workspace.
    :type name: str
    :param resources_being_deployed: Dict for resources being deployed.
    :type resources_being_deployed: dict
    :return: String for name of container registry.
    :rtype: str
    """
    # Application name only allows alphanumeric characters, periods, underscores,
    # hyphens and parenthesis and cannot end in a period
    con_reg = get_name_for_dependent_resource(name, "containerRegistry")
    resources_being_deployed[con_reg] = (
        ArmConstants.CONTAINER_REGISTRY,
        None,
    )
    return str(con_reg)


def _generate_materialization_identity(
    workspace: Workspace, subscription_id: str, resources_being_deployed: dict
) -> str:
    """Generates a name for a materialization identity resource to be created
    with feature store based on workspace information,
    sets name and type in resources_being_deployed.

    :param workspace: The workspace object.
    :type workspace: Workspace
    :param subscription_id: The subscription id
    :type subscription_id: str
    :param resources_being_deployed: Dict for resources being deployed.
    :type resources_being_deployed: dict
    :return: String for name of materialization identity.
    :rtype: str
    """
    import uuid

    namespace = ""
    namespace_raw = f"{subscription_id[:12]}_{str(workspace.resource_group)[:12]}_{workspace.location}"
    for char in namespace_raw.lower():
        if char.isalpha() or char.isdigit():
            namespace = namespace + char
    namespace = namespace.encode("utf-8").hex()
    uuid_namespace = uuid.UUID(namespace[:32].ljust(32, "0"))
    materialization_identity = f"materialization-uai-" f"{uuid.uuid3(uuid_namespace, str(workspace.name).lower()).hex}"
    resources_being_deployed[materialization_identity] = (
        ArmConstants.USER_ASSIGNED_IDENTITIES,
        None,
    )
    return materialization_identity


class CustomArmTemplateDeploymentPollingMethod(PollingMethod):
    """A custom polling method for ARM template deployment used internally for workspace creation."""

    def __init__(self, poller: Any, arm_submit: Any, func: Any) -> None:
        self.poller = poller
        self.arm_submit = arm_submit
        self.func = func
        super().__init__()

    def resource(self) -> Any:
        """
        Polls for the resource creation completing every so often with ability to cancel deployment and outputs
        either error or executes function to "deserialize" result.

        :return: The response from polling result and calling func from CustomArmTemplateDeploymentPollingMethod
        :rtype: Any
        """
        error: Any = None
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
        except Exception as e:  # pylint: disable=W0718
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

    # pylint: disable=docstring-missing-param
    def initialize(self, *args: Any, **kwargs: Any) -> None:
        """
        unused stub overridden from ABC

        :return: No return.
        :rtype: ~azure.ai.ml.entities.OutboundRule
        """

    def finished(self) -> None:
        """
        unused stub overridden from ABC

        :return: No return.
        :rtype: ~azure.ai.ml.entities.OutboundRule
        """

    def run(self) -> None:
        """
        unused stub overridden from ABC

        :return: No return.
        :rtype: ~azure.ai.ml.entities.OutboundRule
        """

    def status(self) -> None:
        """
        unused stub overridden from ABC

        :return: No return.
        :rtype: ~azure.ai.ml.entities.OutboundRule
        """
