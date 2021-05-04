#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from enum import Enum
from typing import Any, Dict, List, Union
try:
    import jsondiff
except ModuleNotFoundError:
    pass
try:
    from breaking_changes_allowlist import IGNORE_BREAKING_CHANGES
except ModuleNotFoundError:
    from .breaking_changes_allowlist import IGNORE_BREAKING_CHANGES


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


class BreakingChangesTracker:
    REMOVED_OR_RENAMED_CLIENT_MSG = \
        "({}): The client '{}.{}' was deleted or renamed in the current version"
    REMOVED_OR_RENAMED_CLIENT_METHOD_MSG = \
        "({}): The '{}.{}' client method '{}' was deleted or renamed in the current version"
    REMOVED_OR_RENAMED_CLASS_MSG = \
        "({}): The model or publicly exposed class '{}.{}' was deleted or renamed in the current version"
    REMOVED_OR_RENAMED_CLASS_METHOD_MSG = \
        "({}): The '{}.{}' method '{}' was deleted or renamed in the current version"
    REMOVED_OR_RENAMED_MODULE_LEVEL_FUNCTION_MSG = \
        "({}): The publicly exposed function '{}.{}' was deleted or renamed in the current version"
    REMOVED_OR_RENAMED_POSITIONAL_PARAM_OF_METHOD_MSG = \
        "({}): The '{}.{} method '{}' had its '{}' parameter '{}' deleted or renamed in the current version"
    REMOVED_OR_RENAMED_POSITIONAL_PARAM_OF_FUNCTION_MSG = \
        "({}): The function '{}.{}' had its '{}' parameter '{}' deleted or renamed in the current version"
    ADDED_POSITIONAL_PARAM_TO_METHOD_MSG = \
        "({}): The '{}.{} method '{}' had a '{}' parameter '{}' inserted in the current version"
    ADDED_POSITIONAL_PARAM_TO_FUNCTION_MSG = \
        "({}): The function '{}.{}' had a '{}' parameter '{}' inserted in the current version"
    REMOVED_OR_RENAMED_INSTANCE_ATTRIBUTE_FROM_CLIENT_MSG = \
        "({}): The client '{}.{}' had its instance variable '{}' deleted or renamed in the current version"
    REMOVED_OR_RENAMED_INSTANCE_ATTRIBUTE_FROM_MODEL_MSG = \
        "({}): The model or publicly exposed class '{}.{}' had its instance variable '{}' deleted or renamed " \
        "in the current version"
    REMOVED_OR_RENAMED_ENUM_VALUE_MSG = \
        "({}): The '{}.{}' enum had its value '{}' deleted or renamed in the current version"
    CHANGED_PARAMETER_DEFAULT_VALUE_MSG = \
        "({}): The class '{}.{}' method '{}' had its parameter '{}' default value changed from '{}' to '{}'"
    CHANGED_PARAMETER_DEFAULT_VALUE_OF_FUNCTION_MSG = \
        "({}): The publicly exposed function '{}.{}' had its parameter '{}' default value changed from '{}' to '{}'"
    REMOVED_PARAMETER_DEFAULT_VALUE_MSG = \
        "({}): The class '{}.{}' method '{}' had default value '{}' removed from its parameter '{}' in " \
        "the current version"
    REMOVED_PARAMETER_DEFAULT_VALUE_OF_FUNCTION_MSG = \
        "({}): The publicly exposed function '{}.{}' had default value '{}' removed from its parameter '{}' in " \
        "the current version"
    CHANGED_PARAMETER_ORDERING_MSG = \
        "({}): The class '{}.{}' method '{}' had its parameters re-ordered from '{}' to '{}' in the current version"
    CHANGED_PARAMETER_ORDERING_OF_FUNCTION_MSG = \
        "({}): The publicly exposed function '{}.{}' had its parameters re-ordered from '{}' to '{}' in " \
        "the current version"
    CHANGED_PARAMETER_KIND_MSG = \
        "({}): The class '{}.{}' method '{}' had its parameter '{}' changed from '{}' to '{}' in the current version"
    CHANGED_PARAMETER_KIND_OF_FUNCTION_MSG = \
        "({}): The function '{}.{}' had its parameter '{}' changed from '{}' to '{}' in the current version"
    CHANGED_CLASS_FUNCTION_KIND_MSG = \
        "({}): The class '{}.{}' method '{}' changed from '{}' to '{}' in the current version."
    CHANGED_FUNCTION_KIND_MSG = \
        "({}): The function '{}.{}' changed from '{}' to '{}' in the current version."
    REMOVED_OR_RENAMED_MODULE_MSG = \
        "({}): The '{}' module was deleted or renamed in the current version"
    REMOVED_CLASS_FUNCTION_KWARGS_MSG = \
        "({}): The class '{}.{}' method '{}' changed from accepting keyword arguments to not accepting them in " \
        "the current version"
    REMOVED_FUNCTION_KWARGS_MSG = \
        "({}): The function '{}.{}' changed from accepting keyword arguments to not accepting them in " \
        "the current version"

    def __init__(self, stable: Dict, current: Dict, diff: Dict, package_name: str, **kwargs: Any) -> None:
        self.stable = stable
        self.current = current
        self.diff = diff
        self.breaking_changes = []
        self.package_name = package_name
        self.module_name = None
        self.class_name = None
        self.function_name = None
        self.parameter_name = None
        self.ignore = kwargs.get("ignore", None)

    def __str__(self):
        formatted = "\n"
        for bc in self.breaking_changes:
            formatted += bc + "\n"

        formatted += "\nSee aka.ms/azsdk/breaking-changes-tool to resolve " \
                     "any reported breaking changes or false positives.\n"
        return formatted

    def run_checks(self) -> None:
        self.run_breaking_change_diff_checks()
        self.check_parameter_ordering()  # not part of diff
        self.report_breaking_changes()

    def run_breaking_change_diff_checks(self) -> None:
        for module_name, module in self.diff.items():
            self.module_name = module_name
            if self.module_name not in self.stable and not isinstance(self.module_name, jsondiff.Symbol):
                continue  # this is a new module/additive change in current version so skip checks

            module_deleted = self.check_module_removed_or_renamed(module)
            if module_deleted:
                continue  # module was deleted, abort other checks

            self.run_class_level_diff_checks(module)
            self.run_function_level_diff_checks(module)

    def run_class_level_diff_checks(self, module: Dict) -> None:
        for class_name, class_components in module.get("class_nodes", {}).items():
            self.class_name = class_name
            stable_class_nodes = self.stable[self.module_name]["class_nodes"]
            if self.class_name not in stable_class_nodes and not isinstance(class_name, jsondiff.Symbol):
                continue  # this is a new model/additive change in current version so skip checks

            class_deleted = self.check_class_removed_or_renamed(class_components)
            if class_deleted:
                continue  # class was deleted, abort other checks
            self.check_class_instance_attribute_removed_or_renamed(class_components)

            for method_name, method_components in class_components.get("methods", {}).items():
                self.function_name = method_name
                stable_methods_node = stable_class_nodes[self.class_name]["methods"]
                current_methods_node = self.current[self.module_name]["class_nodes"][self.class_name]["methods"]
                if self.function_name not in stable_methods_node and \
                        not isinstance(self.function_name, jsondiff.Symbol):
                    continue  # this is a new method/additive change in current version so skip checks

                method_deleted = self.check_class_method_removed_or_renamed(method_components, stable_methods_node)
                if method_deleted:
                    continue  # method was deleted, abort other checks

                self.check_function_type_changed(method_components)

                stable_parameters_node = stable_methods_node[self.function_name]["parameters"]
                current_parameters_node = current_methods_node[self.function_name]["parameters"]
                self.run_parameter_level_diff_checks(
                    method_components,
                    stable_parameters_node,
                    current_parameters_node,
                )

    def run_function_level_diff_checks(self, module: Dict) -> None:
        self.class_name = None
        for function_name, function_components in module.get("function_nodes", {}).items():
            self.function_name = function_name
            stable_function_nodes = self.stable[self.module_name]["function_nodes"]
            if self.function_name not in stable_function_nodes and \
                    not isinstance(self.function_name, jsondiff.Symbol):
                continue  # this is a new function/additive change in current version so skip checks

            function_deleted = self.check_module_level_function_removed_or_renamed(function_components)
            if function_deleted:
                continue  # function was deleted, abort other checks

            self.check_function_type_changed(function_components)

            stable_parameters_node = stable_function_nodes[self.function_name]["parameters"]
            current_parameters_node = self.current[self.module_name]["function_nodes"][self.function_name]["parameters"]
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
            self.parameter_name = param_name
            all_parameters_deleted = self.check_all_parameters_deleted(stable_parameters_node)
            if all_parameters_deleted:
                continue  # all params were removed, abort other checks
            for diff_type in diff:
                if isinstance(self.parameter_name, jsondiff.Symbol):
                    self.check_positional_parameter_removed_or_renamed(
                        stable_parameters_node[diff_type]["param_type"],
                        diff_type,
                        stable_parameters_node,
                    )
                    self.check_kwargs_removed(
                        stable_parameters_node[diff_type]["param_type"],
                        diff_type
                    )
                elif self.parameter_name not in stable_parameters_node:
                    self.check_positional_parameter_added(
                        current_parameters_node[param_name]
                    )
                    break
                elif diff_type == "default":
                    stable_default = stable_parameters_node[self.parameter_name]["default"]
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
            if self.class_name:
                bc = (
                    self.REMOVED_CLASS_FUNCTION_KWARGS_MSG,
                    BreakingChangeType.REMOVED_FUNCTION_KWARGS,
                    self.module_name, self.class_name, self.function_name
                )
            else:
                bc = (
                    self.REMOVED_FUNCTION_KWARGS_MSG,
                    BreakingChangeType.REMOVED_FUNCTION_KWARGS,
                    self.module_name, self.function_name
                )
            self.breaking_changes.append(bc)

    def check_module_removed_or_renamed(self, module: Dict) -> Union[bool, None]:
        if isinstance(self.module_name, jsondiff.Symbol):
            deleted_modules = []
            if self.module_name.label == "delete":
                deleted_modules = [module]
            elif self.module_name.label == "replace":
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
        if isinstance(self.parameter_name, jsondiff.Symbol) and self.parameter_name.label == "replace":
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
            if self.class_name:
                self.breaking_changes.append(
                    (
                        self.CHANGED_CLASS_FUNCTION_KIND_MSG, BreakingChangeType.CHANGED_FUNCTION_KIND,
                        self.module_name, self.class_name, self.function_name, original, change
                    )
                )
            else:
                self.breaking_changes.append(
                    (
                        self.CHANGED_FUNCTION_KIND_MSG, BreakingChangeType.CHANGED_FUNCTION_KIND,
                        self.module_name, self.function_name, original, change
                    )
                )

    def check_parameter_type_changed(self, diff: Dict, stable_parameters_node: Dict) -> None:
        if self.class_name:
            self.breaking_changes.append(
                (
                    self.CHANGED_PARAMETER_KIND_MSG, BreakingChangeType.CHANGED_PARAMETER_KIND,
                    self.module_name, self.class_name, self.function_name, self.parameter_name,
                    stable_parameters_node[self.parameter_name]["param_type"], diff
                )
            )
        else:
            self.breaking_changes.append(
                (
                    self.CHANGED_PARAMETER_KIND_OF_FUNCTION_MSG, BreakingChangeType.CHANGED_PARAMETER_KIND,
                    self.module_name, self.function_name, self.parameter_name,
                    stable_parameters_node[self.parameter_name]["param_type"], diff
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
            if self.class_name:
                self.breaking_changes.append(
                    (
                        self.REMOVED_PARAMETER_DEFAULT_VALUE_MSG,
                        BreakingChangeType.REMOVED_PARAMETER_DEFAULT_VALUE,
                        self.module_name, self.class_name, self.function_name,
                        default, self.parameter_name
                    )
                )
            else:

                self.breaking_changes.append(
                    (
                        self.REMOVED_PARAMETER_DEFAULT_VALUE_OF_FUNCTION_MSG,
                        BreakingChangeType.REMOVED_PARAMETER_DEFAULT_VALUE,
                        self.module_name, self.function_name, default, self.parameter_name
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
                    if self.class_name:
                        self.breaking_changes.append(
                            (
                                self.CHANGED_PARAMETER_DEFAULT_VALUE_MSG,
                                BreakingChangeType.CHANGED_PARAMETER_DEFAULT_VALUE,
                                self.module_name, self.class_name, self.function_name,
                                self.parameter_name, stable_default, default
                            )
                        )
                    else:
                        self.breaking_changes.append(
                            (
                                self.CHANGED_PARAMETER_DEFAULT_VALUE_OF_FUNCTION_MSG,
                                BreakingChangeType.CHANGED_PARAMETER_DEFAULT_VALUE,
                                self.module_name, self.function_name,
                                self.parameter_name, stable_default, default
                            )
                        )

    def check_positional_parameter_added(self, current_parameters_node: Dict) -> None:
        if current_parameters_node["param_type"] == "positional_or_keyword" and \
                current_parameters_node["default"] != "none":
            if self.class_name:
                self.breaking_changes.append(
                    (
                        self.ADDED_POSITIONAL_PARAM_TO_METHOD_MSG, BreakingChangeType.ADDED_POSITIONAL_PARAM,
                        self.module_name, self.class_name, self.function_name,
                        current_parameters_node["param_type"], self.parameter_name
                    )
                )
            else:
                self.breaking_changes.append(
                    (
                        self.ADDED_POSITIONAL_PARAM_TO_FUNCTION_MSG, BreakingChangeType.ADDED_POSITIONAL_PARAM,
                        self.module_name, self.function_name,
                        current_parameters_node["param_type"], self.parameter_name
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
        if self.parameter_name.label == "delete":
            deleted_params = [deleted]
        elif self.parameter_name.label == "replace":  # replace means all positional parameters were removed
            deleted_params = {
                param_name: details
                for param_name, details
                in stable_parameters_node.items()
                if details["param_type"] == "positional_or_keyword"
            }

        for deleted in deleted_params:
            if deleted != "self":
                if self.class_name:
                    self.breaking_changes.append(
                        (
                            self.REMOVED_OR_RENAMED_POSITIONAL_PARAM_OF_METHOD_MSG,
                            BreakingChangeType.REMOVED_OR_RENAMED_POSITIONAL_PARAM,
                            self.module_name, self.class_name, self.function_name, param_type, deleted
                        )
                    )
                else:
                    self.breaking_changes.append(
                        (
                            self.REMOVED_OR_RENAMED_POSITIONAL_PARAM_OF_FUNCTION_MSG,
                            BreakingChangeType.REMOVED_OR_RENAMED_POSITIONAL_PARAM,
                            self.module_name, self.function_name, param_type, deleted
                        )
                    )

    def check_class_instance_attribute_removed_or_renamed(self, components: Dict) -> None:
        for prop in components.get("properties", []):
            if isinstance(prop, jsondiff.Symbol):
                deleted_props = []
                if prop.label == "delete":
                    deleted_props = components["properties"][prop]
                elif prop.label == "replace":
                    deleted_props = self.stable[self.module_name]["class_nodes"][self.class_name]["properties"]

                for property in deleted_props:
                    bc = None
                    if self.class_name.endswith("Client"):
                        bc = (
                            self.REMOVED_OR_RENAMED_INSTANCE_ATTRIBUTE_FROM_CLIENT_MSG,
                            BreakingChangeType.REMOVED_OR_RENAMED_INSTANCE_ATTRIBUTE,
                            self.module_name, self.class_name, property
                        )
                    elif self.stable[self.module_name]["class_nodes"][self.class_name]["type"] == "Enum":
                        if property.upper() not in self.current[self.module_name]["class_nodes"][self.class_name]["properties"] \
                            and property.lower() not in self.current[self.module_name]["class_nodes"][self.class_name]["properties"]:
                            bc = (
                                self.REMOVED_OR_RENAMED_ENUM_VALUE_MSG,
                                BreakingChangeType.REMOVED_OR_RENAMED_ENUM_VALUE,
                                self.module_name, self.class_name, property
                            )
                    else:
                        bc = (
                            self.REMOVED_OR_RENAMED_INSTANCE_ATTRIBUTE_FROM_MODEL_MSG,
                            BreakingChangeType.REMOVED_OR_RENAMED_INSTANCE_ATTRIBUTE,
                            self.module_name, self.class_name, property
                        )
                    if bc:
                        self.breaking_changes.append(bc)

    def check_class_removed_or_renamed(self, class_components: Dict) -> Union[bool, None]:
        if isinstance(self.class_name, jsondiff.Symbol):
            deleted_classes = []
            if self.class_name.label == "delete":
                deleted_classes = class_components
            elif self.class_name.label == "replace":
                deleted_classes = self.stable[self.module_name]["class_nodes"]

            for name in deleted_classes:
                if name.endswith("Client"):
                    bc = (
                        self.REMOVED_OR_RENAMED_CLIENT_MSG,
                        BreakingChangeType.REMOVED_OR_RENAMED_CLIENT,
                        self.module_name, name
                    )
                else:
                    bc = (
                        self.REMOVED_OR_RENAMED_CLASS_MSG,
                        BreakingChangeType.REMOVED_OR_RENAMED_CLASS,
                        self.module_name, name
                    )
                self.breaking_changes.append(bc)
            return True

    def check_class_method_removed_or_renamed(
        self, method_components: Dict,
        stable_methods_node: Dict
    ) -> Union[bool, None]:
        if isinstance(self.function_name, jsondiff.Symbol):
            methods_deleted = []
            if self.function_name.label == "delete":
                methods_deleted = method_components
            elif self.function_name.label == "replace":
                methods_deleted = stable_methods_node

            for method in methods_deleted:
                if self.class_name.endswith("Client"):
                    bc = (
                        self.REMOVED_OR_RENAMED_CLIENT_METHOD_MSG,
                        BreakingChangeType.REMOVED_OR_RENAMED_CLIENT_METHOD,
                        self.module_name, self.class_name, method
                    )
                else:
                    bc = (
                        self.REMOVED_OR_RENAMED_CLASS_METHOD_MSG,
                        BreakingChangeType.REMOVED_OR_RENAMED_CLASS_METHOD,
                        self.module_name, self.class_name, method
                    )
                self.breaking_changes.append(bc)
            return True

    def check_module_level_function_removed_or_renamed(self, function_components: Dict) -> Union[bool, None]:
        if isinstance(self.function_name, jsondiff.Symbol):
            deleted_functions = []
            if self.function_name.label == "delete":
                deleted_functions = function_components
            elif self.function_name.label == "replace":
                deleted_functions = self.stable[self.module_name]["function_nodes"]

            for function in deleted_functions:
                self.breaking_changes.append(
                    (
                        self.REMOVED_OR_RENAMED_MODULE_LEVEL_FUNCTION_MSG,
                        BreakingChangeType.REMOVED_OR_RENAMED_MODULE_LEVEL_FUNCTION,
                        self.module_name, function
                    )
                )
            return True

    def get_reportable_breaking_changes(self, ignore_changes: Dict) -> List:
        reportable_changes = []
        ignored = ignore_changes[self.package_name]
        for bc in self.breaking_changes:
            msg, bc_type, module_name, *args = bc
            class_name = args[0] if args else None
            function_name = args[1] if len(args) > 1 else None
            if (bc_type, module_name) in ignored or \
                    (bc_type, module_name, class_name) in ignored or \
                    (bc_type, module_name, class_name, function_name) in ignored:
                continue
            reportable_changes.append(bc)
        return reportable_changes

    def report_breaking_changes(self) -> None:
        ignore_changes = self.ignore if self.ignore else IGNORE_BREAKING_CHANGES
        if self.package_name in ignore_changes:
            self.breaking_changes = self.get_reportable_breaking_changes(ignore_changes)

        for idx, bc in enumerate(self.breaking_changes):
            msg, *args = bc
            self.breaking_changes[idx] = msg.format(*args)
