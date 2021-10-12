# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=unsubscriptable-object
# disabled unsubscriptable-object because of pylint bug referenced here:
# https://github.com/PyCQA/pylint/issues/3882

from typing import TYPE_CHECKING, Any, List, Optional  # pylint: disable=unused-import

from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.pipeline.transport import HttpResponse

from ..utils._utils import CallingServerUtils
from .._communication_identifier_serializer import serialize_identifier
from .._communication_call_locator_serializer import serialize_call_locator
from .._generated.aio._azure_communication_calling_server_service import \
    AzureCommunicationCallingServerService
from .._generated.models import (
    CreateCallRequest,
    PhoneNumberIdentifierModel,
    PlayAudioResult,
    AddParticipantResult,
    CallRecordingProperties,
    StartCallRecordingWithCallLocatorRequest,
    StartCallRecordingResult,
    RecordingContentType,
    RecordingChannelType,
    RecordingFormatType
    )
from .._shared.models import CommunicationIdentifier
from ._content_downloader_async import ContentDownloader
from ._download_async import ContentStreamDownloader
from .._models import CallLocator, ParallelDownloadOptions
from ._call_connection_async import CallConnection
from .._converters import (
    JoinCallRequestConverter,
    PlayAudioWithCallLocatorRequestConverter,
    PlayAudioToParticipantWithCallLocatorRequestConverter,
    AddParticipantWithCallLocatorRequestConverter,
    RemoveParticipantWithCallLocatorRequestConverter,
    CancelMediaOperationWithCallLocatorRequestConverter,
    CancelParticipantMediaOperationWithCallLocatorRequestConverter
    )
from .._shared.utils import get_authentication_policy, parse_connection_str
from .._version import SDK_MONIKER

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential
    from .._models import CreateCallOptions, JoinCallOptions, PlayAudioOptions

