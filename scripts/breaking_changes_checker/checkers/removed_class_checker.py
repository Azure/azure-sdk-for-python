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
from typing import Dict, List

class RemovedClassChecker:
    node_type = CheckerType.CLASS
    name = "RemovedOrRenamedClass"
    is_breaking = True
    message = {
        "removed_renamed_client": "Deleted or renamed client `{}`",
        "removed_renamed_class": "Deleted or renamed model `{}`",
        "removed_renamed_client_instance_attribute": "Client `{}` deleted or renamed instance variable `{}`",
        "removed_renamed_class_instance_attribute": "Model `{}` deleted or renamed its instance variable `{}`",
        "removed_renamed_enum_value": "Deleted or renamed enum value `{}.{}`",
        "removed_renamed_operation_group": "Deleted or renamed client operation group `{}.{}`"
    }

    def run_check(self, diff, stable_nodes, current_nodes, **kwargs):
        breaking_changes = []
        module_name = kwargs.get("module_name", None)
        if module_name not in stable_nodes:
            # This is a new module, so we won't check for removed classes
            return breaking_changes
        for class_name, class_components in diff.items():
            stable_class_nodes = stable_nodes[module_name]["class_nodes"]
            if class_name not in stable_class_nodes and not isinstance(class_name, jsondiff.Symbol):
                continue  # this is a new model/additive change in current_nodes version so skip checks

            class_deleted = False
            if isinstance(class_name, jsondiff.Symbol):
                deleted_classes = []
                if class_name.label == "delete":
                    deleted_classes = class_components
                elif class_name.label == "replace":
                    deleted_classes = stable_nodes[module_name]["class_nodes"]

                for name in deleted_classes:
                    if name.endswith("Client"):
                        bc = (
                            self.message["client"],
                            "RemovedOrRenamedClient",
                            module_name, name
                        )
                        class_deleted = True
                    else:
                        bc = (
                            self.message["removed_renamed_class"],
                            "RemovedOrRenamedClass",
                            module_name, name
                        )
                        class_deleted = True
                    breaking_changes.append(bc)
            if class_deleted:
                continue  # class was deleted, abort other checks
            breaking_changes.extend(self.check_class_instance_attribute_removed_or_renamed(class_components, stable_nodes=stable_nodes, current_nodes=current_nodes, class_name=class_name, module_name=module_name))
        return breaking_changes

    def check_class_instance_attribute_removed_or_renamed(self, components: Dict, stable_nodes: Dict, current_nodes: Dict, class_name: str, module_name: str) -> List:
        breaking_changes = []
        deleted_props = []
        for prop in components.get("properties", []):
            if isinstance(prop, jsondiff.Symbol):
                if prop.label == "delete":
                    deleted_props = components["properties"][prop]
                elif prop.label == "replace":
                    deleted_props = stable_nodes[module_name]["class_nodes"][class_name]["properties"]

        for property in deleted_props:
            bc = None
            if class_name.endswith("Client"):
                property_type = stable_nodes[module_name]["class_nodes"][class_name]["properties"][property]["attr_type"]
                # property_type is not always a string, such as client_side_validation which is a bool, so we need to check for strings
                if property_type is not None and isinstance(property_type, str) and property_type.lower().endswith("operations"):
                        bc = (
                            self.message["removed_renamed_operation_group"],
                            "RemovedOrRenamedOperationGroup",
                            module_name, class_name, property
                        )
                else:
                    bc = (
                        self.message["removed_renamed_client_instance_attribute"],
                        "RemovedOrRenamedInstanceAttribute",
                        module_name, class_name, property
                    )
            elif stable_nodes[module_name]["class_nodes"][class_name]["type"] == "Enum":
                if property.upper() not in current_nodes[module_name]["class_nodes"][class_name]["properties"] \
                    and property.lower() not in current_nodes[module_name]["class_nodes"][class_name]["properties"]:
                    bc = (
                        self.message["removed_renamed_enum_value"],
                        "RemovedOrRenamedEnumValue",
                        module_name, class_name, property
                    )
            else:
                bc = (
                    self.message["removed_renamed_class_instance_attribute"],
                    "RemovedOrRenamedInstanceAttribute",
                    module_name, class_name, property
                )
            if bc:
                breaking_changes.append(bc)
        return breaking_changes
