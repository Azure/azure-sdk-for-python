# pylint: disable=too-many-lines
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING, Optional, List, Union, Dict, overload
from urllib.parse import urlparse
import warnings

from typing_extensions import Literal

from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace

from ._version import SDK_MONIKER
from ._api_versions import DEFAULT_VERSION
from ._utils import serialize_phone_identifier, serialize_identifier, process_repeatability_first_sent
from ._models import (
    CallParticipant,
    CallConnectionProperties,
    AddParticipantResult,
    RemoveParticipantResult,
    TransferCallResult,
    MuteParticipantResult,
    SendDtmfTonesResult,
    CallInvite,
    CancelAddParticipantOperationResult,
)
from ._generated._client import AzureCommunicationCallAutomationService
from ._generated.models import (
    AddParticipantRequest,
    RemoveParticipantRequest,
    TransferToParticipantRequest,
    PlayRequest,
    RecognizeRequest,
    ContinuousDtmfRecognitionRequest,
    SendDtmfTonesRequest,
    DtmfOptions,
    SpeechOptions,
    PlayOptions,
    RecognizeOptions,
    MuteParticipantsRequest,
    CancelAddParticipantRequest,
    CustomCallingContext,
    StartTranscriptionRequest,
    StopTranscriptionRequest,
    UpdateTranscriptionRequest,
    HoldRequest,
    UnholdRequest,
    StartMediaStreamingRequest,
    StopMediaStreamingRequest,
    InterruptAudioAndAnnounceRequest,
)
from ._generated.models._enums import RecognizeInputType
from ._shared.auth_policy_utils import get_authentication_policy
from ._shared.utils import parse_connection_str
from ._credential.call_automation_auth_policy_utils import get_call_automation_auth_policy
from ._credential.credential_utils import get_custom_enabled, get_custom_url

if TYPE_CHECKING:
    from ._call_automation_client import CallAutomationClient
    from ._generated.models._enums import DtmfTone
    from ._shared.models import PhoneNumberIdentifier, CommunicationIdentifier
    from ._models import FileSource, TextSource, SsmlSource, RecognitionChoice
    from azure.core.credentials import TokenCredential, AzureKeyCredential


