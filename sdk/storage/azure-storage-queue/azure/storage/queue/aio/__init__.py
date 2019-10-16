# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from .queue_client_async import QueueClient
from .queue_service_client_async import QueueServiceClient


__all__ = [
    'QueueClient',
    'QueueServiceClient',
]
