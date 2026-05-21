#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from _models import CheckerType
import jsondiff


class ChangedClassPropertyTypeChecker:
    """Detect a change to a class property type annotation.
    
    This checker identifies when a model property changes its attr_type from one value
    to another (e.g., Operation.display changed from OperationInfo to OperationDisplay).
    It only emits when the property exists in both stable and current snapshots with
    different attr_type values. Add/remove cases are handled by existing checkers.
    """

    node_type = CheckerType.CLASS
    name = "ChangedClassPropertyType"
    is_breaking = True
    message = "Model `{}` changed type of property `{}` from `{}` to `{}`"

    def run_check(self, diff, stable_nodes, current_nodes, **kwargs):
        module_name = kwargs.get("module_name")
        bc_list = []

        # New module: nothing to compare against.
        if module_name not in stable_nodes:
            return bc_list

        for class_name, class_components in diff.items():
            # Skip removed/renamed class entries; those are handled by other checkers.
            if isinstance(class_name, jsondiff.Symbol):
                continue
            
            # Ensure class exists in both stable and current
            if class_name not in stable_nodes[module_name].get("class_nodes", {}):
                continue
            if class_name not in current_nodes[module_name].get("class_nodes", {}):
                continue

            stable_class = stable_nodes[module_name]["class_nodes"][class_name]
            current_class = current_nodes[module_name]["class_nodes"][class_name]

            stable_properties = stable_class.get("properties", {})
            current_properties = current_class.get("properties", {})

            # Iterate over properties that exist in both stable and current
            for prop_name in stable_properties.keys():
                if prop_name not in current_properties:
                    continue  # Property was removed, handled by existing checker

                stable_prop = stable_properties[prop_name]
                current_prop = current_properties[prop_name]

                # Extract attr_type, handling dict and non-dict formats
                stable_type = stable_prop.get("attr_type") if isinstance(stable_prop, dict) else stable_prop
                current_type = current_prop.get("attr_type") if isinstance(current_prop, dict) else current_prop

                # Only report if both have attr_type and they differ
                if stable_type is None or current_type is None:
                    continue
                if stable_type == current_type:
                    continue

                # Emit breaking change
                bc_list.append(
                    (
                        self.message, self.name, module_name, class_name, prop_name,
                        stable_type, current_type,
                    )
                )

        return bc_list
