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
    """This class is used to store common configurations that are shared across operation objects of an MLClient object.

    :param object: _description_
    :type object: _type_
    """

    def __init__(self, show_progress: bool, enable_telemetry: bool) -> None:
        self._show_progress = show_progress
        self._enable_telemetry = enable_telemetry

    @property
    def show_progress(self) -> bool:
        """Decide wether to display progress bars for long running operations.

        :return: show_progress
        :rtype: bool
        """
        return self._show_progress

    @property
    def enable_telemetry(self) -> bool:
        """Decide whether to enable telemetry for Jupyter Notebooks - telemetry cannot be enabled for other contexts.

        :return: enable_telemetry
        :rtype: bool
        """
        return self._enable_telemetry


class OperationScope(object):
    def __init__(
        self,
        subscription_id: str,
        resource_group_name: str,
        workspace_name: Optional[str],
        registry_name: Optional[str] = None,
    ):
        self._subscription_id = subscription_id
        self._resource_group_name = resource_group_name
        self._workspace_name = workspace_name
        self._registry_name = registry_name

    @property
    def subscription_id(self) -> str:
        return self._subscription_id

    @property
    def resource_group_name(self) -> str:
        return self._resource_group_name

    @property
    def workspace_name(self) -> Optional[str]:
        return self._workspace_name

    @property
    def registry_name(self) -> Optional[str]:
        return self._registry_name

    @workspace_name.setter
    def workspace_name(self, value: str) -> None:
        self._workspace_name = value

    @registry_name.setter
    def registry_name(self, value: str) -> None:
        self._registry_name = value


class _ScopeDependentOperations(object):
    def __init__(self, operation_scope: OperationScope, operation_config: OperationConfig):
        self._operation_scope = operation_scope
        self._operation_config = operation_config
        self._scope_kwargs = {
            "resource_group_name": self._operation_scope.resource_group_name,
        }

    @property  # type: ignore
    def _workspace_name(self) -> str:
        return cast(str, self._operation_scope.workspace_name)

    @property  # type: ignore
    def _registry_name(self) -> str:
        return cast(str, self._operation_scope.registry_name)

    @property
    def _subscription_id(self) -> str:
        return self._operation_scope.subscription_id

    @property
    def _resource_group_name(self) -> str:
        return self._operation_scope.resource_group_name

    @property
    def _show_progress(self) -> bool:
        return self._operation_config.show_progress

    @property
    def _enable_telemetry(self) -> bool:
        return self._operation_config.enable_telemetry


class OperationsContainer(object):
    def __init__(self):
        self._all_operations = {}

    @property
    def all_operations(self) -> Dict[str, _ScopeDependentOperations]:
        return self._all_operations

    def add(self, name: str, operation: _ScopeDependentOperations) -> None:
        self._all_operations[name] = operation

    def get_operation(self, resource_type: str, type_check: Callable[[T], bool]) -> T:
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
