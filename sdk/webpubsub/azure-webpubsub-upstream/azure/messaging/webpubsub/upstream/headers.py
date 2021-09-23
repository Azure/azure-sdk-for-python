# coding=utf-8
# --------------------------------------------------------------------------
# Created on Fri Sep 24 2021
#
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root
# for license information.
# --------------------------------------------------------------------------

__prefix = "ce-"

CE_SIGNATURE = __prefix + "signature"
CE_HUB = __prefix + "hub"
CE_CONNECTION_ID = __prefix + "connectionid"
CE_ID = __prefix + "id"
CE_TIME = __prefix + "time"
CE_TYPE = __prefix + "type"
CE_SOURCE = __prefix + "source"
CE_EVENT_NAME = __prefix + "eventname"
CE_SUBPROTOCOL = __prefix + "subprotocol"
CE_USER_ID = __prefix + "userId"
CE_CONNECTION_STATE = __prefix + "connectionstate"

AWPS_SPEC_VERSION = "awps-specversion"
WEBHOOK_REQUEST_ORIGIN = "webhook-request-origin"

EVENT_USER_MESSAGE = "azure.webpubsub.user.message"
EVENT_SYS_CONNECT = "azure.webpubsub.sys.connect"
EVENT_SYS_CONNECTED = "azure.webpubsub.sys.connected"
EVENT_SYS_DISCONNECTED = "azure.webpubsub.sys.disconnected"

__all__ = [
	"AWPS_SPEC_VERSION",
    "CE_CONNECTION_ID",
    "CE_CONNECTION_STATE",
    "CE_EVENT_NAME",
    "CE_HUB",
    "CE_ID",
    "CE_SIGNATURE",
    "CE_SOURCE",
    "CE_SUBPROTOCOL",
    "CE_TIME",
    "CE_TYPE",
    "CE_USER_ID",
    "EVENT_SYS_CONNECT",
    "EVENT_SYS_CONNECTED",
    "EVENT_SYS_DISCONNECTED",
    "EVENT_USER_MESSAGE",
    "WEBHOOK_REQUEST_ORIGIN",
]
