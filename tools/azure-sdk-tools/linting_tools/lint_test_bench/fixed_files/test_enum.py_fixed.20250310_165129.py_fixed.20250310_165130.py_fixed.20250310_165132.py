# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from enum import Enum
from azure.core import CaseInsensitiveEnumMeta

# This code violates enum-must-be-uppercase and enum-must-inherit-case-insensitive-enum-meta

class MYGOODENUM2(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    ONE = "one"

class MYGOODENUM3(str, Enum, metaclass=CaseInsensitiveEnumMeta):  # Fixed naming convention to follow enum-must-inherit-case-insensitive-enum-meta
    ONE = "one"
