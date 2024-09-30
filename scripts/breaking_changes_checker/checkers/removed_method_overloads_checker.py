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

class RemovedMethodOverloadChecker:
    node_type = CheckerType.FUNCTION_OR_METHOD
    name = "RemovedMethodOverload"
    is_breaking = True
    message = {
        "default": "`{}.{}` had an overload `{}` removed",
        "all": "`{}.{}` had all overloads removed"
    }

    def run_check(self, diff, stable_nodes, current_nodes, **kwargs):
        module_name = kwargs.get("module_name")
        class_name = kwargs.get("class_name")
        bc_list = []
        # This is a new module, so we won't check for removed overloads
        if module_name not in stable_nodes:
            return bc_list
        if class_name not in stable_nodes[module_name]["class_nodes"]:
            # This is a new class, so we don't need to check for removed overloads
            return bc_list
        for method_name, method_components in diff.items():
            # We aren't checking for deleted methods in this checker
            if isinstance(method_name, jsondiff.Symbol):
                continue
            # Check if all of the overloads were deleted for an existing stable method
            if len(method_components.get("overloads", [])) == 0:
                if method_name in stable_nodes[module_name]["class_nodes"][class_name]["methods"] and \
                        "overloads" in stable_nodes[module_name]["class_nodes"][class_name]["methods"][method_name]:
                    if len(stable_nodes[module_name]["class_nodes"][class_name]["methods"][method_name]["overloads"]) > 0:
                        bc_list.append((self.message["all"], self.name, module_name, class_name, method_name))
                        continue
            # Check for specific overloads that were deleted
            for overload in method_components.get("overloads", []):
                if isinstance(overload, jsondiff.Symbol):
                    if overload.label == "delete":
                        for deleted_overload in method_components["overloads"][overload]:
                            stable_node_overloads = stable_nodes[module_name]["class_nodes"][class_name]["methods"][method_name]["overloads"][deleted_overload]
                            parsed_overload_signature = f"def {method_name}(" + ", ".join([f"{name}: {data['type']}" for name,  data in stable_node_overloads["parameters"].items()]) + ")"
                            if stable_node_overloads["return_type"] is not None:
                                parsed_overload_signature += f" -> {stable_node_overloads['return_type']}"
                            bc_list.append((self.message["default"], self.name, module_name, class_name, method_name, parsed_overload_signature))
        return bc_list
