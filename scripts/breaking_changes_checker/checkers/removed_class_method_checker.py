#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import sys
import os
sys.path.append(os.path.abspath("../../scripts/breaking_changes_checker"))
from _models import CheckerType
import jsondiff
from typing import Dict, List, Union

class RemovedClassMethodChecker:
    node_type = CheckerType.FUNCTION_OR_METHOD
    name = "RemovedOrRenamedClass"
    is_breaking = True
    message = {
        "removed_renamed_client_method": "Deleted or renamed client method `{}.{}`",
        "removed_renamed_class_method": "Deleted or renamed method `{}.{}`",
        "removed_renamed_module_function": "Deleted or renamed function `{}`",
        "removed_renamed_positional_method_param": "Method `{}.{}` deleted or renamed its parameter `{}` of kind `{}`",
        "removed_renamed_positional_function_param": "Function `{}` deleted or renamed its parameter `{}` of kind `{}`",
        "added_positional_param_method": "Method `{}.{}` inserted a `{}` parameter `{}`",
        "added_positional_param_function": "Function `{}` inserted a `{}` parameter `{}`",
        "changed_default_param_value_method": "Method `{}.{}` parameter `{}` changed default value from `{}` to `{}`",
        "changed_default_param_value_function": "Function `{}` parameter `{}` changed default value from `{}` to `{}`",
        "removed_default_param_value_method": "Method `{}.{}` removed default value `{}` from its parameter `{}`",
        "removed_default_param_value_function": "Function `{}` removed default value `{}` from its parameter `{}`",
        "changed_parameter_ordering_method": "Method `{}.{}` re-ordered its parameters from `{}` to `{}`",
        "changed_parameter_ordering_function": "Function `{}` re-ordered its parameters from `{}` to `{}`",
        "changed_parameter_kind_method": "Method `{}.{}` changed its parameter `{}` from `{}` to `{}`",
        "changed_parameter_kind_function": "Function `{}` changed its parameter `{}` from `{}` to `{}`",
        "changed_class_method_kind": "Method `{}.{}` changed from `{}` to `{}`",
        "changed_function_kind": "Changed function `{}` from `{}` to `{}`",
        "removed_class_method_kwargs": "Method `{}.{}` changed from accepting keyword arguments to not accepting them",
        "removed_function_kwargs": "Function `{}` changed from accepting keyword arguments to not accepting them",
    }

    def run_check(self, diff, stable_nodes, current_nodes, **kwargs):
        self._breaking_changes = []
        self._module_name = kwargs.get("module_name", None)
        self._class_name = kwargs.get("class_name", None)

        for method_name, method_components in diff.get("methods", {}).items():
            self._function_name = method_name
            stable_methods_node = stable_class_nodes[self._class_name]["methods"]
            current_methods_node = current_nodes[self._module_name]["class_nodes"][self._class_name]["methods"]
            if method_name not in stable_methods_node and \
                    not isinstance(method_name, jsondiff.Symbol):
                continue  # this is a new method/additive change in current version so skip checks

            method_deleted = self.check_class_method_removed_or_renamed(method_components, stable_methods_node)
            if method_deleted:
                continue  # method was deleted, abort other checks

            self.check_function_type_changed(method_components)

            stable_parameters_node = stable_methods_node[method_name]["parameters"]
            current_parameters_node = current_methods_node[method_name]["parameters"]
            self.run_parameter_level_diff_checks(
                method_components,
                stable_parameters_node,
                current_parameters_node,
            )
        return self._breaking_changes

    
    def run_parameter_level_diff_checks(
        self, function_components: Dict,
        stable_parameters_node: Dict,
        current_parameters_node: Dict
    ) -> None:
        for param_name, diff in function_components.get("parameters", {}).items():
            param_name = param_name
            all_parameters_deleted = self.check_all_parameters_deleted(stable_parameters_node)
            if all_parameters_deleted:
                continue  # all params were removed, abort other checks
            for diff_type in diff:
                if isinstance(param_name, jsondiff.Symbol):
                    self.check_positional_parameter_removed_or_renamed(
                        stable_parameters_node[diff_type]["param_type"],
                        diff_type,
                        stable_parameters_node,
                    )
                    self.check_kwargs_removed(
                        stable_parameters_node[diff_type]["param_type"],
                        diff_type
                    )
                elif param_name not in stable_parameters_node:
                    self.check_positional_parameter_added(
                        current_parameters_node[param_name]
                    )
                    break
                elif diff_type == "default":
                    stable_default = stable_parameters_node[param_name]["default"]
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

    
    def check_positional_parameter_removed_or_renamed(
        self, param_type: str,
        deleted: str,
        stable_parameters_node: Dict,
        param_name: str,
        class_name: str,
        module_name: str
    ) -> None:
        if param_type != "positional_or_keyword":
            return
        deleted_params = []
        if param_name.label == "delete":
            deleted_params = [deleted]
        elif param_name.label == "replace":  # replace means all positional parameters were removed
            deleted_params = {
                param_name: details
                for param_name, details
                in stable_parameters_node.items()
                if details["param_type"] == "positional_or_keyword"
            }

        for deleted in deleted_params:
            if deleted != "self":
                if self._class_name:
                    self._breaking_changes.append(
                        (
                            self.REMOVED_OR_RENAMED_POSITIONAL_PARAM_OF_METHOD_MSG,
                            BreakingChangeType.REMOVED_OR_RENAMED_POSITIONAL_PARAM,
                            self._module_name, self._class_name, self._function_name, deleted, param_type
                        )
                    )
                else:
                    self._breaking_changes.append(
                        (
                            self.REMOVED_OR_RENAMED_POSITIONAL_PARAM_OF_FUNCTION_MSG,
                            BreakingChangeType.REMOVED_OR_RENAMED_POSITIONAL_PARAM,
                            self._module_name, self._function_name, deleted, param_type
                        )
                    )

    
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
                self._breaking_changes.append(bc)
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
                self._breaking_changes.append(
                    (
                        self.CHANGED_CLASS_FUNCTION_KIND_MSG, BreakingChangeType.CHANGED_FUNCTION_KIND,
                        self._module_name, self._class_name, self._function_name, original, change
                    )
                )
            else:
                self._breaking_changes.append(
                    (
                        self.CHANGED_FUNCTION_KIND_MSG, BreakingChangeType.CHANGED_FUNCTION_KIND,
                        self._module_name, self._function_name, original, change
                    )
                )


    def check_all_parameters_deleted(self, stable_parameters_node: Dict) -> Union[bool, None]:
        if isinstance(self._parameter_name, jsondiff.Symbol) and self._parameter_name.label == "replace":
            self.check_positional_parameter_removed_or_renamed(
                "positional_or_keyword",
                None,
                stable_parameters_node
            )
            return True


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
            self._breaking_changes.append(bc)


    def check_positional_parameter_added(self, current_parameters_node: Dict) -> None:
        if current_parameters_node["param_type"] == "positional_or_keyword" and \
                current_parameters_node["default"] != "none":
            if self._class_name:
                self._breaking_changes.append(
                    (
                        self.ADDED_POSITIONAL_PARAM_TO_METHOD_MSG, BreakingChangeType.ADDED_POSITIONAL_PARAM,
                        self._module_name, self._class_name, self._function_name,
                        current_parameters_node["param_type"], self._parameter_name
                    )
                )
            else:
                self._breaking_changes.append(
                    (
                        self.ADDED_POSITIONAL_PARAM_TO_FUNCTION_MSG, BreakingChangeType.ADDED_POSITIONAL_PARAM,
                        self._module_name, self._function_name,
                        current_parameters_node["param_type"], self._parameter_name
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
                        self._breaking_changes.append(
                            (
                                self.CHANGED_PARAMETER_DEFAULT_VALUE_MSG,
                                BreakingChangeType.CHANGED_PARAMETER_DEFAULT_VALUE,
                                self._module_name, self._class_name, self._function_name,
                                self._parameter_name, stable_default, default
                            )
                        )
                    else:
                        self._breaking_changes.append(
                            (
                                self.CHANGED_PARAMETER_DEFAULT_VALUE_OF_FUNCTION_MSG,
                                BreakingChangeType.CHANGED_PARAMETER_DEFAULT_VALUE,
                                self._module_name, self._function_name,
                                self._parameter_name, stable_default, default
                            )
                        )


    def check_parameter_default_value_removed(
        self, default: Union[str, None],
        stable_default: Union[str, None]
    ) -> None:
        if stable_default is not None and default is None:
            if self._class_name:
                self._breaking_changes.append(
                    (
                        self.REMOVED_PARAMETER_DEFAULT_VALUE_MSG,
                        BreakingChangeType.REMOVED_PARAMETER_DEFAULT_VALUE,
                        self._module_name, self._class_name, self._function_name,
                        default, self._parameter_name
                    )
                )
            else:

                self._breaking_changes.append(
                    (
                        self.REMOVED_PARAMETER_DEFAULT_VALUE_OF_FUNCTION_MSG,
                        BreakingChangeType.REMOVED_PARAMETER_DEFAULT_VALUE,
                        self._module_name, self._function_name, default, self._parameter_name
                    )
                )


    def check_parameter_type_changed(self, diff: Dict, stable_parameters_node: Dict) -> None:
        if self._class_name:
            self._breaking_changes.append(
                (
                    self.CHANGED_PARAMETER_KIND_MSG, BreakingChangeType.CHANGED_PARAMETER_KIND,
                    self._module_name, self._class_name, self._function_name, self._parameter_name,
                    stable_parameters_node[self._parameter_name]["param_type"], diff
                )
            )
        else:
            self._breaking_changes.append(
                (
                    self.CHANGED_PARAMETER_KIND_OF_FUNCTION_MSG, BreakingChangeType.CHANGED_PARAMETER_KIND,
                    self._module_name, self._function_name, self._parameter_name,
                    stable_parameters_node[self._parameter_name]["param_type"], diff
                )
            )
