# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, Iterable, Optional

from azure.ai.ml._restclient.v2022_10_01_preview import AzureMachineLearningWorkspaces as ServiceClient102022Preview
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope

# from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.constants._common import Scope
from azure.ai.ml.entities import Workspace, FeatureStore
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace
from ._workspace_operations import WorkspaceOperations
from azure.ai.ml.constants._common import AzureMLResourceType

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class FeatureStoreOperations():
    """FeatureStoreOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: ServiceClient102022Preview,
        operations_container: OperationsContainer,
        **kwargs: Dict,
    ):
        self._operations_container = operations_container
        self._workspace_operation = service_client.workspaces
        self._resource_group_name = operation_scope.resource_group_name

    # @monitor_with_activity(logger, "FeatureStore.List", ActivityType.PUBLICAPI)
    def list(self, *, scope: str = Scope.RESOURCE_GROUP) -> Iterable[FeatureStore]:
        """List all feature stores that the user has access to in the current
        resource group or subscription.

        :param scope: scope of the listing, "resource_group" or "subscription", defaults to "resource_group"
        :type scope: str, optional
        :return: An iterator like instance of FeatureStore objects
        :rtype: ~azure.core.paging.ItemPaged[FeatureStore]
        """

        if scope == Scope.SUBSCRIPTION:
            return self._workspace_operation.list_by_subscription(
            cls=lambda objs: [
                FeatureStore._from_rest_object(filterObj) for filterObj in filter(lambda ws: ws.kind == "FeatureStore", objs)]
            )
        return self._workspace_operation.list_by_resource_group(
            self._resource_group_name,
            cls=lambda objs: [
                FeatureStore._from_rest_object(filterObj) for filterObj in filter(lambda ws: ws.kind == "FeatureStore", objs)]
        )

    # @monitor_with_activity(logger, "FeatureStore.Get", ActivityType.PUBLICAPI)
    @distributed_trace
    def get(self, name: str, **kwargs: Dict) -> FeatureStore:
        """Get a feature store by name.

        :param name: Name of the feature store.
        :type name: str
        :return: The feature store with the provided name.
        :rtype: FeatureStore
        """

        resource_group = kwargs.get("resource_group") or self._resource_group_name
        obj = self._workspace_operation.get(resource_group, name)
        return FeatureStore._from_rest_object(obj)

    # @monitor_with_activity(logger, "FeatureStore.BeginCreate", ActivityType.PUBLICAPI)
    @distributed_trace
    def begin_create(
        self,
        feature_store: FeatureStore,
        update_dependent_resources: bool = False,
        **kwargs: Dict,
    ) -> LROPoller[FeatureStore]:
        """Create a new FeatureStore.

        Returns the feature store if already exists.

        :param feature store: FeatureStore definition.
        :type feature store: FeatureStore
        :type update_dependent_resources: boolean
        :return: An instance of LROPoller that returns a FeatureStore.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.FeatureStore]
        """
        return self._operations_container.all_operations[AzureMLResourceType.WORKSPACE].begin_create(
            workspace=feature_store,
            update_dependent_resources=update_dependent_resources,
            get_feature_store_poller=True,
            *kwargs
        )

    # @monitor_with_activity(logger, "FeatureStore.BeginUpdate", ActivityType.PUBLICAPI)
    @distributed_trace
    def begin_update(
        self,
        feature_store: FeatureStore,
        *,
        update_dependent_resources: bool = False,
        **kwargs: Dict,
    ) -> LROPoller[FeatureStore]:
        """Update friendly name, description, managed identities or tags of a feature store.

        :param feature store: FeatureStore resource.
        :param update_dependent_resources: gives your consent to update the feature store dependent resources.
            Note that updating the feature store attached Azure Container Registry resource may break lineage
            of previous jobs or your ability to rerun earlier jobs in this feature store.
            Also, updating the feature store attached Azure Application Insights resource may break lineage of
            deployed inference endpoints this feature store. Only set this argument if you are sure that you want
            to perform this operation. If this argument is not set, the command to update
            Azure Container Registry and Azure Application Insights will fail.
        :param application_insights: Application insights resource for feature store.
        :param container_registry: Container registry resource for feature store.
        :type feature store: FeatureStore
        :return: An instance of LROPoller that returns a FeatureStore.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.FeatureStore]
        """
        return self._operations_container.all_operations[AzureMLResourceType.WORKSPACE].begin_update(
            workspace=feature_store,
            update_dependent_resources=update_dependent_resources,
            get_feature_store_poller=True,
            **kwargs
        )

    # @monitor_with_activity(logger, "FeatureStore.BeginDelete", ActivityType.PUBLICAPI)
    @distributed_trace
    def begin_delete(self, feature_store: str, *, delete_dependent_resources: bool, **kwargs: Dict) -> LROPoller:
        """Delete a FeatureStore.

        :param name: Name of the FeatureStore
        :type name: str
        :param delete_dependent_resources: Whether to delete resources associated with the feature store,
            i.e., container registry, storage account, key vault, and application insights.
            The default is False. Set to True to delete these resources.
        :type delete_dependent_resources: bool
        :return: A poller to track the operation status.
        :rtype: ~azure.core.polling.LROPoller[None]
        """
        return self._operations_container.all_operations[AzureMLResourceType.WORKSPACE].begin_delete(
            workspace=feature_store,
            delete_dependent_resources=delete_dependent_resources,
            **kwargs
        )
