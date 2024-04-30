# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Iterable

from azure.ai.ml.exceptions import ValidationException, ErrorTarget, ErrorCategory, ValidationErrorType
from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._restclient.v2024_01_01_preview import AzureMachineLearningWorkspaces as ServiceClient202401Preview
from azure.ai.ml._restclient.v2024_01_01_preview.models import RegenerateEndpointKeysRequest, KeyType
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)
from azure.core.polling import LROPoller
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities._autogen_entities.models import ServerlessEndpoint
from azure.ai.ml.entities._endpoint.online_endpoint import EndpointAuthKeys
from azure.ai.ml.constants._endpoint import EndpointKeyType


ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class ServerlessEndpointOperations(_ScopeDependentOperations):
    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: ServiceClient202401Preview,
        all_operations: OperationsContainer,
    ):
        super().__init__(operation_scope, operation_config)
        self._service_client = service_client.serverless_endpoints
        self._marketplace_subscriptions = service_client.marketplace_subscriptions
        self._all_operations = all_operations

    def _get_workspace_location(self) -> str:
        return str(
            self._all_operations.all_operations[AzureMLResourceType.WORKSPACE].get(self._workspace_name).location
        )

    @experimental
    @monitor_with_activity(ops_logger, "ServerlessEndpoint.BeginCreateOrUpdate", ActivityType.PUBLICAPI)
    def begin_create_or_update(self, endpoint: ServerlessEndpoint, **kwargs) -> LROPoller[ServerlessEndpoint]:
        if not endpoint.location:
            endpoint.location = self._get_workspace_location()
        return self._service_client.begin_create_or_update(
            self._resource_group_name,
            self._workspace_name,
            endpoint.name,
            endpoint._to_rest_object(),  # type: ignore
            cls=lambda response, deserialized, headers: ServerlessEndpoint._from_rest_object(deserialized),  # type: ignore
            **kwargs,
        )

    @experimental
    @monitor_with_activity(ops_logger, "ServerlessEndpoint.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, **kwargs) -> ServerlessEndpoint:
        return self._service_client.get(
            self._resource_group_name,
            self._workspace_name,
            name,
            cls=lambda response, deserialized, headers: ServerlessEndpoint._from_rest_object(deserialized),  # type: ignore
            **kwargs,
        )

    @experimental
    @monitor_with_activity(ops_logger, "ServerlessEndpoint.list", ActivityType.PUBLICAPI)
    def list(self, **kwargs) -> Iterable[ServerlessEndpoint]:
        return self._service_client.list(
            self._resource_group_name,
            self._workspace_name,
            cls=lambda objs: [ServerlessEndpoint._from_rest_object(obj) for obj in objs],  # type: ignore
            **kwargs,
        )

    @experimental
    @monitor_with_activity(ops_logger, "ServerlessEndpoint.BeginDelete", ActivityType.PUBLICAPI)
    def begin_delete(self, name: str, **kwargs) -> LROPoller[None]:
        return self._service_client.begin_delete(
            self._resource_group_name,
            self._workspace_name,
            name,
            **kwargs,
        )

    @experimental
    @monitor_with_activity(ops_logger, "ServerlessEndpoint.GetKeys", ActivityType.PUBLICAPI)
    def get_keys(self, name: str, **kwargs) -> EndpointAuthKeys:
        return self._service_client.list_keys(
            self._resource_group_name,
            self._workspace_name,
            name,
            cls=lambda response, deserialized, headers: EndpointAuthKeys._from_rest_object(deserialized),
            **kwargs,
        )

    @experimental
    @monitor_with_activity(ops_logger, "ServerlessEndpoint.BeginRegenerateKeys", ActivityType.PUBLICAPI)
    def begin_regenerate_keys(
        self,
        name: str,
        *,
        key_type: str = EndpointKeyType.PRIMARY_KEY_TYPE,
        **kwargs,
    ) -> LROPoller[None]:
        keys = self.get_keys(
            name=name,
        )
        if key_type.lower() == EndpointKeyType.PRIMARY_KEY_TYPE:
            key_request = RegenerateEndpointKeysRequest(key_type=KeyType.Primary, key_value=keys.primary_key)
        elif key_type.lower() == EndpointKeyType.SECONDARY_KEY_TYPE:
            key_request = RegenerateEndpointKeysRequest(key_type=KeyType.Secondary, key_value=keys.secondary_key)
        else:
            msg = "Key type must be 'primary' or 'secondary'."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.SERVERLESS_ENDPOINT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        return self._service_client.begin_regenerate_keys(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=name,
            body=key_request,
            cls=lambda response, deserialized, headers: EndpointAuthKeys._from_rest_object(deserialized),
            **kwargs,
        )
