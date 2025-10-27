# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from .._serialize import _SUPPORTED_API_VERSIONS


X_MS_VERSION = _SUPPORTED_API_VERSIONS[-1]

# Default socket timeouts, in seconds
CONNECTION_TIMEOUT = 20
READ_TIMEOUT = 60

DEFAULT_OAUTH_SCOPE = "/.default"
STORAGE_OAUTH_SCOPE = "https://storage.azure.com/.default"

SERVICE_HOST_BASE = "core.windows.net"

# Devstore account information used for Azurite Storage Emulator
DEVSTORE_ACCOUNT_NAME = "devstoreaccount1"
DEVSTORE_ACCOUNT_KEY = "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="
