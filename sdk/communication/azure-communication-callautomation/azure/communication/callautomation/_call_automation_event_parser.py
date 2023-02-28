# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import cast
import json
from ._events_mapping import (
    get_mapping
)

class CallAutomationEventParser(object):
    def __init__(
        self
    ): # type: (...) -> None
        pass

    @classmethod
    def parse(cls, input):
        parsed = cls._convert_to_nonarray_json(input)
        event_data = parsed['data']
        event_type = parsed['type']
        event_mapping = get_mapping()

        if event_type in event_mapping:
            event_class = event_mapping[event_type]
            return cast(event_class, event_class.deserialize(event_data))
        else:
            raise ValueError('Unknown event type:', event_type)

    def _convert_to_nonarray_json(json_str):
        json_obj = json.loads(json_str)
        if isinstance(json_obj, list):
            # If JSON object is an array, extract the first element
            json_obj = json_obj[0]
        return json_obj