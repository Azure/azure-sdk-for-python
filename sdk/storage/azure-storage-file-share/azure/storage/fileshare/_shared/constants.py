# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from .._serialize import _SUPPORTED_API_VERSIONS


X_MS_VERSION = _SUPPORTED_API_VERSIONS[-1]

# Default socket timeouts, in seconds
CONNECTION_TIMEOUT = 20
READ_TIMEOUT = 2000  # 100MB (max block size) / 50KB/s (an arbitrarily chosen minimum upload speed)

STORAGE_OAUTH_SCOPE = "https://storage.azure.com/.default"

SERVICE_HOST_BASE = 'core.windows.net'
