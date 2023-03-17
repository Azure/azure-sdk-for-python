# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum

from azure.ai.ml._utils._experimental import experimental


@experimental
class _DataColumnType(Enum):
    string = 1
    integer = 2
    long = 3
    float = 4
    double = 5
    binary = 6
    datetime = 7
    boolean = 8
