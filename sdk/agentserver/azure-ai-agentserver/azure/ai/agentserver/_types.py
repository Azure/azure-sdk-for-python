# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from dataclasses import dataclass


@dataclass
class InvokeRequest:
    """Incoming invoke request.

    :param body: Raw request body bytes.
    :type body: bytes
    :param headers: All HTTP request headers.
    :type headers: dict[str, str]
    :param invocation_id: Server-generated UUID for this invocation.
    :type invocation_id: str
    """

    body: bytes
    headers: dict[str, str]
    invocation_id: str
