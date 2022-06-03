# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from time import time
from typing import Iterable, Dict, Union
import logging
from azure.ai.ml._arm_deployments.arm_helper import get_template
from azure.core.polling import LROPoller
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope
from azure.ai.ml._restclient.v2022_01_01_preview import AzureMachineLearningWorkspaces as ServiceClient012022Preview
from azure.ai.ml._restclient.v2022_01_01_preview.models import (
    ListWorkspaceKeysResult,
    DiagnoseWorkspaceParameters,
    DiagnoseRequestProperties,
    WorkspaceUpdateParameters,
)
from azure.ai.ml._arm_deployments import ArmDeploymentExecutor
from azure.identity import ChainedTokenCredential
from azure.ai.ml.constants import ArmConstants, WorkspaceResourceConstants, LROConfigurations
from azure.ai.ml._utils._workspace_utils import (
    delete_resource_by_arm_id,
    get_deployment_name,
    get_resource_group_location,
    get_name_for_dependent_resource,
    get_resource_and_group_name,
)
from azure.ai.ml.entities import Workspace
from marshmallow import RAISE
from azure.core.exceptions import ResourceExistsError
from azure.ai.ml._utils._azureml_polling import AzureMLPolling, polling_wait
from azure.ai.ml._version import VERSION

from azure.ai.ml._telemetry import AML_INTERNAL_LOGGER_NAMESPACE, ActivityType, monitor_with_activity
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget

logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE + __name__)
logger.propagate = False
module_logger = logging.getLogger(__name__)


