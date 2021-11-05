# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=unsubscriptable-object,too-many-public-methods
# disabled unsubscriptable-object because of pylint bug referenced here:
# https://github.com/PyCQA/pylint/issues/3882

from typing import TYPE_CHECKING, Any, List, Optional  # pylint: disable=unused-import

from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.pipeline.transport import HttpResponse
from azure.core.exceptions import (
    HttpResponseError,
    map_error
)

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
    RecordingFormatType,
    CallParticipant,
    CallMediaType,
    CallingEventSubscriptionType,
    AnswerCallResult,
    CallRejectReason
    )
from .._shared.models import CommunicationIdentifier
from ._content_downloader_async import ContentDownloader
from ._download_async import ContentStreamDownloader
from .._models import CallLocator, ParallelDownloadOptions
from ._call_connection_async import CallConnection
from .._converters import (
    JoinCallRequestConverter,
    AnswerCallRequestConverter,
    RedirectCallRequestConverter,
    RejectCallRequestConverter,
    PlayAudioWithCallLocatorRequestConverter,
    PlayAudioToParticipantWithCallLocatorRequestConverter,
    AddParticipantWithCallLocatorRequestConverter,
    RemoveParticipantWithCallLocatorRequestConverter,
    CancelMediaOperationWithCallLocatorRequestConverter,
    CancelParticipantMediaOperationWithCallLocatorRequestConverter,
    GetAllParticipantsWithCallLocatorRequestConverter,
    GetParticipantWithCallLocatorRequestConverter,
    MuteParticipantWithCallLocatorRequestConverter,
    UnmuteParticipantWithCallLocatorRequestConverter,
    HoldMeetingAudioWithCallLocatorRequestConverter,
    ResumeMeetingAudioWithCallLocatorRequestConverter
    )
