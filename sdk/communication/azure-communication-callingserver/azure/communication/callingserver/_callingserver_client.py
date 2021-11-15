# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-public-methods
from typing import TYPE_CHECKING, Any, List  # pylint: disable=unused-import
from azure.core.tracing.decorator import distributed_trace
from azure.core.pipeline.transport import HttpResponse
from azure.core.exceptions import (
    HttpResponseError,
    map_error
)

from .utils._utils import CallingServerUtils
from ._content_downloader import ContentDownloader
from ._download import ContentStreamDownloader

from ._communication_identifier_serializer import serialize_identifier
from ._communication_call_locator_serializer import serialize_call_locator
from ._generated._azure_communication_calling_server_service import \
    AzureCommunicationCallingServerService
from ._generated.models import (
    CreateCallRequest,
    PhoneNumberIdentifierModel,
    PlayAudioResult,
    AddParticipantResult,
    CallRecordingProperties,
    StartCallRecordingWithCallLocatorRequest,
    StartCallRecordingResult,
    CallParticipant,
    CallMediaType,
    CallingEventSubscriptionType,
    AnswerCallResult
    )

from ._shared.models import CommunicationIdentifier
from ._call_connection import CallConnection
from ._converters import (
    JoinCallRequestConverter,
    AnswerCallRequestConverter,
    RejectCallRequestConverter,
    RedirectCallRequestConverter,
    PlayAudioWithCallLocatorRequestConverter,
    PlayAudioToParticipantWithCallLocatorRequestConverter,
    AddParticipantWithCallLocatorRequestConverter,
    RemoveParticipantWithCallLocatorRequestConverter,
    CancelMediaOperationWithCallLocatorRequestConverter,
    CancelParticipantMediaOperationWithCallLocatorRequestConverter,
    GetAllParticipantsWithCallLocatorRequestConverter,
    GetParticipantWithCallLocatorRequestConverter
    )
from ._shared.utils import get_authentication_policy, get_host_header_policy, parse_connection_str
from ._version import SDK_MONIKER

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from ._models import (
        ParallelDownloadOptions,
        CallLocator
    )

