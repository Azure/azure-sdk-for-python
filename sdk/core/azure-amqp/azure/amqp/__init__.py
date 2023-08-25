# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from ._version import VERSION
from ._connection import Connection
from ._transport import SSLTransport

from .client import AMQPClient, ReceiveClient, SendClient
from ._frames_v2 import BeginFrame, Performative
from ._encode_v2 import encode_frame
from ._decode_v2 import decode_frame

__version__ = VERSION
__all__ = [
    "Connection",
    "SSLTransport",
    "AMQPClient",
    "ReceiveClient",
    "SendClient",
]
