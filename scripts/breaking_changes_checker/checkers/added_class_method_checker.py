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

class AddedClassMethodChecker:
    node_type = CheckerType.FUNCTION_OR_METHOD
    name = "AddedClassMethod"
    is_breaking = False
    message = {
        "client_method": "Client `{}` added method `{}`",
        "class_method": "Model `{}` added method `{}`",
        "class_method_parameter": "Model `{}` added parameter `{}` in method `{}`",
        "function_parameter": "Function `{}` added parameter `{}`"
    }

    def run_check(self, diff, stable_nodes, current_nodes, **kwargs):
        features_added = []
        module_name = kwargs.get("module_name", None)
        class_name = kwargs.get("class_name", None)
        stable_class_nodes = stable_nodes[module_name]["class_nodes"]
        if not isinstance(class_name, jsondiff.Symbol):
            if class_name in stable_class_nodes:
                # Check existing class for new methods
                stable_methods_node = stable_class_nodes[class_name]["methods"]
                for method_name, method_components in diff.items():
                    function_name = method_name
                    if not isinstance(function_name, jsondiff.Symbol):
                        if function_name not in stable_methods_node:
                            if class_name.endswith("Client"):
                                # This is a new client method
                                fa = (
                                    self.message["client_method"],
                                    "AddedClientMethod",
                                    module_name, class_name, method_name
                                )
                                features_added.append(fa)
                            else:
                                # This is a new class method
                                fa = (
                                    self.message["class_method"],
                                    "AddedClassMethod",
                                    module_name, class_name, method_name
                                )
                                features_added.append(fa)
                        else:
                            # Check existing methods for new parameters
                            stable_parameters_node = stable_methods_node[function_name]["parameters"]
                            current_parameters_node = current_nodes[module_name]["class_nodes"][class_name]["methods"][function_name]["parameters"]
                            for param_name, param_components in method_components.get("parameters", {}).items():
                                parameter_name = param_name
                                if parameter_name not in stable_parameters_node and \
                                        not isinstance(parameter_name, jsondiff.Symbol):
                                    if function_name == "__init__":
                                        # If this is a new class property skip reporting it here and let the class properties check handle it.
                                        # This is because we'll get multiple reports for the same new property if it's a parameter in __init__
                                        # and a class level attribute.
                                        if parameter_name in current_nodes[module_name]["class_nodes"][class_name].get("properties", {}).keys():
                                            continue
                                    if current_parameters_node[param_name]["param_type"] != "positional_or_keyword":
                                        if class_name:
                                            features_added.append(
                                                (
                                                    self.message["class_method_parameter"], "AddedClassMethodParameter",
                                                    module_name, class_name, parameter_name, function_name
                                                )
                                            )
        return features_added
