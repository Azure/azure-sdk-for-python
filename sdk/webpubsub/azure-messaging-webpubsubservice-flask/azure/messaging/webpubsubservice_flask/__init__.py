# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------

# pylint: disable=line-too-long
from functools import wraps
from flask import request, make_response
from .cloud_events_protocols import ConnectResponse, ConnectResquest, ConnectionContext, DisconnectedRequest

class EventHandler:
    TYPE_HEADER='ce-type'
    SIGNATURE_HEADER='ce-signature'
    HUB_HEADER='ce-hub'
    CONNECTION_ID_HEADER='ce-connectionId'
    EVENT_NAME_HEADER='ce-eventName'
    SUBPROTOCOL_HEADER='ce-subprotocol'
    ORIGIN_HEADER='WebHook-Request-Origin'
    USER_ID_HEADER='ce-userId'

    SUPPORTED_TYPE=['azure.webpubsub.sys.connect', 'azure.webpubsub.sys.connected', 'azure.webpubsub.sys.disconnected', 'azure.webpubsub.user.message']

    def __init__(self, app):
        self._app = app

    def handle_abuse_protection_validation(self, endpoints='*'):
        """Decorator to add function a functionality to handle abuse protection validation

        :param endpoints: allowed origin list, use '*' to allow all. defaults to None
        :type endpoints: ~str | list[str], optional
        :return: A decorator
        :rtype: ~types.Function
        """
        if isinstance(endpoints, str):
            endpoints = [endpoints]

        def handle_abuse_protection_validation_internal(func):
            @wraps(func)
            def decorator(*args, **kwargs):
                origin = request.headers.get('WebHook-Request-Origin')
                if request.method != 'OPTIONS' or origin is None:
                    return func(*args, **kwargs)

                res = make_response()
                if origin in endpoints or '*' in endpoints:
                    res.status_code = 200
                    res.headers.add_header('WebHook-Allowed-Origin', ', '.join(endpoints))
                else:
                    res.status_code = 401

                return res

            return decorator
        return handle_abuse_protection_validation_internal

    def handle_event(self, func):
        """Decorator to add function a functionality to handle events. An argument named 'connection_context' will be generated.

        :param func: decorated function
        :type func: ~types.Function
        :return: function with additional 'connection_context' argument
        :rtype: ~types.Function
        """
        @wraps(func)
        def decorator(*args, **kwargs):
            ce_type = request.headers.get(self.TYPE_HEADER)
            if ce_type is None or ce_type not in self.SUPPORTED_TYPE:
                return func(*args, **kwargs)

            context = self._load_connection_context()
            kwargs['connection_context'] = ConnectionContext(**context)
            return func(*args, **kwargs)

        return decorator

    def _load_connection_context(self):
        context = {'hub': request.headers.get(self.HUB_HEADER)}
        context['connection_id'] = request.headers.get(self.CONNECTION_ID_HEADER)
        context['event_name'] = request.headers.get(self.EVENT_NAME_HEADER)
        context['origin'] = request.headers.get(self.ORIGIN_HEADER)
        context['user_id'] = request.headers.get(self.USER_ID_HEADER)
        context['subprotocol'] = request.headers.get(self.SUBPROTOCOL_HEADER)
        context['type'] = request.headers.get(self.TYPE_HEADER)
        return context

def make_connect_response(connect_response: ConnectResponse = None):
    """Build a connect success response

    :param connect_response: connection response, defaults to None
    :type connect_response: ~ConnectResponse, optional
    :return: return a `~flask.Flask.Response` contains connect success response content.
    :rtype: ~flask.Flask.Response
    """
    if connect_response:
        return make_response(connect_response, 200)
    return make_response('', 204)

def make_connect_error_response(error, status: int):
    """Build an error connect response

    :param error: Error content to return
    :type error: ~Any
    :param status: returned status code
    :type status: int
    :return: return a `~flask.Flask.Response` contains error connect response content.
    :rtype: ~flask.Flask.Response
    """
    return make_response(error, status)

def get_connect_request():
    """Helper method to get `~ConnectRequest` from the current request

    :return: `~ConnectResquest` that contains pre-defined content
    :rtype: ~ConnectResquest
    """
    return ConnectResquest(**request.json)

def get_disconnected_request():
    """Helper method to get `~DisconnectedRequest` from the current request

    :return: `~DisconnectedRequest` that contains pre-defined content
    :rtype: ~DisconnectedRequest
    """
    return DisconnectedRequest(**request.json)

def is_user_event(connection_context: ConnectionContext):
    """Helper method to check whether a request is a user event request

    :param connection_context: `~ConnectionContext` of the request
    :type connection_context: ConnectionContext
    :return: whether it's user event request
    :rtype: ~bool
    """
    return connection_context.type.startswith('azure.webpubsub.user.')
