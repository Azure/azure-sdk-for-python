#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from enum import Enum
from typing import Any, Dict
import jsondiff
from breaking_changes_tracker import BreakingChangesTracker

class ChangeType(str, Enum):
    ADDED_CLIENT = "AddedClient"
    ADDED_CLIENT_METHOD = "AddedClientMethod"
    ADDED_CLASS = "AddedClass"
    ADDED_CLASS_METHOD = "AddedClassMethod"
    ADDED_CLASS_METHOD_PARAMETER = "AddedClassMethodParameter"
    ADDED_CLASS_PROPERTY = "AddedClassProperty"
    ADDED_ENUM = "AddedEnum"
    ADDED_ENUM_MEMBER = "AddedEnumMember"
    ADDED_FUNCTION_PARAMETER = "AddedFunctionParameter"
    ADDED_OPERATION_GROUP = "AddedOperationGroup"

class ChangelogTracker(BreakingChangesTracker):
    ADDED_CLIENT_MSG = \
        "Added client `{}`"
    ADDED_CLIENT_METHOD_MSG = \
        "Client `{}` added method `{}`"
    ADDED_CLASS_MSG = \
        "Added model `{}`"
    ADDED_CLASS_METHOD_MSG = \
        "Model `{}` added method `{}`"
    ADDED_CLASS_METHOD_PARAMETER_MSG = \
        "Model `{}` added parameter `{}` in method `{}`"
    ADDED_FUNCTION_PARAMETER_MSG = \
        "Function `{}` added parameter `{}`"
    ADDED_CLASS_PROPERTY_MSG = \
        "Model `{}` added property `{}`"
    ADDED_ENUM_MSG = \
        "Added enum `{}`"
    ADDED_ENUM_MEMBER_MSG = \
        "Enum `{}` added member `{}`"
    ADDED_OPERATION_GROUP_MSG = \
        "Client `{}` added operation group `{}`"


    def __init__(self, stable: Dict, current: Dict, package_name: str, **kwargs: Any) -> None:
        super().__init__(stable, current, package_name, **kwargs)
        self.features_added = []

    def run_checks(self) -> None:
        self.run_non_breaking_change_diff_checks()
        super().run_checks()
        self.run_async_cleanup(self.features_added)

    def run_non_breaking_change_diff_checks(self) -> None:
        for module_name, module in self.diff.items():
            self.module_name = module_name
            if self.module_name not in self.stable and not isinstance(self.module_name, jsondiff.Symbol):
                continue  # TODO add this to reported changes

            self.run_non_breaking_class_level_diff_checks(module)

    def run_non_breaking_class_level_diff_checks(self, module: Dict) -> None:
        for class_name, class_components in module.get("class_nodes", {}).items():
            self.class_name = class_name
            stable_class_nodes = self.stable[self.module_name]["class_nodes"]
            if not isinstance(class_name, jsondiff.Symbol):
                if self.class_name not in stable_class_nodes:
                    if self.class_name.endswith("Client"):
                        # This is a new client
                        fa = (
                            self.ADDED_CLIENT_MSG,
                            ChangeType.ADDED_CLIENT,
                            self.module_name, class_name
                        )
                        self.features_added.append(fa)
                    elif class_components.get("type", None) == "Enum":
                        # This is a new enum
                        fa = (
                            self.ADDED_ENUM_MSG,
                            ChangeType.ADDED_ENUM,
                            self.module_name, class_name
                        )
                        self.features_added.append(fa)
                    else:
                        # This is a new class
                        fa = (
                            self.ADDED_CLASS_MSG,
                            ChangeType.ADDED_CLASS,
                            self.module_name, class_name
                        )
                        self.features_added.append(fa)
                else:
                    # Check existing class for new methods
                    stable_methods_node = stable_class_nodes[self.class_name]["methods"]
                    for method_name, method_components in class_components.get("methods", {}).items():
                        self.function_name = method_name
                        if not isinstance(self.function_name, jsondiff.Symbol):
                            if self.function_name not in stable_methods_node:
                                if self.class_name.endswith("Client"):
                                    # This is a new client method
                                    fa = (
                                        self.ADDED_CLIENT_METHOD_MSG,
                                        ChangeType.ADDED_CLIENT_METHOD,
                                        self.module_name, self.class_name, method_name
                                    )
                                    self.features_added.append(fa)
                                else:
                                    # This is a new class method
                                    fa = (
                                        self.ADDED_CLASS_METHOD_MSG,
                                        ChangeType.ADDED_CLASS_METHOD,
                                        self.module_name, class_name, method_name
                                    )
                                    self.features_added.append(fa)
                            else:
                                # Check existing methods for new parameters
                                stable_parameters_node = stable_methods_node[self.function_name]["parameters"]
                                current_parameters_node = self.current[self.module_name]["class_nodes"][self.class_name]["methods"][self.function_name]["parameters"]
                                for param_name, param_components in method_components.get("parameters", {}).items():
                                    self.parameter_name = param_name
                                    if self.parameter_name not in stable_parameters_node and \
                                            not isinstance(self.parameter_name, jsondiff.Symbol):
                                        if self.function_name == "__init__":
                                            # If this is a new class property skip reporting it here and let the class properties check handle it.
                                            # This is because we'll get multiple reports for the same new property if it's a parameter in __init__
                                            # and a class level attribute.
                                            if self.parameter_name in class_components.get("properties", {}).keys():
                                                continue
                                        self.check_non_positional_parameter_added(
                                            current_parameters_node[param_name]
                                        )
                    stable_property_node = stable_class_nodes[self.class_name]["properties"]
                    for property_name, property_components in class_components.get("properties", {}).items():
                        if property_name not in stable_property_node and \
                                not isinstance(property_name, jsondiff.Symbol):
                            fa = (
                                    self.ADDED_CLASS_PROPERTY_MSG,
                                    ChangeType.ADDED_CLASS_PROPERTY,
                                    self.module_name, class_name, property_name
                                )
                            if self.class_name.endswith("Client"):
                                if property_components["attr_type"] is not None and property_components["attr_type"].lower().endswith("operations"):
                                    fa = (
                                        self.ADDED_OPERATION_GROUP_MSG,
                                        ChangeType.ADDED_OPERATION_GROUP,
                                        self.module_name, self.class_name, property_name
                                    )
                            if stable_class_nodes[self.class_name]["type"] == "Enum":
                                fa = (
                                    self.ADDED_ENUM_MEMBER_MSG,
                                    ChangeType.ADDED_ENUM_MEMBER,
                                    self.module_name, class_name, property_name
                                )
                            self.features_added.append(fa)


    def check_non_positional_parameter_added(self, current_parameters_node: Dict) -> None:
        if current_parameters_node["param_type"] != "positional_or_keyword":
            if self.class_name:
                self.features_added.append(
                    (
                        self.ADDED_CLASS_METHOD_PARAMETER_MSG, ChangeType.ADDED_CLASS_METHOD_PARAMETER,
                        self.module_name, self.class_name, self.parameter_name, self.function_name
                    )
                )
            else:
                self.features_added.append(
                    (
                        self.ADDED_FUNCTION_PARAMETER_MSG, ChangeType.ADDED_FUNCTION_PARAMETER,
                        self.module_name, self.function_name, self.parameter_name
                    )
                )


    def report_changes(self) -> None:
        ignore_changes = self.ignore if self.ignore else {}
        self.get_reportable_changes(ignore_changes, self.breaking_changes)
        self.get_reportable_changes(ignore_changes, self.features_added)
        # Code borrowed and modified from the previous change log tool
        def _build_md(content: list, title: str, buffer: list):
            buffer.append(title)
            buffer.append("")
            for _, bc in enumerate(content):
                # Extract the message, skip the change type and the module name
                msg, _, _,*args = bc
                buffer.append("  - " + msg.format(*args))
            buffer.append("")
            return buffer

        buffer = []
        if self.features_added:
            _build_md(self.features_added, "### Features Added", buffer)
        if self.breaking_changes:
            _build_md(self.breaking_changes, "### Breaking Changes", buffer)
        content =  "\n".join(buffer).strip()

        content = "===== changelog start =====\n" + content + "\n===== changelog end =====\n"
        return content
