import os
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Type

import requests
from azure.communication.callautomation import CallAutomationEventParser
from azure.servicebus import ServiceBusClient

from _shared.asynctestcase import AsyncCommunicationTestCase


class CallAutomationAutomatedLiveTestBase(AsyncCommunicationTestCase):
    def __init__(self, method_name, *args, **kwargs):
        self.servicebus_connection_str = os.environ.get('SERVICEBUS_STRING', 'Endpoint=sb://REDACTED.servicebus.windows.net/;SharedAccessKeyName=REDACTED;SharedAccessKey=REDACTED')
        self.dispatcher_endpoint = 'https://REDACTED.azurewebsites.net'
        self.dispatcher_callback = self.dispatcher_endpoint + '/api/servicebuscallback/events'
        self.processor_store: Dict[str, Any] = {}
        self.incoming_call_context_store: Dict[str, Any] = {}
        self.event_store: Dict[str, Dict[str, Any]] = {}
        super(CallAutomationAutomatedLiveTestBase, self).__init__(method_name, *args, **kwargs)
    
    def _format_string(self, s) -> str:
        s1 = f"{s[:12]}-{s[12:16]}-{s[16:20]}-{s[20:24]}-{s[24:36]}"
        s2 = f"{s[36:44]}-{s[44:48]}-{s[48:52]}-{s[52:56]}-{s[56:]}"
        return f"{s1}_{s2}"
    
    def _parse_ids_from_identifier(self, identifier: str) -> str:
        if identifier is None:
            raise ValueError("Identifier cannot be None")
        return self._format_string(''.join(filter(str.isalnum, identifier)))
    
    def _message_handler(self, message: Any) -> None:
        body = message.body
        body_bytes = b''.join(body)
        body_str = body_bytes.decode('utf-8')

        if not body:
            raise ValueError("Body cannot be empty")

        mapper = json.loads(body_str)
        
        if "incomingCallContext" in mapper:
            incoming_call_context = mapper["incomingCallContext"]
            from_id = mapper["from"]["rawId"]
            to_id = mapper["to"]["rawId"]
            unique_id = self._parse_ids_from_identifier(from_id) + self._parse_ids_from_identifier(to_id)
            self.incoming_call_context_store[unique_id] = incoming_call_context
        else:
            event = CallAutomationEventParser.parse(body_str)

            if event is None:
                raise ValueError("Event cannot be null")

            call_connection_id = event.call_connection_id
            
            if call_connection_id not in self.event_store:
                self.event_store[call_connection_id] = {}

            self.event_store[call_connection_id][type(event)] = event
    
    def service_bus_with_new_call(self, caller, receiver) -> str:
        """Create new ServiceBus client.
        Creates a new queue in the ServiceBus and a client in order to interact with it.

        :param caller: User initiating the call.
        :type caller: CommunicationUserIdentifier
        :param receiver: User receiving the call.
        :type receiver: CommunicationUserIdentifier

        :return: a unique_id that can be used to identify the ServiceBus queue.
        :rtype: str
        """
        unique_id = self._parse_ids_from_identifier(caller.raw_id) + self._parse_ids_from_identifier(receiver.raw_id)
        dispatcher_url = f"{self.dispatcher_endpoint}/api/servicebuscallback/subscribe?q={unique_id}"
        response = requests.post(dispatcher_url)

        if response is None:
            raise ValueError("Response cannot be None")

        print(f"Subscription to dispatcher of {unique_id}: {response.status_code}")
        service_bus_client = ServiceBusClient.from_connection_string(self.servicebus_connection_str)
        self.processor_store[unique_id] = service_bus_client
        return unique_id
    
    def wait_for_messages(self, unique_id, time_out) -> None:
        """Create new ServiceBus client.
        Checks the Service Bus queue specified by the unique_id for messages and stores them in the event_store.

        :param unique_id: Identifier used to keep track of ServiceBus message queue.
        :type unique_id: str
        :param time_out: How long to wait for a response.
        :type time_out: timedelta

        :return: None
        :rtype: None
        """
        service_bus_receiver = self.processor_store[unique_id].get_queue_receiver(queue_name=unique_id)
        time_out_time = datetime.now() + time_out
        while datetime.now() < time_out_time:
            received_messages = service_bus_receiver.receive_messages(max_wait_time=5)
            for msg in received_messages:
                self._message_handler(msg)
                service_bus_receiver.complete_message(msg)
            if not received_messages:
                time.sleep(1)

    def check_for_event(self, event_type: Type, call_connection_id: str) -> Optional[Any]:
        """Check for events.
        Checks the event_store for any events that have been recieved from the Service Bus queue with the specified event_type and call_connection_id.

        :param event_type: Type of event to check for in the event store.
        :type event_type: Type
        :param call_connection_id: The call_connection_id for which to find events for.
        :type call_connection_id: str

        :return: None if no events are found. The event object if an event is found.
        :rtype: Optional[Any]
        """
        if call_connection_id in self.event_store:
            return self.event_store[call_connection_id].get(event_type)
        return None

    def cleanup(self) -> None:
        for _, receiver in self.processor_store.items():
            receiver.close()