# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import json
import os
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from marshmallow.exceptions import ValidationError as SchemaValidationError

from azure.ai.ml._artifacts._artifact_utilities import _check_and_upload_path
from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2023_08_01_preview import AzureMachineLearningWorkspaces as ServiceClient082023Preview
from azure.ai.ml._restclient.v2023_10_01 import AzureMachineLearningServices as ServiceClient102023
from azure.ai.ml._restclient.v2023_10_01.models import (
    FeaturesetVersion,
    FeaturesetVersionBackfillRequest,
    FeatureWindow,
)
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope, _ScopeDependentOperations
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._feature_store_utils import (
    _archive_or_restore,
    _datetime_to_str,
    read_feature_set_metadata,
    read_remote_feature_set_spec_metadata,
)
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._utils.utils import is_url
from azure.ai.ml.constants import ListViewType
from azure.ai.ml.entities._assets._artifacts.feature_set import FeatureSet
from azure.ai.ml.entities._feature_set.data_availability_status import DataAvailabilityStatus
from azure.ai.ml.entities._feature_set.feature import Feature
from azure.ai.ml.entities._feature_set.feature_set_backfill_metadata import FeatureSetBackfillMetadata
from azure.ai.ml.entities._feature_set.feature_set_materialization_metadata import FeatureSetMaterializationMetadata
from azure.ai.ml.entities._feature_set.featureset_spec_metadata import FeaturesetSpecMetadata
from azure.ai.ml.entities._feature_set.materialization_compute_resource import MaterializationComputeResource
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException
from azure.ai.ml.operations._datastore_operations import DatastoreOperations
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class FeatureSetOperations(_ScopeDependentOperations):
    """FeatureSetOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: ServiceClient102023,
        service_client_for_jobs: ServiceClient082023Preview,
        datastore_operations: DatastoreOperations,
        **kwargs: Dict,
    ):
        super(FeatureSetOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self._operation = service_client.featureset_versions
        self._container_operation = service_client.featureset_containers
        self._jobs_operation = service_client_for_jobs.jobs
        self._feature_operation = service_client.features
        self._service_client = service_client
        self._datastore_operation = datastore_operations
        self._init_kwargs = kwargs

    @distributed_trace
    @monitor_with_activity(ops_logger, "FeatureSet.List", ActivityType.PUBLICAPI)
    def list(
        self,
        name: Optional[str] = None,
        *,
        list_view_type: ListViewType = ListViewType.ACTIVE_ONLY,
        **kwargs: Dict,
    ) -> ItemPaged[FeatureSet]:
        """List the FeatureSet assets of the workspace.

        :param name: Name of a specific FeatureSet asset, optional.
        :type name: Optional[str]
        :keyword list_view_type: View type for including/excluding (for example) archived FeatureSet assets.
            Defaults to ACTIVE_ONLY.
        :type list_view_type: Optional[ListViewType]
        :return: An iterator like instance of FeatureSet objects
        :rtype: ~azure.core.paging.ItemPaged[FeatureSet]
        """
        if name:
            return self._operation.list(
                workspace_name=self._workspace_name,
                name=name,
                cls=lambda objs: [FeatureSet._from_rest_object(obj) for obj in objs],
                list_view_type=list_view_type,
                **self._scope_kwargs,
                **kwargs,
            )
        return self._container_operation.list(
            workspace_name=self._workspace_name,
            cls=lambda objs: [FeatureSet._from_container_rest_object(obj) for obj in objs],
            list_view_type=list_view_type,
            **self._scope_kwargs,
            **kwargs,
        )

    def _get(self, name: str, version: Optional[str] = None, **kwargs: Dict) -> FeaturesetVersion:
        return self._operation.get(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            version=version,
            **self._init_kwargs,
            **kwargs,
        )

    @distributed_trace
    @monitor_with_activity(ops_logger, "FeatureSet.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, version: str, **kwargs: Dict) -> FeatureSet:  # type: ignore
        """Get the specified FeatureSet asset.

        :param name: Name of FeatureSet asset.
        :type name: str
        :param version: Version of FeatureSet asset.
        :type version: str
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if FeatureSet cannot be successfully
            identified and retrieved. Details will be provided in the error message.
        :raises ~azure.core.exceptions.HttpResponseError: Raised if the corresponding name and version cannot be
            retrieved from the service.
        :return: FeatureSet asset object.
        :rtype: ~azure.ai.ml.entities.FeatureSet
        """
        try:
            featureset_version_resource = self._get(name, version, **kwargs)
            return FeatureSet._from_rest_object(featureset_version_resource)  # type: ignore[return-value]
        except (ValidationException, SchemaValidationError) as ex:
            log_and_raise_error(ex)

    @distributed_trace
    @monitor_with_activity(ops_logger, "FeatureSet.BeginCreateOrUpdate", ActivityType.PUBLICAPI)
    def begin_create_or_update(self, featureset: FeatureSet, **kwargs: Dict) -> LROPoller[FeatureSet]:
        """Create or update FeatureSet

        :param featureset: FeatureSet definition.
        :type featureset: FeatureSet
        :return: An instance of LROPoller that returns a FeatureSet.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.FeatureSet]
        """
        featureset_copy = deepcopy(featureset)

        featureset_spec = self._validate_and_get_feature_set_spec(featureset_copy)
        featureset_copy.properties["featuresetPropertiesVersion"] = "1"
        featureset_copy.properties["featuresetProperties"] = json.dumps(featureset_spec._to_dict())

        sas_uri = None

        if not is_url(featureset_copy.path):
            with open(os.path.join(str(featureset_copy.path), ".amlignore"), mode="w", encoding="utf-8") as f:
                f.write(".*\n*.amltmp\n*.amltemp")

        featureset_copy, _ = _check_and_upload_path(
            artifact=featureset_copy, asset_operations=self, sas_uri=sas_uri, artifact_type=ErrorTarget.FEATURE_SET
        )

        featureset_resource = FeatureSet._to_rest_object(featureset_copy)

        return self._operation.begin_create_or_update(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            name=featureset_copy.name,
            version=featureset_copy.version,
            body=featureset_resource,
            **kwargs,
            cls=lambda response, deserialized, headers: FeatureSet._from_rest_object(deserialized),
        )

    @distributed_trace
    @monitor_with_activity(ops_logger, "FeatureSet.BeginBackFill", ActivityType.PUBLICAPI)
    def begin_backfill(
        self,
        *,
        name: str,
        version: str,
        feature_window_start_time: Optional[datetime] = None,
        feature_window_end_time: Optional[datetime] = None,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        compute_resource: Optional[MaterializationComputeResource] = None,
        spark_configuration: Optional[Dict[str, str]] = None,
        data_status: Optional[List[Union[str, DataAvailabilityStatus]]] = None,
        job_id: Optional[str] = None,
        **kwargs: Dict,
    ) -> LROPoller[FeatureSetBackfillMetadata]:
        """Backfill.

        :keyword name: Feature set name. This is case-sensitive.
        :paramtype name: str
        :keyword version: Version identifier. This is case-sensitive.
        :paramtype version: str
        :keyword feature_window_start_time: Start time of the feature window to be materialized.
        :paramtype feature_window_start_time: datetime
        :keyword feature_window_end_time: End time of the feature window to be materialized.
        :paramtype feature_window_end_time: datetime
        :keyword display_name: Specifies description.
        :paramtype display_name: str
        :keyword description: Specifies description.
        :paramtype description: str
        :keyword tags: A set of tags. Specifies the tags.
        :paramtype tags: dict[str, str]
        :keyword compute_resource: Specifies the compute resource settings.
        :paramtype compute_resource: ~azure.ai.ml.entities.MaterializationComputeResource
        :keyword spark_configuration: Specifies the spark compute settings.
        :paramtype spark_configuration: dict[str, str]
        :keyword data_status: Specifies the data status that you want to backfill.
        :paramtype data_status: list[str or ~azure.ai.ml.entities.DataAvailabilityStatus]
        :keyword job_id: The job id.
        :paramtype job_id: str
        :return: An instance of LROPoller that returns ~azure.ai.ml.entities.FeatureSetBackfillMetadata
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.FeatureSetBackfillMetadata]
        """
        request_body: FeaturesetVersionBackfillRequest = FeaturesetVersionBackfillRequest(
            description=description,
            display_name=display_name,
            feature_window=FeatureWindow(
                feature_window_start=feature_window_start_time, feature_window_end=feature_window_end_time
            ),
            resource=compute_resource._to_rest_object() if compute_resource else None,
            spark_configuration=spark_configuration,
            data_availability_status=data_status,
            job_id=job_id,
            tags=tags,
        )

        return self._operation.begin_backfill(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            version=version,
            body=request_body,
            **kwargs,
            cls=lambda response, deserialized, headers: FeatureSetBackfillMetadata._from_rest_object(deserialized),
        )

    @distributed_trace
    @monitor_with_activity(ops_logger, "FeatureSet.ListMaterializationOperation", ActivityType.PUBLICAPI)
    def list_materialization_operations(
        self,
        name: str,
        version: str,
        *,
        feature_window_start_time: Optional[Union[str, datetime]] = None,
        feature_window_end_time: Optional[Union[str, datetime]] = None,
        filters: Optional[str] = None,
        **kwargs: Dict,
    ) -> ItemPaged[FeatureSetMaterializationMetadata]:
        """List Materialization operation.

        :param name: Feature set name.
        :type name: str
        :param version: Feature set version.
        :type version: str
        :keyword feature_window_start_time: Start time of the feature window to filter materialization jobs.
        :paramtype feature_window_start_time: Union[str, datetime]
        :keyword feature_window_end_time: End time of the feature window to filter materialization jobs.
        :paramtype feature_window_end_time: Union[str, datetime]
        :keyword filters: Comma-separated list of tag names (and optionally values). Example: tag1,tag2=value2.
        :paramtype filters: str
        :return: An iterator like instance of ~azure.ai.ml.entities.FeatureSetMaterializationMetadata objects
        :rtype: ~azure.core.paging.ItemPaged[FeatureSetMaterializationMetadata]
        """
        feature_window_start_time = _datetime_to_str(feature_window_start_time) if feature_window_start_time else None
        feature_window_end_time = _datetime_to_str(feature_window_end_time) if feature_window_end_time else None
        properties = f"azureml.FeatureSetName={name},azureml.FeatureSetVersion={version}"
        if feature_window_start_time:
            properties = properties + f",azureml.FeatureWindowStart={feature_window_start_time}"
        if feature_window_end_time:
            properties = properties + f",azureml.FeatureWindowEnd={feature_window_end_time}"

        materialization_jobs = self._jobs_operation.list(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            properties=properties,
            tag=filters,
            cls=lambda objs: [FeatureSetMaterializationMetadata._from_rest_object(obj) for obj in objs],
            **kwargs,
        )
        return materialization_jobs

    @distributed_trace
    @monitor_with_activity(ops_logger, "FeatureSet.ListFeatures", ActivityType.PUBLICAPI)
    def list_features(
        self,
        feature_set_name: str,
        version: str,
        *,
        feature_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[str] = None,
        **kwargs: Dict,
    ) -> ItemPaged[Feature]:
        """List features

        :param feature_set_name: Feature set name.
        :type feature_set_name: str
        :param version: Feature set version.
        :type version: str
        :keyword feature_name: feature name.
        :paramtype feature_name: str
        :keyword description: Description of the featureset.
        :paramtype description: str
        :keyword tags: Comma-separated list of tag names (and optionally values). Example: tag1,tag2=value2.
        :paramtype tags: str
        :return: An iterator like instance of Feature objects
        :rtype: ~azure.core.paging.ItemPaged[Feature]
        """
        features = self._feature_operation.list(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            featureset_name=feature_set_name,
            featureset_version=version,
            tags=tags,
            feature_name=feature_name,
            description=description,
            **kwargs,
            cls=lambda objs: [Feature._from_rest_object(obj) for obj in objs],
        )
        return features

    @distributed_trace
    @monitor_with_activity(ops_logger, "FeatureSet.GetFeature", ActivityType.PUBLICAPI)
    def get_feature(
        self, feature_set_name: str, version: str, *, feature_name: str, **kwargs: Dict
    ) -> Optional["Feature"]:
        """Get Feature

        :param feature_set_name: Feature set name.
        :type feature_set_name: str
        :param version: Feature set version.
        :type version: str
        :keyword feature_name: The feature name. This argument is case-sensitive.
        :paramtype feature_name: str
        :keyword tags: String representation of a comma-separated list of tag names, and optionally, values.
            For example, "tag1,tag2=value2". If provided, only features matching the specified tags are returned.
        :paramtype tags: str
        :return: Feature object
        :rtype: ~azure.ai.ml.entities.Feature
        """
        feature = self._feature_operation.get(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            featureset_name=feature_set_name,
            featureset_version=version,
            feature_name=feature_name,
            **kwargs,
        )

        return Feature._from_rest_object(feature)  # type: ignore[return-value]

    @distributed_trace
    @monitor_with_activity(ops_logger, "FeatureSet.Archive", ActivityType.PUBLICAPI)
    def archive(
        self,
        name: str,
        version: str,
        **kwargs: Dict,
    ) -> None:
        """Archive a FeatureSet asset.

        :param name: Name of FeatureSet asset.
        :type name: str
        :param version: Version of FeatureSet asset.
        :type version: str
        :return: None
        """

        _archive_or_restore(
            asset_operations=self,
            version_operation=self._operation,
            is_archived=True,
            name=name,
            version=version,
            **kwargs,
        )

    @distributed_trace
    @monitor_with_activity(ops_logger, "FeatureSet.Restore", ActivityType.PUBLICAPI)
    def restore(
        self,
        name: str,
        version: str,
        **kwargs: Dict,
    ) -> None:
        """Restore an archived FeatureSet asset.

        :param name: Name of FeatureSet asset.
        :type name: str
        :param version: Version of FeatureSet asset.
        :type version: str
        :return: None
        """

        _archive_or_restore(
            asset_operations=self,
            version_operation=self._operation,
            is_archived=False,
            name=name,
            version=version,
            **kwargs,
        )

    def _validate_and_get_feature_set_spec(self, featureset: FeatureSet) -> FeaturesetSpecMetadata:
        # pylint: disable=no-member
        if not (featureset.specification and featureset.specification.path):
            msg = "Missing FeatureSet specification path. Path is required for feature set."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                error_type=ValidationErrorType.MISSING_FIELD,
                target=ErrorTarget.FEATURE_SET,
                error_category=ErrorCategory.USER_ERROR,
            )

        featureset_spec_path: Any = str(featureset.specification.path)
        if is_url(featureset_spec_path):
            try:
                featureset_spec_contents = read_remote_feature_set_spec_metadata(
                    base_uri=featureset_spec_path,
                    datastore_operations=self._datastore_operation,
                )
                featureset_spec_path = None
            except Exception as ex:  # pylint: disable=W0718
                module_logger.info("Unable to access FeaturesetSpec at path %s", featureset_spec_path)
                raise ex
            return FeaturesetSpecMetadata._load(featureset_spec_contents, featureset_spec_path)

        if not os.path.isabs(featureset_spec_path):
            featureset_spec_path = Path(featureset.base_path, featureset_spec_path).resolve()

        if not os.path.isdir(featureset_spec_path):
            raise ValidationException(
                message="No such directory: {}".format(featureset_spec_path),
                no_personal_data_message="No such directory",
                target=ErrorTarget.FEATURE_SET,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND,
            )

        featureset_spec_contents = read_feature_set_metadata(path=featureset_spec_path)
        featureset_spec_yaml_path = Path(featureset_spec_path, "FeatureSetSpec.yaml")
        return FeaturesetSpecMetadata._load(featureset_spec_contents, featureset_spec_yaml_path)
