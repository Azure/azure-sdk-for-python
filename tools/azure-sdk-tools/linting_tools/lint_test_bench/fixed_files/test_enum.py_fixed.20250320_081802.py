# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from enum import Enum
from azure.core import CaseInsensitiveEnumMeta

# Fixing enum-must-be-uppercase and enum-must-inherit-case-insensitive-enum-meta

class MyFixedEnum1(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    ONE = "one"

class MyFixedEnum2(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    ONE = "one"
