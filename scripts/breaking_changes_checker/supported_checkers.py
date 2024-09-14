#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from checkers.removed_class_checker import RemovedClassChecker
from checkers.removed_class_method_checker import RemovedClassMethodChecker
from checkers.removed_method_overloads_checker import RemovedMethodOverloadChecker
from checkers.added_method_overloads_checker import AddedMethodOverloadChecker
from checkers.added_class_checker import AddedClassChecker

CHECKERS = [
    RemovedClassChecker(),
    RemovedClassMethodChecker(),
    RemovedMethodOverloadChecker(),
    AddedClassChecker(),
    AddedMethodOverloadChecker(),
]
