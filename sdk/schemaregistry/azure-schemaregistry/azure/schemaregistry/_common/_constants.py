# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from enum import Enum


class SerializationType(Enum):
    AVRO = "AVRO"
    JSON = "JSON"
