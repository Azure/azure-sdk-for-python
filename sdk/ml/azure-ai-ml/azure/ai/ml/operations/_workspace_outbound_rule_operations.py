# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Iterable, Optional

from azure.ai.ml._restclient.v2024_07_01_preview import AzureMachineLearningWorkspaces as ServiceClient072024Preview
from azure.ai.ml._restclient.v2024_07_01_preview.models import OutboundRuleBasicResource
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities._workspace.networking import OutboundRule
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class WorkspaceOutboundRuleOperations:
    """WorkspaceOutboundRuleOperations.

    You should not instantiate this class directly. Instead, you should create
    an MLClient instance that instantiates it for you and attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: ServiceClient072024Preview,
        all_operations: OperationsContainer,
        credentials: TokenCredential = None,
        **kwargs: Dict,
    ):
        ops_logger.update_info(kwargs)
        self._subscription_id = operation_scope.subscription_id
        self._resource_group_name = operation_scope.resource_group_name
        self._default_workspace_name = operation_scope.workspace_name
        self._all_operations = all_operations
        self._rule_operation = service_client.managed_network_settings_rule
        self._credentials = credentials
        self._init_kwargs = kwargs

    @monitor_with_activity(ops_logger, "WorkspaceOutboundRule.Get", ActivityType.PUBLICAPI)
    def get(self, workspace_name: str, outbound_rule_name: str, **kwargs: Any) -> OutboundRule:
        """Get a workspace OutboundRule by name.

        :param workspace_name: Name of the workspace.
        :type workspace_name: str
        :param outbound_rule_name: Name of the outbound rule.
        :type outbound_rule_name: str
        :return: The OutboundRule with the provided name for the workspace.
        :rtype: ~azure.ai.ml.entities.OutboundRule

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START outbound_rule_get]
                :end-before: [END outbound_rule_get]
                :language: python
                :dedent: 8
                :caption: Get the outbound rule for a workspace with the given name.
        """

        workspace_name = self._check_workspace_name(workspace_name)
        resource_group = kwargs.get("resource_group") or self._resource_group_name

        obj = self._rule_operation.get(resource_group, workspace_name, outbound_rule_name)
        # pylint: disable=protected-access
        res: OutboundRule = OutboundRule._from_rest_object(obj.properties, name=obj.name)  # type: ignore
        return res

    @monitor_with_activity(ops_logger, "WorkspaceOutboundRule.BeginCreate", ActivityType.PUBLICAPI)
    def begin_create(self, workspace_name: str, rule: OutboundRule, **kwargs: Any) -> LROPoller[OutboundRule]:
        """Create a Workspace OutboundRule.

        :param workspace_name: Name of the workspace.
        :type workspace_name: str
        :param rule: OutboundRule definition (FqdnDestination, PrivateEndpointDestination, or ServiceTagDestination).
        :type rule: ~azure.ai.ml.entities.OutboundRule
        :return: An instance of LROPoller that returns an OutboundRule.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.OutboundRule]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START outbound_rule_begin_create]
                :end-before: [END outbound_rule_begin_create]
                :language: python
                :dedent: 8
                :caption: Create an FQDN outbound rule for a workspace with the given name,
                    similar can be done for PrivateEndpointDestination or ServiceTagDestination.
        """

        workspace_name = self._check_workspace_name(workspace_name)
        resource_group = kwargs.get("resource_group") or self._resource_group_name

        # pylint: disable=protected-access
        rule_params = OutboundRuleBasicResource(properties=rule._to_rest_object())  # type: ignore

        # pylint: disable=unused-argument, docstring-missing-param
        def callback(_: Any, deserialized: Any, args: Any) -> Optional[OutboundRule]:
            """Callback to be called after completion

            :return: Outbound rule deserialized.
            :rtype: ~azure.ai.ml.entities.OutboundRule
            """
            properties = deserialized.properties
            name = deserialized.name
            return OutboundRule._from_rest_object(properties, name=name)  # pylint: disable=protected-access

        poller = self._rule_operation.begin_create_or_update(
            resource_group, workspace_name, rule.name, rule_params, polling=True, cls=callback
        )
        module_logger.info("Create request initiated for outbound rule with name: %s\n", rule.name)
        return poller

    @monitor_with_activity(ops_logger, "WorkspaceOutboundRule.BeginUpdate", ActivityType.PUBLICAPI)
    def begin_update(self, workspace_name: str, rule: OutboundRule, **kwargs: Any) -> LROPoller[OutboundRule]:
        """Update a Workspace OutboundRule.

        :param workspace_name: Name of the workspace.
        :type workspace_name: str
        :param rule: OutboundRule definition (FqdnDestination, PrivateEndpointDestination, or ServiceTagDestination).
        :type rule: ~azure.ai.ml.entities.OutboundRule
        :return: An instance of LROPoller that returns an OutboundRule.
        :rtype: ~azure.core.polling.LROPoller[~azure.ai.ml.entities.OutboundRule]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START outbound_rule_begin_update]
                :end-before: [END outbound_rule_begin_update]
                :language: python
                :dedent: 8
                :caption: Update an FQDN outbound rule for a workspace with the given name,
                    similar can be done for PrivateEndpointDestination or ServiceTagDestination.
        """

        workspace_name = self._check_workspace_name(workspace_name)
        resource_group = kwargs.get("resource_group") or self._resource_group_name

        # pylint: disable=protected-access
        rule_params = OutboundRuleBasicResource(properties=rule._to_rest_object())  # type: ignore

        # pylint: disable=unused-argument, docstring-missing-param
        def callback(_: Any, deserialized: Any, args: Any) -> Optional[OutboundRule]:
            """Callback to be called after completion

            :return: Outbound rule deserialized.
            :rtype: ~azure.ai.ml.entities.OutboundRule
            """
            properties = deserialized.properties
            name = deserialized.name
            return OutboundRule._from_rest_object(properties, name=name)  # pylint: disable=protected-access

        poller = self._rule_operation.begin_create_or_update(
            resource_group, workspace_name, rule.name, rule_params, polling=True, cls=callback
        )
        module_logger.info("Update request initiated for outbound rule with name: %s\n", rule.name)
        return poller

    @monitor_with_activity(ops_logger, "WorkspaceOutboundRule.List", ActivityType.PUBLICAPI)
    def list(self, workspace_name: str, **kwargs: Any) -> Iterable[OutboundRule]:
        """List Workspace OutboundRules.

        :param workspace_name: Name of the workspace.
        :type workspace_name: str
        :return: An Iterable of OutboundRule.
        :rtype: Iterable[OutboundRule]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START outbound_rule_list]
                :end-before: [END outbound_rule_list]
                :language: python
                :dedent: 8
                :caption: List the outbound rule for a workspace with the given name.
        """

        workspace_name = self._check_workspace_name(workspace_name)
        resource_group = kwargs.get("resource_group") or self._resource_group_name

        rest_rules = self._rule_operation.list(resource_group, workspace_name)

        result = [
            OutboundRule._from_rest_object(rest_obj=obj.properties, name=obj.name)  # pylint: disable=protected-access
            for obj in rest_rules
        ]
        return result  # type: ignore

    @monitor_with_activity(ops_logger, "WorkspaceOutboundRule.Remove", ActivityType.PUBLICAPI)
    def begin_remove(self, workspace_name: str, outbound_rule_name: str, **kwargs: Any) -> LROPoller[None]:
        """Remove a Workspace OutboundRule.

        :param workspace_name: Name of the workspace.
        :type workspace_name: str
        :param outbound_rule_name: Name of the outbound rule to remove.
        :type outbound_rule_name: str
        :return: An Iterable of OutboundRule.
        :rtype: Iterable[OutboundRule]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_workspace.py
                :start-after: [START outbound_rule_begin_remove]
                :end-before: [END outbound_rule_begin_remove]
                :language: python
                :dedent: 8
                :caption: Remove the outbound rule for a workspace with the given name.
        """

        workspace_name = self._check_workspace_name(workspace_name)
        resource_group = kwargs.get("resource_group") or self._resource_group_name

        poller = self._rule_operation.begin_delete(
            resource_group_name=resource_group,
            workspace_name=workspace_name,
            rule_name=outbound_rule_name,
        )
        module_logger.info("Delete request initiated for outbound rule: %s\n", outbound_rule_name)
        return poller

    def _check_workspace_name(self, name: str) -> str:
        """Validates that a workspace name exists.

        :param name: Name for a workspace resource.
        :type name: str
        :raises ~azure.ai.ml.ValidationException: Raised if updating nothing is specified for name and
        MLClient does not have workspace name set.
        :return: No return
        :rtype: None
        """
        workspace_name = name or self._default_workspace_name
        if not workspace_name:
            msg = "Please provide a workspace name or use a MLClient with a workspace name set."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.WORKSPACE,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        return workspace_name
