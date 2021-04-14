import json
import logging
import sys

import azure.functions as func
from azure.eventgrid import EventGridEvent

def main(event: func.EventGridEvent):
    logging.info(sys.version)
    logging.info(event)
    result = json.dumps({
        'id': event.id,
        'data': event.get_json(),
        'topic': event.topic,
        'subject': event.subject,
        'event_type': event.event_type
    })
    logging.info(result)
    deserialized_event = EventGridEvent.from_dict(json.loads(result))
    ## can only be EventGridEvent
    print("event: {}".format(event))
