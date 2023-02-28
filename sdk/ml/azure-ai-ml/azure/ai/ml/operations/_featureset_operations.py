# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, Optional

from marshmallow.exceptions import ValidationError as SchemaValidationError

from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2023_02_01_preview.models import ListViewType, FeaturesetVersion
from azure.ai.ml._restclient.v2023_02_01_preview import AzureMachineLearningWorkspaces as ServiceClient022023Preview
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope, _ScopeDependentOperations
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException


# from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._http_utils import HttpPipeline
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities._assets import Featureset
from azure.core.paging import ItemPaged

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class FeaturesetOperations(_ScopeDependentOperations):
    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: ServiceClient022023Preview,
        **kwargs: Dict,
    ):

        super(FeaturesetOperations, self).__init__(operation_scope, operation_config)
        # ops_logger.update_info(kwargs)
        self._operation = service_client.featureset_versions
        self._container_operation = service_client.featureset_containers
        self._service_client = service_client
        self._init_kwargs = kwargs
        self._requests_pipeline: HttpPipeline = kwargs.pop("requests_pipeline")
        # Maps a label to a function which given an asset name,
        # returns the asset associated with the label
        self._managed_label_resolver = {"latest": self._get_latest_version}

    def _get(self, name: str, version: str = None) -> FeaturesetVersion:
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

    # @monitor_with_activity(logger, "Featureset.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, version: Optional[str] = None, label: Optional[str] = None) -> Featureset:
        """Get the specified featureset asset.

        :param name: Name of featureset asset.
        :type name: str
        :param version: Version of featureset asset.
        :type version: str
        :param label: Label of the featureset asset. (mutually exclusive with version)
        :type label: str
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Featureset cannot be successfully
            identified and retrieved. Details will be provided in the error message.
        :return: Featureset asset object.
        :rtype: ~azure.ai.ml.entities.Featureset
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

            # if label:
            # return _resolve_label_to_asset(self, name, label)

            if not version:
                msg = "Must provide either version or label."
                raise ValidationException(
                    message=msg,
                    target=ErrorTarget.DATA,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.MISSING_FIELD,
                )
            featureset_version_resource = self._get(name, version)
            return Featureset._from_rest_object(featureset_version_resource)
        except (ValidationException, SchemaValidationError) as ex:
            log_and_raise_error(ex)
