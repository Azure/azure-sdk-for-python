# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, Iterable, Optional

from marshmallow import ValidationError

from azure.ai.ml._restclient.v2023_04_01_preview import AzureMachineLearningWorkspaces as ServiceClient042023Preview
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope

# from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities._hub.lean import _LeanWorkspace

from azure.ai.ml.constants._common import Scope
from azure.ai.ml.entities._hub._constants import LEAN_KIND
from ._workspace_operations_base import WorkspaceOperationsBase

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class LeanOperations(WorkspaceOperationsBase):
    """_LeanOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: ServiceClient042023Preview,
        all_operations: OperationsContainer,
        credentials: Optional[TokenCredential] = None,
        **kwargs: Dict,
    ):
        ops_logger.update_info(kwargs)
        super().__init__(
            operation_scope=operation_scope,
            service_client=service_client,
            all_operations=all_operations,
            credentials=credentials,
            **kwargs,
        )

    # @monitor_with_activity(logger, "Lean.List", ActivityType.PUBLICAPI)
    def list(self, *, scope: str = Scope.RESOURCE_GROUP) -> Iterable[_LeanWorkspace]:
        """List all lean workspaces that the user has access to in the current
        resource group or subscription.

        :param scope: scope of the listing, "resource_group" or "subscription", defaults to "resource_group"
        :type scope: str, optional
        :return: An iterator like instance of _LeanWorkspace objects
        :rtype: ~azure.core.paging.ItemPaged[_LeanWorkspace]
        """

        if scope == Scope.SUBSCRIPTION:
            return self._operation.list_by_subscription(
                cls=lambda objs: [
                    _LeanWorkspace._from_rest_object(filterObj)
                    for filterObj in filter(lambda ws: ws.kind.lower() == LEAN_KIND, objs)
                ]
            )
        return self._operation.list_by_resource_group(
            self._resource_group_name,
            cls=lambda objs: [
                _LeanWorkspace._from_rest_object(filterObj)
                for filterObj in filter(lambda ws: ws.kind.lower() == LEAN_KIND, objs)
            ],
        )

    # @monitor_with_activity(logger, "Lean.Get", ActivityType.PUBLICAPI)
    @distributed_trace
    # pylint: disable=arguments-renamed
    def get(self, name: str, **kwargs: Dict) -> _LeanWorkspace:
        """Get a Lean workspace by name.

        :param name: Name of the lean workspace.
        :type name: str
        :return: The lean workspace with the provided name.
        :rtype: _LeanWorkspace
        """

        Lean_workspace = None
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        rest_workspace_obj = self._operation.get(resource_group, name)
        if rest_workspace_obj and rest_workspace_obj.kind and rest_workspace_obj.kind.lower() == LEAN_KIND:
            Lean_workspace = _LeanWorkspace._from_rest_object(rest_workspace_obj)

        return Lean_workspace

    # @monitor_with_activity(logger, "Lean.BeginCreate", ActivityType.PUBLICAPI)
    @distributed_trace
    # pylint: disable=arguments-differ
    def begin_create(
        self,
        Lean: _LeanWorkspace,
        update_dependent_resources: bool = False,
        **kwargs: Dict,
    ) -> LROPoller[_LeanWorkspace]:
        """Create a new Lean workspace.

        Returns the Lean workspace if already exists.

        :param Lean: Lean workspace definition.
        :type Lean: _LeanWorkspace
        :type update_dependent_resources: boolean
        :return: An instance of LROPoller that returns a _LeanWorkspace.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities._LeanWorkspace]
        """

        def get_callback():
            return self.get(Lean.name)

        return super().begin_create(
            workspace=Lean,
            update_dependent_resources=update_dependent_resources,
            get_callback=get_callback,
            **kwargs,
        )

    # @monitor_with_activity(logger, "Lean.BeginUpdate", ActivityType.PUBLICAPI)
    @distributed_trace
    # pylint: disable=arguments-renamed
    def begin_update(
        self,
        Lean: _LeanWorkspace,
        **kwargs: Dict,
    ) -> LROPoller[_LeanWorkspace]:
        """Update friendly name, description, tags, of a Lean workspace.

        :param Lean: Lean resource.
        :type Lean: _LeanWorkspace
        :return: An instance of LROPoller that returns a _LeanWorkspace.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities._LeanWorkspace]
        """
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        rest_workspace_obj = self._operation.get(resource_group, Lean.name)
        if not (
            rest_workspace_obj and rest_workspace_obj.kind and rest_workspace_obj.kind.lower() == LEAN_KIND
        ):
            raise ValidationError("{0} is not a Lean workspace".format(Lean.name))

        def deserialize_callback(rest_obj):
            return _LeanWorkspace._from_rest_object(rest_obj=rest_obj)

        return super().begin_update(
            workspace=Lean,
            update_dependent_resources=False,
            deserialize_callback=deserialize_callback,
            **kwargs,
        )

    # @monitor_with_activity(logger, "Lean.BeginDelete", ActivityType.PUBLICAPI)
    @distributed_trace
    def begin_delete(self, name: str, *, delete_dependent_resources: bool, **kwargs: Dict) -> LROPoller:
        """Delete a Lean.

        :param name: Name of the Lean
        :type name: str
        :param delete_dependent_resources: Whether to delete resources associated with the Lean,
            i.e., container registry, storage account, key vault.
            The default is False. Set to True to delete these resources.
        :type delete_dependent_resources: bool
        :return: A poller to track the operation status.
        :rtype: ~azure.core.polling.LROPoller[None]
        """
        resource_group = kwargs.get("resource_group") or self._resource_group_name
        rest_workspace_obj = self._operation.get(resource_group, name)
        if not (
            rest_workspace_obj and rest_workspace_obj.kind and rest_workspace_obj.kind.lower() == LEAN_KIND
        ):
            raise ValidationError("{0} is not a feature store".format(name))

        return super().begin_delete(name=name, delete_dependent_resources=delete_dependent_resources, **kwargs)
