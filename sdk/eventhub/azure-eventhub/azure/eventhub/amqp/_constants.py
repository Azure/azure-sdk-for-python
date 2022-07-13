# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class AmqpMessageBodyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    DATA = "data"
    SEQUENCE = "sequence"
    VALUE = "value"
