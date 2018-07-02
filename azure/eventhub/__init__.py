# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

__version__ = "0.2.0b2"

from azure.eventhub.common import EventData, EventHubError, Offset
from azure.eventhub.client import EventHubClient
from azure.eventhub.sender import Sender
from azure.eventhub.receiver import Receiver

try:
    from azure.eventhub._async import (
        EventHubClientAsync,
        AsyncSender,
        AsyncReceiver)
except (ImportError, SyntaxError):
    pass  # Python 3 async features not supported
