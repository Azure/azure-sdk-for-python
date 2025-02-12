# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from enum import Enum
from typing import Literal


WS_VERSION: Literal[13] = 13
WS_KEY = b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

EOF = b'\r\n\r\n'

class ConnectionStatus(Enum):
    # a client opens a connection and sends a handshake
    CONNECTING = 1

    # a client has successfully completed & validated the handshake response from the server
    OPEN = 2

    # upon either sending or receiving a Close control frame
    CLOSING = 3

    # when the underlying TCP connection is closed
    CLOSED = 4