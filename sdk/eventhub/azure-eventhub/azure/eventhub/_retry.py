# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Optional, Dict, Any

from enum import Enum

class RetryMode(str, Enum):
    EXPONENTIAL = 'exponential'
    FIXED = 'fixed'
