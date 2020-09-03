import json
import logging
import sys

import azure.functions as func
from azure.eventgrid import EventGridConsumer

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
    consumer = EventGridConsumer()
    deserialized_event = consumer.deserialize_events(result)
    ## can only be EventGridEvent
    print("model: {}".format(event.model))
