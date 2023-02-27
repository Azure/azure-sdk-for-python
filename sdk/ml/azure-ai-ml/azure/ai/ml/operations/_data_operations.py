# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Iterable

from marshmallow.exceptions import ValidationError as SchemaValidationError

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities import Job, PipelineJob, PipelineJobSettings
from azure.ai.ml.data_transfer import import_data
from azure.ai.ml.entities._inputs_outputs import Output
from azure.ai.ml.entities._inputs_outputs.external_data import Database
from azure.ai.ml._artifacts._artifact_utilities import _check_and_upload_path
from azure.ai.ml._artifacts._constants import (
    ASSET_PATH_ERROR,
    CHANGED_ASSET_PATH_MSG,
    CHANGED_ASSET_PATH_MSG_NO_PERSONAL_DATA,
)
from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2022_10_01_preview.models import ListViewType
from azure.ai.ml._restclient.v2022_10_01 import AzureMachineLearningWorkspaces as ServiceClient102022
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope, _ScopeDependentOperations

from azure.ai.ml._restclient.v2021_10_01_dataplanepreview import (
    AzureMachineLearningWorkspaces as ServiceClient102021Dataplane,
)

# from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._asset_utils import (
    _archive_or_restore,
    _create_or_update_autoincrement,
    _get_latest_version_from_container,
    _resolve_label_to_asset,
)
from azure.ai.ml._utils._data_utils import (
    download_mltable_metadata_schema,
    read_local_mltable_metadata_contents,
    read_remote_mltable_metadata_contents,
    validate_mltable_metadata,
)
from azure.ai.ml._utils._http_utils import HttpPipeline
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._utils._registry_utils import (
    get_asset_body_for_registry_storage,
    get_sas_uri_for_registry_asset,
)
from azure.ai.ml._utils.utils import is_url
from azure.ai.ml.constants._common import MLTABLE_METADATA_SCHEMA_URL_FALLBACK, AssetTypes
from azure.ai.ml.entities._assets import Data
from azure.ai.ml.entities._data_import.data_import import DataImport
from azure.ai.ml.entities._data.mltable_metadata import MLTableMetadata
from azure.ai.ml.exceptions import (
    AssetPathException,
    ErrorCategory,
    ErrorTarget,
    ValidationErrorType,
    ValidationException,
)
from azure.ai.ml.operations._datastore_operations import DatastoreOperations
from azure.core.exceptions import HttpResponseError
from azure.core.paging import ItemPaged

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class DataOperations(_ScopeDependentOperations):
    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: Union[ServiceClient102022, ServiceClient102021Dataplane],
        datastore_operations: DatastoreOperations,
        **kwargs: Dict,
    ):

        super(DataOperations, self).__init__(operation_scope, operation_config)
        # ops_logger.update_info(kwargs)
        self._operation = service_client.data_versions
        self._container_operation = service_client.data_containers
        self._datastore_operation = datastore_operations
        self._service_client = service_client
        self._init_kwargs = kwargs
        self._requests_pipeline: HttpPipeline = kwargs.pop("requests_pipeline")
        # Maps a label to a function which given an asset name,
        # returns the asset associated with the label
        self._managed_label_resolver = {"latest": self._get_latest_version}

    # @monitor_with_activity(logger, "Data.List", ActivityType.PUBLICAPI)
    def list(
        self,
        name: Optional[str] = None,
        *,
        list_view_type: ListViewType = ListViewType.ACTIVE_ONLY,
    ) -> ItemPaged[Data]:
        """List the data assets of the workspace.

        :param name: Name of a specific data asset, optional.
        :type name: Optional[str]
        :param list_view_type: View type for including/excluding (for example) archived data assets.
            Default: ACTIVE_ONLY.
        :type list_view_type: Optional[ListViewType]
        :return: An iterator like instance of Data objects
        :rtype: ~azure.core.paging.ItemPaged[Data]
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

    def _get(self, name: str, version: Optional[str] = None) -> Data:
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

    # @monitor_with_activity(logger, "Data.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, version: Optional[str] = None, label: Optional[str] = None) -> Data:
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

    # @monitor_with_activity(logger, "Data.CreateOrUpdate", ActivityType.PUBLICAPI)
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
                sas_uri = get_sas_uri_for_registry_asset(
                    service_client=self._service_client,
                    name=name,
                    version=version,
                    resource_group=self._resource_group_name,
                    registry=self._registry_name,
                    body=get_asset_body_for_registry_storage(self._registry_name, "data", name, version),
                )
                if not sas_uri:
                    module_logger.debug("Getting the existing asset name: %s, version: %s", name, version)
                    return self.get(name=name, version=version)
            referenced_uris = self._validate(data)
            if referenced_uris:
                data._referenced_uris = referenced_uris

            data, _ = _check_and_upload_path(
                artifact=data, asset_operations=self, sas_uri=sas_uri, artifact_type=ErrorTarget.DATA
            )
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
                    )
            raise ex

    @experimental
    def import_data(self, data_import: DataImport) -> Job:
        """Returns the data import job that is creating the data asset.

        :param data_import: DataImport object.
        :type data_import: azure.ai.ml.entities.DataImport
        :return: data import job object.
        :rtype: ~azure.ai.ml.entities.Job
        """

        experiment_name = "data_import_" + data_import.name
        component_name = (
            "import_data_database" if isinstance(data_import.source, Database) else "import_data_file_system"
        )
        data_import.type = AssetTypes.MLTABLE if isinstance(data_import.source, Database) else AssetTypes.URI_FOLDER
        if "{name}" not in data_import.path:
            data_import.path = data_import.path.rstrip("/") + "/{name}"
        import_job = import_data(
            description=data_import.description or experiment_name,
            display_name=experiment_name,
            experiment_name=experiment_name,
            compute="serverless",
            source=data_import.source,
            outputs={
                "sink": Output(
                    type=data_import.type, path=data_import.path, name=data_import.name, version=data_import.version
                )
            },
            component="azureml://registries/azureml-dev/components/" + component_name + "/versions/1",
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
        return self._job_operation.create_or_update(job=import_pipeline, skip_validation=True)

    @experimental
    def show_materialization_status(
        self,
        name: str,
        *,
        list_view_type: ListViewType = ListViewType.ACTIVE_ONLY,
    ) -> Iterable[Job]:
        """List materialization jobs of the asset.

        :param name: name of asset being created by the materialization jobs.
        :type name: str
        :param list_view_type: View type for including/excluding (for example) archived jobs. Default: ACTIVE_ONLY.
        :type list_view_type: Optional[ListViewType]
        :return: An iterator like instance of Job objects.
        :rtype: ~azure.core.paging.ItemPaged[Job]
        """

        return self._job_operation.list(job_type="Pipeline", asset_name=name, list_view_type=list_view_type)

    # @monitor_with_activity(logger, "Data.Validate", ActivityType.INTERNALCALL)
    def _validate(self, data: Data) -> Union[List[str], None]:
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
                except Exception:  # pylint: disable=broad-except
                    # skip validation for remote MLTable when the contents cannot be read
                    module_logger.info("Unable to access MLTable metadata at path %s", asset_path)
                    return
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
            return metadata.referenced_uris()

        if is_url(asset_path):
            # skip validation for remote URI_FILE or URI_FOLDER
            return

        if os.path.isabs(asset_path):
            _assert_local_path_matches_asset_type(asset_path, asset_type)
        else:
            abs_path = Path(base_path, asset_path).resolve()
            _assert_local_path_matches_asset_type(abs_path, asset_type)

    def _try_get_mltable_metadata_jsonschema(self, mltable_schema_url: str) -> Union[Dict, None]:
        if mltable_schema_url is None:
            mltable_schema_url = MLTABLE_METADATA_SCHEMA_URL_FALLBACK
        try:
            return download_mltable_metadata_schema(mltable_schema_url, self._requests_pipeline)
        except Exception:  # pylint: disable=broad-except
            module_logger.info(
                'Failed to download MLTable metadata jsonschema from "%s", skipping validation', mltable_schema_url
            )
            return None

    # @monitor_with_activity(logger, "Data.Archive", ActivityType.PUBLICAPI)
    def archive(
        self,
        name: str,
        version: Optional[str] = None,
        label: Optional[str] = None,
        **kwargs,  # pylint:disable=unused-argument
    ) -> None:
        """Archive a data asset.

        :param name: Name of data asset.
        :type name: str
        :param version: Version of data asset.
        :type version: str
        :param label: Label of the data asset. (mutually exclusive with version)
        :type label: str
        :return: None
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

    # @monitor_with_activity(logger, "Data.Restore", ActivityType.PUBLICAPI)
    def restore(
        self,
        name: str,
        version: Optional[str] = None,
        label: Optional[str] = None,
        **kwargs,  # pylint:disable=unused-argument
    ) -> None:
        """Restore an archived data asset.

        :param name: Name of data asset.
        :type name: str
        :param version: Version of data asset.
        :type version: str
        :param label: Label of the data asset. (mutually exclusive with version)
        :type label: str
        :return: None
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
        """Returns the latest version of the asset with the given name.

        Latest is defined as the most recently created, not the most
        recently updated.
        """
        latest_version = _get_latest_version_from_container(
            name, self._container_operation, self._resource_group_name, self._workspace_name, self._registry_name
        )
        return self.get(name, version=latest_version)


def _assert_local_path_matches_asset_type(
    local_path: str,
    asset_type: Union[AssetTypes.URI_FILE, AssetTypes.URI_FOLDER],
) -> None:
    # assert file system type matches asset type
    if asset_type == AssetTypes.URI_FOLDER and not os.path.isdir(local_path):
        raise ValidationException(
            message="No such file or directory: {}".format(local_path),
            no_personal_data_message="No such file or directory",
            target=ErrorTarget.DATA,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND,
        )
    if asset_type == AssetTypes.URI_FILE and not os.path.isfile(local_path):
        raise ValidationException(
            message="No such file or directory: {}".format(local_path),
            no_personal_data_message="No such file or directory",
            target=ErrorTarget.DATA,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND,
        )
