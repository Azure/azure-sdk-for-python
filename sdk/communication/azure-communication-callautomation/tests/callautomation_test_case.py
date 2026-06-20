# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
import threading
import time
import os
import inspect
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import requests
from azure.servicebus import ServiceBusClient
from azure.identity import AzureCliCredential
from devtools_testutils import AzureRecordedTestCase, is_live
from devtools_testutils.helpers import get_test_id

from azure.communication.callautomation import (
    CommunicationIdentifierKind,
    CallAutomationClient,
    CallConnectionClient,
    CommunicationIdentifier,
)
from azure.communication.callautomation._shared.models import identifier_from_raw_id
from azure.communication.identity import CommunicationIdentityClient
from azure.communication.phonenumbers import PhoneNumbersClient


class CallAutomationRecordedTestCase(AzureRecordedTestCase):
    @classmethod
    def setup_class(cls):
        if is_live():
            print("Live Test")
            cls.connection_str = os.environ.get("COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING")
            cls.servicebus_str = os.environ.get("SERVICEBUS_STRING")
            cls.dispatcher_endpoint = os.environ.get("DISPATCHER_ENDPOINT")
            cls.file_source_url = os.environ.get("FILE_SOURCE_URL")
            cls.cognitive_service_endpoint = os.environ.get("COGNITIVE_SERVICE_ENDPOINT")
            cls.transport_url = os.environ.get("TRANSPORT_URL")
        else:
            print("Recorded Test")
            cls.connection_str = "endpoint=https://someEndpoint/;accesskey=someAccessKeyw=="
            cls.servicebus_str = "redacted.servicebus.windows.net"
            cls.dispatcher_endpoint = "https://REDACTED.azurewebsites.net"
            cls.file_source_url = "https://REDACTED/prompt.wav"
            cls.cognitive_service_endpoint = "https://sanitized/"
            cls.transport_url = "wss://sanitized/ws"

        cls.credential = AzureCliCredential()
        cls.dispatcher_callback = cls.dispatcher_endpoint + "/api/servicebuscallback/events"
        cls.identity_client = CommunicationIdentityClient.from_connection_string(cls.connection_str)
        cls.phonenumber_client = PhoneNumbersClient.from_connection_string(cls.connection_str)
        cls.service_bus_client = ServiceBusClient(
            fully_qualified_namespace=cls.servicebus_str, credential=cls.credential
        )

        cls.wait_for_event_flags = []
        cls.event_store: Dict[str, Dict[str, Any]] = {}
        cls.event_to_save: Dict[str, Dict[str, Any]] = {}
        cls.open_call_connections: Dict[str, CallConnectionClient] = {}

    @classmethod
    def teardown_class(cls):
        cls.wait_for_event_flags.clear()
        for cc in cls.open_call_connections.values():
            cc.hang_up(is_for_everyone=True)

    def setup_method(self, method):
        self.test_name = get_test_id().split("/")[-1]
        self.event_store: Dict[str, Dict[str, Any]] = {}
        self.event_to_save: Dict[str, Dict[str, Any]] = {}
        self._prepare_events_recording()
        pass

    def teardown_method(self, method):
        self._record_method_events()
        self.event_store: Dict[str, Dict[str, Any]] = {}
        self.event_to_save: Dict[str, Dict[str, Any]] = {}
        pass

    @staticmethod
    def _format_string(s) -> str:
        s1 = f"{s[:12]}-{s[12:16]}-{s[16:20]}-{s[20:24]}-{s[24:36]}"
        s2 = f"{s[36:44]}-{s[44:48]}-{s[48:52]}-{s[52:56]}-{s[56:]}"
        return f"{s1}_{s2}"

    @staticmethod
    def _parse_ids_from_identifier(identifier: CommunicationIdentifier) -> str:
        if identifier is None:
            raise ValueError("Identifier cannot be None")
        elif identifier.kind == CommunicationIdentifierKind.COMMUNICATION_USER:
            return CallAutomationRecordedTestCase._format_string("".join(filter(str.isalnum, identifier.raw_id)))
        elif identifier.kind == CommunicationIdentifierKind.PHONE_NUMBER:
            return identifier.raw_id
        else:
            raise ValueError("Identifier type not supported")

    @staticmethod
    def _event_key_gen(event_type: str) -> str:
        return event_type

    @staticmethod
    def _unique_key_gen(
        caller_identifier: CommunicationIdentifier, receiver_identifier: CommunicationIdentifier
    ) -> str:
        return CallAutomationRecordedTestCase._parse_ids_from_identifier(
            caller_identifier
        ) + CallAutomationRecordedTestCase._parse_ids_from_identifier(receiver_identifier)

    def _get_test_event_file_name(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(script_dir, "events", f"{self.test_name}.event.json")
        return file_path

    def _message_awaiter(self, unique_id) -> None:
        service_bus_receiver = self.service_bus_client.get_queue_receiver(queue_name=unique_id)
        while unique_id in self.wait_for_event_flags:
            received_messages = service_bus_receiver.receive_messages(max_wait_time=20)
            for msg in received_messages:
                body_bytes = b"".join(msg.body)
                body_str = body_bytes.decode("utf-8")
                mapper = json.loads(body_str)
                if "incomingCallContext" in mapper:
                    caller = identifier_from_raw_id(mapper["from"]["rawId"])
                    receiver = identifier_from_raw_id(mapper["to"]["rawId"])
                    unique_id = self._unique_key_gen(caller, receiver)
                    key = self._event_key_gen("IncomingCall")
                    print("EventRegistration(IncomingCall):" + key)
                    self.event_store[key] = mapper
                    self.event_to_save[key] = mapper
                else:
                    if isinstance(mapper, list):
                        mapper = mapper[0]
                    if mapper["type"]:
                        key = self._event_key_gen(mapper["type"].split(".")[-1])
                        print("EventRegistration:" + key)
                        self.event_store[key] = mapper
                        self.event_to_save[key] = mapper
                service_bus_receiver.complete_message(msg)
            time.sleep(1)
        return

    def _prepare_events_recording(self) -> None:
        # only load during playback
        if not is_live():
            file_path = self._get_test_event_file_name()
            try:
                with open(file_path, "r") as json_file:
                    self.event_store = json.load(json_file)
            except IOError as e:
                raise SystemExit(f"File write operation failed: {e}")

    def _record_method_events(self) -> None:
        # only save during live
        if is_live():
            file_path = self._get_test_event_file_name()
            try:
                keys_to_redact = ["incomingCallContext", "callerDisplayName"]
                redacted_dict = self.redact_by_key(self.event_to_save, keys_to_redact)
                with open(file_path, "w") as json_file:
                    json.dump(redacted_dict, json_file)
            except IOError as e:
                raise SystemExit(f"File write operation failed: {e}")

    def check_for_event(self, event_type: str, call_connection_id: str, wait_time: timedelta) -> Any:
        key = self._event_key_gen(event_type)
        time_out_time = datetime.now() + wait_time
        while datetime.now() < time_out_time:
            popped_event = self.event_store.pop(key, None)
            if popped_event is not None:
                print(f"Matching Event Found [{key}]")
                return popped_event
            time.sleep(1)
        return None

    def establish_callconnection_voip(
        self, caller, target, *, cognitive_service_enabled: Optional[bool] = False
    ) -> tuple:
        return self._establish_callconnection(caller, target, cognitive_service_enabled=cognitive_service_enabled)

    def establish_callconnection_pstn(self, caller, target) -> tuple:
        return self._establish_callconnection(caller, target, is_pstn=True)

    def establish_callconnection_voip_with_streaming_options(self, caller, target, options, is_transcription) -> tuple:
        return self._establish_callconnection(caller, target, options=options, is_transcription=is_transcription)

    def establish_callconnection_voip_connect_call(self, caller, target) -> tuple:
        return self._establish_callconnection(caller, target, connect_call=True)

    def _establish_callconnection(
        self,
        caller,
        target,
        cognitive_service_enabled: Optional[bool] = False,
        is_pstn: bool = False,
        options=None,
        is_transcription: bool = False,
        connect_call: bool = False,
    ) -> tuple:
        call_automation_client_caller = self._create_call_automation_client(caller)
        call_automation_client_target = self._create_call_automation_client(target)

        unique_id = self._unique_key_gen(caller, target)
        if is_live():
            self._subscribe_to_dispatcher(unique_id)

        callback_url = f"{self.dispatcher_callback}?q={unique_id}"
        create_call_result = self._create_call(
            call_automation_client_caller,
            caller,
            target,
            unique_id,
            cognitive_service_enabled,
            is_pstn,
            options,
            is_transcription,
        )
        caller_connection_id = self._validate_create_call_result(create_call_result)

        incoming_call_context = self._wait_for_incoming_call(unique_id)
        answer_call_result = self._answer_call(call_automation_client_target, incoming_call_context)

        call_connection_caller = self._create_call_connection_client(caller_connection_id)
        call_connection_target = self._create_call_connection_client(answer_call_result.call_connection_id)
        self.open_call_connections[unique_id] = call_connection_caller

        if connect_call:
            return (
                unique_id,
                call_connection_caller,
                call_connection_target,
                call_automation_client_caller,
                callback_url,
            )

        return unique_id, call_connection_caller, call_connection_target

    def _create_call_automation_client(self, source):
        return CallAutomationClient.from_connection_string(self.connection_str, source=source)

    def _subscribe_to_dispatcher(self, unique_id):
        dispatcher_url = f"{self.dispatcher_endpoint}/api/servicebuscallback/subscribe?q={unique_id}"
        response = requests.post(dispatcher_url)

        if response is None:
            raise ValueError("Response cannot be None")

        print(f"Subscription to dispatcher of {unique_id}: {response.status_code}")

        self.wait_for_event_flags.append(unique_id)
        thread = threading.Thread(target=self._message_awaiter, args=(unique_id,))
        thread.start()

    def _create_call(
        self, client, caller, target, unique_id, cognitive_service_enabled, is_pstn, options, is_transcription
    ):
        if is_pstn:
            return client.create_call(
                target_participant=target,
                source_caller_id_number=caller,
                callback_url=f"{self.dispatcher_callback}?q={unique_id}",
            )
        elif options:
            return client.create_call(
                target_participant=target,
                callback_url=f"{self.dispatcher_callback}?q={unique_id}",
                media_streaming=options if not is_transcription else None,
                transcription=options if is_transcription else None,
                cognitive_services_endpoint=self.cognitive_service_endpoint if is_transcription else None,
            )
        else:
            return client.create_call(
                target_participant=target,
                callback_url=f"{self.dispatcher_callback}?q={unique_id}",
                cognitive_services_endpoint=self.cognitive_service_endpoint if cognitive_service_enabled else None,
            )

    def _validate_create_call_result(self, result):
        if result is None:
            raise ValueError("Invalid create_call_result")

        caller_connection_id = result.call_connection_id
        if caller_connection_id is None:
            raise ValueError("Caller connection ID is None")

        return caller_connection_id

    def _wait_for_incoming_call(self, unique_id):
        incoming_call_event = self.check_for_event("IncomingCall", unique_id, timedelta(seconds=30))
        if incoming_call_event is None:
            raise ValueError("incoming_call_event is None")
        return incoming_call_event["incomingCallContext"]

    def _answer_call(self, client, context):
        result = client.answer_call(incoming_call_context=context, callback_url=self.dispatcher_callback)
        if result is None:
            raise ValueError("Invalid answer_call result")
        return result

    def _create_call_connection_client(self, connection_id):
        return CallConnectionClient.from_connection_string(self.connection_str, connection_id)

    def terminate_call(self, unique_id) -> None:
        try:
            call_connection = self.open_call_connections.pop(unique_id, None)
            if call_connection is not None:
                call_connection.hang_up(is_for_everyone=True)
                disconnected_event = self.check_for_event(
                    "CallDisconnected", call_connection._call_connection_id, timedelta(seconds=15)
                )
                if disconnected_event is None:
                    raise ValueError("Receiver CallDisconnected event is None")
        finally:
            while unique_id in self.wait_for_event_flags:
                self.wait_for_event_flags.remove(unique_id)
            pass

    def redact_by_key(self, data: Dict[str, Dict[str, any]], keys_to_redact: List[str]) -> Dict[str, Dict[str, any]]:
        for _, inner_dict in data.items():
            for key in keys_to_redact:
                if key in inner_dict:
                    inner_dict[key] = "REDACTED"
        return data