class WorkspaceOperations:
    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: ServiceClient012022Preview,
        all_operations: OperationsContainer,
        credentials: ChainedTokenCredential = None,
        **kwargs: Dict,
    ):
        if "app_insights_handler" in kwargs:
            logger.addHandler(kwargs.pop("app_insights_handler"))
        kwargs.pop("base_url", None)

        self._subscription_id = operation_scope.subscription_id
        self._resource_group_name = operation_scope.resource_group_name
        self._default_workspace_name = operation_scope.workspace_name
        self._all_operations = all_operations
        self._operation = service_client.workspaces
        self._credentials = credentials
        self._init_kwargs = kwargs
        self.storage = None
        self.appInsights = None
        self.keyVault = None
        self.resources_being_deployed = {}
        self.containerRegistry = "none"

    @monitor_with_activity(logger, "Workspace.List", ActivityType.PUBLICAPI)
    def list(self, *, scope: str = "resource_group") -> Iterable[Workspace]:
        """List all workspaces that the user has access to in the current resource group or subscription

        :param scope: scope of the listing, "resource_group" or "subscription", defaults to "resource_group"
        :type scope: str, optional
        :return: An iterator like instance of Workspace objects
        :rtype: ~azure.core.paging.ItemPaged[Workspace]
        """

        if scope == "subscription":
            return self._operation.list_by_subscription(
                cls=lambda objs: [Workspace._from_rest_object(obj) for obj in objs]
            )
        else:
            return self._operation.list_by_resource_group(
                self._resource_group_name, cls=lambda objs: [Workspace._from_rest_object(obj) for obj in objs]
            )

    @monitor_with_activity(logger, "Workspace.Get", ActivityType.PUBLICAPI)
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

    @monitor_with_activity(logger, "Workspace.List_Keys", ActivityType.PUBLICAPI)
    def list_keys(self, name: str = None) -> ListWorkspaceKeysResult:
        """List keys for the workspace.

        :param name: Name of the workspace.
        :type name: str
        :return: A list of keys.
        :rtype: ListWorkspaceKeysResult
        """
        workspace_name = self._check_workspace_name(name)
        return self._operation.list_keys(self._resource_group_name, workspace_name)

    @monitor_with_activity(logger, "Workspace.BeginSyncKeys", ActivityType.PUBLICAPI)
    def begin_sync_keys(self, name: str = None, **kwargs: Dict) -> LROPoller:
        """Triggers the workspace to immediately synchronize keys.
        If keys for any resource in the workspace are changed, it can take around an hour for them to automatically be updated. This function enables keys to be updated upon request. An example scenario is needing immediate access to storage after regenerating storage keys.

        :param name: Name of the workspace.
        :type name: str
        """

        no_wait = kwargs.get("no_wait", False)

        workspace_name = self._check_workspace_name(name)
        poller = self._operation.begin_resync_keys(self._resource_group_name, workspace_name)

        if no_wait:
            return poller
        else:
            polling_wait(poller, message="Waiting for the workspace keys sync.")

    @monitor_with_activity(logger, "Workspace.BeginCreate", ActivityType.PUBLICAPI)
    def begin_create(self, workspace: Workspace, update_dependent_resources: bool = False, **kwargs: Dict) -> LROPoller:
        """Create a new Azure Machine Learning Workspace.

        Returns the workspace if already exists.

        :param workspace: Workspace definition.
        :type workspace: Workspace
        :type update_dependent_resources: boolean
        :return: A poller to track the operation status.
        :rtype: LROPoller
        """
        existing_workspace = None
        resource_group = workspace.resource_group or self._resource_group_name
        try:
            existing_workspace = self.get(workspace.name, resource_group=resource_group)
        except Exception:
            pass

        # idempotent behavior
        if existing_workspace:
            if workspace.tags.get("createdByToolkit") is not None:
                workspace.tags.pop("createdByToolkit")
            existing_workspace.tags.update(workspace.tags)
            workspace.tags = existing_workspace.tags
            workspace.container_registry = workspace.container_registry or existing_workspace.container_registry
            workspace.application_insights = workspace.application_insights or existing_workspace.application_insights
            return self.begin_update(workspace, update_dependent_resources=update_dependent_resources, kwargs=kwargs)

        # add tag in the workspace to indicate which sdk version the workspace is created from
        if workspace.tags is None:
            workspace.tags = {}
        if workspace.tags.get("createdByToolkit") is None:
            workspace.tags["createdByToolkit"] = "sdk-v2-{}".format(VERSION)

        self._populate_arm_paramaters(workspace)

        arm_submit = ArmDeploymentExecutor(
            credentials=self._credentials,
            resource_group_name=resource_group,
            subscription_id=self._subscription_id,
            deployment_name=get_deployment_name(workspace.name),
        )

        no_wait = kwargs.get("no_wait", False)
        # deploy_resource() blocks for the poller to succeed if wait is True
        poller = arm_submit.deploy_resource(
            template=self.template,
            resources_being_deployed=self.resources_being_deployed,
            parameters=self.param,
            wait=not no_wait,
        )

        return poller if no_wait else self.get(workspace.name, resource_group=resource_group)

    @monitor_with_activity(logger, "Workspace.BeginUpdate", ActivityType.PUBLICAPI)
    def begin_update(
        self, workspace: Workspace, *, update_dependent_resources: bool = False, **kwargs: Dict
    ) -> Union[LROPoller, Workspace]:
        """Update friendly name, description or tags of a workspace.

        :param workspace: Workspace resource.
        :param update_dependent_resources: gives your consent to update the workspace dependent resources. Note that updating the workspace-attached Azure Container Registry resource may break lineage of previous jobs or your ability to rerun earlier jobs in this workspace. Also, updating the workspace-attached Azure Application Insights resource may break lineage of deployed inference endpoints this workspace. Only set this argument if you are sure that you want to perform this operation. If this argument is not set, the command to update Azure Container Registry and Azure Application Insights will fail.
        :param application_insights: Application insights resource for workspace.
        :param container_registry: Container registry resource for workspace.
        :type workspace: Workspace
        :return: A poller to track the operation status.
        :rtype: LROPoller
        """
        update_param = WorkspaceUpdateParameters(
            tags=workspace.tags,
            description=kwargs.get("description", workspace.description),
            friendly_name=kwargs.get("display_name", workspace.display_name),
            public_network_access=kwargs.get("public_network_access", workspace.public_network_access),
            image_build_compute=kwargs.get("image_build_compute", workspace.image_build_compute),
        )

        update_dependent_resources = update_dependent_resources
        application_insights = kwargs.get("application_insights", workspace.application_insights)
        container_registry = kwargs.get("container_registry", workspace.container_registry)
        old_workspace = self.get(workspace.name, **kwargs)
        if container_registry != old_workspace.container_registry and not update_dependent_resources:
            msg = "Updating the workspace-attached Azure Container Registry resource may break lineage of previous jobs or your ability to rerun earlier jobs in this workspace. Are you sure you want to perform this operation? Include the --update_dependent_resources/-u parameter with this request to confirm."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.WORKSPACE,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        if application_insights != old_workspace.application_insights and not update_dependent_resources:
            msg = "Updating the workspace-attached Azure Application Insights resource may break lineage of deployed inference endpoints this workspace. Are you sure you want to perform this operation? Include the --update_dependent_resources/-u parameter with this request to confirm."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.WORKSPACE,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        update_param.container_registry = container_registry
        update_param.application_insights = application_insights
        no_wait = kwargs.get("no_wait", False)

        poller = self._operation.begin_update(
            self._resource_group_name, workspace.name, update_param, polling=not no_wait
        )

        if not no_wait:
            return Workspace._from_rest_object(poller.result())
        else:
            module_logger.info(
                f"Workspace update request initiated. Status can be checked using `az ml workspace show -n {workspace.name}`\n"
            )
            return poller

    @monitor_with_activity(logger, "Workspace.BeginDelete", ActivityType.PUBLICAPI)
    def begin_delete(self, name: str, *, delete_dependent_resources: bool, **kwargs: Dict) -> LROPoller:
        """Delete a workspace

        :param name: Name of the workspace
        :type name: str
        :param delete_dependent_resources: Whether to delete resources associated with the workspace, i.e., container registry, storage account, key vault, and application insights. The default is False. Set to True to delete these resources.
        :type delete_dependent_resources: bool
        :return: A poller to track the operation status.
        :rtype: LROPoller
        """
        try:
            workspace = self.get(name)
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
                "resourceGroupName": self._resource_group_name,
                "workspaceName": name,
            }
            no_wait = kwargs.get("no_wait", False)

            delete_poller = self._operation.begin_delete(
                resource_group_name=self._resource_group_name,
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
                module_logger.info(f"Delete request initiated for workspace: {name}`\n")
                return delete_poller
            else:
                message = f"Deleting workspace {name} "
                polling_wait(poller=delete_poller, start_time=start_time, message=message)
        except Exception as response_exception:
            raise response_exception

    @monitor_with_activity(logger, "Workspace.BeginDiagnose", ActivityType.PUBLICAPI)
    def begin_diagnose(self, name: str, **kwargs: Dict) -> LROPoller:
        """Diagnose workspace setup problems

        If your workspace is not working as expected, you can run this diagnosis to check if the workspace has been broken.
        For private endpoint workspace, it will also help check out if the network setup to this workspace and its dependent resource
        has problem or not.

        :param name: Name of the workspace
        :type name: str
        :return: A poller to track the operation status.
        :rtype: LROPoller
        """
        no_wait = kwargs.get("no_wait", False)
        parameters = DiagnoseWorkspaceParameters(value=DiagnoseRequestProperties())
        poller = self._operation.begin_diagnose(self._resource_group_name, name, parameters, polling=not no_wait)
        if not no_wait:
            return poller.result().value.as_dict()
        else:
            module_logger.info(f"Diagnose request initiated for workspace:{name}`\n")
            return poller

    def _populate_arm_paramaters(self, workspace: Workspace) -> None:
        if not workspace.location:
            workspace.location = get_resource_group_location(
                self._credentials, self._subscription_id, self._resource_group_name
            )

        self.template = get_template(resource_type=ArmConstants.WORKSPACE_BASE)
        self.param = get_template(resource_type=ArmConstants.WORKSPACE_PARAM)
        self._set_val(self.param["workspaceName"], workspace.name)
        if not workspace.display_name:
            self._set_val(self.param["friendlyName"], workspace.name)
        else:
            self._set_val(self.param["friendlyName"], workspace.display_name)

        if not workspace.description:
            self._set_val(self.param["description"], workspace.name)
        else:
            self._set_val(self.param["description"], workspace.description)
        self._set_val(self.param["location"], workspace.location)

        resource_group_for_new_resources = workspace.resource_group or self._resource_group_name
        self._set_val(self.param["resourceGroupName"], resource_group_for_new_resources)

        if workspace.key_vault:
            resource_name, group_name = get_resource_and_group_name(workspace.key_vault)
            self._set_val(self.param["keyVaultName"], resource_name)
            self._set_val(self.param["keyVaultOption"], "existing")
            self._set_val(self.param["keyVaultResourceGroupName"], group_name)
        else:
            self._generate_key_vault(workspace.name)
            self._set_val(self.param["keyVaultName"], self.keyVault)
            self._set_val(self.param["keyVaultResourceGroupName"], resource_group_for_new_resources)

        if workspace.storage_account:
            resource_name, group_name = get_resource_and_group_name(workspace.storage_account)
            self._set_val(self.param["storageAccountName"], resource_name)
            self._set_val(self.param["storageAccountOption"], "existing")
            self._set_val(self.param["storageAccountResourceGroupName"], group_name)
        else:
            self._generate_storage(workspace.name)
            self._set_val(self.param["storageAccountName"], self.storage)
            self._set_val(self.param["storageAccountResourceGroupName"], resource_group_for_new_resources)

        if workspace.application_insights:
            resource_name, group_name = get_resource_and_group_name(workspace.application_insights)
            self._set_val(self.param["applicationInsightsName"], resource_name)
            self._set_val(self.param["applicationInsightsOption"], "existing")
            self._set_val(
                self.param["applicationInsightsResourceGroupName"],
                group_name,
            )
        else:
            self._generate_appInsights(workspace.name)
            self._set_val(self.param["applicationInsightsName"], self.appInsights)
            self._set_val(self.param["applicationInsightsResourceGroupName"], resource_group_for_new_resources)

        if workspace.container_registry:
            resource_name, group_name = get_resource_and_group_name(workspace.container_registry)
            self._set_val(self.param["containerRegistryName"], resource_name)
            self._set_val(self.param["containerRegistryOption"], "existing")
            self._set_val(self.param["containerRegistryResourceGroupName"], group_name)

        if workspace.customer_managed_key:
            self._set_val(self.param["cmk_keyvault"], workspace.customer_managed_key.key_vault)
            self._set_val(self.param["resource_cmk_uri"], workspace.customer_managed_key.key_uri)
            self._set_val(self.param["encryption_status"], WorkspaceResourceConstants.ENCRYPTION_STATUS_ENABLED)
            self._set_val(self.param["encryption_cosmosdb_resourceid"], workspace.customer_managed_key.cosmosdb_id)
            self._set_val(self.param["encryption_storage_resourceid"], workspace.customer_managed_key.storage_id)
            self._set_val(self.param["encryption_search_resourceid"], workspace.customer_managed_key.search_id)

        if workspace.hbi_workspace:
            self._set_val(self.param["confidential_data"], "true")

        if workspace.public_network_access:
            self._set_val(self.param["publicNetworkAccess"], workspace.public_network_access)

        if workspace.image_build_compute:
            self._set_val(self.param["imageBuildCompute"], workspace.image_build_compute)

        if workspace.tags:
            for key, val in workspace.tags.items():
                self.param["tagValues"]["value"][key] = val

        if workspace.softdelete_enable:
            self._set_val(self.param["soft_delete_enabled"], "true")

        if workspace.allow_recover_softdeleted_workspace:
            self._set_val(self.param["allow_recover_softdeleted_workspace"], "true")

        self.resources_being_deployed[workspace.name] = (ArmConstants.WORKSPACE, None)

    def _set_val(self, key: str, val: str) -> None:
        key["value"] = val

    def _generate_key_vault(self, name: str) -> None:
        # Vault name must only contain alphanumeric characters and dashes and cannot start with a number.
        # Vault name must be between 3-24 alphanumeric characters.
        # The name must begin with a letter, end with a letter or digit, and not contain consecutive hyphens.
        self.keyVault = get_name_for_dependent_resource(name, "keyvault")
        self.resources_being_deployed[self.keyVault] = (ArmConstants.KEY_VAULT, None)

    def _generate_storage(self, name: str) -> None:
        self.storage = get_name_for_dependent_resource(name, "storage")
        self.resources_being_deployed[self.storage] = (ArmConstants.STORAGE, None)

    def _generate_appInsights(self, name: str) -> None:
        # Application name only allows alphanumeric characters, periods, underscores,
        # hyphens and parenthesis and cannot end in a period
        self.appInsights = get_name_for_dependent_resource(name, "insights")
        self.resources_being_deployed[self.appInsights] = (ArmConstants.APP_INSIGHTS, None)

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
        else:
            return workspace_name
