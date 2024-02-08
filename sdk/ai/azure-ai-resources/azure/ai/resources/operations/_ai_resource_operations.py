# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Iterable, Optional

from azure.core.tracing.decorator import distributed_trace

from azure.ai.resources.constants._common import DEFAULT_OPEN_AI_CONNECTION_NAME
from azure.ai.resources.entities import AIResource
from azure.ai.ml import MLClient
from azure.ai.ml.constants._common import Scope
from azure.ai.ml.entities._workspace_hub._constants import ENDPOINT_AI_SERVICE_KIND
from azure.core.polling import LROPoller

from azure.ai.resources._telemetry import ActivityType, monitor_with_activity, monitor_with_telemetry_mixin, ActivityLogger

activity_logger = ActivityLogger(__name__)
logger, module_logger = activity_logger.package_logger, activity_logger.module_logger


class AIResourceOperations:
    """AIResourceOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    # TODO add operation scope at init level?
    def __init__(self, ml_client: MLClient, **kwargs: Any):
        self._ml_client = ml_client
        activity_logger.update_info(kwargs)

    @distributed_trace
    @monitor_with_activity(logger, "AIResource.Get", ActivityType.PUBLICAPI)
    def get(self, *, name: str, **kwargs) -> AIResource:
        """Get an AI resource by name.

        :keyword name: Name of the AI resource.
        :paramtype name: str

        :return: The AI resource with the provided name.
        :rtype: ~azure.ai.resources.entities.AIResource
        """
        workspace_hub = self._ml_client._workspace_hubs.get(name=name, **kwargs)
        resource = AIResource._from_v2_workspace_hub(workspace_hub)
        return resource

    @distributed_trace
    @monitor_with_activity(logger, "AIResource.List", ActivityType.PUBLICAPI)
    def list(self, *, scope: str = Scope.RESOURCE_GROUP) -> Iterable[AIResource]:
        """List all AI resource assets in a project.

        :keyword scope: The scope of the listing. Can be either "resource_group" or "subscription", and defaults to "resource_group".
        :paramtype scope: str

        :return: An iterator like instance of AI resource objects
        :rtype: Iterable[~azure.ai.resources.entities.AIResource]
        """
        return [AIResource._from_v2_workspace_hub(wh) for wh in self._ml_client._workspace_hubs.list(scope=scope)]

    @distributed_trace
    @monitor_with_activity(logger, "AIResource.BeginCreate", ActivityType.PUBLICAPI)
    def begin_create(
        self,
        *,
        ai_resource: AIResource,
        update_dependent_resources: bool = False,
        endpoint_resource_id: Optional[str] = None,
        endpoint_kind: str = ENDPOINT_AI_SERVICE_KIND,
        **kwargs,
    ) -> LROPoller[AIResource]:
        """Create a new AI resource.

        :keyword ai_resource: Resource definition
            or object which can be translated to a AI resource.
        :paramtype ai_resource: ~azure.ai.resources.entities.AIResource
        :keyword update_dependent_resources: Whether to update dependent resources. Defaults to False.
        :paramtype update_dependent_resources: boolean
        :keyword endpoint_resource_id: The UID of an AI service or Open AI resource.
            The created hub will automatically create several
            endpoints connecting to this resource, and creates its own otherwise.
            If an Open AI resource ID is provided, then only a single Open AI
            endpoint will be created. If set, then endpoint_resource_id should also be
            set unless its default value is applicable.
        :paramtype endpoint_resource_id: str
        :keyword endpoint_kind: What kind of endpoint resource is being provided
            by the endpoint_resource_id field. Defaults to "AIServices". The only other valid
            input is "OpenAI".
        :paramtype endpoint_kind: str
        :return: An instance of LROPoller that returns the created AI resource.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.resources.entities.AIResource]
        """
        return self._ml_client.workspace_hubs.begin_create(
            workspace_hub=ai_resource._workspace_hub,
            update_dependent_resources=update_dependent_resources,
            endpoint_resource_id=endpoint_resource_id,
            endpoint_kind=endpoint_kind,
            cls=lambda hub: AIResource._from_v2_workspace_hub(hub),
            **kwargs
        )

    @distributed_trace
    @monitor_with_activity(logger, "AIResource.BeginUpdate", ActivityType.PUBLICAPI)
    def begin_update(
        self, *, ai_resource: AIResource, update_dependent_resources: bool = False, **kwargs
    ) -> LROPoller[AIResource]:
        """Update the name, description, tags, PNA, manageNetworkSettings, or encryption of a Resource

        :keyword ai_resource: AI resource definition.
        :paramtype ai_resource: ~azure.ai.resources.entities.AIResource
        :keyword update_dependent_resources: Whether to update dependent resources. Defaults to False.
        :paramtype update_dependent_resources: boolean
        :return: An instance of LROPoller that returns the updated AI resource.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.resources.entities.AIResource]
        """
        return self._ml_client.workspace_hubs.begin_update(
            workspace_hub=ai_resource._workspace_hub,
            update_dependent_resources=update_dependent_resources,
            cls=lambda hub: AIResource._from_v2_workspace_hub(hub),
            **kwargs
        )

    @distributed_trace
    @monitor_with_activity(logger, "AIResource.BeginDelete", ActivityType.PUBLICAPI)
    def begin_delete(
        self, *, name: str, delete_dependent_resources: bool, permanently_delete: bool = False, **kwargs
    ) -> LROPoller[None]:
        """Delete an AI resource.

        :keyword name: Name of the Resource
        :paramtype name: str
        :keyword delete_dependent_resources: Whether to delete dependent resources associated with the AI resource.
        :paramtype delete_dependent_resources: bool
        :keyword permanently_delete: AI resource are soft-deleted by default to allow recovery of data.
            Set this flag to true to override the soft-delete behavior and permanently delete your AI resource.
        :paramtype permanently_delete: bool
        :return: A poller to track the operation status.
        :rtype: ~azure.core.polling.LROPoller[None]
        """

        return self._ml_client.workspace_hubs.begin_delete(
            name=name,
            delete_dependent_resources=delete_dependent_resources,
            permanently_delete=permanently_delete,
            **kwargs
        )
