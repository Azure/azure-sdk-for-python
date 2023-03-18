# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import json
from azure.communication.callautomation._generated._serialization import Deserializer
from azure.communication.callautomation._generated import models as _models
from ._events_mapping import get_mapping

class CallAutomationEventParser(object):

    _client_models = {k: v for k, v in _models.__dict__.items() if isinstance(v, type)}
    _deserializer = Deserializer(_client_models)

    def __init__(
        self
    ):
        pass

    @classmethod
    def parse(cls, parse_string):

        parsed = json.loads(parse_string)
        if isinstance(parsed, list):
            # If JSON object is an array, extract the first element
            parsed = parsed[0]

        event_type = ""
        if parsed['type']:
            event_type = parsed['type'].split(".")[-1]

        event_mapping = get_mapping()

        if event_type in event_mapping:
            event_data = parsed['data']
            event_class = event_mapping[event_type]

            # deserialize event
            deserialized = cls._deserializer(event_type, event_data)

            # create public event class with given AutoRest deserialized event
            return event_class(deserialized)

        raise ValueError('Unknown event type:', event_type)
