#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------
# This checker is designed to clean up reported changes related to libraries migrating from
# swagger -> typespec where models that where previously flattened are no longer flattened.
# The checker will check for the following:
# 1. Check if a model has a new `properties`` field
# 2. Check if there is a corresponding `<model name>Properties` model
# 3. Remove entries related to the new `properties`` field from the diff
# 4. Remove entries related to the new `<model name>Properties` model from the diff
# 5. Remove entries related losing properties on the original model
# --------------------------------------------------------------------------------------------

import copy
import sys
import os
sys.path.append(os.path.abspath("../../scripts/breaking_changes_checker"))


class UnflattenedModelsChecker:
    def run_check(self, breaking_changes: list, features_added: list, *, diff: dict, stable_nodes: dict, current_nodes: dict, **kwargs) -> tuple[list, list]:
        properties_model_entry = ()
        properties_field_entry = ()

        breaking_changes_copy = copy.deepcopy(breaking_changes)
        features_added_copy = copy.deepcopy(features_added)
        # Look for new "*Properties" models and their corresponding properties field in the original model
        for fa in features_added:
            _, change_type, module_name, class_name, *args = fa
            if change_type == "AddedClass" and class_name.endswith("Properties"):
                properties_model_entry = fa
                # Check if the corresponding model has a properties field
                original_model_name = class_name[:-len("Properties")]
                if original_model_name in stable_nodes[module_name]["class_nodes"]:
                    original_model = stable_nodes[module_name]["class_nodes"][original_model_name]
                    for fa2 in features_added:
                        _, change_type2, module_name2, class_name2, *args2 = fa2
                        # Check if the class name is the original model name
                        if class_name2 and class_name2 == original_model_name:
                            if change_type2 == "AddedClassProperty" and "properties" == args2[0]:
                                properties_field_entry = fa2
                                break
                    if not properties_field_entry or not properties_model_entry:
                        continue
                    # Check the breaking changes list for entries about removing any of the properties that existed in the original model
                    for prop in original_model["properties"]:
                        for breaking_change in breaking_changes_copy:
                            _, bc_change_type, bc_module_name, bc_class_name, *bc_args = breaking_change
                            if (bc_change_type == "RemovedOrRenamedInstanceAttribute" and
                                    bc_class_name == original_model_name and
                                    bc_args[0] == prop):
                                # If we find a breaking change about removing a property, delete it from the breaking changes list
                                breaking_changes_copy.remove(breaking_change)
                                break
                if properties_model_entry and properties_field_entry:
                    # If we found both the properties model and the properties field, remove them from the features added list
                    # since this means the model was unflattened
                    features_added_copy.remove(properties_model_entry)
                    features_added_copy.remove(properties_field_entry)
                properties_field_entry, properties_model_entry = (), ()
        return breaking_changes_copy, features_added_copy
