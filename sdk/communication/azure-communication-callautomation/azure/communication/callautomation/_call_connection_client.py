# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING, Optional, List, Union, Dict
from urllib.parse import urlparse
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace
from ._version import SDK_MONIKER
from ._api_versions import DEFAULT_VERSION
from ._utils import (
    get_repeatability_guid,
    get_repeatability_timestamp,
    serialize_phone_identifier,
    serialize_identifier
)
from ._models import (
    CallParticipant,
    CallConnectionProperties,
    AddParticipantResult,
    RemoveParticipantResult,
    TransferCallResult
)
from ._generated._client import AzureCommunicationCallAutomationService
from ._generated.models import (
    AddParticipantRequest,
    RemoveParticipantRequest,
    TransferToParticipantRequest,
    PlayRequest,
    RecognizeRequest,
    ContinuousDtmfRecognitionRequest,
    SendDtmfRequest,
    CustomContext,
    DtmfOptions,
    PlayOptions,
    RecognizeOptions,
)
from ._shared.utils import (
    get_authentication_policy,
    parse_connection_str
)
if TYPE_CHECKING:
    from ._call_automation_client import CallAutomationClient
    from ._models  import (
        FileSource,
        CallInvite
    )
    from azure.core.credentials import (
        TokenCredential,
        AzureKeyCredential
    )
    from ._shared.models import (
        CommunicationIdentifier,
    )
    from ._generated.models._enums import (
        DtmfTone,
        RecognizeInputType
    )
    from azure.core.exceptions import HttpResponseError

