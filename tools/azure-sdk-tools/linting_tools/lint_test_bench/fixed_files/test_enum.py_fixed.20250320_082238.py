# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from enum import Enum
from azure.core import CaseInsensitiveEnumMeta

# This code violates enum-must-inherit-case-insensitive-enum-meta

class MyGoodEnum2(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    ONE = "one"

class MyGoodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    ONE = "one"
