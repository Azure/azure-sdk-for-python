# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import platform
import sys

__author__ = 'Microsoft Corp. <ptvshelp@microsoft.com>'
__version__ = '2.0.0'

# UserAgent string sample: 'Azure-Storage/0.37.0-0.38.0 (Python CPython 3.4.2; Windows 8)'
# First version(0.37.0) is the common package, and the second version(0.38.0) is the service package
USER_AGENT_STRING_PREFIX = 'Azure-Storage/{}-'.format(__version__)
USER_AGENT_STRING_SUFFIX = '(Python {} {}; {} {})'.format(platform.python_implementation(),
                                                          platform.python_version(), platform.system(),
                                                          platform.release())

# default values for common package, in case it is used directly
DEFAULT_X_MS_VERSION = '2018-03-28'
DEFAULT_USER_AGENT_STRING = '{}None {}'.format(USER_AGENT_STRING_PREFIX, USER_AGENT_STRING_SUFFIX)

# Live ServiceClient URLs
SERVICE_HOST_BASE = 'core.windows.net'
DEFAULT_PROTOCOL = 'https'

# Development ServiceClient URLs
DEV_BLOB_HOST = '127.0.0.1:10000'
DEV_QUEUE_HOST = '127.0.0.1:10001'

# Default credentials for Development Storage Service
DEV_ACCOUNT_NAME = 'devstoreaccount1'
DEV_ACCOUNT_SECONDARY_NAME = 'devstoreaccount1-secondary'
DEV_ACCOUNT_KEY = 'Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=='

# Socket timeout in seconds
DEFAULT_SOCKET_TIMEOUT = 20

# for python 3.5+, there was a change to the definition of the socket timeout (as far as socket.sendall is concerned)
# The socket timeout is now the maximum total duration to send all data.
if sys.version_info >= (3, 5):
    # the timeout to connect is 20 seconds, and the read timeout is 2000 seconds
    # the 2000 seconds was calculated with: 100MB (max block size)/ 50KB/s (an arbitrarily chosen minimum upload speed)
    DEFAULT_SOCKET_TIMEOUT = (20, 2000)

# Encryption constants
_ENCRYPTION_PROTOCOL_V1 = '1.0'

_AUTHORIZATION_HEADER_NAME = 'Authorization'
_COPY_SOURCE_HEADER_NAME = 'x-ms-copy-source'
_REDACTED_VALUE = 'REDACTED'