class CallConnectionClient(object): # pylint: disable=client-accepts-api-version-keyword
    """A client to interact with ongoing call. This client can be used to do mid-call actions,
    such as Transfer and Play Media. Call must be estbalished to perform these actions.

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
    def __init__(# pylint: disable=missing-client-constructor-parameter-credential, missing-client-constructor-parameter-kwargs
        self,
        endpoint: str,
        credential: Union['TokenCredential', 'AzureKeyCredential'],
        call_connection_id: str,
        *,
        api_version: Optional[str] = None,
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
        self._client = AzureCommunicationCallAutomationService(
            endpoint,
            api_version=api_version or DEFAULT_VERSION,
            authentication_policy=get_authentication_policy(
                endpoint, credential),
            sdk_moniker=SDK_MONIKER,
            **kwargs)

        self._call_connection_id = call_connection_id
        self._call_connection_client = self._client.call_connection
        self._call_media_client = self._client.call_media

    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        call_connection_id: str,
        **kwargs
    ) -> 'CallConnectionClient':
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
        cls,
        callautomation_client: 'CallAutomationClient',
        call_connection_id: str
    ) -> 'CallConnectionClient':
        """Internal constructor for sharing the pipeline with CallAutomationClient."""
        return cls(None, None, call_connection_id, _callautomation_client=callautomation_client)

    def get_call_properties(self, **kwargs) -> CallConnectionProperties:
        """Get the latest properties of this call.

        :return: CallConnectionProperties
        :rtype: ~azure.communication.callautomation.CallConnectionProperties
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        call_properties = self._call_connection_client.get_call(call_connection_id=self._call_connection_id, **kwargs)

        return CallConnectionProperties._from_generated(call_properties) # pylint:disable=protected-access

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
            self._call_connection_client.terminate_call(
                self._call_connection_id,
                repeatability_first_sent=get_repeatability_timestamp(),
                repeatability_request_id=get_repeatability_guid(),
                **kwargs)
        else:
            self._call_connection_client.hangup_call(
                self._call_connection_id, **kwargs)

    @distributed_trace
    def get_participant(
        self,
        target_participant: 'CommunicationIdentifier',
        **kwargs
    ) -> 'CallParticipant':
        """Get details of a participant in this call.

        :param target_participant: The participant to retrieve.
        :type target_participant: ~azure.communication.callautomation.CommunicationIdentifier
        :return: CallParticipant
        :rtype: ~azure.communication.callautomation.CallParticipant
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        participant = self._call_connection_client.get_participant(
            self._call_connection_id, target_participant.raw_id, **kwargs)

        return CallParticipant._from_generated(participant) # pylint:disable=protected-access

    @distributed_trace
    def list_participants(self, **kwargs) -> ItemPaged[CallParticipant]:
        """List all participants in this call.

        :return: List of CallParticipant
        :rtype: ItemPaged[azure.communication.callautomation.CallParticipant]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._call_connection_client.get_participants(self._call_connection_id, **kwargs).values

    @distributed_trace
    def transfer_call_to_participant(
        self,
        target_participant: 'CommunicationIdentifier',
        *,
        sip_headers: Optional[Dict[str, str]] = None,
        voip_headers: Optional[Dict[str, str]] = None,
        operation_context: Optional[str] = None,
        **kwargs
    ) -> TransferCallResult:
        """Transfer this call to another participant.

        :param target_participant: The transfer target.
        :type target_participant: CommunicationIdentifier
        :keyword sip_headers: Custom context for PSTN
        :paramtype sip_headers: dict[str, str]
        :keyword voip_headers: Custom context for VOIP
        :paramtype voip_headers: dict[str, str]
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str
        :return: TransferCallResult
        :rtype: ~azure.communication.callautomation.TransferCallResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        user_custom_context = CustomContext(
            voip_headers=voip_headers,
            sip_headers=sip_headers
            ) if sip_headers or voip_headers else None
        request = TransferToParticipantRequest(
            target_participant=serialize_identifier(target_participant),
            custom_context=user_custom_context, operation_context=operation_context)

        return self._call_connection_client.transfer_to_participant(
            self._call_connection_id, request,
            repeatability_first_sent=get_repeatability_timestamp(),
            repeatability_request_id=get_repeatability_guid(),
            **kwargs)

    @distributed_trace
    def add_participant(
        self,
        target_participant: 'CallInvite',
        *,
        invitation_timeout: Optional[int] = None,
        operation_context: Optional[str] = None,
        **kwargs
    ) -> AddParticipantResult:
        """Add a participant to this call.

        :param target_participant: The participant being added.
        :type target_participant: ~azure.communication.callautomation.CallInvite
        :keyword invitation_timeout: Timeout to wait for the invited participant to pickup.
         The maximum value of this is 180 seconds.
        :paramtype invitation_timeout: int
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str
        :return: AddParticipantResult
        :rtype: ~azure.communication.callautomation.AddParticipantResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        user_custom_context = CustomContext(
            voip_headers=target_participant.voip_headers,
            sip_headers=target_participant.sip_headers
            ) if target_participant.sip_headers or target_participant.voip_headers else None
        add_participant_request = AddParticipantRequest(
            participant_to_add=serialize_identifier(target_participant.target),
            source_caller_id_number=serialize_phone_identifier(
                target_participant.source_caller_id_number) if target_participant.source_caller_id_number else None,
            source_display_name=target_participant.source_display_name,
            custom_context=user_custom_context,
            invitation_timeout=invitation_timeout,
            operation_context=operation_context)

        response = self._call_connection_client.add_participant(
            self._call_connection_id,
            add_participant_request,
            repeatability_first_sent=get_repeatability_timestamp(),
            repeatability_request_id=get_repeatability_guid(),
            **kwargs)

        return AddParticipantResult._from_generated(response) # pylint:disable=protected-access

    @distributed_trace
    def remove_participant(
        self,
        target_participant: 'CommunicationIdentifier',
        *,
        operation_context: Optional[str] = None,
        **kwargs
    ) -> RemoveParticipantResult:
        """Remove a participant from this call.

        :param  target_participant: The participant being removed.
        :type target_participant: ~azure.communication.callautomation.CommunicationIdentifier
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str
        :return: RemoveParticipantResult
        :rtype: ~azure.communication.callautomation.RemoveParticipantResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        remove_participant_request = RemoveParticipantRequest(
            participant_to_remove=serialize_identifier(target_participant),
            operation_context=operation_context)

        response = self._call_connection_client.remove_participant(
            self._call_connection_id,
            remove_participant_request,
            repeatability_first_sent=get_repeatability_timestamp(),
            repeatability_request_id=get_repeatability_guid(),
            **kwargs)

        return RemoveParticipantResult._from_generated(response) # pylint:disable=protected-access

    @distributed_trace
    def play_media(
        self,
        play_source: 'FileSource',
        play_to: List['CommunicationIdentifier'],
        *,
        loop: Optional[bool] = False,
        operation_context: Optional[str] = None,
        **kwargs
    ) -> None:
        """Play media to specific participant(s) in this call.

        :param play_source: A PlaySource representing the source to play.
        :type play_source: ~azure.communication.callautomation.FileSource
        :param play_to: The targets to play media to.
        :type play_to: list[~azure.communication.callautomation.CommunicationIdentifier]
        :keyword loop: if the media should be repeated until cancelled.
        :paramtype loop: bool
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        play_request = PlayRequest(
            play_source_info=play_source._to_generated(),#pylint:disable=protected-access
            play_to=[serialize_identifier(identifier)
                     for identifier in play_to],
            play_options=PlayOptions(loop=loop),
            operation_context=operation_context,
            **kwargs
        )
        self._call_media_client.play(self._call_connection_id, play_request)

    @distributed_trace
    def play_media_to_all(
        self,
        play_source: 'FileSource',
        *,
        loop: Optional[bool] = False,
        operation_context: Optional[str] = None,
        **kwargs
    ) -> None:
        """Play media to all participants in this call.

        :param play_source: A PlaySource representing the source to play.
        :type play_source: ~azure.communication.callautomation.FileSource
        :keyword loop: if the media should be repeated until cancelled.
        :paramtype loop: bool
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self.play_media(play_source=play_source,
                        play_to=[],
                        loop=loop,
                        operation_context=operation_context,
                        **kwargs)

    @distributed_trace
    def start_recognizing_media(
        self,
        input_type : Union[str, 'RecognizeInputType'],
        target_participant: 'CommunicationIdentifier',
        *,
        initial_silence_timeout: Optional[int] = None,
        play_prompt: Optional['FileSource'] = None,
        interrupt_call_media_operation: Optional[bool] = False,
        operation_context: Optional[str] = None,
        interrupt_prompt: Optional[bool] = False,
        dtmf_inter_tone_timeout: Optional[int] = None,
        dtmf_max_tones_to_collect: Optional[str] = None,
        dtmf_stop_tones: Optional[List[str or 'DtmfTone']] = None,
        **kwargs
    ) -> None:
        """Recognize tones from specific participant in this call.

        :param input_type: Determines the type of the recognition.
        :type input_type: str or ~azure.communication.callautomation.RecognizeInputType
        :param target_participant: Target participant of DTMF tone recognition.
        :type target_participant: ~azure.communication.callautomation.CommunicationIdentifier
        :keyword initial_silence_timeout: Time to wait for first input after prompt in seconds (if any).
        :paramtype initial_silence_timeout: int
        :keyword play_prompt: The source of the audio to be played for recognition.
        :paramtype play_prompt: ~azure.communication.callautomation.FileSource
        :keyword interrupt_call_media_operation:
         If set recognize can barge into other existing queued-up/currently-processing requests.
        :paramtype interrupt_call_media_operation: bool
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str
        :keyword interrupt_prompt: Determines if we interrupt the prompt and start recognizing.
        :paramtype interrupt_prompt: bool
        :keyword dtmf_inter_tone_timeout: Time to wait between DTMF inputs to stop recognizing.
        :paramtype dtmf_inter_tone_timeout: int
        :keyword dtmf_max_tones_to_collect: Maximum number of DTMF tones to be collected.
        :paramtype dtmf_max_tones_to_collect: int
        :keyword dtmf_stop_tones: List of tones that will stop recognizing.
        :paramtype dtmf_stop_tones: list[str or ~azure.communication.callautomation.DtmfTone]
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        options = RecognizeOptions(
            interrupt_prompt=interrupt_prompt,
            initial_silence_timeout_in_seconds=initial_silence_timeout,
            target_participant=serialize_identifier(target_participant),
            dtmf_options= DtmfOptions(
                inter_tone_timeout_in_seconds=dtmf_inter_tone_timeout,
                max_tones_to_collect=dtmf_max_tones_to_collect,
                stop_tones=dtmf_stop_tones
            )
        )

        recognize_request = RecognizeRequest(
            recognize_input_type=input_type,
            play_prompt=play_prompt._to_generated(),#pylint:disable=protected-access
            interrupt_call_media_operation=interrupt_call_media_operation,
            operation_context=operation_context,
            recognize_options=options,
            **kwargs
        )

        self._call_media_client.recognize(
            self._call_connection_id, recognize_request)

    @distributed_trace
    def cancel_all_media_operations(
        self,
        **kwargs
    ) -> None:
        """Cancels all the ongoing and queued media operations for this call.

        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._call_media_client.cancel_all_media_operations(
            self._call_connection_id, **kwargs)

    @distributed_trace
    def start_continuous_dtmf_recognition(
        self,
        target: 'CommunicationIdentifier',
        *,
        operation_context: Optional[str] = None,
        **kwargs
    ) -> None:
        """Start continuous Dtmf recognition by subscribing to tones.

        :param target: Target participant of continuous DTMF tone recognition.
        :type target: ~azure.communication.callautomation.CommunicationIdentifier
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        continuous_dtmf_recognition_request = ContinuousDtmfRecognitionRequest(
            target_participant=serialize_identifier(target),
            operation_context=operation_context)

        self._call_media_client.start_continuous_dtmf_recognition(
            self._call_connection_id,
            continuous_dtmf_recognition_request,
            **kwargs)

    @distributed_trace
    def stop_continuous_dtmf_recognition(
        self,
        target: 'CommunicationIdentifier',
        *,
        operation_context: Optional[str] = None,
        **kwargs
    ) -> None:
        """Stop continuous Dtmf recognition by unsubscribing to tones.

        :param target: Target participant of continuous DTMF tone recognition.
        :type target: ~azure.communication.callautomation.CommunicationIdentifier
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        continuous_dtmf_recognition_request = ContinuousDtmfRecognitionRequest(
            target_participant=serialize_identifier(target),
            operation_context=operation_context)

        self._call_media_client.stop_continuous_dtmf_recognition(
            self._call_connection_id,
            continuous_dtmf_recognition_request,
            **kwargs)

    @distributed_trace
    def send_dtmf(
        self,
        target: 'CommunicationIdentifier',
        tones: List[Union[str, 'DtmfTone']],
        *,
        operation_context: Optional[str] = None,
        **kwargs
    ) -> None:
        """Send dtmf tones to this call.

        :param target: Target participant of Send DTMF tone.
        :type target: ~azure.communication.callautomation.CommunicationIdentifier
        :param tones: The captured tones.
        :type tones:list[str or ~azure.communication.callautomation.DtmfTone]
        :keyword operation_context: Value that can be used to track this call and its associated events.
        :paramtype operation_context: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        send_dtmf_request = SendDtmfRequest(
            target_participant=serialize_identifier(target),
            tones=tones,
            operation_context=operation_context)

        self._call_media_client.send_dtmf(
            self._call_connection_id,
            send_dtmf_request,
            **kwargs)
