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
CE_CONNECTION_ID = __prefix + "connectionId"
CE_ID = __prefix + "id"
CE_TIME = __prefix + "time"
CE_SPEC_VERSION = __prefix + "specversion"
CE_TYPE = __prefix + "type"
CE_SOURCE = __prefix + "source"
CE_EVENT_NAME = __prefix + "eventName"
CE_SUBPROTOCOL = __prefix + "subprotocol"
CE_USER_ID = __prefix + "userId"
CE_CONNECTION_STATE = __prefix + "connectionState"

WEBHOOK_REQUEST_ORIGIN = "WebHook-Request-Origin"

EVENT_USER_MESSAGE = "azure.webpubsub.user.message"
EVENT_SYS_CONNECT = "azure.webpubsub.sys.connect"
EVENT_SYS_CONNECTED = "azure.webpubsub.sys.connected"
EVENT_SYS_DISCONNECTED = "azure.webpubsub.sys.disconnected"

__all__ = [
	"CE_SIGNATURE",
	"CE_HUB",
	"CE_CONNECTION_ID",
	"CE_ID",
	"CE_TIME",
	"CE_SPEC_VERSION",
	"CE_TYPE",
	"CE_SOURCE",
	"CE_EVENT_NAME",
	"CE_SUBPROTOCOL",
	"CE_USER_ID",
	"CE_CONNECTION_STATE",
	"WEBHOOK_REQUEST_ORIGIN",
    "EVENT_USER_MESSAGE",
    "EVENT_SYS_CONNECT",
    "EVENT_SYS_CONNECTED",
    "EVENT_SYS_DISCONNECTED",
]