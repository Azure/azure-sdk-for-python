#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import jsondiff
import re
from enum import Enum
from typing import Any, Dict, List, Union
from copy import deepcopy
from _models import ChangesChecker, Suppression, RegexSuppression


class BreakingChangeType(str, Enum):
    REMOVED_OR_RENAMED_CLIENT = "RemovedOrRenamedClient"
    REMOVED_OR_RENAMED_CLIENT_METHOD = "RemovedOrRenamedClientMethod"
    REMOVED_OR_RENAMED_CLASS = "RemovedOrRenamedClass"
    REMOVED_OR_RENAMED_CLASS_METHOD = "RemovedOrRenamedClassMethod"
    REMOVED_OR_RENAMED_MODULE_LEVEL_FUNCTION = "RemovedOrRenamedModuleLevelFunction"
    REMOVED_OR_RENAMED_POSITIONAL_PARAM = "RemovedOrRenamedPositionalParam"
    ADDED_POSITIONAL_PARAM = "AddedPositionalParam"
    REMOVED_PARAMETER_DEFAULT_VALUE = "RemovedParameterDefaultValue"
    REMOVED_OR_RENAMED_INSTANCE_ATTRIBUTE = "RemovedOrRenamedInstanceAttribute"
    REMOVED_OR_RENAMED_ENUM_VALUE = "RemovedOrRenamedEnumValue"
    CHANGED_PARAMETER_DEFAULT_VALUE = "ChangedParameterDefaultValue"
    CHANGED_PARAMETER_ORDERING = "ChangedParameterOrdering"
    CHANGED_PARAMETER_KIND = "ChangedParameterKind"
    CHANGED_FUNCTION_KIND = "ChangedFunctionKind"
    REMOVED_OR_RENAMED_MODULE = "RemovedOrRenamedModule"
    REMOVED_FUNCTION_KWARGS = "RemovedFunctionKwargs"
    REMOVED_OR_RENAMED_OPERATION_GROUP = "RemovedOrRenamedOperationGroup"