class CallingServerClient(object):
    """A client to interact with the AzureCommunicationService Calling Server.

    This client provides calling operations.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param TokenCredential credential:
        The TokenCredential we use to authenticate against the service.

    .. admonition:: Example:

        .. literalinclude:: ../samples/identity_samples.py
            :language: python
            :dedent: 8
    """

    def __init__(
        self,
        endpoint,  # type: str
        credential,  # type: TokenCredential
        **kwargs  # type: Any
    ):  # type: (...) -> None
        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Account URL must be a string.")

        if not credential:
            raise ValueError(
                "You need to provide account shared key to authenticate.")

        self._endpoint = endpoint
        self._callingserver_service_client = AzureCommunicationCallingServerService(
            self._endpoint,
            headers_policy=get_host_header_policy(endpoint, credential),
            authentication_policy=get_authentication_policy(endpoint, credential),
            sdk_moniker=SDK_MONIKER,
            **kwargs)

        self._call_connection_client = self._callingserver_service_client.call_connections
        self._server_call_client = self._callingserver_service_client.server_calls

    @classmethod
    def from_connection_string(
        cls,
        conn_str,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> CallingServerClient
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
        call_connection_id,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> CallConnection
        """Initializes a new instance of CallConnection.

        :param str call_connection_id:
           The call connection id for the CallConnection instance.
        :returns: Instance of CallConnection.
        :rtype: ~azure.communication.callingserver.CallConnection
        """

        if not call_connection_id:
            raise ValueError("call_connection_id can not be None")

        return CallConnection(
            call_connection_id,
            self._call_connection_client,
            **kwargs
            )

    @distributed_trace()
    def create_call_connection(
        self,
        source,  # type: CommunicationIdentifier
        targets,  # type: List[CommunicationIdentifier]
        callback_uri,  # type: str
        requested_media_types,  # type: List[CallMediaType]
        requested_call_events,  # type: List[CallingEventSubscriptionType]
        **kwargs  # type: Any
    ):  # type: (...) -> CallConnection
        """Create an outgoing call from source to target identities.

        :param source: Required. The source identity.
        :type source: CommunicationIdentifier
        :param targets:   The target identities.
        :type targets: list[~azure.communication.callingserver.models.CommunicationIdentifier]
        :param callback_uri:  The callback uri.
        :type callback_uri: str
        :param requested_media_types:  The requested modalities.
        :type requested_media_types: list[str or
         ~azure.communication.callingserver.models.CallMediaType]
        :param requested_call_events:  The requested call events to subscribe to.
        :type requested_call_events: list[str or
         ~azure.communication.callingserver.models.CallingEventSubscriptionType]
        :keyword alternate_Caller_Id: The alternate caller id.
        :paramtype alternate_Caller_Id: str
        :keyword subject: The subject.
        :paramtype subject: str
        :return: CallConnection
        :rtype: ~azure.communication.callingserver.CallConnection
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        alternate_Caller_Id = kwargs.pop("alternate_Caller_Id", None)
        subject = kwargs.pop("subject", None)

        request = CreateCallRequest(
            source=serialize_identifier(source),
            targets=[serialize_identifier(m) for m in targets],
            callback_uri=callback_uri,
            requested_media_types=requested_media_types,
            requested_call_events=requested_call_events,
            alternate_caller_id=(None
                if alternate_Caller_Id is None
                else PhoneNumberIdentifierModel(value=alternate_Caller_Id)),
            subject=subject
        )

        create_call_response = self._call_connection_client.create_call(
            call_request=request,
            **kwargs
        )

        return CallConnection(create_call_response.call_connection_id, self._call_connection_client)  # pylint:disable=protected-access

    @distributed_trace()
    def join_call(
        self,
        call_locator,  # type: CallLocator
        source,  # type: CommunicationIdentifier
        callback_uri,  # type: str
        requested_media_types,  # type: List[CallMediaType]
        requested_call_events,  # type: List[CallingEventSubscriptionType]
        **kwargs  # type: Any
    ):  # type: (...) -> CallConnection
        """Join the call using call_locator.

        :param call_locator: Required. The call locator.
        :type call_locator: ~azure.communication.callingserver.models.CallLocator
        :param source: Required. The source identity.
        :type source: CommunicationIdentifier
        :param targets:   The target identities.
        :type targets: list[~azure.communication.callingserver.models.CommunicationIdentifier]
        :param callback_uri:  The callback uri.
        :type callback_uri: str
        :param requested_media_types:  The requested modalities.
        :type requested_media_types: list[str or
         ~azure.communication.callingserver.models.CallMediaType]
        :param requested_call_events:  The requested call events to subscribe to.
        :type requested_call_events: list[str or
         ~azure.communication.callingserver.models.CallingEventSubscriptionType]
        :keyword subject: The subject.
        :paramtype subject: str
        :return: CallConnection
        :rtype: ~azure.communication.callingserver.CallConnection
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        subject = kwargs.pop("subject", None)

        join_call_request = JoinCallRequestConverter.convert(
            call_locator=serialize_call_locator(call_locator),
            source=serialize_identifier(source),
            callback_uri=callback_uri,
            requested_media_types=requested_media_types,
            requested_call_events=requested_call_events,
            subject=subject
        )

        join_call_response = self._server_call_client.join_call(
            call_request=join_call_request,
            **kwargs
        )

        return CallConnection(
            join_call_response.call_connection_id,
            self._call_connection_client
            )

    @distributed_trace()
    def answer_call(
        self,
        incoming_call_context,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> AnswerCallResult
        """Answer the call.

        :param incoming_call_context: Required. The context associated with the call.
        :type incoming_call_context: str
        :keyword callback_uri:  The callback uri.
        :paramtype callback_uri: str
        :keyword requested_media_types: The requested modalities.
        :paramtype requested_media_types: list[str or
         ~azure.communication.callingserver.models.CallMediaType]
        :keyword requested_call_events: The requested call events to subscribe to.
        :paramtype requested_call_events: list[str or
         ~azure.communication.callingserver.models.CallingEventSubscriptionType]
        :return: AnswerCallResult
        :rtype: ~azure.communication.callingserver.AnswerCallResult
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        callback_uri = kwargs.pop("callback_uri", None)
        requested_media_types = kwargs.pop("requested_media_types", None)
        requested_call_events = kwargs.pop("requested_call_events", None)

        answer_call_request = AnswerCallRequestConverter.convert(
            incoming_call_context=incoming_call_context,
            callback_uri=callback_uri,
            requested_media_types=requested_media_types,
            requested_call_events=requested_call_events
            )

        return self._server_call_client.answer_call(
            answer_call_request=answer_call_request,
            **kwargs
        )

    @distributed_trace()
    def reject_call(
        self,
        incoming_call_context,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> None
        """Answer the call.

        :param incoming_call_context: Required. The context associated with the call.
        :type incoming_call_context: str
        :keyword call_reject_reason:  The rejection reason. Possible values include: "none", "busy",
         "forbidden".
        :paramtype call_reject_reason: str or ~azure.communication.callingserver.models.CallRejectReason
        :keyword callback_uri: The callback uri.
        :paramtype callback_uri: str
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        call_reject_reason = kwargs.pop("call_reject_reason", None)
        callback_uri = kwargs.pop("callback_uri", None)

        reject_call_request = RejectCallRequestConverter.convert(
            incoming_call_context=incoming_call_context,
            call_reject_reason=call_reject_reason,
            callback_uri=callback_uri
            )

        return self._server_call_client.reject_call(
            reject_call_request=reject_call_request,
            **kwargs
        )

    @distributed_trace()
    def redirect_call(
        self,
        incoming_call_context,  # type: str
        targets,  # type: List[CommunicationIdentifier]
        **kwargs  # type: Any
    ):  # type: (...) -> None
        """Redirect the call.

        :param incoming_call_context: Required. The call locator.
        :type incoming_call_context: ~azure.communication.callingserver.models.CallLocator
        :param targets: Required. The identifier of the participant to be removed from the call.
        :type targets: ~azure.communication.callingserver.models.CommunicationIdentifier
        :keyword callback_uri: The alternate caller id.
        :paramtype callback_uri: str
        :keyword timeout_in_seconds: The alternate caller id.
        :paramtype timeout_in_seconds: int
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        callback_uri = kwargs.pop("callback_uri", None)
        timeout_in_seconds = kwargs.pop("timeout_in_seconds", None)

        redirect_call_request = RedirectCallRequestConverter.convert(
            incoming_call_context=incoming_call_context,
            target_identities=[serialize_identifier(m) for m in targets],
            callback_uri=callback_uri,
            timeout_in_seconds=timeout_in_seconds
            )

        return self._server_call_client.redirect_call(
            redirect_call_request=redirect_call_request,
            **kwargs
        )

    @distributed_trace()
    def play_audio(
        self,
        call_locator,  # type: CallLocator
        audio_url,  # type: str
        is_looped=False,  # type: bool
        **kwargs  # type: Any
    ):  # type: (...) -> PlayAudioResult
        """Redirect the call.

        :param call_locator: Required. The call locator.
        :type call_locator: ~azure.communication.callingserver.models.CallLocator
        :param audio_url: Required. The media resource uri of the play audio request.
         Currently only Wave file (.wav) format audio prompts are supported.
         More specifically, the audio content in the wave file must be mono (single-channel),
         16-bit samples with a 16,000 (16KHz) sampling rate.
        :type audio_url: str
        :param is_looped: The flag indicating whether audio file needs to be played in loop or
         not.
        :type is_looped: bool
        :keyword operation_context: The value to identify context of the operation.
        :paramtype operation_context: str
        :keyword audio_file_id: An id for the media in the AudioFileUri, using which we cache the media
         resource.
        :paramtype audio_file_id: str
        :keyword callback_uri: The callback Uri to receive PlayAudio status notifications.
        :paramtype callback_uri: str
        :return: PlayAudioResult
        :rtype: ~azure.communication.callingserver.PlayAudioResult
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        operation_context = kwargs.pop("operation_context", None)
        audio_file_id = kwargs.pop("audio_file_id", None)
        callback_uri = kwargs.pop("callback_uri", None)

        play_audio_request = PlayAudioWithCallLocatorRequestConverter.convert(
            call_locator=serialize_call_locator(call_locator),
            audio_url=audio_url,
            loop=is_looped,
            operation_context=operation_context,
            audio_file_id=audio_file_id,
            callback_uri=callback_uri
            )

        return self._server_call_client.play_audio(
            play_audio_request=play_audio_request,
            **kwargs
        )

    @distributed_trace()
    def play_audio_to_participant(
        self,
        call_locator,  # type: CallLocator
        participant,  # type: CommunicationIdentifier
        audio_url,  # type: str
        is_looped: bool = False,
        **kwargs  # type: Any
    ):  # type: (...) -> PlayAudioResult
        """Redirect the call.

        :param call_locator: Required. The call locator.
        :type call_locator: ~azure.communication.callingserver.models.CallLocator
        :param participant: Required. The identifier of the play audio target participant.
        :type participant: ~azure.communication.callingserver.models.CommunicationIdentifier
        :param audio_url: Required. The media resource uri of the play audio request.
         Currently only Wave file (.wav) format audio prompts are supported.
         More specifically, the audio content in the wave file must be mono (single-channel),
         16-bit samples with a 16,000 (16KHz) sampling rate.
        :type audio_url: str
        :param is_looped: The flag indicating whether audio file needs to be played in loop or
         not.
        :type is_looped: bool
        :keyword operation_context: The value to identify context of the operation.
        :paramtype operation_context: str
        :keyword audio_file_id: An id for the media in the AudioFileUri, using which we cache the media
         resource.
        :paramtype audio_file_id: str
        :keyword callback_uri: The callback Uri to receive PlayAudio status notifications.
        :paramtype callback_uri: str
        :return: PlayAudioResult
        :rtype: ~azure.communication.callingserver.PlayAudioResult
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        operation_context = kwargs.pop("operation_context", None)
        audio_file_id = kwargs.pop("audio_file_id", None)
        callback_uri = kwargs.pop("callback_uri", None)
        play_audio_to_participant_request = PlayAudioToParticipantWithCallLocatorRequestConverter.convert(
            call_locator=serialize_call_locator(call_locator),
            identifier=serialize_identifier(participant),
            audio_url=audio_url,
            loop=is_looped,
            operation_context=operation_context,
            audio_file_id=audio_file_id,
            callback_uri=callback_uri
            )

        return self._server_call_client.participant_play_audio(
            play_audio_to_participant_request=play_audio_to_participant_request,
            **kwargs
        )

    @distributed_trace()
    def add_participant( # pylint: disable=too-many-arguments
        self,
        call_locator,  # type: CallLocator
        participant,  # type: CommunicationIdentifier
        callback_uri,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> AddParticipantResult
        """Add a participant to the call.

        :param call_locator: Required. The call locator.
        :type call_locator: ~azure.communication.callingserver.models.CallLocator
        :param participant: Required. The participant to be added to the call.
        :type participant: ~azure.communication.callingserver.models.CommunicationIdentifier
        :param callback_uri: Required. The callback URI.
        :type callback_uri: str
        :keyword alternate_caller_id: The alternate caller id.
        :paramtype alternate_caller_id: str
        :keyword operation_context: The operation context.
        :paramtype operation_context: str
        :return: AddParticipantResult
        :rtype: ~azure.communication.callingserver.AddParticipantResult
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        alternate_caller_id = kwargs.pop("alternate_caller_id", None)
        operation_context = kwargs.pop("operation_context", None)

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

        return self._server_call_client.add_participant(
            add_participant_with_call_locator_request=add_participant_with_call_locator_request,
            **kwargs
        )

    @distributed_trace()
    def remove_participant(
        self,
        call_locator,  # type: CallLocator
        participant,  # type: CommunicationIdentifier
        **kwargs  # type: Any
    ): # type: (...) -> None
        """Remove participant from the call using identifier.

        :param call_locator: Required. The call locator.
        :type call_locator: ~azure.communication.callingserver.models.CallLocator
        :param participant: Required. The identifier of the participant to be removed from the call.
        :type participant: ~azure.communication.callingserver.models.CommunicationIdentifier
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        remove_participant_with_call_locator_request = RemoveParticipantWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator),
            serialize_identifier(participant)
            )

        return self._server_call_client.remove_participant(
            remove_participant_with_call_locator_request=remove_participant_with_call_locator_request,
            **kwargs
        )

    @distributed_trace()
    def list_participants(
            self,
            call_locator,  # type: CallLocator
            **kwargs  # type: Any
        ): # type: (...) -> List[CallParticipant]
        """Get participants from a server call.

        :param call_locator: Required. The call locator.
        :type call_locator: ~azure.communication.callingserver.models.CallLocator
        :return: List[CallParticipant]
        :rtype: List[~azure.communication.callingserver.models.CallParticipant]
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        get_all_participants_with_call_locator_request = GetAllParticipantsWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator)
            )

        return self._server_call_client.get_participants(
            get_all_participants_with_call_locator_request=get_all_participants_with_call_locator_request,
            **kwargs
        )

    @distributed_trace()
    def get_participant(
            self,
            call_locator,  # type: CallLocator
            participant,  # type: CommunicationIdentifier
            **kwargs  # type: Any
        ): # type: (...) -> List[CallParticipant]
        """Get participant from the call using identifier.

        :param call_locator: Required. The call locator.
        :type call_locator: ~azure.communication.callingserver.models.CallLocator
        :param participant: Required. The identifier of the target participant.
        :type participant: ~azure.communication.callingserver.models.CommunicationIdentifier
        :return: list of CallParticipant
        :rtype: List[~azure.communication.callingserver.models.CallParticipant]
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        get_participant_with_call_locator_request = GetParticipantWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator),
            serialize_identifier(participant)
            )

        return self._server_call_client.get_participant(
            get_participant_with_call_locator_request=get_participant_with_call_locator_request,
            **kwargs
        )

    @distributed_trace()
    def cancel_media_operation(
        self,
        call_locator,  # type: CallLocator
        media_operation_id,  # type: str
        **kwargs  # type: Any
    ): # type: (...) -> None
        """Cancel media operation.

        :param call_locator: Required. The call locator.
        :type call_locator: ~azure.communication.callingserver.models.CallLocator
        :param media_operation_id: Required. The operationId of the media operation to cancel.
        :type media_operation_id: str
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        cancel_media_operation_request = CancelMediaOperationWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator),
            media_operation_id=media_operation_id
            )

        return self._server_call_client.cancel_media_operation(
            cancel_media_operation_request=cancel_media_operation_request,
            **kwargs
        )

    @distributed_trace()
    def cancel_participant_media_operation(
        self,
        call_locator,  # type: CallLocator
        participant,  # type: CommunicationIdentifier
        media_operation_id,  # type: str
        **kwargs  # type: Any
    ): # type: (...) -> None
        """Cancel media operation for a participant.

        :param call_locator: Required. The call locator.
        :type call_locator: ~azure.communication.callingserver.models.CallLocator
        :param participant: Required. The identifier of the participant.
        :type participant: ~azure.communication.callingserver.models.CommunicationIdentifier
        :param media_operation_id: Required. The operationId of the media operation to cancel.
        :type media_operation_id: str
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        cancel_participant_media_operation_request = \
        CancelParticipantMediaOperationWithCallLocatorRequestConverter.convert(
            serialize_call_locator(call_locator),
            serialize_identifier(participant),
            media_operation_id=media_operation_id
            )

        return self._server_call_client.cancel_participant_media_operation(
            cancel_participant_media_operation_request=cancel_participant_media_operation_request,
            **kwargs
            )

    @distributed_trace()
    def start_recording( # pylint: disable=too-many-arguments
        self,
        call_locator,  # type: CallLocator
        recording_state_callback_uri,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> StartCallRecordingResult
        """Start recording the call.

        :param call_locator: Required. The call locator.
        :type call_locator: ~azure.communication.callingserver.models.CallLocator
        :param recording_state_callback_uri: Required. The uri to send notifications to.
        :type recording_state_callback_uri: str
        :keyword recording_content_type: The content type of call recording. Possible values include:
         "audio", "audioVideo".
        :paramtype recording_content_type: str or
         ~azure.communication.callingserver.models.RecordingContentType
        :keyword recording_channel_type: The channel type of call recording. Possible values include:
        "mixed", "unmixed".
        :paramtype recording_channel_type: str or
         ~azure.communication.callingserver.models.RecordingChannelType
        :keyword recording_format_type: The format type of call recording. Possible values include: "wav",
         "mp3", "mp4".
        :paramtype recording_format_type: str or
         ~azure.communication.callingserver.models.RecordingFormatType
        :return: StartCallRecordingResult
        :rtype: ~azure.communication.callingserver.StartCallRecordingResult
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        recording_content_type = kwargs.pop("recording_content_type", None)
        recording_channel_type = kwargs.pop("recording_channel_type", None)
        recording_format_type = kwargs.pop("recording_format_type", None)

        start_call_recording_with_calllocator_request = StartCallRecordingWithCallLocatorRequest(
            call_locator=serialize_call_locator(call_locator),
            recording_state_callback_uri=recording_state_callback_uri,
            recording_content_type=kwargs.pop("content_type", None),
            recording_channel_type=kwargs.pop("channel_type", None),
            recording_format_type=kwargs.pop("format_type", None),
            **kwargs
        )

        return self._server_call_client.start_recording(
           start_call_recording_with_call_locator_request=start_call_recording_with_calllocator_request,
            **kwargs
        )

    @distributed_trace()
    def pause_recording(
        self,
        recording_id,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> None
        """Pause recording the call.

        :param recording_id: Required. The recording id.
        :type recording_id: str
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return self._server_call_client.pause_recording(
            recording_id=recording_id,
            **kwargs
        )

    @distributed_trace()
    def resume_recording(
        self,
        recording_id,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> None
        """Resume recording the call.

        :param recording_id: Required. The recording id.
        :type recording_id: str
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return self._server_call_client.resume_recording(
            recording_id=recording_id,
            **kwargs
        )

    @distributed_trace()
    def stop_recording(
        self,
        recording_id,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> None
        """Stop recording the call.

        :param recording_id: Required. The recording id.
        :type recording_id: str
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return self._server_call_client.stop_recording(
            recording_id=recording_id,
            **kwargs
        )

    @distributed_trace()
    def get_recording_properties(
        self,
        recording_id,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> CallRecordingProperties
        """Get recording properities.

        :param recording_id: Required. The recording id.
        :type recording_id: str
        :return: CallRecordingProperties
        :rtype: ~azure.communication.callingserver.CallRecordingProperties
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return self._server_call_client.get_recording_properties(
            recording_id=recording_id,
            **kwargs
        )

    @distributed_trace()
    def download(
        self,
        content_url,  # type: str
        **kwargs  # type: Any
    ):  # type: (...) -> ContentStreamDownloader
        """Download using content url.

        :param content_url: Required. The content url.
        :type content_url: str
        :keyword start_range: Http range where download start.
        :paramtype start_range: int
        :keyword end_range: Http range where download end.
        :paramtype end_range: int
        :keyword parallel_download_options: The options for parallel download.
        :paramtype parallel_download_options: ~azure.communication.callingserver.models.ParallelDownloadOptions
        :return: ContentStreamDownloader
        :rtype: ~azure.communication.callingserver.ContentStreamDownloader
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        start_range = kwargs.pop("start_range", None)
        end_range = kwargs.pop("end_range", None)
        parallel_download_options = kwargs.pop("parallel_download_options", None)
        # pylint:disable=protected-access
        content_downloader = ContentDownloader(
            self._callingserver_service_client._client,
            self._callingserver_service_client._serialize,
            self._callingserver_service_client._deserialize,
            self._callingserver_service_client._config)

        return ContentStreamDownloader(
            content_url,
            content_downloader,
            self._callingserver_service_client._config,
            **kwargs
        )

    @distributed_trace()
    def delete_recording(
        self,
        content_delete_url, # type: str
        **kwargs # type: Any
    ): # type: (...) -> None
        """Deletes the recording and all its related content.

        :param content_delete_url: Required. The content delete url.
        :type content_delete_url: str

        """
        # pylint: disable=protected-access
        if not content_delete_url:
            raise ValueError("content_delete_url can not be None")

        url = content_delete_url
        uri_to_sign_with = CallingServerUtils.get_url_to_sign_request_with(self._endpoint, url)

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
        request = client.delete(url, query_parameters, header_parameters) #pylint: disable=specify-parameter-names-in-call
        pipeline_response = client._pipeline.run(request, **kwargs)
        response = pipeline_response.http_response
        if response.status_code not in [200]:
            map_error(status_code=response.status_code,
                        response=response, error_map=error_map)
            raise HttpResponseError(response=response)
