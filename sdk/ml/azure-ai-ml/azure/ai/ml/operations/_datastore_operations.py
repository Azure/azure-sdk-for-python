# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, Iterable

from marshmallow.exceptions import ValidationError as SchemaValidationError

from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2023_04_01_preview import AzureMachineLearningWorkspaces as ServiceClient042023Preview
from azure.ai.ml._restclient.v2023_04_01_preview.models import Datastore as DatastoreData
from azure.ai.ml._restclient.v2023_04_01_preview.models import DatastoreSecrets, NoneDatastoreCredentials
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope, _ScopeDependentOperations
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities._datastore.datastore import Datastore
from azure.ai.ml.exceptions import ValidationException

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger


class DatastoreOperations(_ScopeDependentOperations):
    """Represents a client for performing operations on Datastores.

    You should not instantiate this class directly. Instead, you should create MLClient and use this client via the
    property MLClient.datastores

    :param operation_scope: Scope variables for the operations classes of an MLClient object.
    :type operation_scope: ~azure.ai.ml._scope_dependent_operations.OperationScope
    :param operation_config: Common configuration for operations classes of an MLClient object.
    :type operation_config: ~azure.ai.ml._scope_dependent_operations.OperationConfig
    :param serviceclient_2022_10_01: Service client to allow end users to operate on Azure Machine Learning Workspace
        resources.
    :type serviceclient_2022_10_01: ~azure.ai.ml._restclient.v2022_10_01._azure_machine_learning_workspaces.
        AzureMachineLearningWorkspaces
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        serviceclient_2023_04_01_preview: ServiceClient042023Preview,
        **kwargs: Dict
    ):
        super(DatastoreOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self._operation = serviceclient_2023_04_01_preview.datastores
        self._credential = serviceclient_2023_04_01_preview._config.credential
        self._init_kwargs = kwargs

    @monitor_with_activity(logger, "Datastore.List", ActivityType.PUBLICAPI)
    def list(self, *, include_secrets: bool = False) -> Iterable[Datastore]:
        """Lists all datastores and associated information within a workspace.

        :keyword include_secrets: Include datastore secrets in returned datastores, defaults to False
        :paramtype include_secrets: bool
        :return: An iterator like instance of Datastore objects
        :rtype: ~azure.core.paging.ItemPaged[Datastore]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_misc.py
                :start-after: [START datastore_operations_list]
                :end-before: [END datastore_operations_list]
                :language: python
                :dedent: 8
                :caption: List datastore example.
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
        """Deletes a datastore reference with the given name from the workspace. This method does not delete the actual
        datastore or underlying data in the datastore.

        :param name: Name of the datastore
        :type name: str

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_misc.py
                :start-after: [START datastore_operations_delete]
                :end-before: [END datastore_operations_delete]
                :language: python
                :dedent: 8
                :caption: Delete datastore example.
        """

        self._operation.delete(
            name=name,
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            **self._init_kwargs
        )

    @monitor_with_activity(logger, "Datastore.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, *, include_secrets: bool = False) -> Datastore:
        """Returns information about the datastore referenced by the given name.

        :param name: Datastore name
        :type name: str
        :keyword include_secrets: Include datastore secrets in the returned datastore, defaults to False
        :paramtype include_secrets: bool
        :return: Datastore with the specified name.
        :rtype: Datastore

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_misc.py
                :start-after: [START datastore_operations_get]
                :end-before: [END datastore_operations_get]
                :language: python
                :dedent: 8
                :caption: Get datastore example.
        """
        try:
            datastore_resource = self._operation.get(
                name=name,
                resource_group_name=self._operation_scope.resource_group_name,
                workspace_name=self._workspace_name,
                **self._init_kwargs
            )
            if include_secrets:
                self._fetch_and_populate_secret(datastore_resource)
            return Datastore._from_rest_object(datastore_resource)
        except (ValidationException, SchemaValidationError) as ex:
            log_and_raise_error(ex)

    def _fetch_and_populate_secret(self, datastore_resource: DatastoreData) -> None:
        if datastore_resource.name and not isinstance(
            datastore_resource.properties.credentials, NoneDatastoreCredentials
        ):
            secrets = self._list_secrets(datastore_resource.name)
            datastore_resource.properties.credentials.secrets = secrets

    @monitor_with_activity(logger, "Datastore.GetDefault", ActivityType.PUBLICAPI)
    def get_default(self, *, include_secrets: bool = False) -> Datastore:
        """Returns the workspace's default datastore.

        :keyword include_secrets: Include datastore secrets in the returned datastore, defaults to False
        :paramtype include_secrets: bool
        :return: The default datastore.
        :rtype: Datastore

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_misc.py
                :start-after: [START datastore_operations_get_default]
                :end-before: [END datastore_operations_get_default]
                :language: python
                :dedent: 8
                :caption: Get default datastore example.
        """
        try:
            datastore_resource = self._operation.list(
                resource_group_name=self._operation_scope.resource_group_name,
                workspace_name=self._workspace_name,
                is_default=True,
                **self._init_kwargs
            ).next()
            if include_secrets:
                self._fetch_and_populate_secret(datastore_resource)
            return Datastore._from_rest_object(datastore_resource)
        except (ValidationException, SchemaValidationError) as ex:
            log_and_raise_error(ex)

    @monitor_with_activity(logger, "Datastore.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(self, datastore: Datastore) -> Datastore:
        """Attaches the passed in datastore to the workspace or updates the datastore if it already exists.

        :param datastore: The configuration of the datastore to attach.
        :type datastore: Datastore
        :return: The attached datastore.
        :rtype: Datastore

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_misc.py
                :start-after: [START datastore_operations_create_or_update]
                :end-before: [END datastore_operations_create_or_update]
                :language: python
                :dedent: 8
                :caption: Create datastore example.
        """
        try:
            ds_request = datastore._to_rest_object()
            datastore_resource = self._operation.create_or_update(
                name=datastore.name,
                resource_group_name=self._operation_scope.resource_group_name,
                workspace_name=self._workspace_name,
                body=ds_request,
                skip_validation=True,
            )
            return Datastore._from_rest_object(datastore_resource)
        except Exception as ex:  # pylint: disable=broad-except
            if isinstance(ex, (ValidationException, SchemaValidationError)):
                log_and_raise_error(ex)
            else:
                raise ex
