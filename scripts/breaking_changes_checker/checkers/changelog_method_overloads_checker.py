#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import jsondiff

class ChangelogMethodOverloadsChecker:
    name = "AddedMethodOverload"
    is_breaking = False
    message = {
        "default": "Method {}.{} has a new overload `{}`",
    }

    def run_check(self, diff, stable_nodes, current_nodes):
        bc_list = []
        for module_name, module in diff.items():
            for class_name, class_components in module.get("class_nodes", {}).items():
                # We aren't checking for deleted classes in this checker
                if isinstance(class_name, jsondiff.Symbol):
                    continue
                for method_name, method_components in class_components.get("methods", {}).items():
                    # We aren't checking for deleted methods in this checker
                    if isinstance(method_name, jsondiff.Symbol):
                        continue
                    # Check for specific overloads that were deleted
                    if method_name == "analyze_text":
                        print(diff)
                    for overload in method_components.get("overloads", []):
                        if isinstance(overload, jsondiff.Symbol):
                            if overload.label == "insert":
                                for _, added_overload in method_components["overloads"][overload]:
                                    parsed_overload_signature = f"def {method_name}(" + ", ".join([f"{name}: {data['type']}" for name,  data in added_overload["parameters"].items()]) + ")"
                                    if added_overload["return_type"] is not None:
                                        parsed_overload_signature += f" -> {added_overload['return_type']}"
                        else:
                            # this case is for when the overload is not a symbol and simply shows as a new overload in the diff
                            parsed_overload_signature = f"def {method_name}(" + ", ".join([f"{name}: {data['type']}" for name,  data in method_components["overloads"][overload]["parameters"].items()]) + ")"
                            if current_nodes[module_name]["class_nodes"][class_name]["methods"][method_name]["overloads"][overload]["return_type"] is not None:
                                parsed_overload_signature += f" -> {overload['return_type']}"
                        bc_list.append((self.message["default"], self.name, module_name, class_name, method_name, parsed_overload_signature))
        return bc_list
