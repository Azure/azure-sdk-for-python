# coding=utf-8
# --------------------------------------------------------------------------
# Created on Mon Oct 18 2021
#
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root
# for license information.
# --------------------------------------------------------------------------

try:
    from ._helper_py3 import EventHandler
    from ._helper_py3 import AccessKeyValidator
except (SyntaxError, ImportError):
    from ._helper import EventHandler
    from ._helper import AccessKeyValidator


from .models import (
    ConnectionContext,
    ServiceRequest,
    ConnectEventRequest,
    ConnectedEventRequest,
    DisconnectedEventRequest,
    MessageEventRequest,
    ServiceResponse,
    ServiceErrorResponse,
    ConnectEventResponse,
    MessageEventResponse,
)

__request_models = [
    "ServiceRequest",
	"ConnectEventRequest",
	"ConnectedEventRequest",
	"DisconnectedEventRequest",
	"MessageEventRequest",
	"InvalidRequest",
]

__response_models = [
    "ServiceResponse",
    "ServiceErrorResponse",
    "ConnectEventResponse",
    "MessageEventResponse"
]

__all__ = [
    "EventHandler",
    "ConnectionContext",
    "AccessKeyValidator",
] + __request_models + __response_models
