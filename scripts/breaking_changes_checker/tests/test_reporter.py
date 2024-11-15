#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import sys
import importlib
import inspect
from typing import Dict
from breaking_changes_checker.detect_breaking_changes import create_function_report, create_class_report

# The build_library_report function has been copied from the original implementation in detect_breaking_changes.
# The function has been modified to remove the test_find_modules function and the modules variable. Instead we
# are directly importing the target_module and using it to build the library report.
# Everything else remains the same.
def build_library_report(target_module: str) -> Dict:
    module = importlib.import_module(target_module)
    # removed for testing purposes
    # modules = test_find_modules(module.__path__[0])
    module_name = module.__name__
    public_api = {}
    public_api[module_name] = {"class_nodes": {}, "function_nodes": {}}
    module = importlib.import_module(module_name)
    importables = [importable for importable in dir(module)]
    for importable in importables:
        if not importable.startswith("_"):
            live_obj = getattr(module, importable)
            if inspect.isfunction(live_obj):
                public_api[module_name]["function_nodes"].update({importable: create_function_report(live_obj)})
            elif inspect.isclass(live_obj):
                public_api[module_name]["class_nodes"].update({importable: create_class_report(live_obj)})
            # else:  # Constants, version, etc. Nothing of interest at the moment
            #     public_api[module_name]["others"].update({importable: live_obj})
    return public_api

def test_base_class_properties():
    sys.path.append(os.path.join(os.path.dirname(__file__), "examples", "base_class_properties"))

    report = build_library_report("base_class")
    # Check the report for properties of the base class in Bar
    assert report["base_class"]["class_nodes"]["Foo"]["properties"] == {"a": None}
    assert report["base_class"]["class_nodes"]["Bar"]["properties"] == {"a": None, "b": None}
