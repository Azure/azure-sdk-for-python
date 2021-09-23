# coding=utf-8
# --------------------------------------------------------------------------
# Created on Thu Sep 23 2021
#
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root
# for license information.
# --------------------------------------------------------------------------

try:
    from ._models_py3 import ConnectionContext
    from ._models_py3 import ServiceRequest
    from ._models_py3 import ConnectEventRequest
    from ._models_py3 import ConnectedEventRequest
    from ._models_py3 import DisconnectedEventRequest
    from ._models_py3 import MessageEventRequest
    from ._models_py3 import ServiceResponse
    from ._models_py3 import ServiceErrorResponse
    from ._models_py3 import ConnectEventResponse
    from ._models_py3 import MessageEventResponse
except (SyntaxError, ImportError):
    from ._models import ConnectionContext
    from ._models import ServiceRequest
    from ._models import ConnectEventRequest
    from ._models import ConnectedEventRequest
    from ._models import DisconnectedEventRequest
    from ._models import MessageEventRequest
    from ._models import ServiceResponse
    from ._models import ServiceErrorResponse
    from ._models import ConnectEventResponse
    from ._models import MessageEventResponse


__all__ = [
    "ConnectionContext",
    "ServiceRequest",
	"ConnectEventRequest",
	"ConnectedEventRequest",
	"DisconnectedEventRequest",
	"MessageEventRequest",
	"InvalidRequest",
    "ServiceResponse",
    "ServiceErrorResponse",
    "ConnectEventResponse",
    "MessageEventResponse"
]