class BreakingChangesTracker:
    REMOVED_OR_RENAMED_CLIENT_MSG = \
        "Deleted or renamed client `{}`"
    REMOVED_OR_RENAMED_CLIENT_METHOD_MSG = \
        "Deleted or renamed client method `{}.{}`"
    REMOVED_OR_RENAMED_CLASS_MSG = \
        "Deleted or renamed model `{}`"
    REMOVED_OR_RENAMED_CLASS_METHOD_MSG = \
        "Deleted or renamed method `{}.{}`"
    REMOVED_OR_RENAMED_MODULE_LEVEL_FUNCTION_MSG = \
        "Deleted or renamed function `{}`"
    REMOVED_OR_RENAMED_POSITIONAL_PARAM_OF_METHOD_MSG = \
        "Method `{}.{}` deleted or renamed its parameter `{}` of kind `{}`"
    REMOVED_OR_RENAMED_POSITIONAL_PARAM_OF_FUNCTION_MSG = \
        "Function `{}` deleted or renamed its parameter `{}` of kind `{}`"
    ADDED_POSITIONAL_PARAM_TO_METHOD_MSG = \
        "Method `{}.{}` inserted a `{}` parameter `{}`"
    ADDED_POSITIONAL_PARAM_TO_FUNCTION_MSG = \
        "Function `{}` inserted a `{}` parameter `{}`"
    REMOVED_OR_RENAMED_INSTANCE_ATTRIBUTE_FROM_CLIENT_MSG = \
        "Client `{}` deleted or renamed instance variable `{}`"
    REMOVED_OR_RENAMED_INSTANCE_ATTRIBUTE_FROM_MODEL_MSG = \
        "Model `{}` deleted or renamed its instance variable `{}`"
    REMOVED_OR_RENAMED_ENUM_VALUE_MSG = \
        "Deleted or renamed enum value `{}.{}`"
    CHANGED_PARAMETER_DEFAULT_VALUE_MSG = \
        "Method `{}.{}` parameter `{}` changed default value from `{}` to `{}`"
    CHANGED_PARAMETER_DEFAULT_VALUE_OF_FUNCTION_MSG = \
        "Function `{}` parameter `{}` changed default value from `{}` to `{}`"
    REMOVED_PARAMETER_DEFAULT_VALUE_MSG = \
        "Method `{}.{}` removed default value `{}` from its parameter `{}`"
    REMOVED_PARAMETER_DEFAULT_VALUE_OF_FUNCTION_MSG = \
        "Function `{}` removed default value `{}` from its parameter `{}`"
    CHANGED_PARAMETER_ORDERING_MSG = \
        "Method `{}.{}` re-ordered its parameters from `{}` to `{}`"
    CHANGED_PARAMETER_ORDERING_OF_FUNCTION_MSG = \
        "Function `{}` re-ordered its parameters from `{}` to `{}`"
    CHANGED_PARAMETER_KIND_MSG = \
        "Method `{}.{}` changed its parameter `{}` from `{}` to `{}`"
    CHANGED_PARAMETER_KIND_OF_FUNCTION_MSG = \
        "Function `{}` changed its parameter `{}` from `{}` to `{}`"
    CHANGED_CLASS_FUNCTION_KIND_MSG = \
        "Method `{}.{}` changed from `{}` to `{}`"
    CHANGED_FUNCTION_KIND_MSG = \
        "Changed function `{}` from `{}` to `{}`"
    REMOVED_OR_RENAMED_MODULE_MSG = \
        "Deleted or renamed module `{}`"
    REMOVED_CLASS_FUNCTION_KWARGS_MSG = \
        "Method `{}.{}` changed from accepting keyword arguments to not accepting them"
    REMOVED_FUNCTION_KWARGS_MSG = \
        "Function `{}` changed from accepting keyword arguments to not accepting them"
    REMOVED_OR_RENAMED_OPERATION_GROUP_MSG = \
        "Deleted or renamed client operation group `{}.{}`"

    def __init__(self, stable: Dict, current: Dict, package_name: str, **kwargs: Any) -> None:
        self.stable = stable
        self.current = current
        self.diff = jsondiff.diff(stable, current)
        self.features_added = []
        self.breaking_changes = []
        self.package_name = package_name
        self._module_name = None
        self._class_name = None
        self._function_name = None
        self._parameter_name = None
        self.ignore = kwargs.get("ignore", {})
        checkers: List[ChangesChecker] = kwargs.get("checkers", [])
        for checker in checkers:
            if not isinstance(checker, ChangesChecker):
                raise TypeError(f"Checker {checker} does not implement ChangesChecker protocol")
        self.checkers = checkers

    def run_checks(self) -> None:
        self.run_breaking_change_diff_checks()
        self.check_parameter_ordering()  # not part of diff
        self.run_async_cleanup(self.breaking_changes)

    # Remove duplicate reporting of changes that apply to both sync and async package components
    def run_async_cleanup(self, changes_list: List) -> None:
        # Create a list of all sync changes
        non_aio_changes = [bc for bc in changes_list if "aio" not in bc[2]]
        # Remove any aio change if there is a sync change that is the same
        for change in non_aio_changes:
            for c in changes_list:
                if "aio" in c[2]:
                    if change[1] == c[1] and change[3:] == c[3:]:
                        changes_list.remove(c)
                        break

    def run_breaking_change_diff_checks(self) -> None:
        for module_name, module in self.diff.items():
            self._module_name = module_name
            if self._module_name not in self.stable and not isinstance(self._module_name, jsondiff.Symbol):
                continue  # this is a new module/additive change in current version so skip checks

            module_deleted = self.check_module_removed_or_renamed(module)
            if module_deleted:
                continue  # module was deleted, abort other checks

            self.run_class_level_diff_checks(module)
            self.run_function_level_diff_checks(module)
        # Run custom checkers in the base class, we only need one CodeReporter class in the tool
        # The changelog reporter class is a result of not having pluggable checks, we're migrating away from it as we add more pluggable checks
        for checker in self.checkers:
            changes_list = self.breaking_changes
            if not checker.is_breaking:
                changes_list = self.features_added

            if checker.node_type == "module":
                # If we are running a module checker, we need to run it on the entire diff
                changes_list.extend(checker.run_check(self.diff, self.stable, self.current))
                continue
            if checker.node_type == "class":
                # If we are running a class checker, we need to run it on all classes in each module in the diff
                for module_name, module_components in self.diff.items():
                    # If the module_name is a symbol, we'll skip it since we can't run class checks on it
                    if not isinstance(module_name, jsondiff.Symbol):
                        changes_list.extend(checker.run_check(module_components.get("class_nodes", {}), self.stable, self.current, module_name=module_name))
                        continue
            if checker.node_type == "function_or_method":
                # If we are running a function or method checker, we need to run it on all functions and class methods in each module in the diff
                for module_name, module_components in self.diff.items():
                    # If the module_name is a symbol, we'll skip it since we can't run class checks on it
                    if not isinstance(module_name, jsondiff.Symbol):
                        for class_name, class_components in module_components.get("class_nodes", {}).items():
                            # If the class_name is a symbol, we'll skip it since we can't run method checks on it
                            if not isinstance(class_name, jsondiff.Symbol):
                                changes_list.extend(checker.run_check(class_components.get("methods", {}), self.stable, self.current, module_name=module_name, class_name=class_name))
                                continue
                        changes_list.extend(checker.run_check(module_components.get("function_nodes", {}), self.stable, self.current, module_name=module_name))


    def run_class_level_diff_checks(self, module: Dict) -> None:
        for class_name, class_components in module.get("class_nodes", {}).items():
            self._class_name = class_name
            stable_class_nodes = self.stable[self._module_name]["class_nodes"]
            if self._class_name not in stable_class_nodes and not isinstance(class_name, jsondiff.Symbol):
                continue  # this is a new model/additive change in current version so skip checks

            class_deleted = self.check_class_removed_or_renamed(class_components)
            if class_deleted:
                continue  # class was deleted, abort other checks
            self.check_class_instance_attribute_removed_or_renamed(class_components)

            for method_name, method_components in class_components.get("methods", {}).items():
                self._function_name = method_name
                stable_methods_node = stable_class_nodes[self._class_name]["methods"]
                current_methods_node = self.current[self._module_name]["class_nodes"][self._class_name]["methods"]
                if self._function_name not in stable_methods_node and \
                        not isinstance(self._function_name, jsondiff.Symbol):
                    continue  # this is a new method/additive change in current version so skip checks

                method_deleted = self.check_class_method_removed_or_renamed(method_components, stable_methods_node)
                if method_deleted:
                    continue  # method was deleted, abort other checks

                self.check_function_type_changed(method_components)

                stable_parameters_node = stable_methods_node[self._function_name]["parameters"]
                current_parameters_node = current_methods_node[self._function_name]["parameters"]
                self.run_parameter_level_diff_checks(
                    method_components,
                    stable_parameters_node,
                    current_parameters_node,
                )

    def run_function_level_diff_checks(self, module: Dict) -> None:
        self._class_name = None
        for function_name, function_components in module.get("function_nodes", {}).items():
            self._function_name = function_name
            stable_function_nodes = self.stable[self._module_name]["function_nodes"]
            if self._function_name not in stable_function_nodes and \
                    not isinstance(self._function_name, jsondiff.Symbol):
                continue  # this is a new function/additive change in current version so skip checks

            function_deleted = self.check_module_level_function_removed_or_renamed(function_components)
            if function_deleted:
                continue  # function was deleted, abort other checks

            self.check_function_type_changed(function_components)

            stable_parameters_node = stable_function_nodes[self._function_name]["parameters"]
            current_parameters_node = self.current[self._module_name]["function_nodes"][self._function_name]["parameters"]
            self.run_parameter_level_diff_checks(
                function_components,
                stable_parameters_node,
                current_parameters_node
            )

    def run_parameter_level_diff_checks(
        self, function_components: Dict,
        stable_parameters_node: Dict,
        current_parameters_node: Dict
    ) -> None:
        for param_name, diff in function_components.get("parameters", {}).items():
            self._parameter_name = param_name
            all_parameters_deleted = self.check_all_parameters_deleted(stable_parameters_node)
            if all_parameters_deleted:
                continue  # all params were removed, abort other checks
            for diff_type in diff:
                if isinstance(self._parameter_name, jsondiff.Symbol):
                    self.check_positional_parameter_removed_or_renamed(
                        stable_parameters_node[diff_type]["param_type"],
                        diff_type,
                        stable_parameters_node,
                    )
                    self.check_kwargs_removed(
                        stable_parameters_node[diff_type]["param_type"],
                        diff_type
                    )
                elif self._parameter_name not in stable_parameters_node:
                    self.check_positional_parameter_added(
                        current_parameters_node[param_name]
                    )
                    break
                elif diff_type == "default":
                    stable_default = stable_parameters_node[self._parameter_name]["default"]
                    self.check_parameter_default_value_changed_or_added(
                        diff[diff_type], stable_default
                    )
                    self.check_parameter_default_value_removed(
                        diff[diff_type], stable_default
                    )
                elif diff_type == "param_type":
                    self.check_parameter_type_changed(
                        diff["param_type"], stable_parameters_node
                    )

    def check_kwargs_removed(self, param_type: str, param_name: str) -> None:
        if param_type == "var_keyword" and param_name == "kwargs":
            if self._class_name:
                bc = (
                    self.REMOVED_CLASS_FUNCTION_KWARGS_MSG,
                    BreakingChangeType.REMOVED_FUNCTION_KWARGS,
                    self._module_name, self._class_name, self._function_name
                )
            else:
                bc = (
                    self.REMOVED_FUNCTION_KWARGS_MSG,
                    BreakingChangeType.REMOVED_FUNCTION_KWARGS,
                    self._module_name, self._function_name
                )
            self.breaking_changes.append(bc)

    def check_module_removed_or_renamed(self, module: Dict) -> Union[bool, None]:
        if isinstance(self._module_name, jsondiff.Symbol):
            deleted_modules = []
            if self._module_name.label == "delete":
                deleted_modules = [module]
            elif self._module_name.label == "replace":
                deleted_modules = self.stable

            for name in deleted_modules:
                bc = (
                    self.REMOVED_OR_RENAMED_MODULE_MSG,
                    BreakingChangeType.REMOVED_OR_RENAMED_MODULE,
                    name
                )
                self.breaking_changes.append(bc)
            return True

    def check_all_parameters_deleted(self, stable_parameters_node: Dict) -> Union[bool, None]:
        if isinstance(self._parameter_name, jsondiff.Symbol) and self._parameter_name.label == "replace":
            self.check_positional_parameter_removed_or_renamed(
                "positional_or_keyword",
                None,
                stable_parameters_node
            )
            return True

    def check_function_type_changed(self, function_components: Dict) -> None:
        value = function_components.get("is_async", None)
        if value is not None:
            if value is True:
                change = "asynchronous"
                original = "synchronous"
            else:
                change = "synchronous"
                original = "asynchronous"
            if self._class_name:
                self.breaking_changes.append(
                    (
                        self.CHANGED_CLASS_FUNCTION_KIND_MSG, BreakingChangeType.CHANGED_FUNCTION_KIND,
                        self._module_name, self._class_name, self._function_name, original, change
                    )
                )
            else:
                self.breaking_changes.append(
                    (
                        self.CHANGED_FUNCTION_KIND_MSG, BreakingChangeType.CHANGED_FUNCTION_KIND,
                        self._module_name, self._function_name, original, change
                    )
                )

    def check_parameter_type_changed(self, diff: Dict, stable_parameters_node: Dict) -> None:
        if self._class_name:
            self.breaking_changes.append(
                (
                    self.CHANGED_PARAMETER_KIND_MSG, BreakingChangeType.CHANGED_PARAMETER_KIND,
                    self._module_name, self._class_name, self._function_name, self._parameter_name,
                    stable_parameters_node[self._parameter_name]["param_type"], diff
                )
            )
        else:
            self.breaking_changes.append(
                (
                    self.CHANGED_PARAMETER_KIND_OF_FUNCTION_MSG, BreakingChangeType.CHANGED_PARAMETER_KIND,
                    self._module_name, self._function_name, self._parameter_name,
                    stable_parameters_node[self._parameter_name]["param_type"], diff
                )
            )

    def check_parameter_ordering(self) -> None:
        modules = self.stable.keys() & self.current.keys()

        for module in modules:
            if "class_nodes" in self.stable[module]:
                stable_cls = self.stable[module]["class_nodes"]
                current_cls = self.current[module]["class_nodes"]
                class_keys = stable_cls.keys() & current_cls.keys()
                for cls in class_keys:
                    stable_method_nodes = stable_cls[cls]["methods"]
                    current_method_nodes = current_cls[cls]["methods"]
                    method_keys = stable_method_nodes.keys() & current_method_nodes.keys()
                    for method in method_keys:
                        stable_params = stable_method_nodes[method]["parameters"].keys()
                        current_params = current_method_nodes[method]["parameters"].keys()
                        if len(stable_params) != len(current_params):
                            # a parameter was deleted and that breaking change was already reported so skip
                            continue
                        for key1, key2 in zip(stable_params, current_params):
                            if key1 != key2:
                                self.breaking_changes.append(
                                    (
                                        self.CHANGED_PARAMETER_ORDERING_MSG,
                                        BreakingChangeType.CHANGED_PARAMETER_ORDERING,
                                        module, cls, method, list(stable_params), list(current_params)
                                    )
                                )
                                break
            if "function_nodes" in self.stable[module]:
                stable_funcs = self.stable[module]["function_nodes"]
                current_funcs = self.current[module]["function_nodes"]
                func_nodes = stable_funcs.keys() & current_funcs.keys()
                for func in func_nodes:
                    stable_params = stable_funcs[func]["parameters"].keys()
                    current_params = current_funcs[func]["parameters"].keys()
                    if len(stable_params) != len(current_params):
                        # a parameter was deleted and that breaking change was already reported so skip
                        continue
                    for key1, key2 in zip(stable_params, current_params):
                        if key1 != key2:
                            self.breaking_changes.append(
                                (
                                    self.CHANGED_PARAMETER_ORDERING_OF_FUNCTION_MSG,
                                    BreakingChangeType.CHANGED_PARAMETER_ORDERING,
                                    module, func, list(stable_params), list(current_params)
                                )
                            )
                            break

    def check_parameter_default_value_removed(
        self, default: Union[str, None],
        stable_default: Union[str, None]
    ) -> None:
        if stable_default is not None and default is None:
            if self._class_name:
                self.breaking_changes.append(
                    (
                        self.REMOVED_PARAMETER_DEFAULT_VALUE_MSG,
                        BreakingChangeType.REMOVED_PARAMETER_DEFAULT_VALUE,
                        self._module_name, self._class_name, self._function_name,
                        default, self._parameter_name
                    )
                )
            else:

                self.breaking_changes.append(
                    (
                        self.REMOVED_PARAMETER_DEFAULT_VALUE_OF_FUNCTION_MSG,
                        BreakingChangeType.REMOVED_PARAMETER_DEFAULT_VALUE,
                        self._module_name, self._function_name, default, self._parameter_name
                    )
                )

    def check_parameter_default_value_changed_or_added(
        self, default: Union[str, None],
        stable_default: Union[str, None]
    ) -> None:
        if default is not None:  # a default was added in the current version
            if default != stable_default:
                if stable_default is not None:  # There is a stable default
                    if stable_default == "none":  # the case in which the stable default was None
                        stable_default = None  # set back to actual None for the message
                    if self._class_name:
                        self.breaking_changes.append(
                            (
                                self.CHANGED_PARAMETER_DEFAULT_VALUE_MSG,
                                BreakingChangeType.CHANGED_PARAMETER_DEFAULT_VALUE,
                                self._module_name, self._class_name, self._function_name,
                                self._parameter_name, stable_default, default
                            )
                        )
                    else:
                        self.breaking_changes.append(
                            (
                                self.CHANGED_PARAMETER_DEFAULT_VALUE_OF_FUNCTION_MSG,
                                BreakingChangeType.CHANGED_PARAMETER_DEFAULT_VALUE,
                                self._module_name, self._function_name,
                                self._parameter_name, stable_default, default
                            )
                        )

    def check_positional_parameter_added(self, current_parameters_node: Dict) -> None:
        if current_parameters_node["param_type"] == "positional_or_keyword" and \
                current_parameters_node["default"] != "none":
            if self._class_name:
                self.breaking_changes.append(
                    (
                        self.ADDED_POSITIONAL_PARAM_TO_METHOD_MSG, BreakingChangeType.ADDED_POSITIONAL_PARAM,
                        self._module_name, self._class_name, self._function_name,
                        current_parameters_node["param_type"], self._parameter_name
                    )
                )
            else:
                self.breaking_changes.append(
                    (
                        self.ADDED_POSITIONAL_PARAM_TO_FUNCTION_MSG, BreakingChangeType.ADDED_POSITIONAL_PARAM,
                        self._module_name, self._function_name,
                        current_parameters_node["param_type"], self._parameter_name
                    )
                )

    def check_positional_parameter_removed_or_renamed(
        self, param_type: str,
        deleted: str,
        stable_parameters_node: Dict
    ) -> None:
        if param_type != "positional_or_keyword":
            return
        deleted_params = []
        if self._parameter_name.label == "delete":
            deleted_params = [deleted]
        elif self._parameter_name.label == "replace":  # replace means all positional parameters were removed
            deleted_params = {
                param_name: details
                for param_name, details
                in stable_parameters_node.items()
                if details["param_type"] == "positional_or_keyword"
            }

        for deleted in deleted_params:
            if deleted != "self":
                if self._class_name:
                    self.breaking_changes.append(
                        (
                            self.REMOVED_OR_RENAMED_POSITIONAL_PARAM_OF_METHOD_MSG,
                            BreakingChangeType.REMOVED_OR_RENAMED_POSITIONAL_PARAM,
                            self._module_name, self._class_name, self._function_name, deleted, param_type
                        )
                    )
                else:
                    self.breaking_changes.append(
                        (
                            self.REMOVED_OR_RENAMED_POSITIONAL_PARAM_OF_FUNCTION_MSG,
                            BreakingChangeType.REMOVED_OR_RENAMED_POSITIONAL_PARAM,
                            self._module_name, self._function_name, deleted, param_type
                        )
                    )

    def check_class_instance_attribute_removed_or_renamed(self, components: Dict) -> None:
        deleted_props = []
        for prop in components.get("properties", []):
            if isinstance(prop, jsondiff.Symbol):
                if prop.label == "delete":
                    deleted_props = components["properties"][prop]
                elif prop.label == "replace":
                    deleted_props = self.stable[self._module_name]["class_nodes"][self._class_name]["properties"]

        for property in deleted_props:
            bc = None
            if self._class_name.endswith("Client"):
                property_type = self.stable[self._module_name]["class_nodes"][self._class_name]["properties"][property]["attr_type"]
                # property_type is not always a string, such as client_side_validation which is a bool, so we need to check for strings
                if property_type is not None and isinstance(property_type, str) and property_type.lower().endswith("operations"):
                        bc = (
                            self.REMOVED_OR_RENAMED_OPERATION_GROUP_MSG,
                            BreakingChangeType.REMOVED_OR_RENAMED_OPERATION_GROUP,
                            self._module_name, self._class_name, property
                        )
                else:
                    bc = (
                        self.REMOVED_OR_RENAMED_INSTANCE_ATTRIBUTE_FROM_CLIENT_MSG,
                        BreakingChangeType.REMOVED_OR_RENAMED_INSTANCE_ATTRIBUTE,
                        self._module_name, self._class_name, property
                    )
            elif self.stable[self._module_name]["class_nodes"][self._class_name]["type"] == "Enum":
                if property.upper() not in self.current[self._module_name]["class_nodes"][self._class_name]["properties"] \
                    and property.lower() not in self.current[self._module_name]["class_nodes"][self._class_name]["properties"]:
                    bc = (
                        self.REMOVED_OR_RENAMED_ENUM_VALUE_MSG,
                        BreakingChangeType.REMOVED_OR_RENAMED_ENUM_VALUE,
                        self._module_name, self._class_name, property
                    )
            else:
                bc = (
                    self.REMOVED_OR_RENAMED_INSTANCE_ATTRIBUTE_FROM_MODEL_MSG,
                    BreakingChangeType.REMOVED_OR_RENAMED_INSTANCE_ATTRIBUTE,
                    self._module_name, self._class_name, property
                )
            if bc:
                self.breaking_changes.append(bc)

    def check_class_removed_or_renamed(self, class_components: Dict) -> Union[bool, None]:
        if isinstance(self._class_name, jsondiff.Symbol):
            deleted_classes = []
            if self._class_name.label == "delete":
                deleted_classes = class_components
            elif self._class_name.label == "replace":
                deleted_classes = self.stable[self._module_name]["class_nodes"]

            for name in deleted_classes:
                if name.endswith("Client"):
                    bc = (
                        self.REMOVED_OR_RENAMED_CLIENT_MSG,
                        BreakingChangeType.REMOVED_OR_RENAMED_CLIENT,
                        self._module_name, name
                    )
                else:
                    bc = (
                        self.REMOVED_OR_RENAMED_CLASS_MSG,
                        BreakingChangeType.REMOVED_OR_RENAMED_CLASS,
                        self._module_name, name
                    )
                self.breaking_changes.append(bc)
            return True

    def check_class_method_removed_or_renamed(
        self, method_components: Dict,
        stable_methods_node: Dict
    ) -> Union[bool, None]:
        if isinstance(self._function_name, jsondiff.Symbol):
            methods_deleted = []
            if self._function_name.label == "delete":
                methods_deleted = method_components
            elif self._function_name.label == "replace":
                methods_deleted = stable_methods_node

            for method in methods_deleted:
                if self._class_name.endswith("Client"):
                    bc = (
                        self.REMOVED_OR_RENAMED_CLIENT_METHOD_MSG,
                        BreakingChangeType.REMOVED_OR_RENAMED_CLIENT_METHOD,
                        self._module_name, self._class_name, method
                    )
                else:
                    bc = (
                        self.REMOVED_OR_RENAMED_CLASS_METHOD_MSG,
                        BreakingChangeType.REMOVED_OR_RENAMED_CLASS_METHOD,
                        self._module_name, self._class_name, method
                    )
                self.breaking_changes.append(bc)
            return True

    def check_module_level_function_removed_or_renamed(self, function_components: Dict) -> Union[bool, None]:
        if isinstance(self._function_name, jsondiff.Symbol):
            deleted_functions = []
            if self._function_name.label == "delete":
                deleted_functions = function_components
            elif self._function_name.label == "replace":
                deleted_functions = self.stable[self._module_name]["function_nodes"]

            for function in deleted_functions:
                self.breaking_changes.append(
                    (
                        self.REMOVED_OR_RENAMED_MODULE_LEVEL_FUNCTION_MSG,
                        BreakingChangeType.REMOVED_OR_RENAMED_MODULE_LEVEL_FUNCTION,
                        self._module_name, function
                    )
                )
            return True

    def match(self, bc, ignored):
        if bc == ignored:
            return True
        for b, i in zip(bc, ignored):
            if i == "*":
                continue
            if isinstance(i, RegexSuppression) and b is not None:
                if i.match(b):
                    continue
                else:
                    return False
            if b != i:
                return False
        return True

    def get_reportable_changes(self, ignore_changes: Dict, changes_list: List) -> List:
        ignored = []
        # Match all ignore rules that should apply to this package
        for ignored_package, ignore_rules in ignore_changes.items():
            if re.findall(ignored_package, self.package_name):
                ignored.extend(ignore_rules)

        # Remove ignored changes from list of reportable changes
        bc_copy = deepcopy(changes_list)
        for bc in bc_copy:
            _, bc_type, module_name, *args = bc
            class_name = args[0] if args else None
            function_name = args[1] if len(args) > 1 else None
            parameter_name = args[2] if len(args) > 2 else None

            for rule in ignored:
                suppression = Suppression(*rule)

                if suppression.parameter_or_property_name is not None:
                    # If the ignore rule is for a property or parameter, we should check up to that level on the original change
                    if self.match((bc_type, module_name, class_name, function_name, parameter_name), suppression):
                        changes_list.remove(bc)
                        break
                elif self.match((bc_type, module_name, class_name, function_name), suppression):
                    changes_list.remove(bc)
                    break

    def report_changes(self) -> None:
        ignore_changes = self.ignore if self.ignore else {}
        self.get_reportable_changes(ignore_changes, self.breaking_changes)

        # If there are no breaking changes after the ignore check, return early
        if not self.breaking_changes:
            return f"\nNo breaking changes found for {self.package_name} between versions."

        formatted = "\n"
        for idx, bc in enumerate(self.breaking_changes):
            msg, bc_type, module_name, *args = bc
            if bc_type == BreakingChangeType.REMOVED_OR_RENAMED_MODULE:
                # For module-level changes, the module name is the first argument
                formatted += f"({bc_type}): " + msg.format(module_name) + "\n"
                continue
            # For simple breaking changes reporting, prepend the change code to the message
            msg = f"({bc_type}): " + msg + "\n"
            formatted += msg.format(*args)
        
        formatted += f"\nFound {len(self.breaking_changes)} breaking changes.\n"
        formatted += "\nSee aka.ms/azsdk/breaking-changes-tool to resolve " \
                     "any reported breaking changes or false positives.\n"
        return formatted
