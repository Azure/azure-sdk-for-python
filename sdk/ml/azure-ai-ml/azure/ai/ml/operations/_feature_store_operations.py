# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import uuid
from typing import Dict, Iterable, Optional

from marshmallow import ValidationError

from azure.ai.ml._restclient.v2023_06_01_preview import AzureMachineLearningWorkspaces as ServiceClient062023Preview
from azure.ai.ml._restclient.v2023_06_01_preview.models import ManagedNetworkProvisionOptions
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants import ManagedServiceIdentityType
from azure.ai.ml.constants._common import Scope
from azure.ai.ml.entities import (
    IdentityConfiguration,
    ManagedIdentityConfiguration,
    ManagedNetworkProvisionStatus,
    WorkspaceConnection,
)
from azure.ai.ml.entities._feature_store._constants import (
    FEATURE_STORE_KIND,
    OFFLINE_MATERIALIZATION_STORE_TYPE,
    OFFLINE_STORE_CONNECTION_CATEGORY,
    OFFLINE_STORE_CONNECTION_NAME,
    ONLINE_MATERIALIZATION_STORE_TYPE,
    ONLINE_STORE_CONNECTION_CATEGORY,
    ONLINE_STORE_CONNECTION_NAME,
)
from azure.ai.ml.entities._feature_store.feature_store import FeatureStore
from azure.ai.ml.entities._feature_store.materialization_store import MaterializationStore
from azure.ai.ml.entities._workspace.feature_store_settings import FeatureStoreSettings
from azure.core.credentials import TokenCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

from ._workspace_operations_base import WorkspaceOperationsBase

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger


