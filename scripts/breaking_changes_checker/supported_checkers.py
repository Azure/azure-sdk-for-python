#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from checkers.removed_method_overloads_checker import RemovedMethodOverloadChecker
from checkers.added_method_overloads_checker import AddedMethodOverloadChecker
from checkers.changed_function_return_type_checker import ChangedFunctionReturnTypeChecker
from checkers.shadow_types_module_checker import ShadowTypesModuleChecker

CHECKERS = [
    RemovedMethodOverloadChecker(),
    AddedMethodOverloadChecker(),
    ChangedFunctionReturnTypeChecker(),
]

POST_PROCESSING_CHECKERS = [
    ShadowTypesModuleChecker(),
]
