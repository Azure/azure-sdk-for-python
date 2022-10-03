# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from time import time
from typing import Dict, Iterable, Tuple, Union

from azure.ai.ml._arm_deployments import ArmDeploymentExecutor
from azure.ai.ml._arm_deployments.arm_helper import get_template
from azure.ai.ml._restclient.v2022_05_01 import AzureMachineLearningWorkspaces as ServiceClient052022
from azure.ai.ml._restclient.v2022_05_01.models import (
    DiagnoseRequestProperties,
    DiagnoseWorkspaceParameters,
    WorkspaceUpdateParameters,
)
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope
from azure.ai.ml._utils._azureml_polling import AzureMLPolling, polling_wait
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._utils._workspace_utils import (
    delete_resource_by_arm_id,
    get_deployment_name,
    get_name_for_dependent_resource,
    get_resource_and_group_name,
    get_resource_group_location,
)
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml._version import VERSION
from azure.ai.ml.constants import ManagedServiceIdentityType
from azure.ai.ml.constants._common import ArmConstants, LROConfigurations, WorkspaceResourceConstants
from azure.ai.ml.entities import Workspace, WorkspaceKeys
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class WorkspaceOperations:
    """WorkspaceOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: ServiceClient052022,
        all_operations: OperationsContainer,
        credentials: TokenCredential = None,
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

    # @monitor_with_activity(logger, "Workspace.List", ActivityType.PUBLICAPI)
    def list(self, *, scope: str = "resource_group") -> Iterable[Workspace]:
        """List all workspaces that the user has access to in the current
        resource group or subscription.

        :param scope: scope of the listing, "resource_group" or "subscription", defaults to "resource_group"
        :type scope: str, optional
        :return: An iterator like instance of Workspace objects
        :rtype: ~azure.core.paging.ItemPaged[Workspace]
        """

        if scope == "subscription":
            return self._operation.list_by_subscription(
                cls=lambda objs: [Workspace._from_rest_object(obj) for obj in objs]
            )
        return self._operation.list_by_resource_group(
            self._resource_group_name,
            cls=lambda objs: [Workspace._from_rest_object(obj) for obj in objs],
        )

    # @monitor_with_activity(logger, "Workspace.Get", ActivityType.PUBLICAPI)
    def get(self, name: str = None, **kwargs: Dict) -> Workspace:
        """Get a workspace by name.

        :param name: Name of the workspace.
        :type name: str
        :return: The workspace with the provided name.
        :rtype: Workspace
        """

        workspace_name = self._check_workspace_name(name)
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        obj = self._operation.get(resource_group, workspace_name)
        return Workspace._from_rest_object(obj)

    # @monitor_with_activity(logger, "Workspace.Get_Keys", ActivityType.PUBLICAPI)
    def get_keys(self, name: str = None) -> WorkspaceKeys:
        """Get keys for the workspace.

        :param name: Name of the workspace.
        :type name: str
        :return: Keys of workspace dependent resources.
        :rtype: WorkspaceKeys
        """
        workspace_name = self._check_workspace_name(name)
        obj = self._operation.list_keys(self._resource_group_name, workspace_name)
        return WorkspaceKeys._from_rest_object(obj)

    # @monitor_with_activity(logger, "Workspace.BeginSyncKeys", ActivityType.PUBLICAPI)
    def begin_sync_keys(self, name: str = None, **kwargs: Dict) -> LROPoller:
        """Triggers the workspace to immediately synchronize keys. If keys for
        any resource in the workspace are changed, it can take around an hour
        for them to automatically be updated. This function enables keys to be
        updated upon request. An example scenario is needing immediate access
        to storage after regenerating storage keys.

        :param name: Name of the workspace.
        :type name: str
        """

        no_wait = kwargs.get("no_wait", False)

        workspace_name = self._check_workspace_name(name)
        poller = self._operation.begin_resync_keys(self._resource_group_name, workspace_name)

        if no_wait:
            return poller
        polling_wait(poller, message="Waiting for the workspace keys sync.")

    # @monitor_with_activity(logger, "Workspace.BeginCreate", ActivityType.PUBLICAPI)
    def begin_create(
        self,
        workspace: Workspace,
        update_dependent_resources: bool = False,
        **kwargs: Dict,
    ) -> LROPoller:
        """Create a new Azure Machine Learning Workspace.

        Returns the workspace if already exists.

        :param workspace: Workspace definition.
        :type workspace: Workspace
        :type update_dependent_resources: boolean
        :return: A poller to track the operation status.
        :rtype: LROPoller
        """
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
            return self.begin_update(
                workspace,
                update_dependent_resources=update_dependent_resources,
                kwargs=kwargs,
            )
        # add tag in the workspace to indicate which sdk version the workspace is created from
        if workspace.tags is None:
            workspace.tags = {}
        if workspace.tags.get("createdByToolkit") is None:
            workspace.tags["createdByToolkit"] = "sdk-v2-{}".format(VERSION)

        workspace.resource_group = resource_group
        template, param, resources_being_deployed = self._populate_arm_paramaters(workspace)

        arm_submit = ArmDeploymentExecutor(
            credentials=self._credentials,
            resource_group_name=resource_group,
            subscription_id=self._subscription_id,
            deployment_name=get_deployment_name(workspace.name),
        )

        no_wait = kwargs.get("no_wait", False)
        # deploy_resource() blocks for the poller to succeed if wait is True
        poller = arm_submit.deploy_resource(
            template=template,
            resources_being_deployed=resources_being_deployed,
            parameters=param,
            wait=not no_wait,
        )

        return poller if no_wait else self.get(workspace.name, resource_group=resource_group)

    # @monitor_with_activity(logger, "Workspace.BeginUpdate", ActivityType.PUBLICAPI)
    def begin_update(
        self,
        workspace: Workspace,
        *,
        update_dependent_resources: bool = False,
        **kwargs: Dict,
    ) -> Union[LROPoller, Workspace]:
        """Update friendly name, description, managed identities or tags of a workspace.

        :param workspace: Workspace resource.
        :param update_dependent_resources: gives your consent to update the workspace dependent resources.
            Note that updating the workspace-attached Azure Container Registry resource may break lineage
            of previous jobs or your ability to rerun earlier jobs in this workspace.
            Also, updating the workspace-attached Azure Application Insights resource may break lineage of
            deployed inference endpoints this workspace. Only set this argument if you are sure that you want
            to perform this operation. If this argument is not set, the command to update
            Azure Container Registry and Azure Application Insights will fail.
        :param application_insights: Application insights resource for workspace.
        :param container_registry: Container registry resource for workspace.
        :type workspace: Workspace
        :return: A poller to track the operation status.
        :rtype: LROPoller
        """
        identity = kwargs.get("identity", workspace.identity)
        if identity:
            identity = identity._to_workspace_rest_object()
        update_param = WorkspaceUpdateParameters(
            tags=workspace.tags,
            description=kwargs.get("description", workspace.description),
            friendly_name=kwargs.get("display_name", workspace.display_name),
            public_network_access=kwargs.get("public_network_access", workspace.public_network_access),
            image_build_compute=kwargs.get("image_build_compute", workspace.image_build_compute),
            identity=identity,
            primary_user_assigned_identity=kwargs.get(
                "primary_user_assigned_identity", workspace.primary_user_assigned_identity
            ),
        )

        container_registry = kwargs.get("container_registry", workspace.container_registry)
        old_workspace = self.get(workspace.name, **kwargs)
        # Empty string is for erasing the value of container_registry, None is to be ignored value
        if (
            container_registry is not None
            and container_registry != old_workspace.container_registry
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
            and application_insights != old_workspace.application_insights
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
        update_param.container_registry = container_registry
        update_param.application_insights = application_insights
        no_wait = kwargs.get("no_wait", False)

        resource_group = kwargs.get("resource_group") or workspace.resource_group or self._resource_group_name
        poller = self._operation.begin_update(resource_group, workspace.name, update_param, polling=not no_wait)

        if not no_wait:
            return Workspace._from_rest_object(poller.result())
        module_logger.info(
            "Workspace update request initiated. Status can be checked using `az ml workspace show -n %s`\n",
            workspace.name,
        )
        return poller

    # @monitor_with_activity(logger, "Workspace.BeginDelete", ActivityType.PUBLICAPI)
    def begin_delete(self, name: str, *, delete_dependent_resources: bool, **kwargs: Dict) -> LROPoller:
        """Delete a workspace.

        :param name: Name of the workspace
        :type name: str
        :param delete_dependent_resources: Whether to delete resources associated with the workspace,
            i.e., container registry, storage account, key vault, and application insights.
            The default is False. Set to True to delete these resources.
        :type delete_dependent_resources: bool
        :return: A poller to track the operation status.
        :rtype: LROPoller
        """
        try:
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

            start_time = time()
            path_format_arguments = {
                "endpointName": name,
                "resourceGroupName": resource_group,
                "workspaceName": name,
            }
            no_wait = kwargs.get("no_wait", False)

            delete_poller = self._operation.begin_delete(
                resource_group_name=resource_group,
                workspace_name=name,
                polling=AzureMLPolling(
                    LROConfigurations.POLL_INTERVAL,
                    path_format_arguments=path_format_arguments,
                    **self._init_kwargs,
                )
                if not no_wait
                else False,
                polling_interval=LROConfigurations.POLL_INTERVAL,
                **self._init_kwargs,
            )

            if no_wait:
                module_logger.info("Delete request initiated for workspace: %s`\n", name)
                return delete_poller
            message = f"Deleting workspace {name} "
            polling_wait(poller=delete_poller, start_time=start_time, message=message)
        except Exception as response_exception:
            raise response_exception

    # @monitor_with_activity(logger, "Workspace.BeginDiagnose", ActivityType.PUBLICAPI)
    def begin_diagnose(self, name: str, **kwargs: Dict) -> LROPoller:
        """Diagnose workspace setup problems.

        If your workspace is not working as expected, you can run this diagnosis to
        check if the workspace has been broken.
        For private endpoint workspace, it will also help check out if the network
        setup to this workspace and its dependent resource as problem or not.

        :param name: Name of the workspace
        :type name: str
        :return: A poller to track the operation status.
        :rtype: LROPoller
        """
        no_wait = kwargs.get("no_wait", False)
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        parameters = DiagnoseWorkspaceParameters(value=DiagnoseRequestProperties())
        poller = self._operation.begin_diagnose(resource_group, name, parameters, polling=not no_wait)
        if not no_wait:
            return poller.result().value.as_dict()
        module_logger.info("Diagnose request initiated for workspace:%s`\n", name)
        return poller

    # pylint: disable=too-many-statements,too-many-branches
    def _populate_arm_paramaters(self, workspace: Workspace) -> Tuple[dict, dict, dict]:
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
                type=camel_to_snake(ManagedServiceIdentityType.SYSTEM_ASSIGNED))._to_workspace_rest_object()
        _set_val(param["identity"], identity)

        if workspace.primary_user_assigned_identity:
            _set_val(param["primaryUserAssignedIdentity"], workspace.primary_user_assigned_identity)

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


def _generate_app_insights(name: str, resources_being_deployed: dict) -> str:
    # Application name only allows alphanumeric characters, periods, underscores,
    # hyphens and parenthesis and cannot end in a period
    app_insights = get_name_for_dependent_resource(name, "insights")
    resources_being_deployed[app_insights] = (
        ArmConstants.APP_INSIGHTS,
        None,
    )
    return app_insights
