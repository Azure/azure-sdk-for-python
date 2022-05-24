# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import functools
import logging
import yaml
from collections import OrderedDict
from typing import Any, Callable, Optional, cast, Dict, TypeVar
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget


T = TypeVar("T")
module_logger = logging.getLogger(__name__)


class OperationScope(object):
    def __init__(
        self,
        subscription_id: str,
        resource_group_name: str,
        workspace_name: Optional[str],
        registry_name: Optional[str] = None,
        cloud_name: Optional[str] = None,
    ):
        self._subscription_id = subscription_id
        self._resource_group_name = resource_group_name
        self._workspace_name = workspace_name
        self._registry_name = registry_name
        self._cloud_name = cloud_name

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

    @property
    def cloud_name(self) -> Optional[str]:
        return self._cloud_name

    @workspace_name.setter
    def workspace_name(self, value: str) -> None:
        self._workspace_name = value

    @registry_name.setter
    def registry_name(self, value: str) -> None:
        self._registry_name = value


def workspace_none_check(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)  # This is to preserve metadata of func
    def new_function(self: Any, *args: Any, **kwargs: Any) -> Any:
        if not self._operation_scope.workspace_name:
            msg = "Please set the default workspace with MLClient."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.GENERAL,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        return func(self, *args, **kwargs)

    return new_function


class _ScopeDependentOperations(object):
    def __init__(self, operation_scope: OperationScope):
        self._operation_scope = operation_scope
        self._scope_kwargs = {
            "resource_group_name": self._operation_scope.resource_group_name,
        }
        # Marshmallow supports load/dump of ordered dicts, but pollutes the yaml to tag dicts as ordered dicts
        # Setting these load/dump functions make ordered dict the default in place of dict, allowing for clean yaml
        _mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG

        def dict_representer(dumper: yaml.Dumper, data) -> yaml.representer.Representer:  # type: ignore
            return dumper.represent_mapping(_mapping_tag, data.items())

        def dict_constructor(loader, node) -> OrderedDict:  # type: ignore
            loader.flatten_mapping(node)
            return OrderedDict(loader.construct_pairs(node))

        # setup yaml to load and dump in order
        yaml.add_representer(OrderedDict, dict_representer)
        yaml.add_constructor(_mapping_tag, dict_constructor, Loader=yaml.SafeLoader)

    @property  # type: ignore
    @workspace_none_check
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
    def _cloud_name(self) -> str:
        return self._operation_scope.cloud_name


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
            else:
                msg = f"{resource_type} operations are initialized with wrong type: {type(operation)}."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.JOB,
                )
        else:
            msg = f"Operation {resource_type} is not available for this client."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.JOB,
            )
