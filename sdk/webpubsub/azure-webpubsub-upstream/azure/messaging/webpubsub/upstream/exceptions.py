# coding=utf-8
# --------------------------------------------------------------------------
# Created on Sun Sep 26 2021
#
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root
# for license information.
# --------------------------------------------------------------------------

__all__ = [
    "BaseError",
    "ContextBasedError",
    "InvalidEventTypeError",
    "InvalidEventNameError",
    "InvalidRequestError",
    "HandlerNotFoundError",
]

from http import HTTPStatus


class BaseError(Exception):
    pass


class ContextBasedError(BaseError):

    @property
    def status_code(self):
        return int(HTTPStatus.BAD_REQUEST)

    @property
    def context(self):
        return self._context

    def __init__(self, context):
        self._context = context
        super().__init__()


class InvalidEventTypeError(ContextBasedError):

    @property
    def event_type(self):
        return self.context.event_type

    def __init__(self, context):
        self._context = context
        super().__init__(context)


class InvalidEventNameError(ContextBasedError):

    @property
    def event_name(self):
        return self.context.event_name

    def __init__(self, context):
        super().__init__(context)


class ValidationFailedError(ContextBasedError):

    @property
    def status_code(self):
        return int(HTTPStatus.UNAUTHORIZED)


class HeaderNotFoundError(ContextBasedError):

    @property
    def key(self):
        return self._key

    def __init__(self, context, key):
        self._key = key
        super().__init__(context)


class HandlerNotFoundError(BaseError):

    @property
    def handler_name(self):
        return "handle_connect"

    def __init__(self):
        super().__init__("{}` is required while using Azure Web PubSub".format(self.handler_name))
