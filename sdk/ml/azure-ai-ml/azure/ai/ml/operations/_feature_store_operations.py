# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, Iterable, Optional

from marshmallow import ValidationError

from azure.ai.ml._restclient.v2023_04_01_preview import AzureMachineLearningWorkspaces as ServiceClient042023Preview
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope

# from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities._feature_store.feature_store import FeatureStore
from azure.ai.ml.entities._workspace.feature_store_settings import FeatureStoreSettings
from azure.ai.ml.entities._feature_store.materialization_store import MaterializationStore
from azure.ai.ml.entities import (
    ManagedIdentityConfiguration,
    IdentityConfiguration,
    WorkspaceConnection,
)
from azure.ai.ml.constants._common import Scope
from azure.ai.ml.entities._feature_store._constants import (
    OFFLINE_STORE_CONNECTION_NAME,
    OFFLINE_MATERIALIZATION_STORE_TYPE,
    OFFLINE_STORE_CONNECTION_CATEGORY,
    ONLINE_STORE_CONNECTION_NAME,
    ONLINE_MATERIALIZATION_STORE_TYPE,
    ONLINE_STORE_CONNECTION_CATEGORY,
    FEATURE_STORE_KIND,
)
from azure.ai.ml.constants import ManagedServiceIdentityType
from azure.ai.ml._utils.utils import camel_to_snake
from ._workspace_operations_base import WorkspaceOperationsBase

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class FeatureStoreOperations(WorkspaceOperationsBase):
    """FeatureStoreOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: ServiceClient042023Preview,
        all_operations: OperationsContainer,
        credentials: Optional[TokenCredential] = None,
        **kwargs: Dict,
    ):
        ops_logger.update_info(kwargs)
        super().__init__(
            operation_scope=operation_scope,
            service_client=service_client,
            all_operations=all_operations,
            credentials=credentials,
            **kwargs,
        )
        self._workspace_connection_operation = service_client.workspace_connections

    # @monitor_with_activity(logger, "FeatureStore.List", ActivityType.PUBLICAPI)
    def list(self, *, scope: str = Scope.RESOURCE_GROUP, **kwargs: Dict) -> Iterable[FeatureStore]:
        """List all feature stores that the user has access to in the current
        resource group or subscription.

        :param scope: scope of the listing, "resource_group" or "subscription", defaults to "resource_group"
        :type scope: str, optional
        :return: An iterator like instance of FeatureStore objects
        :rtype: ~azure.core.paging.ItemPaged[FeatureStore]
        """

        if scope == Scope.SUBSCRIPTION:
            return self._operation.list_by_subscription(
                **kwargs,
                cls=lambda objs: [
                    FeatureStore._from_rest_object(filterObj)
                    for filterObj in filter(lambda ws: ws.kind.lower() == FEATURE_STORE_KIND, objs)
                ],
            )
        return self._operation.list_by_resource_group(
            self._resource_group_name,
            **kwargs,
            cls=lambda objs: [
                FeatureStore._from_rest_object(filterObj)
                for filterObj in filter(lambda ws: ws.kind.lower() == FEATURE_STORE_KIND, objs)
            ],
        )

    # @monitor_with_activity(logger, "FeatureStore.Get", ActivityType.PUBLICAPI)
    @distributed_trace
    # pylint: disable=arguments-renamed
    def get(self, name: str, **kwargs: Dict) -> FeatureStore:
        """Get a feature store by name.

        :param name: Name of the feature store.
        :type name: str
        :return: The feature store with the provided name.
        :rtype: FeatureStore
        """

        feature_store = None
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        rest_workspace_obj = self._operation.get(resource_group, name, **kwargs)
        if rest_workspace_obj and rest_workspace_obj.kind and rest_workspace_obj.kind.lower() == FEATURE_STORE_KIND:
            feature_store = FeatureStore._from_rest_object(rest_workspace_obj)

        if feature_store:
            offline_store_connection = None
            if (
                rest_workspace_obj.feature_store_settings
                and rest_workspace_obj.feature_store_settings.offline_store_connection_name
            ):
                try:
                    offline_store_connection = self._workspace_connection_operation.get(
                        resource_group, name, rest_workspace_obj.feature_store_settings.offline_store_connection_name
                    )
                except ResourceNotFoundError:
                    pass

            if offline_store_connection:
                if (
                    offline_store_connection.properties
                    and offline_store_connection.properties.category == OFFLINE_STORE_CONNECTION_CATEGORY
                ):
                    feature_store.offline_store = MaterializationStore(
                        type=OFFLINE_MATERIALIZATION_STORE_TYPE, target=offline_store_connection.properties.target
                    )

            online_store_connection = None
            if (
                rest_workspace_obj.feature_store_settings
                and rest_workspace_obj.feature_store_settings.online_store_connection_name
            ):
                try:
                    online_store_connection = self._workspace_connection_operation.get(
                        resource_group, name, rest_workspace_obj.feature_store_settings.online_store_connection_name
                    )
                except ResourceNotFoundError:
                    pass

            if online_store_connection:
                if (
                    online_store_connection.properties
                    and online_store_connection.properties.category == ONLINE_STORE_CONNECTION_CATEGORY
                ):
                    feature_store.online_store = MaterializationStore(
                        type=ONLINE_MATERIALIZATION_STORE_TYPE, target=online_store_connection.properties.target
                    )

            # materialization identity = identity when created through feature store operations
            if (offline_store_connection and offline_store_connection.name == OFFLINE_STORE_CONNECTION_NAME) or (
                online_store_connection and online_store_connection.name == ONLINE_STORE_CONNECTION_NAME
            ):
                if (
                    feature_store.identity
                    and feature_store.identity.user_assigned_identities
                    and isinstance(feature_store.identity.user_assigned_identities[0], ManagedIdentityConfiguration)
                ):
                    feature_store.materialization_identity = feature_store.identity.user_assigned_identities[0]

        return feature_store

    # @monitor_with_activity(logger, "FeatureStore.BeginCreate", ActivityType.PUBLICAPI)
    @distributed_trace
    # pylint: disable=arguments-differ
    def begin_create(
        self,
        feature_store: FeatureStore,
        *,
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
        if feature_store.offline_store and feature_store.offline_store.type != OFFLINE_MATERIALIZATION_STORE_TYPE:
            raise ValidationError("offline store type should be azure_data_lake_gen2")
        if feature_store.offline_store and not feature_store.materialization_identity:
            raise ValidationError("materialization_identity is required to setup offline store")

        if feature_store.online_store and feature_store.online_store.type != ONLINE_MATERIALIZATION_STORE_TYPE:
            raise ValidationError("online store type should be redis")
        if feature_store.online_store and not feature_store.materialization_identity:
            raise ValidationError("materialization_identity is required to setup online store")

        def get_callback():
            return self.get(feature_store.name)

        return super().begin_create(
            workspace=feature_store,
            update_dependent_resources=update_dependent_resources,
            get_callback=get_callback,
            offline_store_target=feature_store.offline_store.target if feature_store.offline_store else None,
            online_store_target=feature_store.online_store.target if feature_store.online_store else None,
            materialization_identity=feature_store.materialization_identity,
            **kwargs,
        )

    # @monitor_with_activity(logger, "FeatureStore.BeginUpdate", ActivityType.PUBLICAPI)
    @distributed_trace
    # pylint: disable=arguments-renamed
    def begin_update(
        self,
        feature_store: FeatureStore,
        *,
        update_dependent_resources: bool = False,
        **kwargs: Dict,
    ) -> LROPoller[FeatureStore]:
        """Update friendly name, description, materialization identities or tags of a feature store.

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
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        rest_workspace_obj = self._operation.get(resource_group, feature_store.name)
        if not (
            rest_workspace_obj and rest_workspace_obj.kind and rest_workspace_obj.kind.lower() == FEATURE_STORE_KIND
        ):
            raise ValidationError("{0} is not a feature store".format(feature_store.name))

        resource_group = kwargs.get("resource_group") or self._resource_group_name
        offline_store = kwargs.get("offline_store", feature_store.offline_store)
        online_store = kwargs.get("online_store", feature_store.online_store)
        materialization_identity = kwargs.get("materialization_identity", feature_store.materialization_identity)

        if offline_store and offline_store.type != OFFLINE_MATERIALIZATION_STORE_TYPE:
            raise ValidationError("offline store type should be azure_data_lake_gen2")

        if offline_store and rest_workspace_obj.feature_store_settings.offline_store_connection_name:
            existing_offline_store_connection = self._workspace_connection_operation.get(
                resource_group,
                feature_store.name,
                rest_workspace_obj.feature_store_settings.offline_store_connection_name,
            )

            if existing_offline_store_connection:
                if (
                    not existing_offline_store_connection.properties
                    or existing_offline_store_connection.properties.target != offline_store.target
                ):
                    module_logger.info(
                        "Warning: You have changed the offline store connection, "
                        "any data that was materialized "
                        "earlier will not be available. You have to run backfill again."
                    )
            else:
                if not materialization_identity:
                    raise ValidationError("Materialization identity is required to setup offline store connection")

        if online_store and online_store.type != ONLINE_MATERIALIZATION_STORE_TYPE:
            raise ValidationError("online store type should be redis")

        if online_store and rest_workspace_obj.feature_store_settings.online_store_connection_name:
            existing_online_store_connection = self._workspace_connection_operation.get(
                resource_group,
                feature_store.name,
                rest_workspace_obj.feature_store_settings.online_store_connection_name,
            )

            if existing_online_store_connection:
                if (
                    not existing_online_store_connection.properties
                    or existing_online_store_connection.properties.target != online_store.target
                ):
                    module_logger.info(
                        "Warning: You have changed the online store connection, "
                        "any data that was materialized earlier "
                        "will not be available. You have to run backfill again."
                    )
            else:
                if not materialization_identity:
                    raise ValidationError("Materialization identity is required to setup online store connection")

        feature_store_settings = FeatureStoreSettings._from_rest_object(rest_workspace_obj.feature_store_settings)

        if offline_store and materialization_identity:
            offline_store_connection_name = (
                feature_store_settings.offline_store_connection_name
                if feature_store_settings.offline_store_connection_name
                else OFFLINE_STORE_CONNECTION_NAME
            )
            offline_store_connection = WorkspaceConnection(
                name=offline_store_connection_name,
                type=offline_store.type,
                target=offline_store.target,
                credentials=materialization_identity,
            )
            rest_offline_store_connection = offline_store_connection._to_rest_object()
            self._workspace_connection_operation.create(
                resource_group_name=resource_group,
                workspace_name=feature_store.name,
                connection_name=offline_store_connection_name,
                parameters=rest_offline_store_connection,
            )
            feature_store_settings.offline_store_connection_name = offline_store_connection_name

        if online_store and materialization_identity:
            online_store_connection_name = (
                feature_store_settings.online_store_connection_name
                if feature_store_settings.online_store_connection_name
                else ONLINE_STORE_CONNECTION_NAME
            )
            online_store_connection = WorkspaceConnection(
                name=online_store_connection_name,
                type=online_store.type,
                target=online_store.target,
                credentials=materialization_identity,
            )
            rest_online_store_connection = online_store_connection._to_rest_object()
            self._workspace_connection_operation.create(
                resource_group_name=resource_group,
                workspace_name=feature_store.name,
                connection_name=online_store_connection_name,
                parameters=rest_online_store_connection,
            )
            feature_store_settings.online_store_connection_name = online_store_connection_name

        identity = kwargs.pop("identity", feature_store.identity)
        if materialization_identity:
            identity = IdentityConfiguration(
                type=camel_to_snake(ManagedServiceIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED),
                # At most 1 UAI can be attached to workspace when materialization is enabled
                user_assigned_identities=[materialization_identity],
            )

        def deserialize_callback(rest_obj):
            return FeatureStore._from_rest_object(rest_obj=rest_obj)

        return super().begin_update(
            workspace=feature_store,
            update_dependent_resources=update_dependent_resources,
            feature_store_settings=feature_store_settings,
            identity=identity,
            deserialize_callback=deserialize_callback,
            **kwargs,
        )

    # @monitor_with_activity(logger, "FeatureStore.BeginDelete", ActivityType.PUBLICAPI)
    @distributed_trace
    def begin_delete(self, name: str, *, delete_dependent_resources: bool, **kwargs: Dict) -> LROPoller[None]:
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
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        rest_workspace_obj = self._operation.get(resource_group, name)
        if not (
            rest_workspace_obj and rest_workspace_obj.kind and rest_workspace_obj.kind.lower() == FEATURE_STORE_KIND
        ):
            raise ValidationError("{0} is not a feature store".format(name))

        return super().begin_delete(name=name, delete_dependent_resources=delete_dependent_resources, **kwargs)
