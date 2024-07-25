# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import time
import uuid
from typing import Dict, Iterable, Optional, cast

from marshmallow.exceptions import ValidationError as SchemaValidationError

from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2024_01_01_preview import AzureMachineLearningWorkspaces as ServiceClient012024Preview
from azure.ai.ml._restclient.v2024_01_01_preview.models import ComputeInstanceDataMount
from azure.ai.ml._restclient.v2024_07_01_preview import AzureMachineLearningWorkspaces as ServiceClient072024Preview
from azure.ai.ml._restclient.v2024_07_01_preview.models import Datastore as DatastoreData
from azure.ai.ml._restclient.v2024_07_01_preview.models import DatastoreSecrets, NoneDatastoreCredentials, SecretExpiry
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope, _ScopeDependentOperations
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities._datastore.datastore import Datastore
from azure.ai.ml.exceptions import MlException, ValidationException

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class DatastoreOperations(_ScopeDependentOperations):
    """Represents a client for performing operations on Datastores.

    You should not instantiate this class directly. Instead, you should create MLClient and use this client via the
    property MLClient.datastores

    :param operation_scope: Scope variables for the operations classes of an MLClient object.
    :type operation_scope: ~azure.ai.ml._scope_dependent_operations.OperationScope
    :param operation_config: Common configuration for operations classes of an MLClient object.
    :type operation_config: ~azure.ai.ml._scope_dependent_operations.OperationConfig
    :param serviceclient_2024_01_01_preview: Service client to allow end users to operate on Azure Machine Learning
        Workspace resources.
    :type serviceclient_2024_01_01_preview: ~azure.ai.ml._restclient.v2023_01_01_preview.
        _azure_machine_learning_workspaces.AzureMachineLearningWorkspaces
    :param serviceclient_2024_07_01_preview: Service client to allow end users to operate on Azure Machine Learning
        Workspace resources.
    :type serviceclient_2024_07_01_preview: ~azure.ai.ml._restclient.v2024_07_01_preview.
        _azure_machine_learning_workspaces.AzureMachineLearningWorkspaces
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        serviceclient_2024_01_01_preview: ServiceClient012024Preview,
        serviceclient_2024_07_01_preview: ServiceClient072024Preview,
        **kwargs: Dict,
    ):
        super(DatastoreOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self._operation = serviceclient_2024_07_01_preview.datastores
        self._compute_operation = serviceclient_2024_01_01_preview.compute
        self._credential = serviceclient_2024_07_01_preview._config.credential
        self._init_kwargs = kwargs

    @monitor_with_activity(ops_logger, "Datastore.List", ActivityType.PUBLICAPI)
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

        def _list_helper(datastore_resource: Datastore, include_secrets: bool) -> Datastore:
            if include_secrets:
                self._fetch_and_populate_secret(datastore_resource)
            return Datastore._from_rest_object(datastore_resource)

        return cast(
            Iterable[Datastore],
            self._operation.list(
                resource_group_name=self._operation_scope.resource_group_name,
                workspace_name=self._workspace_name,
                cls=lambda objs: [_list_helper(obj, include_secrets) for obj in objs],
                **self._init_kwargs,
            ),
        )

    @monitor_with_activity(ops_logger, "Datastore.ListSecrets", ActivityType.PUBLICAPI)
    def _list_secrets(self, name: str, expirable_secret: bool = False) -> DatastoreSecrets:
        return self._operation.list_secrets(
            name=name,
            body=SecretExpiry(expirable_secret=expirable_secret),
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            **self._init_kwargs,
        )

    @monitor_with_activity(ops_logger, "Datastore.Delete", ActivityType.PUBLICAPI)
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
            **self._init_kwargs,
        )

    @monitor_with_activity(ops_logger, "Datastore.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, *, include_secrets: bool = False) -> Datastore:  # type: ignore
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
                **self._init_kwargs,
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
            secrets = self._list_secrets(name=datastore_resource.name, expirable_secret=True)
            datastore_resource.properties.credentials.secrets = secrets

    @monitor_with_activity(ops_logger, "Datastore.GetDefault", ActivityType.PUBLICAPI)
    def get_default(self, *, include_secrets: bool = False) -> Datastore:  # type: ignore
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
                **self._init_kwargs,
            ).next()
            if include_secrets:
                self._fetch_and_populate_secret(datastore_resource)
            return Datastore._from_rest_object(datastore_resource)
        except (ValidationException, SchemaValidationError) as ex:
            log_and_raise_error(ex)

    @monitor_with_activity(ops_logger, "Datastore.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(self, datastore: Datastore) -> Datastore:  # type: ignore
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
        except Exception as ex:  # pylint: disable=W0718
            if isinstance(ex, (ValidationException, SchemaValidationError)):
                log_and_raise_error(ex)
            else:
                raise ex

    @monitor_with_activity(ops_logger, "Datastore.Mount", ActivityType.PUBLICAPI)
    @experimental
    def mount(
        self,
        path: str,
        mount_point: Optional[str] = None,
        mode: str = "ro_mount",
        debug: bool = False,
        persistent: bool = False,
        **_kwargs,
    ) -> None:
        """Mount a datastore to a local path, so that you can access data inside it
        under a local path with any tools of your choice.

        :param path: The data store path to mount, in the form of `<name>` or `azureml://datastores/<name>`.
        :type path: str
        :param mount_point: A local path used as mount point.
        :type mount_point: str
        :param mode: Mount mode, either `ro_mount` (read-only) or `rw_mount` (read-write).
        :type mode: str
        :param debug: Whether to enable verbose logging.
        :type debug: bool
        :param persistent: Whether to persist the mount after reboot. Applies only when running on Compute Instance,
                where the 'CI_NAME' environment variable is set."
        :type persistent: bool
        :return: None
        """

        assert mode in ["ro_mount", "rw_mount"], "mode should be either `ro_mount` or `rw_mount`"
        read_only = mode == "ro_mount"

        import os

        ci_name = os.environ.get("CI_NAME")
        assert not persistent or (
            persistent and ci_name is not None
        ), "persistent mount is only supported on Compute Instance, where the 'CI_NAME' environment variable is set."

        try:
            from azureml.dataprep import rslex_fuse_subprocess_wrapper
        except ImportError as exc:
            msg = "Mount operations requires package azureml-dataprep-rslex installed. \
                You can install it with Azure ML SDK with `pip install azure-ai-ml[mount]`."
            raise MlException(message=msg, no_personal_data_message=msg) from exc

        uri = rslex_fuse_subprocess_wrapper.build_datastore_uri(
            self._operation_scope._subscription_id, self._resource_group_name, self._workspace_name, path
        )
        if persistent and ci_name is not None:
            mount_name = f"unified_mount_{str(uuid.uuid4()).replace('-', '')}"
            self._compute_operation.update_data_mounts(
                self._resource_group_name,
                self._workspace_name,
                ci_name,
                [
                    ComputeInstanceDataMount(
                        source=uri,
                        source_type="URI",
                        mount_name=mount_name,
                        mount_action="Mount",
                        mount_path=mount_point or "",
                    )
                ],
                api_version="2021-01-01",
            )
            print(f"Mount requested [name: {mount_name}]. Waiting for completion ...")
            while True:
                compute = self._compute_operation.get(self._resource_group_name, self._workspace_name, ci_name)
                mounts = compute.properties.properties.data_mounts
                try:
                    mount = [mount for mount in mounts if mount.mount_name == mount_name][0]
                    if mount.mount_state == "Mounted":
                        print(f"Mounted [name: {mount_name}].")
                        break
                    if mount.mount_state == "MountRequested":
                        pass
                    elif mount.mount_state == "MountFailed":
                        msg = f"Mount failed [name: {mount_name}]: {mount.error}"
                        raise MlException(message=msg, no_personal_data_message=msg)
                    else:
                        msg = f"Got unexpected mount state [name: {mount_name}]: {mount.mount_state}"
                        raise MlException(message=msg, no_personal_data_message=msg)
                except IndexError:
                    pass
                time.sleep(5)
        else:
            rslex_fuse_subprocess_wrapper.start_fuse_mount_subprocess(
                uri, mount_point, read_only, debug, credential=self._operation._config.credential
            )
