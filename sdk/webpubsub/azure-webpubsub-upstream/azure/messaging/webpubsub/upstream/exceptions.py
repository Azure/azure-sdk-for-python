# coding=utf-8
# --------------------------------------------------------------------------
# Created on Sun Sep 26 2021
#
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root
# for license information.
# --------------------------------------------------------------------------

# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

__all__ = [
    "BaseError",
    "ContextBasedError",
    "HandlerNotFoundError",
    "HeaderNotFoundError",
    "InvalidConnectRequestError",
    "InvalidEventNameError",
    "InvalidEventTypeError",
]

from http import HTTPStatus

from typing import Any


class BaseError(Exception):

    @property
    def status(self):
        return HTTPStatus.BAD_REQUEST


class ContextBasedError(BaseError):

    @property
    def context(self):
        return self._context

    def __init__(self, context, message=""):
        # type: (ContextBasedError, Any, str) -> None
        self._context = context
        super().__init__(message)


class InvalidEventTypeError(ContextBasedError):

    @property
    def event_type(self):
        return self.context.event_type

    def __init__(self, context):
        # type: (InvalidEventTypeError, Any) -> None
        self._context = context
        super().__init__(context)


class InvalidEventNameError(ContextBasedError):

    @property
    def event_name(self):
        return self.context.event_name

    def __init__(self, context):
        # type: (InvalidEventNameError, Any) -> None
        super().__init__(context)


class InvalidConnectRequestError(ContextBasedError):

    def __init__(self, context):
        # type: (InvalidConnectRequestError, Any) -> None
        super().__init__(context, "connect event request body must be a json.")


class ValidationFailedError(ContextBasedError):

    @property
    def status(self):
        return HTTPStatus.UNAUTHORIZED


class HeaderNotFoundError(BaseError):

    @property
    def status(self):
        return HTTPStatus.BAD_REQUEST

    @property
    def key(self):
        return self._key

    def __init__(self, key):
        # type: (HeaderNotFoundError, str) -> None
        self._key = key
        super().__init__()


class HandlerNotFoundError(BaseError):

    @property
    def handler_name(self):
        return "handle_connect"

    def __init__(self):
        # type: (HandlerNotFoundError) -> None
        super().__init__(
            "`{self.handler_name}` is required while using Azure Web PubSub")
