# pylint: disable=line-too-long
import json
from functools import wraps
from .cloud_events_protocols import ConnectResponse, ConnectResquest, ConnectionContext, DisconnectedRequest
from flask import request, make_response, session, g, Response, current_app

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

    def handle_abuse_protection_validation(self, endpoints=None):
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
    if connect_response:
        return make_response(connect_response, 200)
    return make_response('', 204)

def make_connect_error_response(error, status: int):
    return make_response(error, status)

def get_connect_request():
    return ConnectResquest(**request.json)

def get_disconnected_request():
    return DisconnectedRequest(**request.json)

def is_user_event(connection_context: ConnectionContext):
    return connection_context.type.startswith('azure.webpubsub.user.')