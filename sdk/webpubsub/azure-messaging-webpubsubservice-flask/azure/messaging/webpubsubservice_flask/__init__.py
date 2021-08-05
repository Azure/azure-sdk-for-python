# pylint: disable=line-too-long
import json
from functools import wraps
from .cloud_events_protocols import ConnectResquest, ConnectedRequest, DisconnectedRequest
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

    def __init__(self, app):
        self._app = app

    def abuse_protection_validation(self, endpoints=None):
        if isinstance(endpoints, str):
            endpoints = [endpoints]

        def abuse_protection_validation_internal(func):
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

                kwargs['response'] = res
                return func(*args, **kwargs)

            return decorator
        return abuse_protection_validation_internal

    def handle_connect(self, func):
        @wraps(func)
        def decorator(*args, **kwargs):
            ce_type = request.headers.get(self.TYPE_HEADER)
            if ce_type is None or ce_type != 'azure.webpubsub.sys.connect':
                return func(*args, **kwargs)

            self._validate_signature()

            kwargs['webpubsub_request'] = ConnectResquest(**request.json)
            return func(*args, **kwargs)

        return decorator

    def handle_connected(self, func):
        @wraps(func)
        def decorator(*args, **kwargs):
            ce_type = request.headers.get(self.TYPE_HEADER)
            if ce_type is None or ce_type != 'azure.webpubsub.sys.connected':
                return func(*args, **kwargs)

            self._validate_signature()

            context = self._load_connection_context()
            kwargs['webpubsub_request'] = ConnectedRequest(**{'context': context})
            return func(*args, **kwargs)

        return decorator

    def handle_disconnected(self, func):
        @wraps(func)
        def decorator(*args, **kwargs):
            ce_type = request.headers.get(self.TYPE_HEADER)
            if ce_type is None or ce_type != 'azure.webpubsub.sys.disconnected':
                return func(*args, **kwargs)

            self._validate_signature()

            context = self._load_connection_context()
            kwargs['webpubsub_request'] = DisconnectedRequest(**{'context': context, 'reason': request.json.get('reason')})
            return func(*args, **kwargs)

        return decorator

    def _validate_signature(self):
        pass

    def _load_connection_context(self):
        context = {'hub': request.headers.get(self.HUB_HEADER)}
        context['connection_id'] =request.headers.get(self.CONNECTION_ID_HEADER)
        context['event_name']=request.headers.get(self.EVENT_NAME_HEADER)
        context['origin']=request.headers.get(self.ORIGIN_HEADER)
        context['user_id']=request.headers.get(self.USER_ID_HEADER)
        context['subprotocol']=request.headers.get(self.SUBPROTOCOL_HEADER)
        return context
