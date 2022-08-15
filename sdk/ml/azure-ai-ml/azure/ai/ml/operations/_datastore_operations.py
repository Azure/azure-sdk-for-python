# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from typing import Dict, Iterable

from azure.ai.ml._restclient.v2022_05_01 import AzureMachineLearningWorkspaces as ServiceClient2022_05_01
from azure.ai.ml._restclient.v2022_05_01.models import DatastoreData, DatastoreSecrets, NoneDatastoreCredentials
from azure.ai.ml._scope_dependent_operations import OperationScope, _ScopeDependentOperations
from azure.ai.ml._telemetry import AML_INTERNAL_LOGGER_NAMESPACE, ActivityType, monitor_with_activity
from azure.ai.ml.entities._datastore.datastore import Datastore

logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE + __name__)
logger.propagate = False

module_logger = logging.getLogger(__name__)


class DatastoreOperations(_ScopeDependentOperations):
    """Represents a client for performing operations on Datastores.

    You should not instantiate this class directly. Instead, you should
    create MLClient and use this client via the property
    MLClient.datastores
    """

    def __init__(
        self, operation_scope: OperationScope, serviceclient_2022_05_01: ServiceClient2022_05_01, **kwargs: Dict
    ):
        super(DatastoreOperations, self).__init__(operation_scope)
        if "app_insights_handler" in kwargs:
            logger.addHandler(kwargs.pop("app_insights_handler"))
        self._operation = serviceclient_2022_05_01.datastores
        self._credential = serviceclient_2022_05_01._config.credential
        self._init_kwargs = kwargs

    @monitor_with_activity(logger, "Datastore.List", ActivityType.PUBLICAPI)
    def list(self, *, include_secrets: bool = False) -> Iterable[Datastore]:
        """Lists all datastores and associated information within a workspace.

        :param include_secrets: Include datastore secrets in returned datastores, defaults to False
        :type include_secrets: bool, optional
        :return: An iterator like instance of Datastore objects
        :rtype: ~azure.core.paging.ItemPaged[Datastore]
        """

        def _list_helper(datastore_resource, include_secrets: bool):
            if include_secrets:
                self._fetch_and_populate_secret(datastore_resource)
            return Datastore._from_rest_object(datastore_resource)

        return self._operation.list(
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            cls=lambda objs: [_list_helper(obj, include_secrets) for obj in objs],
            **self._init_kwargs
        )

    @monitor_with_activity(logger, "Datastore.ListSecrets", ActivityType.PUBLICAPI)
    def _list_secrets(self, name: str) -> DatastoreSecrets:
        return self._operation.list_secrets(
            name=name,
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            **self._init_kwargs
        )

    @monitor_with_activity(logger, "Datastore.Delete", ActivityType.PUBLICAPI)
    def delete(self, name: str) -> None:
        """Deletes a datastore reference with the given name from the
        workspace. This method does not delete the actual datastore or
        underlying data in the datastore.

        :param name: Name of the datastore
        :type name: str
        """

        return self._operation.delete(
            name=name,
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            **self._init_kwargs
        )

    @monitor_with_activity(logger, "Datastore.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, *, include_secrets: bool = False) -> Datastore:
        """Returns information about the datastore referenced by the given
        name.

        :param name: Datastore name
        :type name: str
        :param include_secrets: Include datastore secrets in the returned datastore, defaults to False
        :type include_secrets: bool, optional
        :return: Datastore with the specified name.
        :rtype: Datastore
        """

        datastore_resource = self._operation.get(
            name=name,
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            **self._init_kwargs
        )
        if include_secrets:
            self._fetch_and_populate_secret(datastore_resource)
        return Datastore._from_rest_object(datastore_resource)

    def _fetch_and_populate_secret(self, datastore_resource: DatastoreData) -> None:
        if datastore_resource.name and not isinstance(
            datastore_resource.properties.credentials, NoneDatastoreCredentials
        ):
            secrets = self._list_secrets(datastore_resource.name)
            datastore_resource.properties.credentials.secrets = secrets

    @monitor_with_activity(logger, "Datastore.GetDefault", ActivityType.PUBLICAPI)
    def get_default(self, *, include_secrets: bool = False) -> Datastore:
        """Returns the workspace's default datastore.

        :param include_secrets: Include datastore secrets in the returned datastore, defaults to False
        :type include_secrets: bool, optional
        :return: The default datastore.
        :rtype: Datastore
        """

        datastore_resource = self._operation.list(
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            is_default=True,
            **self._init_kwargs
        ).next()
        if include_secrets:
            self._fetch_and_populate_secret(datastore_resource)
        return Datastore._from_rest_object(datastore_resource)

    @monitor_with_activity(logger, "Datastore.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(self, datastore: Datastore) -> Datastore:
        """Attaches the passed in datastore to the workspace or updates the
        datastore if it already exists.

        :param datastore: The configuration of the datastore to attach.
        :type datastore: Datastore
        :return: The attached datastore.
        :rtype: Datastore
        """
        ds_request = datastore._to_rest_object()
        datastore_resource = self._operation.create_or_update(
            name=datastore.name,
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            body=ds_request,
            skip_validation=True,
        )
        return Datastore._from_rest_object(datastore_resource)
