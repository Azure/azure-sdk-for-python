# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, Iterable, Optional

from azure.core.tracing.decorator import distributed_trace

from azure.ai.resources.entities.project import Project
from azure.ai.ml import MLClient
from azure.ai.ml._restclient.v2023_06_01_preview import AzureMachineLearningWorkspaces as ServiceClient062023Preview
from azure.ai.ml.constants._common import Scope

# TODO remove resclient references once v2 SDK operations supports lean filtering
from azure.ai.ml.entities import Workspace
from azure.core.polling import LROPoller

from azure.ai.resources._telemetry import ActivityType, monitor_with_activity, monitor_with_telemetry_mixin, ActivityLogger

ops_logger = ActivityLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger


class ProjectOperations:
    """ProjectOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    # TODO add scope back in?
    def __init__(
        self, resource_group_name: str, ml_client: MLClient, service_client: ServiceClient062023Preview, **kwargs: Any
    ):
        self._ml_client = ml_client
        self._service_client = service_client
        self._resource_group_name = resource_group_name
        ops_logger.update_info(kwargs)


    @distributed_trace
    @monitor_with_activity(logger, "Project.Get", ActivityType.PUBLICAPI)
    # Note: Can get non-lean workspaces this way. Should we prevent that? Does not currently seem possible via restclient.
    def get(self, *, name: Optional[str] = None, **kwargs: Dict) -> Project:
        """Get a project by name.

        :keyword name: Name of the project.
        :paramtype name: str
        :return: The project with the provided name.
        :rtype: ~azure.ai.resource.entities.Project
        """

        workspace = self._ml_client._workspaces.get(name=name, **kwargs)
        project = Project._from_v2_workspace(workspace)
        return project

    @distributed_trace
    @monitor_with_activity(logger, "Project.List", ActivityType.PUBLICAPI)
    def list(self, *, scope: str = Scope.RESOURCE_GROUP) -> Iterable[Project]:
        """List all projects that the user has access to in the current resource group or subscription.

        :keyword scope: The scope of the listing. Can be either "resource_group" or "subscription", and defaults to "resource_group".
        :paramtype scope: str
        :return: An iterator like instance of Project objects
        :rtype: Iterable[~azure.ai.resource.entities.Project]
        """

        workspaces = []
        if scope == Scope.SUBSCRIPTION:
            workspaces = self._service_client.workspaces.list_by_subscription(
                kind="project",  # TODO constant this
                cls=lambda objs: [Workspace._from_rest_object(obj) for obj in objs],
            )
        else:  # scope == Scope.RESOURCE_GROUP
            workspaces = self._service_client.workspaces.list_by_resource_group(
                kind="project",
                resource_group_name=self._resource_group_name,
                cls=lambda objs: [Workspace._from_rest_object(obj) for obj in objs],
            )
        return [Project._from_v2_workspace(ws) for ws in workspaces]

    @distributed_trace
    @monitor_with_activity(logger, "Project.BeginCreate", ActivityType.PUBLICAPI)
    def begin_create(
        self, *, project: Project, update_dependent_resources: bool = False, **kwargs
    ) -> LROPoller[Project]:
        """Create a new project. Returns the project if it already exists.

        :keyword project: Project definition.
        :paramtype project: ~azure.ai.resources.entities.project
        :keyword update_dependent_resources: Whether to update dependent resources
        :paramtype update_dependent_resources: boolean
        :return: An instance of LROPoller that returns a project.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.resources.entities.project]
        """
        return self._ml_client.workspaces.begin_create(
            workspace=project._workspace,
            update_dependent_resources=update_dependent_resources,
            cls=lambda workspace: Project._from_v2_workspace(workspace=workspace),
            **kwargs,
        )

    @distributed_trace
    @monitor_with_activity(logger, "Project.BeginUpdate", ActivityType.PUBLICAPI)
    def begin_update(
        self, *, project: Project, update_dependent_resources: bool = False, **kwargs
    ) -> LROPoller[Project]:
        """Update a project.

        :keyword project: Project definition.
        :paramtype project: ~azure.ai.resources.entities.project
        :keyword update_dependent_resources: Whether to update dependent resources
        :paramtype update_dependent_resources: boolean
        :return: An instance of LROPoller that returns a project.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.resources.entities.project]
        """
        return self._ml_client.workspaces.begin_update(
            workspace=project._workspace,
            update_dependent_resources=update_dependent_resources,
            cls=lambda workspace: Project._from_v2_workspace(workspace=workspace),
            **kwargs,
        )

    @distributed_trace
    @monitor_with_activity(logger, "Project.BeginDelete", ActivityType.PUBLICAPI)
    def begin_delete(
        self,
        *,
        name: str,
        delete_dependent_resources: bool,
        permanently_delete: bool = False,
    ):
        """Delete a project.

        :keyword name: Name of the project
        :paramtype name: str
        :keyword delete_dependent_resources: Whether to delete resources associated with the project,
            i.e., container registry, storage account, key vault, and application insights.
            The default is False. Set to True to delete these resources.
        :paramtype delete_dependent_resources: bool
        :keyword permanently_delete: Project are soft-deleted by default to allow recovery of project data.
            Set this flag to true to override the soft-delete behavior and permanently delete your project.
        :paramtype permanently_delete: bool
        :return: A poller to track the operation status.
        :rtype: ~azure.core.polling.LROPoller[None]
        """

        return self._ml_client.workspaces.begin_delete(
            name=name, delete_dependent_resources=delete_dependent_resources, permanently_delete=permanently_delete
        )