class CallConnectionClient:  # pylint: disable=too-many-public-methods
    """A client to interact with an ongoing call. This client can be used to do mid-call actions,
    such as Transfer and Play Media. Call must be established to perform these actions.

    :param endpoint: The endpoint of the Azure Communication resource.
    :type endpoint: str
    :param credential: The credentials with which to authenticate.
    :type credential: ~azure.core.credentials.TokenCredential
     or ~azure.core.credentials.AzureKeyCredential
    :param call_connection_id: Call Connection ID of ongoing call.
    :type call_connection_id: str
    :keyword api_version: Azure Communication Call Automation API version.
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union["TokenCredential", "AzureKeyCredential"],
        call_connection_id: str,
        *,
        api_version: Optional[str] = None,
        **kwargs,
    ) -> None:
        call_automation_client = kwargs.get("_callautomation_client", None)
        if call_automation_client is None:
            if not credential:
                raise ValueError("credential can not be None")
            try:
                if not endpoint.lower().startswith("http"):
                    endpoint = "https://" + endpoint
            except AttributeError:
                raise ValueError("Host URL must be a string")  # pylint: disable=raise-missing-from
            parsed_url = urlparse(endpoint.rstrip("/"))
            if not parsed_url.netloc:
                raise ValueError(f"Invalid URL: {format(endpoint)}")

            custom_enabled = get_custom_enabled()
            custom_url = get_custom_url()
            if custom_enabled and custom_url is not None:
                self._client = AzureCommunicationCallAutomationService(
                    custom_url,
                    credential,
                    api_version=api_version or DEFAULT_VERSION,
                    authentication_policy=get_call_automation_auth_policy(custom_url, credential, acs_url=endpoint),
                    sdk_moniker=SDK_MONIKER,
                    **kwargs,
                )
            else:
                self._client = AzureCommunicationCallAutomationService(
                    endpoint,
                    credential,
                    api_version=api_version or DEFAULT_VERSION,
                    authentication_policy=get_authentication_policy(endpoint, credential),
                    sdk_moniker=SDK_MONIKER,
                    **kwargs,
                )
        else:
            self._client = call_automation_client

        self._call_connection_id = call_connection_id
        self._call_connection_client = self._client.call_connection
        self._call_media_client = self._client.call_media

    @classmethod
    def from_connection_string(cls, conn_str: str, call_connection_id: str, **kwargs) -> "CallConnectionClient":
        """Create CallConnectionClient from a Connection String.

        :param conn_str: A connection string to an Azure Communication Service resource.
        :type conn_str: str
        :param call_connection_id: Call Connection Id of ongoing call.
        :type call_connection_id: str
        :return: CallConnectionClient
        :rtype: ~azure.communication.callautomation.CallConnectionClient
        """
        endpoint, access_key = parse_connection_str(conn_str)
        return cls(endpoint, access_key, call_connection_id, **kwargs)

    @classmethod
    def _from_callautomation_client(
        cls, callautomation_client: "CallAutomationClient", call_connection_id: str
    ) -> "CallConnectionClient":
        """Internal constructor for sharing the pipeline with CallAutomationClient.

        :param callautomation_client: An existing callautomation client.
        :type callautomation_client: ~azure.communication.callautomation.CallAutomationClient
        :param call_connection_id: Call Connection Id of ongoing call.
        :type call_connection_id: str
        :return: CallConnectionClient
        :rtype: ~azure.communication.callautomation.CallConnectionClient
        """
        return cls(None, None, call_connection_id, _callautomation_client=callautomation_client)

    @distributed_trace
    def get_call_properties(self, **kwargs) -> CallConnectionProperties:
        """Get the latest properties of this call.

        :return: CallConnectionProperties
        :rtype: ~azure.communication.callautomation.CallConnectionProperties
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        call_properties = self._call_connection_client.get_call(call_connection_id=self._call_connection_id, **kwargs)
        return CallConnectionProperties._from_generated(call_properties)  # pylint:disable=protected-access

    @distributed_trace
    def hang_up(self, is_for_everyone: bool, **kwargs) -> None:
        """Hangup this call.

        :param is_for_everyone: Determine if this call should be ended for all participants.
        :type is_for_everyone: bool
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if is_for_everyone:
            process_repeatability_first_sent(kwargs)
            self._call_connection_client.terminate_call(self._call_connection_id, **kwargs)
        else:
            self._call_connection_client.hangup_call(self._call_connection_id, **kwargs)

    @distributed_trace
    def get_participant(self, target_participant: "CommunicationIdentifier", **kwargs) -> "CallParticipant":
        """Get details of a participant in this call.

        :param target_participant: The participant to retrieve.
        :type target_participant: ~azure.communication.callautomation.CommunicationIdentifier
        :return: CallParticipant
        :rtype: ~azure.communication.callautomation.CallParticipant
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        participant = self._call_connection_client.get_participant(
            self._call_connection_id, target_participant.raw_id, **kwargs
        )
        return CallParticipant._from_generated(participant)  # pylint:disable=protected-access

    @distributed_trace
    def list_participants(self, **kwargs) -> ItemPaged[CallParticipant]:
        """List all participants in this call.

        :return: An iterable of CallParticipant
        :rtype: ~azure.core.paging.ItemPaged[azure.communication.callautomation.CallParticipant]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._call_connection_client.get_participants(
            self._call_connection_id,
            cls=lambda participants: [
                CallParticipant._from_generated(p) for p in participants  # pylint:disable=protected-access
            ],
            **kwargs,
        )

    @distributed_trace
    def transfer_call_to_participant(
        self,
        target_participant: "CommunicationIdentifier",
        *,
        operation_context: Optional[str] = None,
        operation_callback_url: Optional[str] = None,
        transferee: Optional["CommunicationIdentifier"] = None,
        sip_headers: Optional[Dict[str, str]] = None,
        voip_headers: Optional[Dict[str, str]] = None,
        source_caller_id_number: Optional["PhoneNumberIdentifier"] = None,
        **kwargs,
    ) -> TransferCallResult:
        """Transfer this call to another participant.

        :param target_participant: The transfer target.
        :type target_participant: CommunicationIdentifier
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str
        :keyword operation_callback_url: Set a callback URL that overrides the default callback URL set
         by CreateCall/AnswerCall for this operation.
         This setup is per-action. If this is not set, the default callback URL set by
         CreateCall/AnswerCall will be used.
        :paramtype operation_callback_url: str or None
        :keyword transferee: Transferee is the participant who is transferred away.
        :paramtype transferee: ~azure.communication.callautomation.CommunicationIdentifier or None
        :keyword sip_headers: Custom context for PSTN
        :paramtype sip_headers: dict[str, str]
        :keyword voip_headers: Custom context for VOIP
        :paramtype voip_headers: dict[str, str]
        :keyword source_caller_id_number: The source caller Id, a phone number, that's will be used as the
         transferor's(Contoso) caller id when transfering a call a pstn target.
        :paramtype source_caller_id_number: ~azure.communication.callautomation.PhoneNumberIdentifier or None
        :return: TransferCallResult
        :rtype: ~azure.communication.callautomation.TransferCallResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        user_custom_context = (
            CustomCallingContext(voip_headers=voip_headers, sip_headers=sip_headers)
            if sip_headers or voip_headers
            else None
        )
        request = TransferToParticipantRequest(
            target_participant=serialize_identifier(target_participant),
            operation_context=operation_context,
            operation_callback_uri=operation_callback_url,
            custom_calling_context=user_custom_context,
            source_caller_id_number=serialize_phone_identifier(source_caller_id_number),
        )
        process_repeatability_first_sent(kwargs)
        if transferee:
            request.transferee = serialize_identifier(transferee)
        result = self._call_connection_client.transfer_to_participant(self._call_connection_id, request, **kwargs)
        return TransferCallResult._from_generated(result)  # pylint:disable=protected-access

    @distributed_trace
    def add_participant(
        self,
        target_participant: "CommunicationIdentifier",
        *,
        invitation_timeout: Optional[int] = None,
        operation_context: Optional[str] = None,
        source_caller_id_number: Optional["PhoneNumberIdentifier"] = None,
        source_display_name: Optional[str] = None,
        operation_callback_url: Optional[str] = None,
        sip_headers: Optional[Dict[str, str]] = None,
        voip_headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> AddParticipantResult:
        """Add a participant to this call.

        :param target_participant: The participant being added.
        :type target_participant: ~azure.communication.callautomation.CommunicationIdentifier
        :keyword invitation_timeout: Timeout to wait for the invited participant to pickup.
         The maximum value of this is 180 seconds.
        :paramtype invitation_timeout: int or None
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str or None
        :keyword source_caller_id_number: The source caller Id, a phone number,
         that's shown to the PSTN participant being invited.
         Required only when calling a PSTN callee.
        :paramtype source_caller_id_number: ~azure.communication.callautomation.PhoneNumberIdentifier or None
        :keyword source_display_name: Display name of the caller.
        :paramtype source_display_name: str or None
        :keyword operation_callback_url: Set a callback URL that overrides the default callback URL set
         by CreateCall/AnswerCall for this operation.
         This setup is per-action. If this is not set, the default callback URL set by
         CreateCall/AnswerCall will be used.
        :paramtype operation_callback_url: str or None
        :keyword sip_headers: Sip Headers for PSTN Call
        :paramtype sip_headers: Dict[str, str] or None
        :keyword voip_headers: Voip Headers for Voip Call
        :paramtype voip_headers: Dict[str, str] or None
        :return: AddParticipantResult
        :rtype: ~azure.communication.callautomation.AddParticipantResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Backwards compatibility with old API signature
        if isinstance(target_participant, CallInvite):
            source_caller_id_number = source_caller_id_number or target_participant.source_caller_id_number
            source_display_name = source_display_name or target_participant.source_display_name
            target_participant = target_participant.target

        user_custom_context = None
        if sip_headers or voip_headers:
            user_custom_context = CustomCallingContext(voip_headers=voip_headers, sip_headers=sip_headers)
        add_participant_request = AddParticipantRequest(
            participant_to_add=serialize_identifier(target_participant),
            source_caller_id_number=serialize_phone_identifier(source_caller_id_number),
            source_display_name=source_display_name,
            invitation_timeout_in_seconds=invitation_timeout,
            operation_context=operation_context,
            operation_callback_uri=operation_callback_url,
            custom_calling_context=user_custom_context,
        )
        process_repeatability_first_sent(kwargs)
        response = self._call_connection_client.add_participant(
            self._call_connection_id, add_participant_request, **kwargs
        )
        return AddParticipantResult._from_generated(response)  # pylint:disable=protected-access

    @distributed_trace
    def remove_participant(
        self,
        target_participant: "CommunicationIdentifier",
        *,
        operation_context: Optional[str] = None,
        operation_callback_url: Optional[str] = None,
        **kwargs,
    ) -> RemoveParticipantResult:
        """Remove a participant from this call.

        :param  target_participant: The participant being removed.
        :type target_participant: ~azure.communication.callautomation.CommunicationIdentifier
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str
        :keyword operation_callback_url: Set a callback URL that overrides the default callback URL set
         by CreateCall/AnswerCall for this operation.
         This setup is per-action. If this is not set, the default callback URL set by
         CreateCall/AnswerCall will be used.
        :paramtype operation_callback_url: str or None
        :return: RemoveParticipantResult
        :rtype: ~azure.communication.callautomation.RemoveParticipantResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        remove_participant_request = RemoveParticipantRequest(
            participant_to_remove=serialize_identifier(target_participant),
            operation_context=operation_context,
            operation_callback_uri=operation_callback_url,
        )
        process_repeatability_first_sent(kwargs)
        response = self._call_connection_client.remove_participant(
            self._call_connection_id, remove_participant_request, **kwargs
        )

        return RemoveParticipantResult._from_generated(response)  # pylint:disable=protected-access

    @overload
    def play_media(
        self,
        play_source: Union[Union['FileSource', 'TextSource', 'SsmlSource'],
                           List[Union['FileSource', 'TextSource', 'SsmlSource']]],
        play_to: List['CommunicationIdentifier'],
        *,
        loop: bool = False,
        operation_context: Optional[str] = None,
        operation_callback_url: Optional[str] = None,
        **kwargs
    ) -> None:
        """Play media to specific participant(s) in this call.

        :param play_source: A PlaySource representing the source to play.
        :type play_source: ~azure.communication.callautomation.FileSource or
         ~azure.communication.callautomation.TextSource or
         ~azure.communication.callautomation.SsmlSource or
         list[~azure.communication.callautomation.FileSource] or
         list[~azure.communication.callautomation.TextSource] or
         list[~azure.communication.callautomation.SsmlSource]
        :param play_to: The targets to play media to. Default value is 'all', to play media
         to all participants in the call.
        :type play_to: list[~azure.communication.callautomation.CommunicationIdentifier]
        :keyword loop: Whether the media should be repeated until cancelled.
        :paramtype loop: bool
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str or None
        :keyword operation_callback_url: Set a callback URL that overrides the default callback URL set
         by CreateCall/AnswerCall for this operation.
         This setup is per-action. If this is not set, the default callback URL set by
         CreateCall/AnswerCall will be used.
        :paramtype operation_callback_url: str or None
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def play_media(
        self,
        play_source: Union[Union['FileSource', 'TextSource', 'SsmlSource'],
                           List[Union['FileSource', 'TextSource', 'SsmlSource']]],
        play_to: Literal["all"] = 'all',
        *,
        loop: bool = False,
        operation_context: Optional[str] = None,
        operation_callback_url: Optional[str] = None,
        interrupt_call_media_operation: bool = False,
        **kwargs
    ) -> None:
        """Play media to specific participant(s) in this call.

        :param play_source: A PlaySource representing the source to play.
        :type play_source: ~azure.communication.callautomation.FileSource or
         ~azure.communication.callautomation.TextSource or
         ~azure.communication.callautomation.SsmlSource or
         list[~azure.communication.callautomation.FileSource] or
         list[~azure.communication.callautomation.TextSource] or
         list[~azure.communication.callautomation.SsmlSource]
        :param play_to: The targets to play media to. Default value is 'all', to play media
         to all participants in the call.
        :type play_to: list[~azure.communication.callautomation.CommunicationIdentifier]
        :keyword loop: Whether the media should be repeated until cancelled.
        :paramtype loop: bool
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str or None
        :keyword operation_callback_url: Set a callback URL that overrides the default callback URL set
         by CreateCall/AnswerCall for this operation.
         This setup is per-action. If this is not set, the default callback URL set by
         CreateCall/AnswerCall will be used.
        :paramtype operation_callback_url: str or None
        :keyword interrupt_call_media_operation: If set, media will take priority over other existing
         queued-up/currently-processing requests. This is applicable only when play_to set to all.
        :paramtype interrupt_call_media_operation: bool
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def play_media(
        self,
        play_source: Union[Union['FileSource', 'TextSource', 'SsmlSource'],
                           List[Union['FileSource', 'TextSource', 'SsmlSource']]],
        play_to: Union[Literal["all"], List['CommunicationIdentifier']] = 'all',
        *,
        loop: bool = False,
        operation_context: Optional[str] = None,
        operation_callback_url: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Play media to specific participant(s) in this call.

        :param play_source: A PlaySource representing the source to play.
        :type play_source: ~azure.communication.callautomation.FileSource or
         ~azure.communication.callautomation.TextSource or
         ~azure.communication.callautomation.SsmlSource or
         list[~azure.communication.callautomation.FileSource] or
         list[~azure.communication.callautomation.TextSource] or
         list[~azure.communication.callautomation.SsmlSource]
        :param play_to: The targets to play media to. Default value is 'all', to play media
         to all participants in the call.
        :type play_to: list[~azure.communication.callautomation.CommunicationIdentifier]
        :keyword loop: Whether the media should be repeated until cancelled.
        :paramtype loop: bool
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str or None
        :keyword operation_callback_url: Set a callback URL that overrides the default callback URL set
         by CreateCall/AnswerCall for this operation.
         This setup is per-action. If this is not set, the default callback URL set by
         CreateCall/AnswerCall will be used.
        :paramtype operation_callback_url: str or None
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._play_media(
            play_source=play_source,
            play_to=play_to,
            loop=loop,
            operation_context=operation_context,
            operation_callback_url=operation_callback_url,
            **kwargs,
        )

    def _play_media(
        self,
        play_source: Union[Union['FileSource', 'TextSource', 'SsmlSource'],
                           List[Union['FileSource', 'TextSource', 'SsmlSource']]],
        play_to: Union[Literal["all"], List['CommunicationIdentifier']] = 'all',
        *,
        loop: bool = False,
        operation_context: Optional[str] = None,
        operation_callback_url: Optional[str] = None,
        interrupt_call_media_operation: Optional[bool] = False,
        **kwargs
    ) -> None:
        """Play media to specific participant(s) in this call.

        :param play_source: A PlaySource representing the source to play.
        :type play_source: ~azure.communication.callautomation.FileSource or
         ~azure.communication.callautomation.TextSource or
         ~azure.communication.callautomation.SsmlSource or
         list[~azure.communication.callautomation.FileSource] or
         list[~azure.communication.callautomation.TextSource] or
         list[~azure.communication.callautomation.SsmlSource]
        :param play_to: The targets to play media to. Default value is 'all', to play media
         to all participants in the call.
        :type play_to: list[~azure.communication.callautomation.CommunicationIdentifier]
        :keyword loop: Whether the media should be repeated until cancelled.
        :paramtype loop: bool
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str or None
        :keyword operation_callback_url: Set a callback URL that overrides the default callback URL set
         by CreateCall/AnswerCall for this operation.
         This setup is per-action. If this is not set, the default callback URL set by
         CreateCall/AnswerCall will be used.
        :paramtype operation_callback_url: str or None
        :keyword interrupt_call_media_operation: If set play can barge into other existing
         queued-up/currently-processing requests.
        :paramtype interrupt_call_media_operation: bool
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        play_source_single: Optional[Union['FileSource', 'TextSource', 'SsmlSource']] = None
        play_sources: Optional[List[Union['FileSource', 'TextSource', 'SsmlSource']]] = None
        if isinstance(play_source, list):
            if play_source:  # Check if the list is not empty
                play_sources = play_source
        else:
            play_source_single = play_source

        audience = [] if play_to == "all" else [serialize_identifier(i) for i in play_to]
        interrupt_call_media_operation = interrupt_call_media_operation if play_to == "all" else False
        play_request = PlayRequest(
            play_sources=[play_source_single._to_generated()] if play_source_single else # pylint:disable=protected-access
            [source._to_generated() for source in play_sources] if play_sources else None,  # pylint:disable=protected-access
            play_to=audience,
            play_options=PlayOptions(loop=loop,interrupt_call_media_operation=interrupt_call_media_operation),
            operation_context=operation_context,
            operation_callback_uri=operation_callback_url,
            **kwargs,
        )
        self._call_media_client.play(self._call_connection_id, play_request)

    @distributed_trace
    def play_media_to_all(
        self,
        play_source: Union[Union['FileSource', 'TextSource', 'SsmlSource'],
                           List[Union['FileSource', 'TextSource', 'SsmlSource']]],
        *,
        loop: bool = False,
        operation_context: Optional[str] = None,
        operation_callback_url: Optional[str] = None,
        interrupt_call_media_operation: bool = False,
        **kwargs,
    ) -> None:
        """Play media to all participants in this call.

        :param play_source: A PlaySource representing the source to play.
        :type play_source: ~azure.communication.callautomation.FileSource or
         ~azure.communication.callautomation.TextSource or
         ~azure.communication.callautomation.SsmlSource or         
         list[~azure.communication.callautomation.FileSource] or
         list[~azure.communication.callautomation.TextSource] or
         list[~azure.communication.callautomation.SsmlSource]
        :keyword loop: Whether the media should be repeated until cancelled.
        :paramtype loop: bool
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str or None
        :keyword operation_callback_url: Set a callback URL that overrides the default callback URL set
         by CreateCall/AnswerCall for this operation.
         This setup is per-action. If this is not set, the default callback URL set by
         CreateCall/AnswerCall will be used.
        :paramtype operation_callback_url: str or None
        :keyword interrupt_call_media_operation: If set play can barge into other existing
         queued-up/currently-processing requests.
        :paramtype interrupt_call_media_operation: bool
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        warnings.warn(
            "The method 'play_media_to_all' is deprecated. Please use 'play_media' instead.", DeprecationWarning
        )
        self._play_media(
            play_source=play_source,
            loop=loop,
            operation_context=operation_context,
            operation_callback_url=operation_callback_url,
            interrupt_call_media_operation=interrupt_call_media_operation,
            **kwargs,
        )

    @distributed_trace
    def start_recognizing_media(
        self,
        input_type: Union[str, "RecognizeInputType"],
        target_participant: "CommunicationIdentifier",
        *,
        initial_silence_timeout: Optional[int] = None,
        play_prompt: Optional[Union[Union['FileSource', 'TextSource', 'SsmlSource'],
                                    List[Union['FileSource', 'TextSource', 'SsmlSource']]]] = None,
        interrupt_call_media_operation: bool = False,
        operation_context: Optional[str] = None,
        interrupt_prompt: bool = False,
        dtmf_inter_tone_timeout: Optional[int] = None,
        dtmf_max_tones_to_collect: Optional[int] = None,
        dtmf_stop_tones: Optional[List[str or "DtmfTone"]] = None,
        speech_language: Optional[str] = None,
        choices: Optional[List["RecognitionChoice"]] = None,
        end_silence_timeout: Optional[int] = None,
        speech_recognition_model_endpoint_id: Optional[str] = None,
        operation_callback_url: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Recognize inputs from specific participant in this call.

        :param input_type: Determines the type of the recognition.
        :type input_type: str or ~azure.communication.callautomation.RecognizeInputType
        :param target_participant: Target participant of DTMF tone recognition.
        :type target_participant: ~azure.communication.callautomation.CommunicationIdentifier
        :keyword initial_silence_timeout: Time to wait for first input after prompt in seconds (if any).
        :paramtype initial_silence_timeout: int
        :type play_prompt: ~azure.communication.callautomation.FileSource or
         ~azure.communication.callautomation.TextSource or
         ~azure.communication.callautomation.SsmlSource or         
         list[~azure.communication.callautomation.FileSource] or
         list[~azure.communication.callautomation.TextSource] or
         list[~azure.communication.callautomation.SsmlSource]
        :keyword interrupt_call_media_operation:
         If set recognize can barge into other existing queued-up/currently-processing requests.
        :paramtype interrupt_call_media_operation: bool
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str
        :keyword interrupt_prompt: Determines if we interrupt the prompt and start recognizing.
        :paramtype interrupt_prompt: bool
        :keyword dtmf_inter_tone_timeout: Time to wait between DTMF inputs to stop recognizing. Will be ignored
         unless input_type is 'dtmf' or 'speechOrDtmf'.
        :paramtype dtmf_inter_tone_timeout: int
        :keyword dtmf_max_tones_to_collect: Maximum number of DTMF tones to be collected. Will be ignored
         unless input_type is 'dtmf' or 'speechOrDtmf'.
        :paramtype dtmf_max_tones_to_collect: int
        :keyword dtmf_stop_tones: List of tones that will stop recognizing. Will be ignored
         unless input_type is 'dtmf' or 'speechOrDtmf'.
        :paramtype dtmf_stop_tones: list[str or ~azure.communication.callautomation.DtmfTone]
        :keyword speech_language: Speech language to be recognized, If not set default is en-US.
        :paramtype speech_language: str
        :keyword choices: Defines Ivr choices for recognize. Will be ignored unless input_type is 'choices'.
        :paramtype choices: list[~azure.communication.callautomation.RecognitionChoice]
        :keyword end_silence_timeout: The length of end silence when user stops speaking and cogservice
         send response. Will be ingored unless input_type is 'speech' or 'speechOrDtmf'.
        :paramtype end_silence_timeout: int
        :keyword speech_recognition_model_endpoint_id: Endpoint where the custom model was deployed.
        :paramtype speech_recognition_model_endpoint_id: str
        :keyword operation_callback_url: Set a callback URL that overrides the default callback URL set
         by CreateCall/AnswerCall for this operation.
         This setup is per-action. If this is not set, the default callback URL set by
         CreateCall/AnswerCall will be used.
        :paramtype operation_callback_url: str or None
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        options = RecognizeOptions(
            interrupt_prompt=interrupt_prompt,
            initial_silence_timeout_in_seconds=initial_silence_timeout,
            target_participant=serialize_identifier(target_participant),
            speech_language=speech_language,
            speech_recognition_model_endpoint_id=speech_recognition_model_endpoint_id,
        )

        play_prompt_single: Optional[Union['FileSource', 'TextSource', 'SsmlSource']] = None
        play_prompts: Optional[List[Union['FileSource', 'TextSource', 'SsmlSource']]] = None
        if isinstance(play_prompt, list):
            if play_prompt:  # Check if the list is not empty
                play_prompts = play_prompt
        else:
            play_prompt_single = play_prompt

        if input_type == RecognizeInputType.DTMF:
            dtmf_options = DtmfOptions(
                inter_tone_timeout_in_seconds=dtmf_inter_tone_timeout,
                max_tones_to_collect=dtmf_max_tones_to_collect,
                stop_tones=dtmf_stop_tones,
            )
            options.dtmf_options = dtmf_options
        elif input_type == RecognizeInputType.SPEECH:
            speech_options = SpeechOptions(
                end_silence_timeout_in_ms=end_silence_timeout * 1000 if end_silence_timeout is not None else None
            )
            options.speech_options = speech_options
        elif input_type == RecognizeInputType.SPEECH_OR_DTMF:
            dtmf_options = DtmfOptions(
                inter_tone_timeout_in_seconds=dtmf_inter_tone_timeout,
                max_tones_to_collect=dtmf_max_tones_to_collect,
                stop_tones=dtmf_stop_tones,
            )
            speech_options = SpeechOptions(
                end_silence_timeout_in_ms=end_silence_timeout * 1000 if end_silence_timeout is not None else None
            )
            options.dtmf_options = dtmf_options
            options.speech_options = speech_options
        elif input_type == RecognizeInputType.CHOICES:
            options.choices = [choice._to_generated() for choice in choices]  # pylint:disable=protected-access
        else:
            raise ValueError(f"Input type '{input_type}' is not supported.")

        recognize_request = RecognizeRequest(
            recognize_input_type=input_type,
            play_prompt=play_prompt_single._to_generated() if play_prompt_single else None,  # pylint:disable=protected-access
            play_prompts=[prompt._to_generated() for prompt in play_prompts] if play_prompts else None, # pylint:disable=protected-access
            interrupt_call_media_operation=interrupt_call_media_operation,
            operation_context=operation_context,
            recognize_options=options,
            operation_callback_uri=operation_callback_url,
        )
        self._call_media_client.recognize(self._call_connection_id, recognize_request, **kwargs)

    @distributed_trace
    def cancel_all_media_operations(self, **kwargs) -> None:
        """Cancels all the ongoing and queued media operations for this call.

        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._call_media_client.cancel_all_media_operations(self._call_connection_id, **kwargs)

    @distributed_trace
    def start_continuous_dtmf_recognition(
        self,
        target_participant: "CommunicationIdentifier",
        *,
        operation_context: Optional[str] = None,
        operation_callback_url: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Start continuous Dtmf recognition by subscribing to tones.

        :param target_participant: Target participant.
        :type target_participant: ~azure.communication.callautomation.CommunicationIdentifier
        :keyword operation_context: The value to identify context of the operation.
        :paramtype operation_context: str
        :keyword operation_callback_url: Set a callback URL that overrides the default callback URL set
         by CreateCall/AnswerCall for this operation.
         This setup is per-action. If this is not set, the default callback URL set by
         CreateCall/AnswerCall will be used.
        :paramtype operation_callback_url: str or None
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        continuous_dtmf_recognition_request = ContinuousDtmfRecognitionRequest(
            target_participant=serialize_identifier(target_participant),
            operation_context=operation_context,
            operation_callback_uri=operation_callback_url,
        )
        self._call_media_client.start_continuous_dtmf_recognition(
            self._call_connection_id, continuous_dtmf_recognition_request, **kwargs
        )

    @distributed_trace
    def stop_continuous_dtmf_recognition(
        self,
        target_participant: "CommunicationIdentifier",
        *,
        operation_context: Optional[str] = None,
        operation_callback_url: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Stop continuous Dtmf recognition by unsubscribing to tones.

        :param target_participant: Target participant.
        :type target_participant: ~azure.communication.callautomation.CommunicationIdentifier
        :keyword operation_context: The value to identify context of the operation.
        :paramtype operation_context: str
        :keyword operation_callback_url: Set a callback URL that overrides the default callback URL set
         by CreateCall/AnswerCall for this operation.
         This setup is per-action. If this is not set, the default callback URL set by
         CreateCall/AnswerCall will be used.
        :paramtype operation_callback_url: str or None
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        continuous_dtmf_recognition_request = ContinuousDtmfRecognitionRequest(
            target_participant=serialize_identifier(target_participant),
            operation_context=operation_context,
            operation_callback_uri=operation_callback_url,
        )
        self._call_media_client.stop_continuous_dtmf_recognition(
            self._call_connection_id, continuous_dtmf_recognition_request, **kwargs
        )

    @distributed_trace
    def send_dtmf_tones(
        self,
        tones: List[Union[str, "DtmfTone"]],
        target_participant: "CommunicationIdentifier",
        *,
        operation_context: Optional[str] = None,
        operation_callback_url: Optional[str] = None,
        **kwargs,
    ) -> SendDtmfTonesResult:
        """Send Dtmf tones to this call.

        :param tones: List of tones to be sent to target participant.
        :type tones: list[str or ~azure.communication.callautomation.DtmfTone]
        :param target_participant: Target participant.
        :type target_participant: ~azure.communication.callautomation.CommunicationIdentifier
        :keyword operation_context: The value to identify context of the operation.
        :paramtype operation_context: str
        :keyword operation_callback_url: Set a callback URL that overrides the default callback URL set
         by CreateCall/AnswerCall for this operation.
         This setup is per-action. If this is not set, the default callback URL set by
         CreateCall/AnswerCall will be used.
        :paramtype operation_callback_url: str or None
        :return: SendDtmfTonesResult
        :rtype: ~azure.communication.callautomation.SendDtmfTonesResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        send_dtmf_tones_request = SendDtmfTonesRequest(
            tones=tones,
            target_participant=serialize_identifier(target_participant),
            operation_context=operation_context,
            operation_callback_uri=operation_callback_url,
        )
        process_repeatability_first_sent(kwargs)
        response = self._call_media_client.send_dtmf_tones(self._call_connection_id, send_dtmf_tones_request, **kwargs)

        return SendDtmfTonesResult._from_generated(response)  # pylint:disable=protected-access

    @distributed_trace
    def mute_participant(
        self, target_participant: "CommunicationIdentifier", *, operation_context: Optional[str] = None, **kwargs
    ) -> MuteParticipantResult:
        """Mute participant from the call using identifier.

        :param target_participant: Participant to be muted from the call. Only ACS Users are supported.
        :type target_participant: ~azure.communication.callautomation.CommunicationIdentifier
        :keyword operation_context: Used by customers when calling mid-call actions to correlate the request to the
         response event.
        :paramtype operation_context: str
        :return: MuteParticipantResult
        :rtype: ~azure.communication.callautomation.MuteParticipantResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        mute_participants_request = MuteParticipantsRequest(
            target_participants=[serialize_identifier(target_participant)], operation_context=operation_context
        )
        process_repeatability_first_sent(kwargs)
        response = self._call_connection_client.mute(self._call_connection_id, mute_participants_request, **kwargs)
        return MuteParticipantResult._from_generated(response)  # pylint:disable=protected-access

    @distributed_trace
    def cancel_add_participant_operation(
        self,
        invitation_id: str,
        *,
        operation_context: Optional[str] = None,
        operation_callback_url: Optional[str] = None,
        **kwargs,
    ) -> CancelAddParticipantOperationResult:
        """Cancel add participant request sent out to a participant.

        :param invitation_id: The invitation ID that was used to add the participant.
        :type invitation_id: str
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str
        :keyword operation_callback_url: Set a callback URL that overrides the default callback URL set
         by CreateCall/AnswerCall for this operation.
         This setup is per-action. If this is not set, the default callback URL set by
         CreateCall/AnswerCall will be used.
        :paramtype operation_callback_url: str or None
        :return: CancelAddParticipantOperationResult
        :rtype: ~azure.communication.callautomation.CancelAddParticipantOperationResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        cancel_add_participant_request = CancelAddParticipantRequest(
            invitation_id=invitation_id,
            operation_context=operation_context,
            operation_callback_uri=operation_callback_url,
        )
        process_repeatability_first_sent(kwargs)
        response = self._call_connection_client.cancel_add_participant(
            self._call_connection_id, cancel_add_participant_request, **kwargs
        )
        return CancelAddParticipantOperationResult._from_generated(response)  # pylint:disable=protected-access

    @distributed_trace
    def start_transcription(
        self,
        *,
        locale: Optional[str] = None,
        operation_context: Optional[str] = None,
        speech_recognition_model_endpoint_id: Optional[str] = None,
        operation_callback_url: Optional[str] = None,
        **kwargs
    ) -> None:
        """Starts transcription in the call.

        :keyword locale: Defines Locale for the transcription e,g en-US.
        :paramtype locale: str
        :keyword operation_context: The value to identify context of the operation.
        :paramtype operation_context: str
        :keyword speech_recognition_model_endpoint_id: Endpoint where the custom model was deployed.
        :paramtype speech_recognition_model_endpoint_id: str
        :keyword operation_callback_url: Set a callback URL that overrides the default callback URL set
         by CreateCall/AnswerCall for this operation.
         This setup is per-action. If this is not set, the default callback URL set by
         CreateCall/AnswerCall will be used.
        :paramtype operation_callback_url: str or None
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        start_transcription_request = StartTranscriptionRequest(
            locale=locale,
            operation_context=operation_context,
            speech_recognition_model_endpoint_id=speech_recognition_model_endpoint_id,
            operation_callback_uri=operation_callback_url,
            **kwargs
        )
        self._call_media_client.start_transcription(self._call_connection_id, start_transcription_request)

    @distributed_trace
    def stop_transcription(
        self,
        *,
        operation_context: Optional[str] = None,
        operation_callback_url: Optional[str] = None,
        **kwargs) -> None:
        """Stops transcription in the call.

        :keyword operation_context: The value to identify context of the operation.
        :paramtype operation_context: str
        :keyword operation_callback_url: Set a callback URL that overrides the default callback URL set
         by CreateCall/AnswerCall for this operation.
         This setup is per-action. If this is not set, the default callback URL set by
         CreateCall/AnswerCall will be used.
        :paramtype operation_callback_url: str or None
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        stop_transcription_request = StopTranscriptionRequest(
            operation_context=operation_context,
            operation_callback_uri=operation_callback_url,
            **kwargs
        )
        self._call_media_client.stop_transcription(self._call_connection_id, stop_transcription_request)

    @distributed_trace
    def update_transcription(
        self,
        locale: str,
        *,
        operation_context: Optional[str] = None,
        speech_recognition_model_endpoint_id: Optional[str] = None,
        operation_callback_url: Optional[str] = None,
        **kwargs) -> None:
        """API to change transcription language.

        :param locale: Defines new locale for transcription.
        :type locale: str
        :keyword operation_context: The value to identify context of the operation.
        :paramtype operation_context: str
        :keyword speech_recognition_model_endpoint_id: Endpoint where the custom model was deployed.
        :paramtype speech_recognition_model_endpoint_id: str
        :keyword operation_callback_url: Set a callback URL that overrides the default callback URL set
         by CreateCall/AnswerCall for this operation.
         This setup is per-action. If this is not set, the default callback URL set by
         CreateCall/AnswerCall will be used.
        :paramtype operation_callback_url: str or None
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        update_transcription_request = UpdateTranscriptionRequest(
            locale=locale,
            operation_context=operation_context,
            speech_recognition_model_endpoint_id=speech_recognition_model_endpoint_id,
            operation_callback_uri=operation_callback_url,
            **kwargs
        )
        self._call_media_client.update_transcription(self._call_connection_id, update_transcription_request)

    @distributed_trace
    def hold(
        self,
        target_participant: "CommunicationIdentifier",
        *,
        play_source: Optional[Union["FileSource", "TextSource", "SsmlSource"]] = None,
        operation_context: Optional[str] = None,
        operation_callback_url: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Play media to specific participant(s) in this call.

        :param target_participant: The participant being added.
        :type target_participant: ~azure.communication.callautomation.CommunicationIdentifier
        :keyword play_source: A PlaySource representing the source to play.
        :paramtype play_source: ~azure.communication.callautomation.FileSource or
         ~azure.communication.callautomation.TextSource or
         ~azure.communication.callautomation.SsmlSource
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str or None
        :keyword operation_callback_url: Set a callback URL that overrides the default callback URL set
         by CreateCall/AnswerCall for this operation.
         This setup is per-action. If this is not set, the default callback URL set by
         CreateCall/AnswerCall will be used.
        :paramtype operation_callback_url: str or None
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        play_source_single: Optional[Union["FileSource", "TextSource", "SsmlSource"]] = None
        if isinstance(play_source, list):
            warnings.warn("Currently only single play source per request is supported.")
            if play_source:  # Check if the list is not empty
                play_source_single = play_source[0]
        else:
            play_source_single = play_source

        hold_request = HoldRequest(
            target_participant=serialize_identifier(target_participant),
            play_source_info=(
                play_source_single._to_generated() if play_source_single else None  # pylint:disable=protected-access
            ),
            operation_context=operation_context,
            operation_callback_uri=operation_callback_url,
            kwargs=kwargs,
        )

        self._call_media_client.hold(self._call_connection_id, hold_request)

    @distributed_trace
    def unhold(
        self, target_participant: "CommunicationIdentifier", *, operation_context: Optional[str] = None, **kwargs
    ) -> None:
        """Play media to specific participant(s) in this call.

        :param target_participant: The participant being added.
        :type target_participant: ~azure.communication.callautomation.CommunicationIdentifier
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str or None
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        unhold_request = UnholdRequest(
            target_participant=serialize_identifier(target_participant),
            operation_context=operation_context,
            kwargs=kwargs,
        )

        self._call_media_client.unhold(self._call_connection_id, unhold_request)

    @distributed_trace
    def start_media_streaming(
        self,
        *,
        operation_callback_url: Optional[str] = None,
        operation_context: Optional[str] = None,
        **kwargs
    ) -> None:
        """Starts media streaming in the call.
        
        :keyword operation_callback_url: (Optional) Set a callback URL that overrides the default 
         callback URL set by CreateCall/AnswerCall for this operation.
         This setup is per-action. If this is not set, the default callback URL set by
         CreateCall/AnswerCall will be used.
        :paramtype operation_callback_url: str or None
        :keyword operation_context: (Optional) Value that can be used to track this call and its associated events.
        :paramtype operation_context: str or None
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError: If there's an HTTP response error.
        """
        start_media_streaming_request=StartMediaStreamingRequest(
            operation_callback_uri=operation_callback_url,
            operation_context=operation_context
        )
        self._call_media_client.start_media_streaming(
            self._call_connection_id,
            start_media_streaming_request,
            **kwargs)

    @distributed_trace
    def stop_media_streaming(
        self,
        *,
        operation_callback_url: Optional[str] = None,
        operation_context: Optional[str] = None,
        **kwargs
    ) -> None:
        """Stops media streaming in the call.
        
        :keyword operation_callback_url: (Optional) Set a callback URL that overrides the default 
         callback URL set by CreateCall/AnswerCall for this operation.
         This setup is per-action. If this is not set, the default callback URL set by
         CreateCall/AnswerCall will be used.
        :paramtype operation_callback_url: str or None
        :keyword operation_context: (Optional) Value that can be used to track this call and its associated events.
        :paramtype operation_context: str or None
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError: If there's an HTTP response error.
        """
        stop_media_streaming_request=StopMediaStreamingRequest(
            operation_callback_uri=operation_callback_url,
            operation_context=operation_context
            )
        self._call_media_client.stop_media_streaming(
            self._call_connection_id,
            stop_media_streaming_request,
            **kwargs
            )

    @distributed_trace
    def interrupt_audio_and_announce(
        self,
        target_participant: "CommunicationIdentifier",
        play_sources: List[Union['FileSource', 'TextSource', 'SsmlSource']],
        *,
        operation_context: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Interrupt audio and announce to specific participant(s) in this call.

        :param target_participant: The participant being added.
        :type target_participant: ~azure.communication.callautomation.CommunicationIdentifier
        :param play_sources: A PlaySource representing the source to play.
        :type play_sources: list[~azure.communication.callautomation.FileSource] or
         list[~azure.communication.callautomation.TextSource] or
         list[~azure.communication.callautomation.SsmlSource]
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str or None
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        interrupt_audio_announce_request = InterruptAudioAndAnnounceRequest(
            play_sources=[source._to_generated() for source in play_sources] if play_sources else None, # pylint: disable=protected-access
            play_to=serialize_identifier(target_participant),
            operation_context=operation_context,
            kwargs=kwargs,
        )

        self._call_media_client.interrupt_audio_and_announce(
            self._call_connection_id,
            interrupt_audio_announce_request,
            **kwargs
            )
