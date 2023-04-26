# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING, Any, Optional, List, Union  # pylint: disable=unused-import
from urllib.parse import urlparse
from azure.core.credentials import TokenCredential
from azure.core.paging import ItemPaged
from ._version import SDK_MONIKER
from ._api_versions import DEFAULT_VERSION
from ._communication_identifier_serializer import (
    serialize_phone_identifier,
    serialize_identifier
)
from ._utils import (
    _get_repeatability_guid,
    _get_repeatability_timestamp
)
from ._models import (
    CallConnectionProperties,
    CallParticipant,
    CallInvite,
    AddParticipantResult,
    PlaySource,
    FileSource
)
from ._shared.models import CommunicationIdentifier
from ._generated._client import AzureCommunicationCallAutomationService
from ._generated.models import (
    TransferCallResult,
    TransferToParticipantRequest,
    CustomContext,
    AddParticipantRequest,
    RemoveParticipantResult,
    RemoveParticipantRequest,
    PlayRequest,
    RecognizeRequest,
    RecognizeOptions,
    PlaySource as PlaySourceInternal,
    FileSource as FileSourceInternal,
    PlaySourceType,
    DtmfOptions,
    PlayOptions,
    ContinuousDtmfRecognitionRequest,
    SendDtmfRequest,
    Tone
)
from ._shared.utils import get_authentication_policy

