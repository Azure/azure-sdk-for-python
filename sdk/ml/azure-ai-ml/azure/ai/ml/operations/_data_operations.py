# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,no-value-for-parameter

import os
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, Iterable, List, Optional, Union, cast

from marshmallow.exceptions import ValidationError as SchemaValidationError

from azure.ai.ml._artifacts._artifact_utilities import _check_and_upload_path
from azure.ai.ml._artifacts._constants import (
    ASSET_PATH_ERROR,
    CHANGED_ASSET_PATH_MSG,
    CHANGED_ASSET_PATH_MSG_NO_PERSONAL_DATA,
)
from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2021_10_01_dataplanepreview import (
    AzureMachineLearningWorkspaces as ServiceClient102021Dataplane,
)
from azure.ai.ml._restclient.v2023_04_01_preview import AzureMachineLearningWorkspaces as ServiceClient042023_preview
from azure.ai.ml._restclient.v2023_04_01_preview.models import ListViewType
from azure.ai.ml._restclient.v2024_01_01_preview import AzureMachineLearningWorkspaces as ServiceClient012024_preview
from azure.ai.ml._restclient.v2024_01_01_preview.models import ComputeInstanceDataMount
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._asset_utils import (
    _archive_or_restore,
    _check_or_modify_auto_delete_setting,
    _create_or_update_autoincrement,
    _get_latest_version_from_container,
    _resolve_label_to_asset,
    _validate_auto_delete_setting_in_data_output,
    _validate_workspace_managed_datastore,
)
from azure.ai.ml._utils._data_utils import (
    download_mltable_metadata_schema,
    read_local_mltable_metadata_contents,
    read_remote_mltable_metadata_contents,
    validate_mltable_metadata,
)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils._http_utils import HttpPipeline
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._utils._registry_utils import (
    get_asset_body_for_registry_storage,
    get_registry_client,
    get_sas_uri_for_registry_asset,
)
from azure.ai.ml._utils.utils import is_url
from azure.ai.ml.constants._common import (
    ASSET_ID_FORMAT,
    MLTABLE_METADATA_SCHEMA_URL_FALLBACK,
    AssetTypes,
    AzureMLResourceType,
)
from azure.ai.ml.data_transfer import import_data as import_data_func
from azure.ai.ml.entities import PipelineJob, PipelineJobSettings
from azure.ai.ml.entities._assets import Data, WorkspaceAssetReference
from azure.ai.ml.entities._data.mltable_metadata import MLTableMetadata
from azure.ai.ml.entities._data_import.data_import import DataImport
from azure.ai.ml.entities._inputs_outputs import Output
from azure.ai.ml.entities._inputs_outputs.external_data import Database
from azure.ai.ml.exceptions import (
    AssetPathException,
    ErrorCategory,
    ErrorTarget,
    MlException,
    ValidationErrorType,
    ValidationException,
)
from azure.ai.ml.operations._datastore_operations import DatastoreOperations
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.paging import ItemPaged

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class DataOperations(_ScopeDependentOperations):
    """DataOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.

    :param operation_scope: Scope variables for the operations classes of an MLClient object.
    :type operation_scope: ~azure.ai.ml._scope_dependent_operations.OperationScope
    :param operation_config: Common configuration for operations classes of an MLClient object.
    :type operation_config: ~azure.ai.ml._scope_dependent_operations.OperationConfig
    :param service_client: Service client to allow end users to operate on Azure Machine Learning Workspace
        resources (ServiceClient042023Preview or ServiceClient102021Dataplane).
    :type service_client: typing.Union[
        ~azure.ai.ml._restclient.v2023_04_01_preview._azure_machine_learning_workspaces.AzureMachineLearningWorkspaces,
        ~azure.ai.ml._restclient.v2021_10_01_dataplanepreview._azure_machine_learning_workspaces.
        AzureMachineLearningWorkspaces]
    :param datastore_operations: Represents a client for performing operations on Datastores.
    :type datastore_operations: ~azure.ai.ml.operations._datastore_operations.DatastoreOperations
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: Union[ServiceClient042023_preview, ServiceClient102021Dataplane],
        service_client_012024_preview: ServiceClient012024_preview,
        datastore_operations: DatastoreOperations,
        **kwargs: Any,
    ):
        super(DataOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self._operation = service_client.data_versions
        self._container_operation = service_client.data_containers
        self._datastore_operation = datastore_operations
        self._compute_operation = service_client_012024_preview.compute
        self._service_client = service_client
        self._init_kwargs = kwargs
        self._requests_pipeline: HttpPipeline = kwargs.pop("requests_pipeline")
        self._all_operations: OperationsContainer = kwargs.pop("all_operations")
        # Maps a label to a function which given an asset name,
        # returns the asset associated with the label
        self._managed_label_resolver = {"latest": self._get_latest_version}

    @monitor_with_activity(ops_logger, "Data.List", ActivityType.PUBLICAPI)
    def list(
        self,
        name: Optional[str] = None,
        *,
        list_view_type: ListViewType = ListViewType.ACTIVE_ONLY,
    ) -> ItemPaged[Data]:
        """List the data assets of the workspace.

        :param name: Name of a specific data asset, optional.
        :type name: Optional[str]
        :keyword list_view_type: View type for including/excluding (for example) archived data assets.
            Default: ACTIVE_ONLY.
        :type list_view_type: Optional[ListViewType]
        :return: An iterator like instance of Data objects
        :rtype: ~azure.core.paging.ItemPaged[Data]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_misc.py
                :start-after: [START data_operations_list]
                :end-before: [END data_operations_list]
                :language: python
                :dedent: 8
                :caption: List data assets example.
        """
        if name:
            return (
                self._operation.list(
                    name=name,
                    registry_name=self._registry_name,
                    cls=lambda objs: [Data._from_rest_object(obj) for obj in objs],
                    list_view_type=list_view_type,
                    **self._scope_kwargs,
                )
                if self._registry_name
                else self._operation.list(
                    name=name,
                    workspace_name=self._workspace_name,
                    cls=lambda objs: [Data._from_rest_object(obj) for obj in objs],
                    list_view_type=list_view_type,
                    **self._scope_kwargs,
                )
            )
        return (
            self._container_operation.list(
                registry_name=self._registry_name,
                cls=lambda objs: [Data._from_container_rest_object(obj) for obj in objs],
                list_view_type=list_view_type,
                **self._scope_kwargs,
            )
            if self._registry_name
            else self._container_operation.list(
                workspace_name=self._workspace_name,
                cls=lambda objs: [Data._from_container_rest_object(obj) for obj in objs],
                list_view_type=list_view_type,
                **self._scope_kwargs,
            )
        )

    def _get(self, name: Optional[str], version: Optional[str] = None) -> Data:
        if version:
            return (
                self._operation.get(
                    name=name,
                    version=version,
                    registry_name=self._registry_name,
                    **self._scope_kwargs,
                    **self._init_kwargs,
                )
                if self._registry_name
                else self._operation.get(
                    resource_group_name=self._resource_group_name,
                    workspace_name=self._workspace_name,
                    name=name,
                    version=version,
                    **self._init_kwargs,
                )
            )
        return (
            self._container_operation.get(
                name=name,
                registry_name=self._registry_name,
                **self._scope_kwargs,
                **self._init_kwargs,
            )
            if self._registry_name
            else self._container_operation.get(
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                name=name,
                **self._init_kwargs,
            )
        )

    @monitor_with_activity(ops_logger, "Data.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, version: Optional[str] = None, label: Optional[str] = None) -> Data:  # type: ignore
        """Get the specified data asset.

        :param name: Name of data asset.
        :type name: str
        :param version: Version of data asset.
        :type version: str
        :param label: Label of the data asset. (mutually exclusive with version)
        :type label: str
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Data cannot be successfully
            identified and retrieved. Details will be provided in the error message.
        :return: Data asset object.
        :rtype: ~azure.ai.ml.entities.Data

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_misc.py
                :start-after: [START data_operations_get]
                :end-before: [END data_operations_get]
                :language: python
                :dedent: 8
                :caption: Get data assets example.
        """
        try:
            if version and label:
                msg = "Cannot specify both version and label."
                raise ValidationException(
                    message=msg,
                    target=ErrorTarget.DATA,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )

            if label:
                return _resolve_label_to_asset(self, name, label)

            if not version:
                msg = "Must provide either version or label."
                raise ValidationException(
                    message=msg,
                    target=ErrorTarget.DATA,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.MISSING_FIELD,
                )
            data_version_resource = self._get(name, version)
            return Data._from_rest_object(data_version_resource)
        except (ValidationException, SchemaValidationError) as ex:
            log_and_raise_error(ex)

    @monitor_with_activity(ops_logger, "Data.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(self, data: Data) -> Data:
        """Returns created or updated data asset.

        If not already in storage, asset will be uploaded to the workspace's blob storage.

        :param data: Data asset object.
        :type data: azure.ai.ml.entities.Data
        :raises ~azure.ai.ml.exceptions.AssetPathException: Raised when the Data artifact path is
            already linked to another asset
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Data cannot be successfully validated.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.EmptyDirectoryError: Raised if local path provided points to an empty directory.
        :return: Data asset object.
        :rtype: ~azure.ai.ml.entities.Data

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_misc.py
                :start-after: [START data_operations_create_or_update]
                :end-before: [END data_operations_create_or_update]
                :language: python
                :dedent: 8
                :caption: Create data assets example.
        """
        try:
            name = data.name
            if not data.version and self._registry_name:
                msg = "Data asset version is required for registry"
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.DATA,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.MISSING_FIELD,
                )
            version = data.version

            sas_uri = None
            if self._registry_name:
                # If the data asset is a workspace asset, promote to registry
                if isinstance(data, WorkspaceAssetReference):
                    try:
                        self._operation.get(
                            name=data.name,
                            version=data.version,
                            resource_group_name=self._resource_group_name,
                            registry_name=self._registry_name,
                        )
                    except Exception as err:  # pylint: disable=W0718
                        if isinstance(err, ResourceNotFoundError):
                            pass
                        else:
                            raise err
                    else:
                        msg = "An data asset with this name and version already exists in registry"
                        raise ValidationException(
                            message=msg,
                            no_personal_data_message=msg,
                            target=ErrorTarget.DATA,
                            error_category=ErrorCategory.USER_ERROR,
                        )
                    data_res_obj = data._to_rest_object()
                    result = self._service_client.resource_management_asset_reference.begin_import_method(
                        resource_group_name=self._resource_group_name,
                        registry_name=self._registry_name,
                        body=data_res_obj,
                    ).result()

                    if not result:
                        data_res_obj = self._get(name=data.name, version=data.version)
                        return Data._from_rest_object(data_res_obj)

                sas_uri = get_sas_uri_for_registry_asset(
                    service_client=self._service_client,
                    name=name,
                    version=version,
                    resource_group=self._resource_group_name,
                    registry=self._registry_name,
                    body=get_asset_body_for_registry_storage(self._registry_name, "data", name, version),
                )

            referenced_uris = self._validate(data)
            if referenced_uris:
                data._referenced_uris = referenced_uris

            data, _ = _check_and_upload_path(
                artifact=data,
                asset_operations=self,
                sas_uri=sas_uri,
                artifact_type=ErrorTarget.DATA,
                show_progress=self._show_progress,
            )

            _check_or_modify_auto_delete_setting(data.auto_delete_setting)

            data_version_resource = data._to_rest_object()
            auto_increment_version = data._auto_increment_version

            if auto_increment_version:
                result = _create_or_update_autoincrement(
                    name=data.name,
                    body=data_version_resource,
                    version_operation=self._operation,
                    container_operation=self._container_operation,
                    resource_group_name=self._operation_scope.resource_group_name,
                    workspace_name=self._workspace_name,
                    **self._init_kwargs,
                )
            else:
                result = (
                    self._operation.begin_create_or_update(
                        name=name,
                        version=version,
                        registry_name=self._registry_name,
                        body=data_version_resource,
                        **self._scope_kwargs,
                    ).result()
                    if self._registry_name
                    else self._operation.create_or_update(
                        name=name,
                        version=version,
                        workspace_name=self._workspace_name,
                        body=data_version_resource,
                        **self._scope_kwargs,
                    )
                )

            if not result and self._registry_name:
                result = self._get(name=name, version=version)

            return Data._from_rest_object(result)
        except Exception as ex:
            if isinstance(ex, (ValidationException, SchemaValidationError)):
                log_and_raise_error(ex)
            elif isinstance(ex, HttpResponseError):
                # service side raises an exception if we attempt to update an existing asset's asset path
                if str(ex) == ASSET_PATH_ERROR:
                    raise AssetPathException(
                        message=CHANGED_ASSET_PATH_MSG,
                        tartget=ErrorTarget.DATA,
                        no_personal_data_message=CHANGED_ASSET_PATH_MSG_NO_PERSONAL_DATA,
                        error_category=ErrorCategory.USER_ERROR,
                    ) from ex
            raise ex

    @monitor_with_activity(ops_logger, "Data.ImportData", ActivityType.PUBLICAPI)
    @experimental
    def import_data(self, data_import: DataImport, **kwargs: Any) -> PipelineJob:
        """Returns the data import job that is creating the data asset.

        :param data_import: DataImport object.
        :type data_import: azure.ai.ml.entities.DataImport
        :return: data import job object.
        :rtype: ~azure.ai.ml.entities.PipelineJob

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_misc.py
                :start-after: [START data_operations_import_data]
                :end-before: [END data_operations_import_data]
                :language: python
                :dedent: 8
                :caption: Import data assets example.
        """

        experiment_name = "data_import_" + str(data_import.name)
        data_import.type = AssetTypes.MLTABLE if isinstance(data_import.source, Database) else AssetTypes.URI_FOLDER

        # avoid specifying auto_delete_setting in job output now
        _validate_auto_delete_setting_in_data_output(data_import.auto_delete_setting)

        # block cumtomer specified path on managed datastore
        data_import.path = _validate_workspace_managed_datastore(data_import.path)

        if "${{name}}" not in str(data_import.path):
            data_import.path = data_import.path.rstrip("/") + "/${{name}}"  # type: ignore
        import_job = import_data_func(
            description=data_import.description or experiment_name,
            display_name=experiment_name,
            experiment_name=experiment_name,
            compute="serverless",
            source=data_import.source,
            outputs={
                "sink": Output(
                    type=data_import.type,
                    path=data_import.path,  # type: ignore
                    name=data_import.name,
                    version=data_import.version,
                )
            },
        )
        import_pipeline = PipelineJob(
            description=data_import.description or experiment_name,
            tags=data_import.tags,
            display_name=experiment_name,
            experiment_name=experiment_name,
            properties=data_import.properties or {},
            settings=PipelineJobSettings(force_rerun=True),
            jobs={experiment_name: import_job},
        )
        import_pipeline.properties["azureml.materializationAssetName"] = data_import.name
        return self._all_operations.all_operations[AzureMLResourceType.JOB].create_or_update(
            job=import_pipeline, skip_validation=True, **kwargs
        )

    @monitor_with_activity(ops_logger, "Data.ListMaterializationStatus", ActivityType.PUBLICAPI)
    def list_materialization_status(
        self,
        name: str,
        *,
        list_view_type: ListViewType = ListViewType.ACTIVE_ONLY,
        **kwargs: Any,
    ) -> Iterable[PipelineJob]:
        """List materialization jobs of the asset.

        :param name: name of asset being created by the materialization jobs.
        :type name: str
        :keyword list_view_type: View type for including/excluding (for example) archived jobs. Default: ACTIVE_ONLY.
        :paramtype list_view_type: Optional[ListViewType]
        :return: An iterator like instance of Job objects.
        :rtype: ~azure.core.paging.ItemPaged[PipelineJob]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_misc.py
                :start-after: [START data_operations_list_materialization_status]
                :end-before: [END data_operations_list_materialization_status]
                :language: python
                :dedent: 8
                :caption: List materialization jobs example.
        """

        return cast(
            Iterable[PipelineJob],
            self._all_operations.all_operations[AzureMLResourceType.JOB].list(
                job_type="Pipeline",
                asset_name=name,
                list_view_type=list_view_type,
                **kwargs,
            ),
        )

    @monitor_with_activity(ops_logger, "Data.Validate", ActivityType.INTERNALCALL)
    def _validate(self, data: Data) -> Optional[List[str]]:
        if not data.path:
            msg = "Missing data path. Path is required for data."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                error_type=ValidationErrorType.MISSING_FIELD,
                target=ErrorTarget.DATA,
                error_category=ErrorCategory.USER_ERROR,
            )

        asset_path = str(data.path)
        asset_type = data.type
        base_path = data.base_path

        if asset_type == AssetTypes.MLTABLE:
            if is_url(asset_path):
                try:
                    metadata_contents = read_remote_mltable_metadata_contents(
                        base_uri=asset_path,
                        datastore_operations=self._datastore_operation,
                        requests_pipeline=self._requests_pipeline,
                    )
                    metadata_yaml_path = None
                except Exception:  # pylint: disable=W0718
                    # skip validation for remote MLTable when the contents cannot be read
                    module_logger.info("Unable to access MLTable metadata at path %s", asset_path)
                    return None
            else:
                metadata_contents = read_local_mltable_metadata_contents(path=asset_path)
                metadata_yaml_path = Path(asset_path, "MLTable")
            metadata = MLTableMetadata._load(metadata_contents, metadata_yaml_path)
            mltable_metadata_schema = self._try_get_mltable_metadata_jsonschema(data._mltable_schema_url)
            if mltable_metadata_schema and not data._skip_validation:
                validate_mltable_metadata(
                    mltable_metadata_dict=metadata_contents,
                    mltable_schema=mltable_metadata_schema,
                )
            return cast(Optional[List[str]], metadata.referenced_uris())

        if is_url(asset_path):
            # skip validation for remote URI_FILE or URI_FOLDER
            pass
        elif os.path.isabs(asset_path):
            _assert_local_path_matches_asset_type(asset_path, asset_type)
        else:
            abs_path = Path(base_path, asset_path).resolve()
            _assert_local_path_matches_asset_type(str(abs_path), asset_type)

        return None

    def _try_get_mltable_metadata_jsonschema(self, mltable_schema_url: Optional[str]) -> Optional[Dict]:
        if mltable_schema_url is None:
            mltable_schema_url = MLTABLE_METADATA_SCHEMA_URL_FALLBACK
        try:
            return cast(Optional[Dict], download_mltable_metadata_schema(mltable_schema_url, self._requests_pipeline))
        except Exception:  # pylint: disable=W0718
            module_logger.info(
                'Failed to download MLTable metadata jsonschema from "%s", skipping validation',
                mltable_schema_url,
            )
            return None

    @monitor_with_activity(ops_logger, "Data.Archive", ActivityType.PUBLICAPI)
    def archive(
        self,
        name: str,
        version: Optional[str] = None,
        label: Optional[str] = None,
        # pylint:disable=unused-argument
        **kwargs: Any,
    ) -> None:
        """Archive a data asset.

        :param name: Name of data asset.
        :type name: str
        :param version: Version of data asset.
        :type version: str
        :param label: Label of the data asset. (mutually exclusive with version)
        :type label: str
        :return: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_misc.py
                :start-after: [START data_operations_archive]
                :end-before: [END data_operations_archive]
                :language: python
                :dedent: 8
                :caption: Archive data asset example.
        """

        _archive_or_restore(
            asset_operations=self,
            version_operation=self._operation,
            container_operation=self._container_operation,
            is_archived=True,
            name=name,
            version=version,
            label=label,
        )

    @monitor_with_activity(ops_logger, "Data.Restore", ActivityType.PUBLICAPI)
    def restore(
        self,
        name: str,
        version: Optional[str] = None,
        label: Optional[str] = None,
        # pylint:disable=unused-argument
        **kwargs: Any,
    ) -> None:
        """Restore an archived data asset.

        :param name: Name of data asset.
        :type name: str
        :param version: Version of data asset.
        :type version: str
        :param label: Label of the data asset. (mutually exclusive with version)
        :type label: str
        :return: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_misc.py
                :start-after: [START data_operations_restore]
                :end-before: [END data_operations_restore]
                :language: python
                :dedent: 8
                :caption: Restore data asset example.
        """

        _archive_or_restore(
            asset_operations=self,
            version_operation=self._operation,
            container_operation=self._container_operation,
            is_archived=False,
            name=name,
            version=version,
            label=label,
        )

    def _get_latest_version(self, name: str) -> Data:
        """Returns the latest version of the asset with the given name. Latest is defined as the most recently created,
         not the most recently updated.

        :param name: The asset name
        :type name: str
        :return: The latest asset
        :rtype: Data
        """
        latest_version = _get_latest_version_from_container(
            name,
            self._container_operation,
            self._resource_group_name,
            self._workspace_name,
            self._registry_name,
        )
        return self.get(name, version=latest_version)

    @monitor_with_activity(ops_logger, "data.Share", ActivityType.PUBLICAPI)
    @experimental
    def share(
        self,
        name: str,
        version: str,
        *,
        share_with_name: str,
        share_with_version: str,
        registry_name: str,
        **kwargs: Any,
    ) -> Data:
        """Share a data asset from workspace to registry.

        :param name: Name of data asset.
        :type name: str
        :param version: Version of data asset.
        :type version: str
        :keyword share_with_name: Name of data asset to share with.
        :paramtype share_with_name: str
        :keyword share_with_version: Version of data asset to share with.
        :paramtype share_with_version: str
        :keyword registry_name: Name of the destination registry.
        :paramtype registry_name: str
        :return: Data asset object.
        :rtype: ~azure.ai.ml.entities.Data

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_misc.py
                :start-after: [START data_operations_share]
                :end-before: [END data_operations_share]
                :language: python
                :dedent: 8
                :caption: Share data asset example.
        """

        #  Get workspace info to get workspace GUID
        workspace = self._service_client.workspaces.get(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            **kwargs,
        )
        workspace_guid = workspace.workspace_id
        workspace_location = workspace.location

        # Get data asset ID
        asset_id = ASSET_ID_FORMAT.format(
            workspace_location,
            workspace_guid,
            AzureMLResourceType.DATA,
            name,
            version,
        )

        data_ref = WorkspaceAssetReference(
            name=share_with_name if share_with_name else name,
            version=share_with_version if share_with_version else version,
            asset_id=asset_id,
        )

        with self._set_registry_client(registry_name):
            return self.create_or_update(data_ref)

    @monitor_with_activity(ops_logger, "data.Mount", ActivityType.PUBLICAPI)
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
        """Mount a data asset to a local path, so that you can access data inside it
        under a local path with any tools of your choice.

        :param path: The data asset path to mount, in the form of `azureml:<name>` or `azureml:<name>:<version>`.
        :type path: str
        :param mount_point: A local path used as mount point.
        :type mount_point: str
        :param mode: Mount mode. Only `ro_mount` (read-only) is supported for data asset mount.
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
        assert read_only, "read-write mount for data asset is not supported yet"

        ci_name = os.environ.get("CI_NAME")
        assert not persistent or (
            persistent and ci_name is not None
        ), "persistent mount is only supported on Compute Instance, where the 'CI_NAME' environment variable is set."

        try:
            from azureml.dataprep import rslex_fuse_subprocess_wrapper
        except ImportError as exc:
            raise MlException(  # pylint: disable=W0718
                "Mount operations requires package azureml-dataprep-rslex installed. "
                + "You can install it with Azure ML SDK with `pip install azure-ai-ml[mount]`."
            ) from exc

        uri = rslex_fuse_subprocess_wrapper.build_data_asset_uri(
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

    @contextmanager
    # pylint: disable-next=docstring-missing-return,docstring-missing-rtype
    def _set_registry_client(self, registry_name: str) -> Generator:
        """Sets the registry client for the data operations.

        :param registry_name: Name of the registry.
        :type registry_name: str
        """
        rg_ = self._operation_scope._resource_group_name
        sub_ = self._operation_scope._subscription_id
        registry_ = self._operation_scope.registry_name
        client_ = self._service_client
        data_versions_operation_ = self._operation

        try:
            _client, _rg, _sub = get_registry_client(self._service_client._config.credential, registry_name)
            self._operation_scope.registry_name = registry_name
            self._operation_scope._resource_group_name = _rg
            self._operation_scope._subscription_id = _sub
            self._service_client = _client
            self._operation = _client.data_versions
            yield
        finally:
            self._operation_scope.registry_name = registry_
            self._operation_scope._resource_group_name = rg_
            self._operation_scope._subscription_id = sub_
            self._service_client = client_
            self._operation = data_versions_operation_


def _assert_local_path_matches_asset_type(
    local_path: str,
    asset_type: str,
) -> None:
    # assert file system type matches asset type
    if asset_type == AssetTypes.URI_FOLDER and not os.path.isdir(local_path):
        raise ValidationException(
            message="File path does not match asset type {}: {}".format(asset_type, local_path),
            no_personal_data_message="File path does not match asset type {}".format(asset_type),
            target=ErrorTarget.DATA,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND,
        )
    if asset_type == AssetTypes.URI_FILE and not os.path.isfile(local_path):
        raise ValidationException(
            message="File path does not match asset type {}: {}".format(asset_type, local_path),
            no_personal_data_message="File path does not match asset type {}".format(asset_type),
            target=ErrorTarget.DATA,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND,
        )
