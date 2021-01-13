# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
from ._generated._version import VERSION

# default values for common package, in case it is used directly
DEFAULT_X_MS_VERSION = "2018-03-28"

# Live ServiceClient URLs
SERVICE_HOST_BASE = "core.windows.net"
DEFAULT_PROTOCOL = "https"

# Development ServiceClient URLs
DEV_BLOB_HOST = "127.0.0.1:10000"
DEV_QUEUE_HOST = "127.0.0.1:10001"

# Default credentials for Development Storage Service
DEV_ACCOUNT_NAME = "devstoreaccount1"
DEV_ACCOUNT_SECONDARY_NAME = "devstoreaccount1-secondary"
DEV_ACCOUNT_KEY = "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="

# Socket timeout in seconds
DEFAULT_SOCKET_TIMEOUT = 20

# for python 3.5+, there was a change to the definition of the socket timeout (as far as socket.sendall is concerned)
# The socket timeout is now the maximum total duration to send all data.
if sys.version_info >= (3, 5):
    # the timeout to connect is 20 seconds, and the read timeout is 2000 seconds
    # the 2000 seconds was calculated with: 100MB (max block size)/ 50KB/s (an arbitrarily chosen minimum upload speed)
    DEFAULT_SOCKET_TIMEOUT = (20, 2000)

# Encryption constants
_ENCRYPTION_PROTOCOL_V1 = "1.0"

_AUTHORIZATION_HEADER_NAME = "Authorization"
_COPY_SOURCE_HEADER_NAME = "x-ms-copy-source"
_REDACTED_VALUE = "REDACTED"


X_MS_VERSION = VERSION

# Socket timeout in seconds
CONNECTION_TIMEOUT = 20
READ_TIMEOUT = 20

# for python 3.5+, there was a change to the definition of the socket timeout (as far as socket.sendall is concerned)
# The socket timeout is now the maximum total duration to send all data.
if sys.version_info >= (3, 5):
    # the timeout to connect is 20 seconds, and the read timeout is 2000 seconds
    # the 2000 seconds was calculated with: 100MB (max block size)/ 50KB/s (an arbitrarily chosen minimum upload speed)
    READ_TIMEOUT = 2000

STORAGE_OAUTH_SCOPE = "https://storage.azure.com/.default"

NEXT_TABLE_NAME = "x-ms-continuation-NextTableName"
NEXT_PARTITION_KEY = "x-ms-continuation-NextPartitionKey"
NEXT_ROW_KEY = "x-ms-continuation-NextRowKey"