class CallConnectionClient(object): # pylint: disable=client-accepts-api-version-keyword
    """
    A client to interact with ongoing call.
    """
    def __init__(# pylint: disable=missing-client-constructor-parameter-credential, missing-client-constructor-parameter-kwargs
        self,
        endpoint: str,
        credential: TokenCredential,
        call_connection_id: str,
        **kwargs  # type: Any
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
                endpoint, credential),
            sdk_moniker=SDK_MONIKER,
            **kwargs)

        self._call_connection_id = call_connection_id
        self._call_connection_client = self._client.call_connection
        self._call_media_client = self._client.call_media

    def get_call_properties(self, **kwargs) -> CallConnectionProperties:
        """
        Get the latest properties of the call.

        :return: CallConnectionProperties of this call.
        :rtype: ~azure.communication.callautomation.models.CallConnectionProperties
        :raises ~azure.core.exceptions.HttpResponseError
        """

        call_properties = self._call_connection_client.get_call(call_connection_id=self._call_connection_id, **kwargs)

        return CallConnectionProperties._from_generated(call_properties) # pylint:disable=protected-access

    def hang_up(self, is_for_everyone: bool, **kwargs) -> None:
        """
        Hangup the call.

        :param bool is_for_everyone:
            Determine if the call should be ended for all participants.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError
        """

        if is_for_everyone:
            self._call_connection_client.terminate_call(
                self._call_connection_id,
                repeatability_first_sent=_get_repeatability_guid(),
                repeatability_request_id=_get_repeatability_timestamp(),
                **kwargs)
        else:
            self._call_connection_client.hangup_call(
                self._call_connection_id, **kwargs)

    def get_participant(self, target_participant: CommunicationIdentifier, **kwargs) -> CallParticipant:
        """
        Get details of a participant from a call.

        :param ~azure.communication.callautomation._shared.models.CommunicationIdentifier target_participant:
            The participant to retrieve.
        :return: Details of requested CallParticipant.
        :rtype: azure.communication.callautomation.models.CallParticipant
        :raises ~azure.core.exceptions.HttpResponseError
        """

        participant = self._call_connection_client.get_participant(
            self._call_connection_id, target_participant.raw_id, **kwargs)

        return CallParticipant._from_generated(participant) # pylint:disable=protected-access

    def list_participants(self, **kwargs) -> ItemPaged[CallParticipant]:
        """
        List all participants from a call.

        :return: Details of all participants.
        :rtype: ItemPaged[azure.communication.callautomation.models.CallParticipant]
        :raises ~azure.core.exceptions.HttpResponseError
        """
        return self._call_connection_client.get_participants(self._call_connection_id, **kwargs).values

    def transfer_call_to_participant(self, target_participant: CallInvite, **kwargs: Any) -> TransferCallResult:
        """
        Transfer the call to a participant.

        :param CallInvite target_participant:
            The transfer target.
        :keyword str operation_context:
            Value that can be used to track the call and its associated events.
        :return: TransferCallResult
        :raises ~azure.core.exceptions.HttpResponseError
        """
        user_custom_context = CustomContext(
            voip_headers=target_participant.voip_headers, sip_headers=target_participant.sip_headers)
        request = TransferToParticipantRequest(
            target_participant=serialize_identifier(target_participant.target),
            transferee_caller_id=serialize_identifier(
                target_participant.source_caller_id_number) if target_participant.source_caller_id_number else None,
            custom_context=user_custom_context, operation_context=kwargs.pop("operation_context", None))

        return self._call_connection_client.transfer_to_participant(
            self._call_connection_id, request,
            repeatability_first_sent=_get_repeatability_guid(),
            repeatability_request_id=_get_repeatability_timestamp(),
            **kwargs)

    def add_participant(self, target_participant: CallInvite, **kwargs: Any) -> AddParticipantResult:
        """
        Add a participant to the call.

        :param CallInvite target_participant: The participant being added.
        :keyword int invitation_timeout:
            Timeout to wait for the invited participant to pickup.
            The maximum value of this is 180 seconds.
        :keyword str operation_context:
            Value that can be used to track the call and its associated events.
        :return: AddParticipantResult
        :raises ~azure.core.exceptions.HttpResponseError
        """
        user_custom_context = CustomContext(
            voip_headers=target_participant.voip_headers, sip_headers=target_participant.sip_headers)
        add_participant_request = AddParticipantRequest(
            participant_to_add=serialize_identifier(target_participant.target),
            source_caller_id_number=serialize_phone_identifier(
                target_participant.source_caller_id_number) if target_participant.source_caller_id_number else None,
            source_display_name=target_participant.source_display_name,
            custom_context=user_custom_context,
            invitation_timeout=kwargs.pop(
                "invitation_timeout", None),
            operation_context=kwargs.pop("operation_context", None))

        response = self._call_connection_client.add_participant(
            self._call_connection_id,
            add_participant_request,
            repeatability_first_sent=_get_repeatability_guid(),
            repeatability_request_id=_get_repeatability_timestamp())

        return AddParticipantResult._from_generated(response) # pylint:disable=protected-access

    def remove_participant(self, target_participant: CommunicationIdentifier, **kwargs: Any) -> RemoveParticipantResult:
        """
        Remove a participant from the call.

        :param ~azure.communication.callautomation._shared.models.CommunicationIdentifier target_participant:
            The participant being removed.
        :keyword str operation_context:
            Value that can be used to track the call and its associated events.
            request to the response event.
        :return: AddParticipantResult
        :raises ~azure.core.exceptions.HttpResponseError
        """

        remove_participant_request = RemoveParticipantRequest(
            participant_to_remove=serialize_identifier(target_participant),
            operation_context=kwargs.pop("operation_context", None))

        return self._call_connection_client.remove_participant(
            self._call_connection_id,
            remove_participant_request,
            repeatability_first_sent=_get_repeatability_guid(),
            repeatability_request_id=_get_repeatability_timestamp())

    def play_media_to_all(
        self,
        play_source: PlaySource,
        **kwargs
    ) -> None:
        """
        Play media to all participants in the call.

        :param ~azure.communication.callautomation.PlaySource play_source:
            A PlaySource representing the source to play.
        :keyword bool loop:
            if the media should be repeated until cancelled.
        :return: None
        :rtype: None
        """
        if not play_source:
            raise ValueError('play_source cannot be None.')

        self.play_media(play_source=play_source, play_to=[], **kwargs)

    def play_media(
        self,
        play_source: PlaySource,
        play_to: List[CommunicationIdentifier],
        **kwargs
    ) -> None:
        """
        Play media to specific participant(s) in the call.

        :param ~azure.communication.callautomation.PlaySource play_source:
            A PlaySource representing the source to play.
        :param list[~azure.communication.callautomation._shared.models.CommunicationIdentifier] play_to:
            The targets to play to.
        :keyword bool loop:
            if the media should be repeated until cancelled.
        :return: None
        :rtype: None
        """

        if not play_source:
            raise ValueError('play_source cannot be None.')

        play_request = PlayRequest(
            play_source_info=self._create_play_source_internal(play_source),
            play_to=[serialize_identifier(identifier)
                     for identifier in play_to],
            play_options=PlayOptions(loop=kwargs.get('loop', False))
        )
        self._call_media_client.play(self._call_connection_id, play_request)

    def start_recognizing_media(
        self,
        input_type,
        target_participant,
        **kwargs
    ) -> None:
        """
        Recognize tones from specific participant in the call.

        :param input_type:
            Determines the type of the recognition.
        :type input_type: str or ~azure.communication.callautomation.models.RecognizeInputType
        :param target_participant:
            Target participant of DTMF tone recognition.
        :type target_participant: ~azure.communication.callautomation._shared.models.CommunicationIdentifier
        :keyword int initial_silence_timeout:
            Time to wait for first input after prompt in seconds (if any).
        :keyword  ~azure.communication.callautomation.models.PlaySource play_prompt:
            The source of the audio to be played for recognition.
        :keyword bool interrupt_call_media_operation:
            If set recognize can barge into
            other existing queued-up/currently-processing requests.
        :keyword str operation_context:
            Value that can be used to track the call and its associated events.
        :keyword bool interrupt_prompt: Determines if we interrupt the prompt and start recognizing.
        :keyword int dtmf_inter_tone_timeout:
            Time to wait between DTMF inputs to stop recognizing.
        :keyword int dtmf_max_tones_to_collect:
            Maximum number of DTMF tones to be collected.
        :keyword list[str or ~azure.communication.callautomation.models.DtmfTone] dtmf_stop_tones:
            List of tones that will stop recognizing.
        :return: None
        :rtype: None
        """

        if not input_type:
            raise ValueError('input_type cannot be None.')

        if not target_participant:
            raise ValueError('target_participant cannot be None.')

        options = RecognizeOptions(
            interrupt_prompt=kwargs.pop("interrupt_prompt", None),
            initial_silence_timeout_in_seconds=kwargs.pop("initial_silence_timeout", None),
            target_participant=serialize_identifier(target_participant),
            dtmf_options= DtmfOptions(
                inter_tone_timeout_in_seconds=kwargs.pop("dtmf_inter_tone_timeout", None),
                max_tones_to_collect=kwargs.pop("dtmf_max_tones_to_collect", None),
                stop_tones=kwargs.pop("dtmf_stop_tones", None)
            )
        )

        recognize_request = RecognizeRequest(
            recognize_input_type=input_type,
            play_prompt=self._create_play_source_internal(kwargs.pop("play_prompt", None)),
            interrupt_call_media_operation=kwargs.pop("interrupt_call_media_operation", None),
            operation_context=kwargs.pop("operation_context", None),
            recognize_options=options
        )

        self._call_media_client.recognize(
            self._call_connection_id, recognize_request)

    def cancel_all_media_operations(
        self
    ) -> None:
        """
        Cancels all the queued media operations.

        :return: None
        :rtype: None
        """
        self._call_media_client.cancel_all_media_operations(
            self._call_connection_id)

    def start_continuous_dtmf_recognition(
        self,
        target: CommunicationIdentifier,
        operation_context: str = None,
        **kwargs
    ) -> None:
        """
        Start continuous Dtmf recognition by subscribing to tones.

        :param target: Target participant of continuous DTMF tone recognition. Required.
        :type target: ~azure.communication.callautomation.models.CommunicationIdentifier
        :param operation_context: The value to identify context of the operation. Optional.
        :type operation_context: str

        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if not target:
            raise ValueError('target cannot be None.')

        continuous_dtmf_recognition_request = ContinuousDtmfRecognitionRequest(
            target_participant=serialize_identifier(target),
            operation_context=operation_context)

        self._call_media_operations.start_continuous_dtmf_recognition(
            self.call_connection_id,
            continuous_dtmf_recognition_request,
            **kwargs)

    def stop_continuous_dtmf_recognition(
        self,
        target: CommunicationIdentifier,
        operation_context: str = None,
        **kwargs
    ) -> None:
        """
        Stop continuous Dtmf recognition by unsubscribing to tones.

        :param target: Target participant of continuous DTMF tone recognition. Required.
        :type target: ~azure.communication.callautomation.models.CommunicationIdentifier
        :param operation_context: The value to identify context of the operation. Optional.
        :type operation_context: str

        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if not target:
            raise ValueError('target cannot be None.')

        continuous_dtmf_recognition_request = ContinuousDtmfRecognitionRequest(
            target_participant=serialize_identifier(target),
            operation_context=operation_context)

        self._call_media_operations.stop_continuous_dtmf_recognition(
            self.call_connection_id,
            continuous_dtmf_recognition_request,
            **kwargs)

    def send_dtmf(
        self,
        target: CommunicationIdentifier,
        tones: List[Union[str, Tone]],
        operation_context: str = None,
        **kwargs
    ) -> None:
        """
        Send dtmf tones.

        :param target: Target participant of Send DTMF tone. Required.
        :type target: ~azure.communication.callautomation.models.CommunicationIdentifier
        :param tones: The captured tones. Required.
        :type tones: list[str or ~azure.communication.callautomation.models.Tone]
        :param operation_context: The value to identify context of the operation. Optional.
        :type operation_context: str

        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if not target:
            raise ValueError('target cannot be None.')

        send_dtmf_request = SendDtmfRequest(
            target_participant=serialize_identifier(target),
            tones=tones,
            operation_context=operation_context)

        self._call_media_operations.send_dtmf(
            self.call_connection_id,
            send_dtmf_request,
            **kwargs)

    @staticmethod
    def _create_play_source_internal(play_source):
        if isinstance(play_source, FileSource):
            file_source = FileSourceInternal(uri=play_source.url)
            return PlaySourceInternal(
                source_type=PlaySourceType.FILE,
                file_source=file_source,
                play_source_id=play_source.play_source_id
            )
        return None