class CallingServerClient:
    """A client to interact with the AzureCommunicationService Calling Server.

    This client provides calling operations.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param AsyncTokenCredential credential:
        The AsyncTokenCredential we use to authenticate against the service.

    .. admonition:: Example:

        .. literalinclude:: ../samples/identity_samples.py
            :language: python
            :dedent: 8
    """
    def __init__(
        self,
        endpoint: str,
        credential: 'AsyncTokenCredential',
        **kwargs: Any
    ) -> None:
        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError as ex:
            raise ValueError("Account URL must be a string.") from ex

        if not credential:
            raise ValueError(
                "You need to provide account shared key to authenticate.")

        self._endpoint = endpoint
        self._callingserver_service_client = AzureCommunicationCallingServerService(
            self._endpoint,
            authentication_policy=get_authentication_policy(endpoint, credential, decode_url=True, is_async=True),
            sdk_moniker=SDK_MONIKER,
            **kwargs
            )

        self._call_connection_client = self._callingserver_service_client.call_connections
        self._server_call_client = self._callingserver_service_client.server_calls

    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        **kwargs: Any
    ) -> 'CallingServerClient':
        """Create CallingServerClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :returns: Instance of CallingServerClient.
        :rtype: ~azure.communication.callingserver.CallingServerClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/callingserver_sample.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Creating the CallingServerClient from a connection string.
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)

    def get_call_connection(
        self,
        call_connection_id: str,
    ) -> CallConnection:
        """Initializes a new instance of CallConnection.

        :param str call_connection_id:
           The thread id for the ChatThreadClient instance.
        :returns: Instance of CallConnection.
        :rtype: ~azure.communication..callingserver.CallConnection
        """
        if not call_connection_id:
            raise ValueError("call_connection_id can not be None")

        return CallConnection(call_connection_id, self._call_connection_client, self._callingserver_service_client)

    @distributed_trace_async()
    async def create_call_connection(
        self,
        source: CommunicationIdentifier,
        targets: List[CommunicationIdentifier],
        options: 'CreateCallOptions',
        **kwargs: Any
    ) -> CallConnection:
        """Create an outgoing call from source to target identities.

        :param CommunicationIdentifier source:
           The source identity.
        :param List[CommunicationIdentifier] targets:
           The target identities.
        :param CreateCallOptions options:
           The call options.
        :returns: CallConnection for a successful creating callConnection request.
        :rtype: ~azure.communication.callingserver.CallConnection
        """
        if not source:
            raise ValueError("source can not be None")
        if not targets:
            raise ValueError("targets can not be None or empty")
        if not options:
            raise ValueError("options can not be None")

        request = CreateCallRequest(
            source=serialize_identifier(source),
            targets=[serialize_identifier(m) for m in targets],
            callback_uri=options.callback_uri,
            requested_media_types=options.requested_media_types,
            requested_call_events=options.requested_call_events,
            alternate_caller_id=(None
                if options.alternate_Caller_Id is None
                else PhoneNumberIdentifierModel(value=options.alternate_Caller_Id.properties['value'])),
            subject=options.subject
        )

        create_call_response = await self._call_connection_client.create_call(
            call_request=request,
            **kwargs
        )
        return CallConnection(
            create_call_response.call_connection_id,
            self._call_connection_client,
            self._callingserver_service_client
            )  # pylint:disable=protected-access

    @distributed_trace_async()
    async def join_call(
        self,
        call_locator: CallLocator,
        source: CommunicationIdentifier,
        call_options: 'JoinCallOptions',
        **kwargs: Any
    ) -> CallConnection:
        """Join the call using call_locator.

        :param CallLocator call_locator:
           The callLocator.
        :param CommunicationIdentifier source:
           The source identity.
        :param JoinCallOptions call_options:
           The call Options.
        :returns: CallConnection for a successful join request.
        :rtype: ~azure.communication.callingserver.CallConnection
        """
        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not source:
            raise ValueError("source can not be None")
        if not call_options:
            raise ValueError("call_options can not be None")

        join_call_request = JoinCallRequestConverter.convert(
            call_locator=serialize_call_locator(call_locator),
            source=serialize_identifier(source),
            join_call_options=call_options
            )

        join_call_response = await self._server_call_client.join_call(
            call_request=join_call_request,
            **kwargs
        )

        return CallConnection(
            join_call_response.call_connection_id,
            self._call_connection_client,
            self._callingserver_service_client
            )

    @distributed_trace_async()
    async def play_audio(
        self,
        call_locator: 'CallLocator',
        audio_file_uri: str,
        play_audio_options: 'PlayAudioOptions',
        **kwargs: Any
    ) -> PlayAudioResult:

        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not audio_file_uri:
            raise ValueError("audio_file_uri can not be None")
        if not CallingServerUtils.is_valid_url(audio_file_uri):
            raise ValueError("audio_file_uri is invalid")
        if not play_audio_options:
            raise ValueError("options can not be None")
        if not CallingServerUtils.is_valid_url(play_audio_options.callback_uri):
            raise ValueError("callback_uri is invalid")

        play_audio_request = PlayAudioWithCallLocatorRequestConverter.convert(
            call_locator=serialize_call_locator(call_locator),
            audio_file_uri=audio_file_uri,
            play_audio_options=play_audio_options
            )

        return await self._server_call_client.play_audio(
            play_audio_request=play_audio_request,
            **kwargs
        )

    @distributed_trace_async()
    async def play_audio_to_participant(
        self,
        call_locator: 'CallLocator',
        participant: 'CommunicationIdentifier',
        audio_file_uri: str,
        play_audio_options: 'PlayAudioOptions',
        **kwargs: Any
    ) -> PlayAudioResult:

        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not participant:
            raise ValueError("participant can not be None")
        if not audio_file_uri:
            raise ValueError("audio_file_uri can not be None")
        if not CallingServerUtils.is_valid_url(audio_file_uri):
            raise ValueError("audio_file_uri is invalid")
        if not play_audio_options:
            raise ValueError("play_audio_options can not be None")
        if not CallingServerUtils.is_valid_url(play_audio_options.callback_uri):
            raise ValueError("callback_uri is invalid")

        play_audio_to_participant_request = PlayAudioToParticipantWithCallLocatorRequestConverter.convert(
            call_locator=serialize_call_locator(call_locator),
            identifier=serialize_identifier(participant),
            audio_file_uri=audio_file_uri,
            play_audio_options=play_audio_options
            )

        return await self._server_call_client.participant_play_audio(
            play_audio_to_participant_request=play_audio_to_participant_request,
            **kwargs
        )

    @distributed_trace_async()
    async def add_participant( # pylint: disable=too-many-arguments
        self,
        call_locator: 'CallLocator',
        participant: 'CommunicationIdentifier',
        callback_uri: str,
        alternate_caller_id: Optional[str] = None,
        operation_context: Optional[str] = None,
        **kwargs: Any
    ) -> AddParticipantResult:

        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not participant:
            raise ValueError("participant can not be None")
        if not CallingServerUtils.is_valid_url(callback_uri):
            raise ValueError("callback_uri is invalid")

        alternate_caller_id = (None
            if alternate_caller_id is None
            else PhoneNumberIdentifierModel(value=alternate_caller_id))

        add_participant_with_call_locator_request = AddParticipantWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator),
            serialize_identifier(participant),
            alternate_caller_id=alternate_caller_id,
            operation_context=operation_context,
            callback_uri=callback_uri
            )

        return await self._server_call_client.add_participant(
            add_participant_with_call_locator_request=add_participant_with_call_locator_request,
            **kwargs
        )

    @distributed_trace_async()
    async def remove_participant(
        self,
        call_locator: 'CallLocator',
        participant: 'CommunicationIdentifier',
        **kwargs: Any
    ) -> None:

        remove_participant_with_call_locator_request = RemoveParticipantWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator),
            serialize_identifier(participant)
            )

        return await self._server_call_client.remove_participant(
            remove_participant_with_call_locator_request=remove_participant_with_call_locator_request,
            **kwargs
        )

    @distributed_trace_async()
    async def cancel_media_operation(
        self,
        call_locator: 'CallLocator',
        media_operation_id: str,
        **kwargs: Any
    ) -> None:

        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not media_operation_id:
            raise ValueError("media_operation_id can not be None")

        cancel_media_operation_request = CancelMediaOperationWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator),
            media_operation_id=media_operation_id
            )

        return await self._server_call_client.cancel_media_operation(
            cancel_media_operation_request=cancel_media_operation_request,
            **kwargs
        )

    @distributed_trace_async()
    async def cancel_participant_media_operation(
        self,
        call_locator: 'CallLocator',
        participant: 'CommunicationIdentifier',
        media_operation_id: str,
        **kwargs: Any
    ) -> None:

        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not participant:
            raise ValueError("participant can not be None")
        if not media_operation_id:
            raise ValueError("media_operation_id can not be None")

        cancel_participant_media_operation_request = \
        CancelParticipantMediaOperationWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator),
            serialize_identifier(participant),
            media_operation_id=media_operation_id
            )

        return await self._server_call_client.cancel_participant_media_operation(
            cancel_participant_media_operation_request=cancel_participant_media_operation_request,
            **kwargs
            )

    @distributed_trace_async()
    async def start_recording( # pylint: disable=too-many-arguments
        self,
        call_locator: CallLocator,
        recording_state_callback_uri: str,
        recording_content_type: Optional[RecordingContentType] = None,
        recording_channel_type: Optional[RecordingChannelType] = None,
        recording_format_type: Optional[RecordingFormatType] = None,
        **kwargs: Any
    ) -> StartCallRecordingResult:

        if not call_locator:
            raise ValueError("call_locator cannot be None")
        if not CallingServerUtils.is_valid_url(recording_state_callback_uri):
            raise ValueError("recording_state_callback_uri is invalid")

        start_call_recording_request = StartCallRecordingWithCallLocatorRequest(
            call_locator=serialize_call_locator(call_locator),
            recording_state_callback_uri=recording_state_callback_uri,
            recording_content_type=recording_content_type,
            recording_channel_type=recording_channel_type,
            recording_format_type=recording_format_type,
            **kwargs
        )

        return await self._server_call_client.start_recording(
            start_call_recording_request,
            **kwargs
        )

    @distributed_trace_async()
    async def pause_recording(
        self,
        recording_id: str,
        **kwargs: Any
    ) -> HttpResponse:

        if not recording_id:
            raise ValueError("recording_id cannot be None")

        return await self._server_call_client.pause_recording(
            recording_id=recording_id,
            **kwargs
        )

    @distributed_trace_async()
    async def resume_recording(
        self,
        recording_id: str,
        **kwargs: Any
    ) -> HttpResponse:

        if not recording_id:
            raise ValueError("recording_id cannot be None")

        return await self._server_call_client.resume_recording(
            recording_id=recording_id,
            **kwargs
        )

    @distributed_trace_async()
    async def stop_recording(
        self,
        recording_id: str,
        **kwargs: Any
    ) -> HttpResponse:

        if not recording_id:
            raise ValueError("recording_id cannot be None")

        return await self._server_call_client.stop_recording(
            recording_id=recording_id,
            **kwargs
        )

    @distributed_trace_async()
    async def get_recording_properities(
        self,
        recording_id: str,
        **kwargs: Any
    ) -> CallRecordingProperties:

        if not recording_id:
            raise ValueError("recording_id cannot be None")

        return await self._server_call_client.get_recording_properties(
            recording_id=recording_id,
            **kwargs
        )

    @distributed_trace_async
    async def download(
            self,
            content_url: str,
            start_range: int = None,
            end_range: int = None,
            parallel_download_options: ParallelDownloadOptions = None,
            **kwargs: Any
        ) -> ContentStreamDownloader:

        #pylint: disable=protected-access
        content_downloader = ContentDownloader(
            self._callingserver_service_client._client,
            self._callingserver_service_client._config,
            self._callingserver_service_client._serialize,
            self._callingserver_service_client._deserialize
        )
        stream_downloader = ContentStreamDownloader(
            content_downloader,
            self._callingserver_service_client._config,
            start_range,
            end_range,
            endpoint=content_url,
            parallel_download_options=parallel_download_options,
            **kwargs
        )
        await stream_downloader._setup()
        return stream_downloader

    async def close(self) -> None:
        """Close the :class:
        `~azure.communication.callingserver.aio.CallingServerClient` session.
        """
        await self._callingserver_service_client.close()

    async def __aenter__(self) -> "CallingServerClient":
        await self._callingserver_service_client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._callingserver_service_client.__aexit__(*args)