from .._shared.utils import get_authentication_policy, get_host_header_policy, parse_connection_str
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
            headers_policy=get_host_header_policy(endpoint, credential),
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
    async def answer_call(
        self,
        incoming_call_context: str,
        callback_uri: Optional[str] = None,
        requested_media_types: Optional[List[CallMediaType]] = None,
        requested_call_events: Optional[List[CallingEventSubscriptionType]] = None,
        **kwargs: Any
    ) -> AnswerCallResult:

        answer_call_request = AnswerCallRequestConverter.convert(
            incoming_call_context=incoming_call_context,
            callback_uri=callback_uri,
            requested_media_types=requested_media_types,
            requested_call_events=requested_call_events
            )

        return await self._server_call_client.answer_call(
            answer_call_request=answer_call_request,
            **kwargs
        )

    @distributed_trace_async()
    async def reject_call(
        self,
        incoming_call_context: Optional[str] = None,
        call_reject_reason: Optional[CallRejectReason] = None,
        callback_uri: Optional[str] = None,
        **kwargs: Any
    ) -> None:

        reject_call_request = RejectCallRequestConverter.convert(
            incoming_call_context=incoming_call_context,
            call_reject_reason=call_reject_reason,
            callback_uri=callback_uri
            )

        return await self._server_call_client.reject_call(
            reject_call_request=reject_call_request,
            **kwargs
        )

    @distributed_trace_async()
    async def redirect_call(
        self,
        incoming_call_context,  # type: str
        targets,  # type: List[CommunicationIdentifier]
        callback_uri=None,  # type: str
        timeout_in_seconds=None,  # type: int
        **kwargs  # type: Any
    ):  # type: (...) -> None

        redirect_call_request = RedirectCallRequestConverter.convert(
            incoming_call_context=incoming_call_context,
            target_identities=[serialize_identifier(m) for m in targets],
            callback_uri=callback_uri,
            timeout_in_seconds=timeout_in_seconds
            )

        return await self._server_call_client.redirect_call(
            redirect_call_request=redirect_call_request,
            **kwargs
        )

    @distributed_trace_async()
    async def play_audio(
        self,
        call_locator: 'CallLocator',
        audio_url: str,
        play_audio_options: 'PlayAudioOptions',
        **kwargs: Any
    ) -> PlayAudioResult:

        play_audio_request = PlayAudioWithCallLocatorRequestConverter.convert(
            call_locator=serialize_call_locator(call_locator),
            audio_url=audio_url,
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
        audio_url: str,
        play_audio_options: 'PlayAudioOptions',
        **kwargs: Any
    ) -> PlayAudioResult:

        play_audio_to_participant_request = PlayAudioToParticipantWithCallLocatorRequestConverter.convert(
            call_locator=serialize_call_locator(call_locator),
            identifier=serialize_identifier(participant),
            audio_url=audio_url,
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
        call_locator: CallLocator,
        participant: CommunicationIdentifier,
        **kwargs: Any
    ) -> None:

        if not call_locator:
            raise ValueError("call_locator can not be None")
        if not participant:
            raise ValueError("participant can not be None")

        remove_participant_with_call_locator_request = RemoveParticipantWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator),
            serialize_identifier(participant)
            )

        return await self._server_call_client.remove_participant(
            remove_participant_with_call_locator_request=remove_participant_with_call_locator_request,
            **kwargs
        )

    @distributed_trace_async()
    async def get_participants(
            self,
            call_locator: CallLocator,
            **kwargs: Any
        ) -> List[CallParticipant]:

        get_all_participants_with_call_locator_request = GetAllParticipantsWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator)
            )

        return await self._server_call_client.get_participants(
            get_all_participants_with_call_locator_request=get_all_participants_with_call_locator_request,
            **kwargs
        )

    @distributed_trace_async()
    async def get_participant(
            self,
            call_locator: CallLocator,
            participant: CommunicationIdentifier,
            **kwargs: Any
        ) -> List[CallParticipant]:

        get_participant_with_call_locator_request = GetParticipantWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator),
            serialize_identifier(participant)
            )

        return await self._server_call_client.get_participant(
            get_participant_with_call_locator_request=get_participant_with_call_locator_request,
            **kwargs
        )

    @distributed_trace_async()
    async def mute_participant(
            self,
            call_locator,  # type: CallLocator
            participant,  # type: CommunicationIdentifier
            **kwargs  # type: Any
        ):  # type: (...) -> None

        mute_participant_with_call_locator_request = MuteParticipantWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator),
            serialize_identifier(participant)
            )

        return await self._server_call_client.mute_participant(
            mute_participant_with_call_locator_request=mute_participant_with_call_locator_request,
            **kwargs
        )

    @distributed_trace_async()
    async def unmute_participant(
            self,
            call_locator,  # type: CallLocator
            participant,  # type: CommunicationIdentifier
            **kwargs  # type: Any
        ):  # type: (...) -> None

        unmute_participant_with_call_locator_request = UnmuteParticipantWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator),
            serialize_identifier(participant)
            )

        return await self._server_call_client.unmute_participant(
            unmute_participant_with_call_locator_request=unmute_participant_with_call_locator_request,
            **kwargs
        )

    @distributed_trace_async()
    async def cancel_media_operation(
        self,
        call_locator: 'CallLocator',
        media_operation_id: str,
        **kwargs: Any
    ) -> None:

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
    async def hold_participant_meeting_audio(
            self,
            call_locator,  # type: CallLocator
            participant,  # type: CommunicationIdentifier
            **kwargs  # type: Any
        ):  # type: (...) -> None

        hold_meeting_audio_with_call_locator_request = HoldMeetingAudioWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator),
            serialize_identifier(participant)
            )

        return await self._server_call_client.hold_participant_meeting_audio(
            hold_meeting_audio_with_call_locator_request=hold_meeting_audio_with_call_locator_request,
            **kwargs
        )

    @distributed_trace_async()
    async def resume_participant_meeting_audio(
            self,
            call_locator,  # type: CallLocator
            participant,  # type: CommunicationIdentifier
            **kwargs  # type: Any
        ):  # type: (...) -> None

        resume_meeting_audio_with_call_locator_request = ResumeMeetingAudioWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator),
            serialize_identifier(participant)
            )

        return await self._server_call_client.resume_participant_meeting_audio(
            resume_meeting_audio_with_call_locator_request=resume_meeting_audio_with_call_locator_request,
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

    @distributed_trace_async()
    async def delete_recording(
        self,
        content_delete_url: str,
        **kwargs: Any

    ): # type: (...) -> HttpResponse
        # pylint: disable=protected-access
        if not content_delete_url:
            raise ValueError("content_delete_url can not be None")

        uri_to_sign_with = CallingServerUtils.get_url_to_sign_request_with(self._endpoint, content_delete_url)

        query_parameters = {} # type: Dict[str, Any]
        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        header_parameters['UriToSignWith'] = self._callingserver_service_client._serialize.header(
            name="uri_to_sign_with",
            data=uri_to_sign_with,
            data_type='str')

        error_map = CallingServerUtils.get_error_response_map(
            kwargs.pop('error_map', {}))

        client = self._callingserver_service_client._client
        request = client.delete(content_delete_url, query_parameters, header_parameters) #pylint: disable=specify-parameter-names-in-call
        pipeline_response = await client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response
        if response.status_code not in [200]:
            map_error(status_code=response.status_code,
                        response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        return response

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