class FeatureStoreOperations(WorkspaceOperationsBase):
    """FeatureStoreOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: ServiceClient062023Preview,
        all_operations: OperationsContainer,
        credentials: Optional[TokenCredential] = None,
        **kwargs: Dict,
    ):
        ops_logger.update_info(kwargs)
        self._provision_network_operation = service_client.managed_network_provisions
        super().__init__(
            operation_scope=operation_scope,
            service_client=service_client,
            all_operations=all_operations,
            credentials=credentials,
            **kwargs,
        )
        self._workspace_connection_operation = service_client.workspace_connections

    @distributed_trace
    @monitor_with_activity(logger, "FeatureStore.List", ActivityType.PUBLICAPI)
    # pylint: disable=unused-argument
    def list(self, *, scope: str = Scope.RESOURCE_GROUP, **kwargs: Dict) -> Iterable[FeatureStore]:
        """List all feature stores that the user has access to in the current
        resource group or subscription.

        :keyword scope: scope of the listing, "resource_group" or "subscription", defaults to "resource_group"
        :paramtype scope: str
        :return: An iterator like instance of FeatureStore objects
        :rtype: ~azure.core.paging.ItemPaged[FeatureStore]
        """

        if scope == Scope.SUBSCRIPTION:
            return self._operation.list_by_subscription(
                cls=lambda objs: [
                    FeatureStore._from_rest_object(filterObj)
                    for filterObj in filter(lambda ws: ws.kind.lower() == FEATURE_STORE_KIND, objs)
                ],
            )
        return self._operation.list_by_resource_group(
            self._resource_group_name,
            cls=lambda objs: [
                FeatureStore._from_rest_object(filterObj)
                for filterObj in filter(lambda ws: ws.kind.lower() == FEATURE_STORE_KIND, objs)
            ],
        )

    @distributed_trace
    @monitor_with_activity(logger, "FeatureStore.Get", ActivityType.PUBLICAPI)
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
        rest_workspace_obj = kwargs.get("rest_workspace_obj", None) or self._operation.get(resource_group, name)
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
            if (
                offline_store_connection and offline_store_connection.name.startswith(OFFLINE_STORE_CONNECTION_NAME)
            ) or (online_store_connection and online_store_connection.name.startswith(ONLINE_STORE_CONNECTION_NAME)):
                if (
                    feature_store.identity
                    and feature_store.identity.user_assigned_identities
                    and isinstance(feature_store.identity.user_assigned_identities[0], ManagedIdentityConfiguration)
                ):
                    feature_store.materialization_identity = feature_store.identity.user_assigned_identities[0]

        return feature_store

    @distributed_trace
    @monitor_with_activity(logger, "FeatureStore.BeginCreate", ActivityType.PUBLICAPI)
    # pylint: disable=arguments-differ
    def begin_create(
        self,
        feature_store: FeatureStore,
        *,
        grant_materialization_permissions: bool = True,
        update_dependent_resources: bool = False,
        **kwargs: Dict,
    ) -> LROPoller[FeatureStore]:
        """Create a new FeatureStore.

        Returns the feature store if already exists.

        :param feature_store: FeatureStore definition.
        :type feature_store: FeatureStore
        :type update_dependent_resources: boolean
        :return: An instance of LROPoller that returns a FeatureStore.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.FeatureStore]
        """
        resource_group = kwargs.get("resource_group", self._resource_group_name)
        try:
            rest_workspace_obj = self._operation.get(resource_group, feature_store.name)
            if rest_workspace_obj:
                return self.begin_update(
                    feature_store=feature_store, update_dependent_resources=update_dependent_resources, kwargs=kwargs
                )
        except Exception:  # pylint: disable=broad-except
            pass

        if feature_store.offline_store and feature_store.offline_store.type != OFFLINE_MATERIALIZATION_STORE_TYPE:
            raise ValidationError("offline store type should be azure_data_lake_gen2")

        if feature_store.online_store and feature_store.online_store.type != ONLINE_MATERIALIZATION_STORE_TYPE:
            raise ValidationError("online store type should be redis")

        # generate a random suffix for online/offline store connection name,
        # please don't refer to OFFLINE_STORE_CONNECTION_NAME and
        # ONLINE_STORE_CONNECTION_NAME directly from FeatureStore
        random_string = uuid.uuid4().hex[:8]
        feature_store._feature_store_settings.offline_store_connection_name = (
            f"{OFFLINE_STORE_CONNECTION_NAME}-{random_string}"
        )
        feature_store._feature_store_settings.online_store_connection_name = (
            f"{ONLINE_STORE_CONNECTION_NAME}-{random_string}"
            if feature_store.online_store and feature_store.online_store.target
            else None
        )

        def get_callback():
            return self.get(feature_store.name)

        return super().begin_create(
            workspace=feature_store,
            update_dependent_resources=update_dependent_resources,
            get_callback=get_callback,
            offline_store_target=feature_store.offline_store.target if feature_store.offline_store else None,
            online_store_target=feature_store.online_store.target if feature_store.online_store else None,
            materialization_identity=feature_store.materialization_identity,
            grant_materialization_permissions=grant_materialization_permissions,
            **kwargs,
        )

    @distributed_trace
    @monitor_with_activity(logger, "FeatureStore.BeginUpdate", ActivityType.PUBLICAPI)
    # pylint: disable=arguments-renamed
    # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    def begin_update(
        self,
        feature_store: FeatureStore,
        *,
        grant_materialization_permissions: bool = True,
        update_dependent_resources: bool = False,
        **kwargs: Dict,
    ) -> LROPoller[FeatureStore]:
        """Update friendly name, description, online store connection, offline store connection, materialization
            identities or tags of a feature store.

        :param feature_store: FeatureStore resource.
        :type feature_store: FeatureStore
        :keyword update_dependent_resources: gives your consent to update the feature store dependent resources.
            Note that updating the feature store attached Azure Container Registry resource may break lineage
            of previous jobs or your ability to rerun earlier jobs in this feature store.
            Also, updating the feature store attached Azure Application Insights resource may break lineage of
            deployed inference endpoints this feature store. Only set this argument if you are sure that you want
            to perform this operation. If this argument is not set, the command to update
            Azure Container Registry and Azure Application Insights will fail.
        :keyword application_insights: Application insights resource for feature store. Defaults to None.
        :paramtype application_insights: Optional[str]
        :keyword container_registry: Container registry resource for feature store. Defaults to None.
        :paramtype container_registry: Optional[str]
        :return: An instance of LROPoller that returns a FeatureStore.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.FeatureStore]
        """
        resource_group = kwargs.get("resource_group", self._resource_group_name)
        rest_workspace_obj = self._operation.get(resource_group, feature_store.name)
        if not (
            rest_workspace_obj and rest_workspace_obj.kind and rest_workspace_obj.kind.lower() == FEATURE_STORE_KIND
        ):
            raise ValidationError("{0} is not a feature store".format(feature_store.name))

        resource_group = kwargs.get("resource_group") or self._resource_group_name
        offline_store = kwargs.get("offline_store", feature_store.offline_store)
        online_store = kwargs.get("online_store", feature_store.online_store)
        offline_store_target_to_update = offline_store.target if offline_store else None
        online_store_target_to_update = online_store.target if online_store else None
        update_workspace_role_assignment = False
        update_offline_store_role_assignment = False
        update_online_store_role_assignment = False

        update_offline_store_connection = False
        update_online_store_connection = False

        existing_materialization_identity = None
        if rest_workspace_obj.identity:
            identity = IdentityConfiguration._from_workspace_rest_object(rest_workspace_obj.identity)
            if (
                identity
                and identity.user_assigned_identities
                and isinstance(identity.user_assigned_identities[0], ManagedIdentityConfiguration)
            ):
                existing_materialization_identity = identity.user_assigned_identities[0]

        materialization_identity = kwargs.get(
            "materialization_identity", feature_store.materialization_identity or existing_materialization_identity
        )

        if (
            feature_store.materialization_identity
            and feature_store.materialization_identity.resource_id
            and (
                not existing_materialization_identity
                or feature_store.materialization_identity.resource_id != existing_materialization_identity.resource_id
            )
        ):
            update_workspace_role_assignment = True
            update_offline_store_role_assignment = True
            update_online_store_role_assignment = True

        if offline_store and offline_store.type != OFFLINE_MATERIALIZATION_STORE_TYPE:
            raise ValidationError("offline store type should be azure_data_lake_gen2")

        if (
            rest_workspace_obj.feature_store_settings
            and rest_workspace_obj.feature_store_settings.offline_store_connection_name
        ):
            existing_offline_store_connection = self._workspace_connection_operation.get(
                resource_group,
                feature_store.name,
                rest_workspace_obj.feature_store_settings.offline_store_connection_name,
            )

            offline_store_target_to_update = (
                offline_store_target_to_update or existing_offline_store_connection.properties.target
            )
            if offline_store and (
                not existing_offline_store_connection.properties
                or existing_offline_store_connection.properties.target != offline_store.target
            ):
                update_offline_store_connection = True
                update_offline_store_role_assignment = True
                module_logger.info(
                    "Warning: You have changed the offline store connection, "
                    "any data that was materialized "
                    "earlier will not be available. You have to run backfill again."
                )
        elif offline_store_target_to_update:
            update_offline_store_connection = True
            update_offline_store_role_assignment = True

        if online_store and online_store.type != ONLINE_MATERIALIZATION_STORE_TYPE:
            raise ValidationError("online store type should be redis")

        if (
            rest_workspace_obj.feature_store_settings
            and rest_workspace_obj.feature_store_settings.online_store_connection_name
        ):
            existing_online_store_connection = self._workspace_connection_operation.get(
                resource_group,
                feature_store.name,
                rest_workspace_obj.feature_store_settings.online_store_connection_name,
            )

            online_store_target_to_update = (
                online_store_target_to_update or existing_online_store_connection.properties.target
            )
            if online_store and (
                not existing_online_store_connection.properties
                or existing_online_store_connection.properties.target != online_store.target
            ):
                update_online_store_connection = True
                update_online_store_role_assignment = True
                module_logger.info(
                    "Warning: You have changed the online store connection, "
                    "any data that was materialized earlier "
                    "will not be available. You have to run backfill again."
                )
        elif online_store_target_to_update:
            update_online_store_connection = True
            update_online_store_role_assignment = True

        feature_store_settings = FeatureStoreSettings._from_rest_object(rest_workspace_obj.feature_store_settings)

        # generate a random suffix for online/offline store connection name
        random_string = uuid.uuid4().hex[:8]
        if offline_store:
            if materialization_identity:
                if update_offline_store_connection:
                    offline_store_connection_name_new = f"{OFFLINE_STORE_CONNECTION_NAME}-{random_string}"
                    offline_store_connection = WorkspaceConnection(
                        name=offline_store_connection_name_new,
                        type=offline_store.type,
                        target=offline_store.target,
                        credentials=materialization_identity,
                    )
                    rest_offline_store_connection = offline_store_connection._to_rest_object()
                    self._workspace_connection_operation.create(
                        resource_group_name=resource_group,
                        workspace_name=feature_store.name,
                        connection_name=offline_store_connection_name_new,
                        body=rest_offline_store_connection,
                    )
                    feature_store_settings.offline_store_connection_name = offline_store_connection_name_new
                else:
                    module_logger.info(
                        "No need to update Offline store connection, name: %s.\n",
                        feature_store_settings.offline_store_connection_name,
                    )
            else:
                raise ValidationError("Materialization identity is required to setup offline store connection")

        if online_store:
            if materialization_identity:
                if update_online_store_connection:
                    online_store_connection_name_new = f"{ONLINE_STORE_CONNECTION_NAME}-{random_string}"
                    online_store_connection = WorkspaceConnection(
                        name=online_store_connection_name_new,
                        type=online_store.type,
                        target=online_store.target,
                        credentials=materialization_identity,
                    )
                    rest_online_store_connection = online_store_connection._to_rest_object()
                    self._workspace_connection_operation.create(
                        resource_group_name=resource_group,
                        workspace_name=feature_store.name,
                        connection_name=online_store_connection_name_new,
                        body=rest_online_store_connection,
                    )
                    feature_store_settings.online_store_connection_name = online_store_connection_name_new
                else:
                    module_logger.info(
                        "No need to update Online store connection, name: %s.\n",
                        feature_store_settings.online_store_connection_name,
                    )
            else:
                raise ValidationError("Materialization identity is required to setup online store connection")

        if not offline_store_target_to_update:
            update_offline_store_role_assignment = False
        if not online_store_target_to_update:
            update_online_store_role_assignment = False

        identity = kwargs.pop("identity", feature_store.identity)
        if materialization_identity:
            identity = IdentityConfiguration(
                type=camel_to_snake(ManagedServiceIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED),
                # At most 1 UAI can be attached to workspace when materialization is enabled
                user_assigned_identities=[materialization_identity],
            )

        def deserialize_callback(rest_obj):
            return self.get(rest_obj.name, rest_workspace_obj=rest_obj)

        return super().begin_update(
            workspace=feature_store,
            update_dependent_resources=update_dependent_resources,
            deserialize_callback=deserialize_callback,
            feature_store_settings=feature_store_settings,
            identity=identity,
            grant_materialization_permissions=grant_materialization_permissions,
            update_workspace_role_assignment=update_workspace_role_assignment,
            update_offline_store_role_assignment=update_offline_store_role_assignment,
            update_online_store_role_assignment=update_online_store_role_assignment,
            materialization_identity_id=materialization_identity.resource_id
            if update_workspace_role_assignment
            or update_offline_store_role_assignment
            or update_online_store_role_assignment
            else None,
            offline_store_target=offline_store_target_to_update if update_offline_store_role_assignment else None,
            online_store_target=online_store_target_to_update if update_online_store_role_assignment else None,
            **kwargs,
        )

    @distributed_trace
    @monitor_with_activity(logger, "FeatureStore.BeginDelete", ActivityType.PUBLICAPI)
    def begin_delete(self, name: str, *, delete_dependent_resources: bool = False, **kwargs: Dict) -> LROPoller[None]:
        """Delete a FeatureStore.

        :param name: Name of the FeatureStore
        :type name: str
        :keyword delete_dependent_resources: Whether to delete resources associated with the feature store,
            i.e., container registry, storage account, key vault, and application insights.
            The default is False. Set to True to delete these resources.
        :paramtype delete_dependent_resources: bool
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

    @distributed_trace
    @monitor_with_activity(logger, "FeatureStore.BeginProvisionNetwork", ActivityType.PUBLICAPI)
    def begin_provision_network(
        self,
        *,
        feature_store_name: Optional[str] = None,
        include_spark: Optional[bool] = False,
        **kwargs,
    ) -> LROPoller[ManagedNetworkProvisionStatus]:
        """Triggers the feature store to provision the managed network. Specifying spark enabled
        as true prepares the feature store managed network for supporting Spark.

        :keyword feature_store_name: Name of the feature store.
        :paramtype feature_store_name: str
        :return: An instance of LROPoller.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.ManagedNetworkProvisionStatus]
        """
        workspace_name = self._check_workspace_name(feature_store_name)

        poller = self._provision_network_operation.begin_provision_managed_network(
            self._resource_group_name,
            workspace_name,
            ManagedNetworkProvisionOptions(include_spark=include_spark),
            polling=True,
            cls=lambda response, deserialized, headers: ManagedNetworkProvisionStatus._from_rest_object(deserialized),
            **kwargs,
        )
        module_logger.info("Provision network request initiated for feature store: %s\n", workspace_name)
        return poller
