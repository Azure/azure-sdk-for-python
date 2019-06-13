# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys


X_MS_VERSION = '2018-03-28'

# Socket timeout in seconds
DEFAULT_SOCKET_TIMEOUT = 20

# for python 3.5+, there was a change to the definition of the socket timeout (as far as socket.sendall is concerned)
# The socket timeout is now the maximum total duration to send all data.
if sys.version_info >= (3, 5):
    # the timeout to connect is 20 seconds, and the read timeout is 2000 seconds
    # the 2000 seconds was calculated with: 100MB (max block size)/ 50KB/s (an arbitrarily chosen minimum upload speed)
    DEFAULT_SOCKET_TIMEOUT = (20, 2000)

# Default credentials for Development Storage Service
DEV_ACCOUNT_NAME = 'devstoreaccount1'
DEV_ACCOUNT_SECONDARY_NAME = 'devstoreaccount1-secondary'
DEV_ACCOUNT_KEY = 'Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=='
