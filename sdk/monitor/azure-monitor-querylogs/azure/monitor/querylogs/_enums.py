#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# cspell:ignore milli
from enum import Enum

from azure.core import CaseInsensitiveEnumMeta


class LogsQueryStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The status of the result object."""

    PARTIAL = "PartialError"
    SUCCESS = "Success"
    FAILURE = "Failure"
