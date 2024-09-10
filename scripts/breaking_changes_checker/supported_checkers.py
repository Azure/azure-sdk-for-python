#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from checkers.method_overloads_checker import MethodOverloadsChecker
from checkers.changelog_method_overloads_checker import ChangelogMethodOverloadsChecker

CHECKERS = [
    MethodOverloadsChecker(),
    ChangelogMethodOverloadsChecker(),
]
