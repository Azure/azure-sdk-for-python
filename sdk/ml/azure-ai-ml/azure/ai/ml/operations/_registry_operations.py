# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,unused-argument

import json
from typing import Any, Dict, Iterable, Optional, cast

from azure.ai.ml._restclient.arm_ml_service import MachineLearningServicesMgmtClient as ServiceClient102022
from azure.ai.ml._restclient.arm_ml_service._utils.model_base import SdkJSONEncoder
from azure.ai.ml._restclient.arm_ml_service.models import Registry as RestRegistry
from azure.ai.ml._restclient.arm_ml_service.operations._operations import build_registries_create_or_update_request
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities import Registry
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller

from .._utils._azureml_polling import AzureMLPolling
from ..constants._common import LROConfigurations, Scope

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class RegistryOperations:
    """RegistryOperations.

    You should not instantiate this class directly. Instead, you should create an MLClient instance that instantiates it
    for you and attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: ServiceClient102022,
        all_operations: OperationsContainer,
        credentials: Optional[TokenCredential] = None,
        **kwargs: Dict,
    ):
        ops_logger.update_filter()
        self._subscription_id = operation_scope.subscription_id
        self._resource_group_name = operation_scope.resource_group_name
        self._default_registry_name = operation_scope.registry_name
        self._operation = service_client.registries
        self._all_operations = all_operations
        self._credentials = credentials
        self.containerRegistry = "none"
        self._init_kwargs = kwargs

    @monitor_with_activity(ops_logger, "Registry.List", ActivityType.PUBLICAPI)
    def list(self, *, scope: str = Scope.RESOURCE_GROUP) -> Iterable[Registry]:
        """List all registries that the user has access to in the current resource group or subscription.

        :keyword scope: scope of the listing, "resource_group" or "subscription", defaults to "resource_group"
        :paramtype scope: str
        :return: An iterator like instance of Registry objects
        :rtype: ~azure.core.paging.ItemPaged[Registry]
        """
        if scope.lower() == Scope.SUBSCRIPTION:
            return cast(
                Iterable[Registry],
                self._operation.list_by_subscription(
                    cls=lambda objs: [Registry._from_rest_object(obj) for obj in objs]
                ),
            )
        return cast(
            Iterable[Registry],
            self._operation.list(
                cls=lambda objs: [Registry._from_rest_object(obj) for obj in objs],
                resource_group_name=self._resource_group_name,
            ),
        )

    @monitor_with_activity(ops_logger, "Registry.Get", ActivityType.PUBLICAPI)
    def get(self, name: Optional[str] = None) -> Registry:
        """Get a registry by name.

        :param name: Name of the registry.
        :type name: str
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Registry name cannot be
            successfully validated. Details will be provided in the error message.
        :raises ~azure.core.exceptions.HttpResponseError: Raised if the corresponding name and version cannot be
            retrieved from the service.
        :return: The registry with the provided name.
        :rtype: ~azure.ai.ml.entities.Registry
        """

        registry_name = self._check_registry_name(name)
        resource_group = self._resource_group_name
        obj = self._operation.get(resource_group, registry_name)
        return Registry._from_rest_object(obj)  # type: ignore[return-value]

    def _check_registry_name(self, name: Optional[str]) -> str:
        registry_name = name or self._default_registry_name
        if not registry_name:
            msg = "Please provide a registry name or use a MLClient with a registry name set."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.REGISTRY,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        return registry_name

    def _get_polling(self, name: str) -> AzureMLPolling:
        """Return the polling with custom poll interval.

        :param name: The registry name
        :type name: str
        :return: A poller with custom poll interval.
        :rtype: AzureMLPolling
        """
        path_format_arguments = {
            "registryName": name,
            "resourceGroupName": self._resource_group_name,
        }
        return AzureMLPolling(
            LROConfigurations.POLL_INTERVAL,
            path_format_arguments=path_format_arguments,
        )

    @monitor_with_activity(ops_logger, "Registry.BeginCreate", ActivityType.PUBLICAPI)
    def begin_create(
        self,
        registry: Registry,
        **kwargs: Dict,
    ) -> LROPoller[Registry]:
        """Create a new Azure Machine Learning Registry, or try to update if it already exists.

        Note: Due to service limitations we have to sleep for
        an additional 30~45 seconds AFTER the LRO Poller concludes
        before the registry will be consistently deleted from the
        perspective of subsequent operations.
        If a deletion is required for subsequent operations to
        work properly, callers should implement that logic until the
        service has been fixed to return a reliable LRO.

        :param registry: Registry definition.
        :type registry: Registry
        :return: A poller to track the operation status.
        :rtype: LROPoller
        """
        registry_data = registry._to_rest_object()
        # The shared arm_ml_service ``begin_create_or_update`` was generated against an api-version whose
        # registry-create swagger declares only 200/201 as terminal initial statuses, so it raises on the
        # 202 Accepted the service actually returns for this LRO. We send the create request ourselves,
        # accept 202, and drive our own poller (mirrors how we build the request body as a dict).
        registries_op = self._operation
        client = registries_op._client
        config = registries_op._config
        content = json.dumps(registry_data, cls=SdkJSONEncoder, exclude_readonly=True)
        request = build_registries_create_or_update_request(
            resource_group_name=self._resource_group_name,
            registry_name=registry.name,
            subscription_id=config.subscription_id,
            content_type="application/json",
            api_version=config.api_version,
            content=content,
        )
        path_format_arguments = {"endpoint": config.base_url}
        request.url = client.format_url(request.url, **path_format_arguments)
        initial_response = client._pipeline.run(request, stream=False)
        status = initial_response.http_response.status_code
        if status not in (200, 201, 202):
            initial_response.http_response.raise_for_status()

        def _get_long_running_output(pipeline_response: Any) -> Registry:
            rest_registry = RestRegistry._deserialize(pipeline_response.http_response.json(), [])
            return Registry._from_rest_object(rest_registry)  # type: ignore[return-value]

        poller: LROPoller = LROPoller(
            client,
            initial_response,
            _get_long_running_output,
            self._get_polling(str(registry.name)),
        )
        return poller

    @monitor_with_activity(ops_logger, "Registry.BeginDelete", ActivityType.PUBLICAPI)
    def begin_delete(self, *, name: str, **kwargs: Dict) -> LROPoller[None]:
        """Delete a registry if it exists. Returns nothing on a successful operation.

        :keyword name: Name of the registry
        :paramtype name: str
        :return: A poller to track the operation status.
        :rtype: LROPoller
        """
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        return self._operation.begin_delete(
            resource_group_name=resource_group,
            registry_name=name,
            **self._init_kwargs,
        )
