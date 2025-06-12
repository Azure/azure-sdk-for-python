import asyncio
import time
import os
from datetime import timedelta
from typing import Dict, Any
from azure.communication.callautomation.aio import (
    CallAutomationClient as AsyncCallAutomationClient,
    CallConnectionClient as AsyncCallConnectionClient,
)
from azure.communication.callautomation._shared.models import CommunicationUserIdentifier, identifier_from_raw_id
from azure.communication.callautomation._models import ChannelAffinity
from azure.communication.identity import CommunicationIdentityClient
from azure.identity import AzureCliCredential
from azure.communication.phonenumbers.aio import PhoneNumbersClient
from azure.servicebus.aio import ServiceBusClient


class AsyncCallAutomationRecordedTestCase:
    @classmethod
    async def async_setup_class(cls):
        cls.connection_str = os.environ.get('COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING', "endpoint=https://someEndpoint/;accesskey=someAccessKeyw==")
        cls.identity_client = CommunicationIdentityClient.from_connection_string(cls.connection_str)
        cls.event_store: Dict[str, Dict[str, Any]] = {}
        cls.open_call_connections: Dict[str, AsyncCallConnectionClient] = {}
        cls.servicebus_str = os.environ.get('SERVICEBUS_STRING', "redacted.servicebus.windows.net")
        cls.dispatcher_endpoint = os.environ.get('DISPATCHER_ENDPOINT', "https://REDACTED.azurewebsites.net")
        cls.file_source_url = os.environ.get('FILE_SOURCE_URL', "https://REDACTED/prompt.wav")
        cls.cognitive_service_endpoint = os.environ.get('COGNITIVE_SERVICE_ENDPOINT', "https://sanitized/")
        cls.transport_url = os.environ.get('TRANSPORT_URL', "wss://sanitized/ws")
        cls.credential = AzureCliCredential()
        cls.dispatcher_callback = cls.dispatcher_endpoint + "/api/servicebuscallback/events"
        cls.phonenumber_client = PhoneNumbersClient.from_connection_string(cls.connection_str)
        cls.service_bus_client = ServiceBusClient(
            fully_qualified_namespace=cls.servicebus_str,
            credential=cls.credential)

        cls.wait_for_event_flags = []
        cls.event_to_save: Dict[str, Dict[str, Any]] = {}

    @classmethod
    async def async_teardown_class(cls):
        for cc in cls.open_call_connections.values():
            await cc.hang_up(is_for_everyone=True)

    async def async_setup_method(self, method):
        self.event_store: Dict[str, Dict[str, Any]] = {}

    async def async_teardown_method(self, method):
        self.event_store: Dict[str, Dict[str, Any]] = {}

    async def check_for_event(self, event_type: str, call_connection_id: str, wait_time: timedelta) -> Any:
        # Dummy async event checker for demonstration
        timeout = time.time() + wait_time.total_seconds()
        while time.time() < timeout:
            event = self.event_store.pop(event_type, None)
            if event:
                return event
            await asyncio.sleep(1)
        return None

    async def establish_callconnection_voip_async(self, caller, target) -> tuple:
        # Create async call automation client for the caller
        client = AsyncCallAutomationClient.from_connection_string(self.connection_str, source=caller)

        # Generate a unique_id for the call (mimic sync logic if needed)
        unique_id = f"{caller.raw_id}_{target.raw_id}"

        # Use a callback URL 
        callback_url = f"{self.dispatcher_callback}?q={unique_id}"

        # Create the call asynchronously
        create_call_result = await client.create_call(target_participant=target, callback_url=callback_url)

        # Create async call connection client
        call_connection = AsyncCallConnectionClient.from_connection_string(self.connection_str, create_call_result.call_connection_id)

        # Store the connection for later cleanup
        self.open_call_connections[unique_id] = call_connection

        # Return unique_id (for event correlation), call_connection, and None for compatibility
        return unique_id, call_connection, None

    async def terminate_call(self, call_connection_id) -> None:
        call_connection = self.open_call_connections.pop(call_connection_id, None)
        if call_connection:
            await call_connection.hang_up(is_for_everyone=True)
    
    async def establish_callconnection_voip_connect_call_async(self, caller, target):
        """
        Async version of establish_callconnection_voip_connect_call.
        Returns: unique_id, call_connection, _, call_automation_client, callback_url
        """
        # Create async call automation client for the caller
        call_automation_client = AsyncCallAutomationClient.from_connection_string(self.connection_str, source=caller)

        # Generate a unique_id for the call
        unique_id = f"{caller.raw_id}_{target.raw_id}"

        # Use a callback URL
        callback_url = f"{self.dispatcher_callback}?q={unique_id}"

        # Create the call asynchronously
        create_call_result = await call_automation_client.create_call(target_participant=target, callback_url=callback_url)

        # Create async call connection client
        call_connection = AsyncCallConnectionClient.from_connection_string(self.connection_str, create_call_result.call_connection_id)

        # Store the connection for later cleanup
        self.open_call_connections[unique_id] = call_connection

        # Return all needed values for the test
        return unique_id, call_connection, None, call_automation_client, callback_url

    # If get_call_properties is not async, wrap it
    async def get_call_properties_async(self, call_connection):
        # If get_call_properties is async, just await it
        if hasattr(call_connection, "get_call_properties") and asyncio.iscoroutinefunction(call_connection.get_call_properties):
            return await call_connection.get_call_properties()
        # Otherwise, run in thread
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, call_connection.get_call_properties)

    # If connect_call is not async, wrap it
    async def connect_call_async(self, call_automation_client, server_call_id, callback_url):
        if hasattr(call_automation_client, "connect_call") and asyncio.iscoroutinefunction(call_automation_client.connect_call):
            return await call_automation_client.connect_call(server_call_id=server_call_id, callback_url=callback_url)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, call_automation_client.connect_call, server_call_id, callback_url)

    async def establish_callconnection_voip_answercall_withcustomcontext_async(self, caller, target):
        """
        Async version of establish_callconnection_voip_answercall_withcustomcontext.
        Returns: unique_id, call_connection, None
        """
        # Create async call automation client for the caller
        client = AsyncCallAutomationClient.from_connection_string(self.connection_str, source=caller)

        # Generate a unique_id for the call
        unique_id = f"{caller.raw_id}_{target.raw_id}"

        # Use a callback URL
        callback_url = f"{self.dispatcher_callback}?q={unique_id}"

        # Here you would add any custom context logic if needed
        # For demonstration, we'll assume a custom context parameter is passed
        custom_context = {"key": "value"}  # Replace with actual context if needed

        # Create the call asynchronously with custom context
        create_call_result = await client.create_call(
            target_participant=target,
            callback_url=callback_url,
            custom_context=custom_context
        )

        # Create async call connection client
        call_connection = AsyncCallConnectionClient.from_connection_string(
            self.connection_str, create_call_result.call_connection_id
        )

        # Store the connection for later cleanup
        self.open_call_connections[unique_id] = call_connection

        # Return unique_id, call_connection, and None for compatibility
        return unique_id, call_connection, None

    async def start_recording_with_call_connection_id_async(self, call_automation_client, call_connection_id, callback_url, target_participant_id="testId"):
        target_participant = CommunicationUserIdentifier(target_participant_id)
        channel_affinity = ChannelAffinity(target_participant=target_participant, channel=0)
        # If start_recording is async, await it; otherwise, run in executor
        if hasattr(call_automation_client, "start_recording") and asyncio.iscoroutinefunction(call_automation_client.start_recording):
            return await call_automation_client.start_recording(
                call_connection_id=call_connection_id,
                recording_state_callback_url=callback_url,
                channel_affinity=[channel_affinity]
            )
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            call_automation_client.start_recording,
            call_connection_id,
            callback_url,
            [channel_affinity]
        )

    async def stop_recording_async(self, call_automation_client, recording_id):
        if hasattr(call_automation_client, "stop_recording") and asyncio.iscoroutinefunction(call_automation_client.stop_recording):
            return await call_automation_client.stop_recording(recording_id=recording_id)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, call_automation_client.stop_recording, recording_id)

    async def start_recording_with_server_call_id_async(self, call_automation_client, server_call_id, callback_url, target_participant_id="testId"):
        target_participant = CommunicationUserIdentifier(target_participant_id)
        channel_affinity = ChannelAffinity(target_participant=target_participant, channel=0)
        # If start_recording is async, await it; otherwise, run in executor
        if hasattr(call_automation_client, "start_recording") and asyncio.iscoroutinefunction(call_automation_client.start_recording):
            return await call_automation_client.start_recording(
                server_call_id=server_call_id,
                recording_state_callback_url=callback_url,
                channel_affinity=[channel_affinity]
            )
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            call_automation_client.start_recording,
            server_call_id,
            callback_url,
            [channel_affinity]
        )
