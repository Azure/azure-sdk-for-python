# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from typing import Callable, Dict, Optional, TypeVar, cast

from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

T = TypeVar("T")
module_logger = logging.getLogger(__name__)


class OperationConfig(object):
    """This class is used to store common configurations that are shared across operation objects of an MLClient object."""

    def __init__(self, show_progress: bool, enable_telemetry: bool) -> None:
        """Return common configurations that are shared across operation objects of an MLClient object.

        :param show_progress: Whether to display progress bars for long running operations
        :type show_progress: bool
        :param enable_telemetry: Whether to enable telemetry for Jupyter Notebooks. Telemetry cannot be enabled for other contexts.
        :type enable_telemetry: bool
        """
        self._show_progress = show_progress
        self._enable_telemetry = enable_telemetry

    @property
    def show_progress(self) -> bool:
        """Indicate whether to display progress bars for long running operations.

        :return: Value of show_progress
        :rtype: bool
        """
        return self._show_progress

    @property
    def enable_telemetry(self) -> bool:
        """Indicate whether to enable telemetry for Jupyter Notebooks. Telemetry cannot be enabled for other contexts.

        :return: Value of enable_telemetry
        :rtype: bool
        """
        return self._enable_telemetry


class OperationScope(object):
    """This class is used to store scope variables for the operations classes of an MLClient object."""

    def __init__(
        self,
        subscription_id: str,
        resource_group_name: str,
        workspace_name: str,
        registry_name: Optional[str] = None,
    ):
        """Scope variables for the operations classes of an MLClient object.

        :param subscription_id: Azure Subscription ID
        :type subscription_id: str
        :param resource_group_name: Resource group name
        :type resource_group_name: str
        :param workspace_name: Workspace name, defaults to None
        :type workspace_name: str
        :param registry_name: Registry name, defaults to None
        :type registry_name: Optional[str]
        """
        self._subscription_id = subscription_id
        self._resource_group_name = resource_group_name
        self._workspace_name = workspace_name
        self._registry_name = registry_name

    @property
    def subscription_id(self) -> str:
        """Return Azure subscription ID.

        :return: Azure subscription ID
        :rtype: str
        """
        return self._subscription_id

    @property
    def resource_group_name(self) -> str:
        """Return resource group name.

        :return: Resource group name
        :rtype: str
        """
        return self._resource_group_name

    @property
    def workspace_name(self) -> str:
        """Return workspace name.

        :return: Workspace name
        :rtype: str
        """
        return self._workspace_name

    @property
    def registry_name(self) -> Optional[str]:
        """Return registry name.

        :return: Registry name
        :rtype: Optional[str]
        """
        return self._registry_name

    @workspace_name.setter
    def workspace_name(self, value: str) -> None:
        """Set workspace name.

        :param value: Workspace name
        :type value: str
        """
        self._workspace_name = value

    @registry_name.setter
    def registry_name(self, value: str) -> None:
        """Set registry name.

        :param value: Registry name
        :type value: str
        """
        self._registry_name = value


class _ScopeDependentOperations(object):
    """This class is a container object holding the OperationScope and OperationConfig."""

    def __init__(self, operation_scope: OperationScope, operation_config: OperationConfig):
        """Return container object holding the OperationScope and OperationConfig.

        :param operation_scope: Scope variables for the operations classes of an MLClient object
        :type operation_scope: azure.ai.ml._scope_dependent_operations.OperationScope
        :param operation_config: Common configurations that are shared across operation objects of an MLClient object
        :type operation_config: azure.ai.ml._scope_dependent_operations.OperationConfig
        """
        self._operation_scope = operation_scope
        self._operation_config = operation_config
        self._scope_kwargs = {
            "resource_group_name": self._operation_scope.resource_group_name,
        }

    @property  # type: ignore
    def _workspace_name(self) -> str:
        """Return workspace name.

        :return: Workspace name
        :rtype: str
        """
        return cast(str, self._operation_scope.workspace_name)

    @property  # type: ignore
    def _registry_name(self) -> str:
        """Return registry name.

        :return: Registry name
        :rtype: str
        """
        return cast(str, self._operation_scope.registry_name)

    @property
    def _subscription_id(self) -> str:
        """Return subscription ID.

        :return: Subscription ID
        :rtype: str
        """
        return self._operation_scope.subscription_id

    @property
    def _resource_group_name(self) -> str:
        """Return resource group name.

        :return: Resource group name
        :rtype: str
        """
        return self._operation_scope.resource_group_name

    @property
    def _show_progress(self) -> bool:
        """Return value of show_progress.

        :return: Value of show_progress
        :rtype: bool
        """
        return self._operation_config.show_progress

    @property
    def _enable_telemetry(self) -> bool:
        """Return value of enable_telemetry.

        :return: Value of enable_telemetry
        :rtype: bool
        """
        return self._operation_config.enable_telemetry


class OperationsContainer(object):
    """This class is used to store all operations classes of an MLClient object."""

    def __init__(self):
        """Return class storing all operations classes of an MLClient object."""
        self._all_operations = {}

    @property
    def all_operations(self) -> Dict[str, _ScopeDependentOperations]:
        """All operations classes of an MLClient object.

        :return: A dictionary of all operations
        :rtype: Dict[str, _ScopeDependentOperations]
        """
        return self._all_operations

    def add(self, name: str, operation: _ScopeDependentOperations) -> None:
        """Add a operation class.

        :param name: Resource type
        :type name: str
        :param operation: Operation class
        :type operation: _ScopeDependentOperations
        """
        self._all_operations[name] = operation

    def get_operation(self, resource_type: str, type_check: Callable[[T], bool]) -> T:
        """Retrieve an operation.

        :param resource_type: Resource type
        :type resource_type: str
        :param type_check: Method to check type of operation
        :type type_check: Callable[[T], bool]
        :raises ValidationException: Raises ValidationException if operations initialized with the wrong type or if operation type not available for the MLClient
        :return: Operation class
        :rtype: T
        """
        if resource_type in self.all_operations:
            operation = self.all_operations[resource_type]
            from unittest.mock import MagicMock

            if isinstance(operation, MagicMock) or type_check(operation):
                return operation
            msg = f"{resource_type} operations are initialized with wrong type: {type(operation)}."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.JOB,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
        msg = f"Operation {resource_type} is not available for this client."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            error_category=ErrorCategory.USER_ERROR,
            target=ErrorTarget.JOB,
            error_type=ValidationErrorType.INVALID_VALUE,
        )
