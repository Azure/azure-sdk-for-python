# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._client import LoadTestAdministrationClient, LoadTestRunClient
from ._version import VERSION

__version__ = VERSION
__all__ = ["LoadTestAdministrationClient", "LoadTestRunClient"]
