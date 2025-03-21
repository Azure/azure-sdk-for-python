# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from enum import Enum
from azure.core import CaseInsensitiveEnumMeta

class MyBadEnum2(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    One = "one"

class MyGoodEnum2(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    ONE = "one"

class MyBadEnum(str, Enum):
    One = "one"
