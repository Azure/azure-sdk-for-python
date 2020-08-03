import json
import logging
import sys

import azure.functions as func
from azure.eventgrid._consumer import EventGridConsumer

def main(event: func.EventGridEvent):
    logging.info(sys.version)
    result = json.dumps({
        'id': event.id,
        'data': event.get_json(),
        'topic': event.topic,
        'subject': event.subject,
        'event_type': event.event_type,
    })

