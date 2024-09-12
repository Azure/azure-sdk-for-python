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

class AddedClassChecker:
    node_type = CheckerType.CLASS
    name = "AddedClass"
    is_breaking = False
    message = {
        "default": "Added model `{}`",
        "client": "Added client `{}`",
        "enum": "Added enum `{}`",
        "enum_member": "Enum `{}` added member `{}`",
        "class_property": "Model `{}` added property `{}`",
        "client_operation_group": "Client `{}` added operation group `{}`",
    }

    def run_check(self, diff, stable_nodes, current_nodes, **kwargs):
        features_added = []
        module_name = kwargs.get("module_name")
        for class_name, class_components in diff.items():
            class_name = class_name
            stable_class_nodes = stable_nodes[module_name]["class_nodes"]
            if not isinstance(class_name, jsondiff.Symbol):
                if class_name not in stable_class_nodes:
                    if class_name.endswith("Client"):
                        # This is a new client
                        fa = (
                            self.message["client"],
                            "AddedClient",
                            module_name, class_name
                        )
                        features_added.append(fa)
                    elif class_components.get("type", None) == "Enum":
                        # This is a new enum
                        fa = (self.message["enum"], "AddedEnum", module_name, class_name)
                        features_added.append(fa)
                    else:
                        # This is a new class
                        fa = (self.message["default"], self.name, module_name, class_name)
                        features_added.append(fa)
                else:
                    stable_property_node = stable_class_nodes[class_name]["properties"]
                    for property_name, property_components in class_components.get("properties", {}).items():
                        if property_name not in stable_property_node and \
                                not isinstance(property_name, jsondiff.Symbol):
                            fa = (
                                    self.message["class_property"],
                                    "AddedClassProperty",
                                    module_name, class_name, property_name
                                )
                            if class_name.endswith("Client"):
                                if property_components["attr_type"] is not None and property_components["attr_type"].lower().endswith("operations"):
                                    fa = (
                                        self.message["client_operation_group"],
                                        "AddedOperationGroup",
                                        module_name, class_name, property_name
                                    )
                            if stable_class_nodes[class_name]["type"] == "Enum":
                                fa = (
                                    self.message["enum_member"],
                                    "AddedEnumMember",
                                    module_name, class_name, property_name
                                )
                            features_added.append(fa)
        return features_added
