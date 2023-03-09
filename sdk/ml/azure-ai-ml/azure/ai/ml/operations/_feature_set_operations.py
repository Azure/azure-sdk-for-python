# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import os
import json
from pathlib import Path
from typing import Dict, Optional

from marshmallow.exceptions import ValidationError as SchemaValidationError

from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2023_02_01_preview.models import ListViewType, FeaturesetVersion
from azure.ai.ml._restclient.v2023_02_01_preview import AzureMachineLearningWorkspaces as ServiceClient022023Preview
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope, _ScopeDependentOperations
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException
from azure.ai.ml._artifacts._artifact_utilities import _check_and_upload_path
from azure.ai.ml.operations._datastore_operations import DatastoreOperations

# from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._asset_utils import (
    _archive_or_restore,
    _get_latest_version_from_container,
    _resolve_label_to_asset,
)
from azure.ai.ml._utils._feature_set_utils import read_feature_set_metadata_contents
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities._assets import FeatureSet
from azure.ai.ml.entities._feature_set.featureset_spec import FeaturesetSpec
from azure.ai.ml._utils._experimental import experimental
from azure.core.polling import LROPoller
from azure.core.paging import ItemPaged

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


@experimental
class FeatureSetOperations(_ScopeDependentOperations):
    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: ServiceClient022023Preview,
        datastore_operations: DatastoreOperations,
        **kwargs: Dict,
    ):

        super(FeatureSetOperations, self).__init__(operation_scope, operation_config)
        # ops_logger.update_info(kwargs)
        self._operation = service_client.featureset_versions
        self._container_operation = service_client.featureset_containers
        self._service_client = service_client
        self._datastore_operation = datastore_operations
        self._init_kwargs = kwargs

        # Maps a label to a function which given an asset name,
        # returns the asset associated with the label
        self._managed_label_resolver = {"latest": self._get_latest_version}

    # @monitor_with_activity(logger, "FeatureSet.List", ActivityType.PUBLICAPI)
    def list(
        self,
        *,
        name: Optional[str] = None,
        list_view_type: ListViewType = ListViewType.ACTIVE_ONLY,
    ) -> ItemPaged[FeatureSet]:
        """List the FeatureSet assets of the workspace.

        :param name: Name of a specific FeatureSet asset, optional.
        :type name: Optional[str]
        :param list_view_type: View type for including/excluding (for example) archived FeatureSet assets.
        Default: ACTIVE_ONLY.
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
            )
        return self._container_operation.list(
            workspace_name=self._workspace_name,
            cls=lambda objs: [FeatureSet._from_container_rest_object(obj) for obj in objs],
            list_view_type=list_view_type,
            **self._scope_kwargs,
        )

    def _get(self, name: str, version: str = None) -> FeaturesetVersion:
        return self._operation.get(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            version=version,
            **self._init_kwargs,
        )

    # @monitor_with_activity(logger, "FeatureSet.Get", ActivityType.PUBLICAPI)
    def get(self, *, name: str, version: Optional[str] = None, label: Optional[str] = None) -> FeatureSet:
        """Get the specified FeatureSet asset.

        :param name: Name of FeatureSet asset.
        :type name: str
        :param version: Version of FeatureSet asset.
        :type version: str
        :param label: Label of the FeatureSet asset. (mutually exclusive with version)
        :type label: str
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if FeatureSet cannot be successfully
            identified and retrieved. Details will be provided in the error message.
        :return: FeatureSet asset object.
        :rtype: ~azure.ai.ml.entities.FeatureSet
        """
        try:
            if version and label:
                msg = "Cannot specify both version and label."
                raise ValidationException(
                    message=msg,
                    target=ErrorTarget.FEATURE_SET,
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
                    target=ErrorTarget.FEATURE_SET,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.MISSING_FIELD,
                )
            featureset_version_resource = self._get(name, version)
            return FeatureSet._from_rest_object(featureset_version_resource)
        except (ValidationException, SchemaValidationError) as ex:
            log_and_raise_error(ex)

    # @monitor_with_activity(logger, "FeatureSet.BeginCreateOrUpdate", ActivityType.PUBLICAPI)
    def begin_create_or_update(self, featureset: FeatureSet) -> LROPoller[FeatureSet]:
        """Create or update FeatureSet

        :param featureset: FeatureSet definition.
        :type featureset: FeatureSet
        :return: An instance of LROPoller that returns a FeatureSet.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.FeatureSet]
        """

        featureset_spec = validate_and_get_feature_set_spec(featureset)
        featureset.properties["spec_version"] = "1"
        featureset.properties["spec_data"] = json.dumps(featureset_spec._to_dict())

        sas_uri = None
        featureset, _ = _check_and_upload_path(
            artifact=featureset, asset_operations=self, sas_uri=sas_uri, artifact_type=ErrorTarget.FEATURE_SET
        )

        featureset_resource = FeatureSet._to_rest_object(featureset)

        return self._operation.begin_create_or_update(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            name=featureset.name,
            version=featureset.version,
            body=featureset_resource,
        )

    # @monitor_with_activity(logger, "FeatureSet.Archive", ActivityType.PUBLICAPI)
    def archive(
        self,
        *,
        name: str,
        version: Optional[str] = None,
        label: Optional[str] = None,
        **kwargs,  # pylint:disable=unused-argument
    ) -> None:
        """Archive a FeatureSet asset.

        :param name: Name of FeatureSet asset.
        :type name: str
        :param version: Version of FeatureSet asset.
        :type version: str
        :param label: Label of the FeatureSet asset. (mutually exclusive with version)
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

    # @monitor_with_activity(logger, "FeatureSet.Restore", ActivityType.PUBLICAPI)
    def restore(
        self,
        *,
        name: str,
        version: Optional[str] = None,
        label: Optional[str] = None,
        **kwargs,  # pylint:disable=unused-argument
    ) -> None:
        """Restore an archived FeatureSet asset.

        :param name: Name of FeatureSet asset.
        :type name: str
        :param version: Version of FeatureSet asset.
        :type version: str
        :param label: Label of the FeatureSet asset. (mutually exclusive with version)
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

    def _get_latest_version(self, name: str) -> FeatureSet:
        """Returns the latest version of the asset with the given name.

        Latest is defined as the most recently created, not the most
        recently updated.
        """
        latest_version = _get_latest_version_from_container(
            name, self._container_operation, self._resource_group_name, self._workspace_name
        )
        return self.get(name=name, version=latest_version)


def validate_and_get_feature_set_spec(featureset: FeatureSet) -> FeaturesetSpec:
    # pylint: disable=no-member
    if not featureset.specification and not featureset.specification.path:
        msg = "Missing FeatureSet spec path. Path is required for featureset."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            error_type=ValidationErrorType.MISSING_FIELD,
            target=ErrorTarget.FEATURE_SET,
            error_category=ErrorCategory.USER_ERROR,
        )

    featureset_spec_path = str(featureset.specification.path)

    if not os.path.isdir(featureset_spec_path):
        raise ValidationException(
            message="No such directory: {}".format(featureset_spec_path),
            no_personal_data_message="No such directory",
            target=ErrorTarget.FEATURE_SET,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND,
        )

    featureset_spec_contents = read_feature_set_metadata_contents(path=featureset_spec_path)
    featureset_spec_yaml_path = Path(featureset_spec_path, "FeaturesetSpec")
    return FeaturesetSpec._load(featureset_spec_contents, featureset_spec_yaml_path)
