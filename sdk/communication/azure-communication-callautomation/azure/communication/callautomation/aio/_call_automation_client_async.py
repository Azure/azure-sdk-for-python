# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, List, Union, Optional, TYPE_CHECKING # pylint: disable=unused-import
from urllib.parse import urlparse
from io import BytesIO
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.transport import HttpResponse
from .._version import SDK_MONIKER
from .._api_versions import DEFAULT_VERSION
from ._call_connection_client_async import CallConnectionClient
from .._generated.aio._client import AzureCommunicationCallAutomationService
from .._shared.models import CommunicationIdentifier
from .._communication_identifier_serializer import serialize_phone_identifier, serialize_identifier
from .._shared.utils import get_authentication_policy, parse_connection_str
from .._generated.models import (
    CreateCallRequest,
    AnswerCallRequest,
    RedirectCallRequest,
    RejectCallRequest,
    CustomContext,
    StartCallRecordingRequest
)
from .._models import (
    CallInvite,
    CallConnectionProperties,
    RecordingStateResult,
    ServerCallLocator,
    GroupCallLocator
)
from .._content_downloader import ContentDownloader
from .._utils import (
    _get_repeatability_guid,
    _get_repeatability_timestamp
)

class CallAutomationClient(object):
    """
    A client to interact with the AzureCommunicationService CallAutomation service.

    Call Automation provides developers the ability to build server-based,
    intelligent call workflows, and call recording for voice and PSTN channels.

    :param str endpoint:
        The endpoint of the Azure Communication resource.
    :param Union[AsyncTokenCredential, AzureKeyCredential] credential:
        The access key we use to authenticate against the service.
    :keyword str api_version:
        Azure Communication Call Automation API version.
        Default value is "2023-01-15-preview".
        Note that overriding this default value may result in unsupported behavior.
    :keyword ~azure.communication.callautomation._shared.models.CommunicationUserIdentifier source_identity:
        ACS User Identity to be used when the call is created or answered.
        If not provided, service will generate one.
    """

    def __init__(
            self,
            endpoint: str,
            credential: Union[AsyncTokenCredential, AzureKeyCredential],
            **kwargs
    ) -> None:
        if not credential:
            raise ValueError("credential can not be None")

        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Host URL must be a string")

        parsed_url = urlparse(endpoint.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError(f"Invalid URL: {format(endpoint)}")

        self._endpoint = endpoint
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._credential = credential

        self._client = AzureCommunicationCallAutomationService(
            self._endpoint,
            api_version=self._api_version,
            authentication_policy=get_authentication_policy(
                endpoint, credential,is_async=True),
            sdk_moniker=SDK_MONIKER,
            **kwargs)

        self._call_recording_client = self._client.call_recording
        self._downloader = ContentDownloader(self._call_recording_client)
        self.source_identity = kwargs.pop("source_identity", None)

    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        **kwargs
    ) -> 'CallAutomationClient':
        """
        Create CallAutomation from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :return: Instance of CallAutomationClient.
        :rtype: ~azure.communication.callautomation.CallAutomationClient
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)

    def get_call_connection(
        self,
        call_connection_id: str,
        **kwargs
    ) -> CallConnectionClient:
        """
        Get CallConnectionClient object.
        Interact with ongoing call with CallConnectionClient.

        :param str call_connection_id:
            CallConnectionId of ongoing call.
        :return: Instance of CallConnectionClient.
        :rtype: ~azure.communication.callautomation.CallConnectionClient
        """
        if not call_connection_id:
            raise ValueError("call_connection_id can not be None")

        return CallConnectionClient(
            endpoint=self._endpoint,
            credential=self._credential,
            call_connection_id=call_connection_id,
            **kwargs
        )

    async def create_call(
        self,
        target_participant: CallInvite,
        callback_url: str,
        **kwargs
    ) -> CallConnectionProperties:
        """
        Create a call connection request to a target identity.

        :param ~azure.communication.callautomation.models.CallInvite target_participant:
            Call invitee's information.
        :param str callback_url:
            The call back url where callback events are sent.
        :keyword str operation_context:
            Value that can be used to track the call and its associated events.
        :keyword ~azure.communication.callautomation.models.MediaStreamingConfiguration media_streaming_configuration:
            Media Streaming Configuration.
        :keyword str azure_cognitive_services_endpoint_url:
            The identifier of the Cognitive Service resource assigned to this call.
        :return: CallConnectionProperties of this call.
        :rtype: ~azure.communication.callautomation.models.CallConnectionProperties
        :raises ~azure.core.exceptions.HttpResponseError
        """

        if not target_participant:
            raise ValueError('target_participant cannot be None.')
        if not callback_url:
            raise ValueError('callback_url cannot be None.')

        media_streaming_config = kwargs.pop(
            "media_streaming_configuration", None)
        user_custom_context = CustomContext(
            voip_headers=target_participant.voip_headers,
            sip_headers=target_participant.sip_headers
            ) if target_participant.sip_headers or target_participant.voip_headers else None
        create_call_request = CreateCallRequest(
            targets=[serialize_identifier(target_participant.target)],
            callback_uri=callback_url,
            source_caller_id_number=serialize_phone_identifier(
                target_participant.source_caller_id_number) if target_participant.source_caller_id_number else None,
            source_display_name=target_participant.source_display_name,
            source_identity=serialize_identifier(
                self.source_identity) if self.source_identity else None,
            operation_context=kwargs.pop("operation_context", None),
            media_streaming_configuration=media_streaming_config.to_generated(
            ) if media_streaming_config else None,
            azure_cognitive_services_endpoint_url=kwargs.pop(
                "azure_cognitive_services_endpoint_url", None),
            custom_context=user_custom_context
        )

        result = await self._client.create_call(
            create_call_request=create_call_request,
            repeatability_first_sent=_get_repeatability_guid(),
            repeatability_request_id=_get_repeatability_timestamp(),
            **kwargs)

        return CallConnectionProperties._from_generated(  # pylint:disable=protected-access
                result)

    async def create_group_call(
        self,
        target_participants: List[CommunicationIdentifier],
        callback_url: str,
        **kwargs
    ) -> CallConnectionProperties:
        """
        Create a call connection request to a list of multiple target identities.

        :param list[~azure.communication.callautomation._shared.models.CommunicationIdentifier] target_participants:
            A list of targets.
        :param str callback_url:
            The call back url for receiving events.
        :keyword ~azure.communication.callautomation._shared.models.PhoneNumberIdentifier source_caller_id_number:
            The source caller Id, a phone number, that's shown to the PSTN participant being invited.
            Required only when calling a PSTN callee.
        :keyword str source_display_name:
            Display name of the caller.
        :keyword str operation_context:
            Value that can be used to track the call and its associated events.
        :keyword ~azure.communication.callautomation.models.MediaStreamingConfiguration media_streaming_configuration:
            Media Streaming Configuration.
        :keyword str azure_cognitive_services_endpoint_url:
            The identifier of the Cognitive Service resource assigned to this call.
        :keyword Dict[str, str] sip_headers:
            Sip Headers for PSTN Call
        :keyword Dict[str, str] voip_headers:
            Voip Headers for Voip Call
        :return: CallConnectionProperties of this call.
        :rtype: ~azure.communication.callautomation.models.CallConnectionProperties
        :raises ~azure.core.exceptions.HttpResponseError
        """

        if not target_participants:
            raise ValueError('target_participants cannot be None.')
        if not callback_url:
            raise ValueError('callback_url cannot be None.')

        caller_id_number = kwargs.pop("source_caller_id_number", None)
        media_streaming_config = kwargs.pop(
            "media_streaming_configuration", None)
        sip_headers = kwargs.pop("sip_headers", None)
        voip_headers = kwargs.pop("voip_headers", None)
        user_custom_context = CustomContext(
            voip_headers=voip_headers, sip_headers=sip_headers) if sip_headers or voip_headers else None

        create_call_request = CreateCallRequest(
            targets=[serialize_identifier(identifier)
                     for identifier in target_participants],
            callback_uri=callback_url,
            source_caller_id_number=serialize_phone_identifier(
                caller_id_number) if caller_id_number else None,
            source_display_name=kwargs.pop("source_display_name", None),
            source_identity=serialize_identifier(
                self.source_identity) if self.source_identity else None,
            operation_context=kwargs.pop("operation_context", None),
            media_streaming_configuration=media_streaming_config.to_generated(
            ) if media_streaming_config else None,
            azure_cognitive_services_endpoint_url=kwargs.pop(
                "azure_cognitive_services_endpoint_url", None),
            custom_context=user_custom_context,
        )

        result = await self._client.create_call(
            create_call_request=create_call_request,
            repeatability_first_sent=_get_repeatability_guid(),
            repeatability_request_id=_get_repeatability_timestamp(),
            **kwargs)

        return CallConnectionProperties._from_generated(  # pylint:disable=protected-access
                result)

    async def answer_call(
        self,
        incoming_call_context: str,
        callback_url: str,
        **kwargs
    ) -> CallConnectionProperties:
        """
        Answer incoming call with Azure Communication Service's IncomingCall event

        :param str incoming_call_context:
            The incoming call context. This can be read from body of IncomingCall event.
        :param str callback_url:
            The call back url for receiving events.
        :keyword ~azure.communication.callautomation.models.MediaStreamingConfiguration media_streaming_configuration:
            Media Streaming Configuration.
        :keyword str azure_cognitive_services_endpoint_url:
            The endpoint url of the Azure Cognitive Services resource attached.
        :return: CallConnectionProperties of this call.
        :rtype: ~azure.communication.callautomation.models.CallConnectionProperties
        :raises ~azure.core.exceptions.HttpResponseError
        """

        if not incoming_call_context:
            raise ValueError('incoming_call_context cannot be None.')
        if not callback_url:
            raise ValueError('callback_url cannot be None.')

        media_streaming_config = kwargs.pop(
            "media_streaming_configuration", None)

        answer_call_request = AnswerCallRequest(
            incoming_call_context=incoming_call_context,
            callback_uri=callback_url,
            media_streaming_configuration=media_streaming_config.to_generated(
            ) if media_streaming_config else None,
            azure_cognitive_services_endpoint_url=kwargs.pop(
                "azure_cognitive_services_endpoint_url", None),
            answered_by_identifier=serialize_identifier(
                self.source_identity) if self.source_identity else None
        )

        result = await self._client.answer_call(
            answer_call_request=answer_call_request,
            repeatability_first_sent=_get_repeatability_guid(),
            repeatability_request_id=_get_repeatability_timestamp(),
            **kwargs)

        return CallConnectionProperties._from_generated(  # pylint:disable=protected-access
                result)

    async def redirect_call(
        self,
        incoming_call_context: str,
        target_participant: CallInvite,
        **kwargs
    ) -> None:
        """
        Redirect incoming call to a specific target.

        :param str incoming_call_context:
            The incoming call context. This can be read from body of IncomingCall event.
        :param ~azure.communication.callautomation.models.CallInvite target_participant:
            The target identity to redirect the call to.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError
        """

        if not incoming_call_context:
            raise ValueError('incoming_call_context cannot be None.')
        if not target_participant:
            raise ValueError('target_participant cannot be None.')

        user_custom_context = CustomContext(
            voip_headers=target_participant.voip_headers,
            sip_headers=target_participant.sip_headers
            ) if target_participant.sip_headers or target_participant.voip_headers else None

        redirect_call_request = RedirectCallRequest(
            incoming_call_context=incoming_call_context,
            target=serialize_identifier(target_participant.target),
            custom_context=user_custom_context
        )

        await self._client.redirect_call(
            redirect_call_request=redirect_call_request,
            repeatability_first_sent=_get_repeatability_guid(),
            repeatability_request_id=_get_repeatability_timestamp(),
            **kwargs)

    async def reject_call(
        self,
        incoming_call_context: str,
        **kwargs
    ) -> None:
        """
        Reject incoming call.

        :param str incoming_call_context:
            The incoming call context. This can be read from body of IncomingCall event.
        :keyword Union[str, CallRejectReason] call_reject_reason:
            The rejection reason.
            Known values are: "none", "busy", and "forbidden".
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError
        """

        if not incoming_call_context:
            raise ValueError('incoming_call_context cannot be None.')

        reject_call_request = RejectCallRequest(
            incoming_call_context=incoming_call_context,
            call_reject_reason=kwargs.pop("call_reject_reason", None)
        )

        await self._client.reject_call(
            reject_call_request=reject_call_request,
            repeatability_first_sent=_get_repeatability_guid(),
            repeatability_request_id=_get_repeatability_timestamp(),
            **kwargs)

    async def start_recording(
        self,
        call_locator: Union[ServerCallLocator, GroupCallLocator],
        **kwargs
    ) -> RecordingStateResult:
        """
        Start recording for a ongoing call.

        :param ~azure.communication.callautomation.models.CallLocator call_locator:
            The call locator to locate ongoing call.
        :keyword str recording_state_callback_url:
            The url to send notifications to.
        :keyword Union[str, ~azure.communication.callautomation.models.RecordingContent] recording_content_type:
            The content type of call recording. Known values are: "audio" and "audioVideo".
        :keyword Union[str, ~azure.communication.callautomation.models.RecordingChannel] recording_channel_type:
            The channel type of call recording. Known values are: "mixed" and "unmixed".
        :keyword recording_format_type: The format type of call recording. Known values are: "wav", "mp3", and "mp4".
        :type recording_format_type: str or ~azure.communication.callautomation.models.RecordingFormat
        :keyword list[CommunicationIdentifier] audio_channel_participant_ordering:
            The sequential order in which audio channels are assigned to participants in the unmixed recording.
            When 'recordingChannelType' is set to 'unmixed' and `audioChannelParticipantOrdering is not specified,
            the audio channel to participant mapping will be automatically assigned based on the order in
            which participant first audio was detected.
            Channel to participant mapping details can be found in the metadata of the recording.
        :keyword str recording_storage_type:
            Recording storage mode. ``External`` enables bring your own storage.
            Known values are: "acs" and "azureBlob".
        :keyword str external_storage_location:
            The location where recording is stored, when RecordingStorageType is set to 'BlobStorage'.
        :return: RecordingStateResult
        :rtype: ~azure.communication.callautomation.models.RecordingStateResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        start_recording_request = StartCallRecordingRequest(
            call_locator=call_locator._to_generated(# pylint:disable=protected-access
            ),
            recording_state_callback_uri = kwargs.pop("recording_state_callback_url", None),
            recording_content_type = kwargs.pop("recording_content_type", None),
            recording_channel_type = kwargs.pop("recording_channel_type", None),
            recording_format_type = kwargs.pop("recording_format_type", None),
            audio_channel_participant_ordering = kwargs.pop("audio_channel_participant_ordering_list", None),
            recording_storage_type = kwargs.pop("recording_storage_type", None),
            external_storage_location = kwargs.pop("external_storage_location", None),
            repeatability_first_sent=_get_repeatability_guid(),
            repeatability_request_id=_get_repeatability_timestamp()
        )

        recording_state_result = await self._call_recording_client.start_recording(
        start_call_recording = start_recording_request)

        return RecordingStateResult._from_generated(# pylint:disable=protected-access
            recording_state_result)

    async def stop_recording(
        self,
        recording_id: str,
        **kwargs
    ) -> None:
        """
        Stop recording the call.

        :param str recording_id:
            The recording id.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        await self._call_recording_client.stop_recording(recording_id = recording_id, **kwargs)

    async def pause_recording(
        self,
        recording_id: str,
        **kwargs
    ) -> None:
        """
        Pause recording the call.

        :param str recording_id:
            The recording id.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        await self._call_recording_client.pause_recording(recording_id = recording_id, **kwargs)

    async def resume_recording(
        self,
        recording_id: str,
        **kwargs
    ) -> None:
        """
        Resume recording the call.

        :param str recording_id:
            The recording id.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        await self._call_recording_client.resume_recording(recording_id = recording_id, **kwargs)

    async def get_recording_properties(
        self,
        recording_id: str,
        **kwargs
    ) -> RecordingStateResult:
        """
        Get call recording properties.

        :param str recording_id: The recording id.
        :return: RecordingStateResult
        :rtype: ~azure.communication.callautomation.models.RecordingStateResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        recording_state_result = await self._call_recording_client.get_recording_properties(
            recording_id = recording_id, **kwargs)
        return RecordingStateResult._from_generated(# pylint:disable=protected-access
            recording_state_result)

    def download_recording_streaming(
        self,
        source_location: str,
        **kwargs
    ) -> HttpResponse:
        """
        Download a stream of the call recording.

        :param str source_location:
            The source location. Required.
        :keyword int offset:
            Offset byte.
        :keyword int length:
            how many bytes
        :return: HttpResponse (octet-stream)
        :rtype: HttpResponse (octet-stream)
        """
        offset = kwargs.pop("offset", None)
        length = kwargs.pop("length", None)
        stream = self._downloader.download_streaming(
            source_location = source_location,
            offset = offset,
            length = length,
            **kwargs
        )
        return stream

    def delete_recording(
        self,
        recording_location: str,
        **kwargs
    ) -> None:
        """
        Delete a call recording.

        :param str recording_location:
            The recording location.
        :return: None
        :rtype: None
        """
        self._downloader.delete_recording(recording_location = recording_location, **kwargs)

    def download_recording_to_path(
        self,
        source_location: str,
        destination_path: str,
        **kwargs
    ) -> None:
        """
        Download a stream of the call recording to the destination.

        :param str source_location:
            The source location url.
        :param str destination_path:
            The destination path.
        :keyword int offset:
            Offset byte.
        :keyword int length:
            how many bytes
        :return: None
        :rtype: None
        """
        offset = kwargs.pop("offset", None)
        length = kwargs.pop("length", None)
        stream = self._downloader.download_streaming(source_location = source_location,
                                                     offset = offset,
                                                     length = length,
                                                     **kwargs
                                                    )
        with open(destination_path, 'wb') as writer:
            writer.write(stream.read())


    def download_recording_to_stream(
        self,
        source_location: str,
        destination_stream: BytesIO,
        **kwargs
    ) -> None:
        """
        Download a stream of the call recording to the destination.

        :param str source_location:
            The source location url.
        :param BytesIO destination_stream:
            The destination stream.
        :keyword int offset:
            Offset byte.
        :keyword int length:
            how many bytes
        :return: None
        :rtype: None
        """
        offset = kwargs.pop("offset", None)
        length = kwargs.pop("length", None)
        stream = self._downloader.download_streaming(source_location = source_location,
                                                     offset = offset,
                                                     length = length,
                                                     **kwargs
                                                    )
        with open(destination_stream, 'wb') as writer:
            writer.write(stream.read())

    async def __aenter__(self) -> "CallAutomationClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.__aexit__()
