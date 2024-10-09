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

class AddedMethodOverloadChecker:
    node_type = CheckerType.FUNCTION_OR_METHOD
    name = "AddedMethodOverload"
    is_breaking = False
    message = {
        "default": "Method `{}.{}` has a new overload `{}`",
    }

    def run_check(self, diff, stable_nodes, current_nodes, **kwargs):
        module_name = kwargs.get("module_name")
        class_name = kwargs.get("class_name")
        changes_list = []
        for method_name, method_components in diff.items():
            # We aren't checking for deleted methods in this checker
            if isinstance(method_name, jsondiff.Symbol):
                continue
            for overload in method_components.get("overloads", []):
                if isinstance(overload, jsondiff.Symbol):
                    if overload.label == "insert":
                        for _, added_overload in method_components["overloads"][overload]:
                            parsed_overload_signature = f"def {method_name}(" + ", ".join([f"{name}: {data['type']}" for name,  data in added_overload["parameters"].items()]) + ")"
                            if added_overload["return_type"] is not None:
                                parsed_overload_signature += f" -> {added_overload['return_type']}"
                            changes_list.append((self.message["default"], self.name, module_name, class_name, method_name, parsed_overload_signature))
                else:
                    # this case is for when the overload is not a symbol and simply shows as a new overload in the diff
                    parsed_overload_signature = f"def {method_name}(" + ", ".join([f"{name}: {data['type']}" for name,  data in overload["parameters"].items()]) + ")"
                    if overload["return_type"] is not None:
                        parsed_overload_signature += f" -> {overload['return_type']}"
                    changes_list.append((self.message["default"], self.name, module_name, class_name, method_name, parsed_overload_signature))
        return changes_list
