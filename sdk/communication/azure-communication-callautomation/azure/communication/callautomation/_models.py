# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, List, Optional, Union, Mapping

from enum import Enum, EnumMeta
import re
from six import with_metaclass
try:
    from typing import Protocol, TypedDict
except ImportError:
    from typing_extensions import Protocol, TypedDict

from azure.core import CaseInsensitiveEnumMeta

from ._generated.models import (
    CallLocator,
    StartCallRecordingRequest as StartCallRecordingRequestRest,
    RecordingContentType, RecordingChannelType, RecordingFormatType,
    CommunicationIdentifierModel,
    CallConnectionStateModel,
    RecordingStorageType,
    RecognizeInputType
)

from ._generated.models import CallParticipant as CallParticipantGenerated
from ._generated.models import CallConnectionProperties as CallConnectionPropertiesGenerated
from ._generated.models import GetParticipantsResponse as GetParticipantsResponseGenerated
from ._generated.models import AddParticipantResponse as AddParticipantResponseGenerated

from ._communication_identifier_serializer import *


class ServerCallLocator(object):
    def __init__(
        self,
        *,
        locator_id: str,
        **kwargs: Any
    ) -> None:

        super().__init__(**kwargs)
        self.id = locator_id
        self.kind = "serverCallLocator"

    def _to_generated(self):

        return CallLocator(kind=self.kind,
                           server_call_id=self.id
                           )


class GroupCallLocator(object):
    def __init__(
        self,
        *,
        locator_id: str,
        **kwargs: Any
    ) -> None:

        super().__init__(**kwargs)
        self.id = locator_id
        self.kind = "groupCallLocator"

    def _to_generated(self):

        return CallLocator(kind=self.kind,
                           group_call_id=self.id
                           )


class StartCallRecordingRequest(object):
    def __init__(
        self,
        *,
        call_locator: ServerCallLocator | GroupCallLocator,
        recording_state_callback_uri: Optional[str] = None,
        recording_content_type: Optional[Union[str,
                                               "RecordingContentType"]] = None,
        recording_channel_type: Optional[Union[str,
                                               "RecordingChannelType"]] = None,
        recording_format_type: Optional[Union[str,
                                              "RecordingFormatType"]] = None,
        audio_channel_participant_ordering: Optional[List["CommunicationIdentifierModel"]] = None,
        recording_storage_type: Optional[Union[str,
                                               "RecordingStorageType"]] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword call_locator: The call locator. Required.
        :paramtype call_locator: ~azure.communication.callautomation.models.CallLocator
        :keyword recording_state_callback_uri: The uri to send notifications to.
        :paramtype recording_state_callback_uri: str
        :keyword recording_content_type: The content type of call recording. Known values are: "audio"
         and "audioVideo".
        :paramtype recording_content_type: str or
         ~azure.communication.callautomation.models.RecordingContentType
        :keyword recording_channel_type: The channel type of call recording. Known values are: "mixed"
         and "unmixed".
        :paramtype recording_channel_type: str or
         ~azure.communication.callautomation.models.RecordingChannelType
        :keyword recording_format_type: The format type of call recording. Known values are: "wav",
         "mp3", and "mp4".
        :paramtype recording_format_type: str or
         ~azure.communication.callautomation.models.RecordingFormatType
        :keyword audio_channel_participant_ordering: The sequential order in which audio channels are
         assigned to participants in the unmixed recording.
         When 'recordingChannelType' is set to 'unmixed' and `audioChannelParticipantOrdering is not
         specified,
         the audio channel to participant mapping will be automatically assigned based on the order in
         which participant
         first audio was detected.  Channel to participant mapping details can be found in the metadata
         of the recording.
        :paramtype audio_channel_participant_ordering:
         list[~azure.communication.callautomation.models.CommunicationIdentifierModel]
        :keyword recording_storage_type: Recording storage mode. ``External`` enables bring your own
         storage. Known values are: "acs" and "azureBlob".
        :paramtype recording_storage_type: str or
         ~azure.communication.callautomation.models.RecordingStorageType
        """
        super().__init__(**kwargs)
        self.call_locator = call_locator
        self.recording_state_callback_uri = recording_state_callback_uri
        self.recording_content_type = recording_content_type
        self.recording_channel_type = recording_channel_type
        self.recording_format_type = recording_format_type
        self.audio_channel_participant_ordering = audio_channel_participant_ordering
        self.recording_storage_type = recording_storage_type

    def _to_generated(self):

        return StartCallRecordingRequestRest(call_locator=self.call_locator._to_generated(),
                                             recording_state_callback_uri=self.recording_state_callback_uri,
                                             recording_content_type=self.recording_content_type,
                                             recording_channel_type=self.recording_channel_type,
                                             recording_format_type=self.recording_format_type,
                                             audio_channel_participant_ordering=self.audio_channel_participant_ordering,
                                             recording_storage_type=self.recording_storage_type
                                             )


class RecordingStateResponse(object):
    """RecordingStateResponse.

    :ivar recording_id:
    :vartype recording_id: str
    :ivar recording_state: Known values are: "active" and "inactive".
    :vartype recording_state: str or ~azure.communication.callautomation.models.RecordingState
    """

    # pylint:disable=protected-access

    def __init__(
        self,
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        self.recording_id = kwargs['recording_id']
        self.recording_state = kwargs['recording_state']

    @classmethod
    def _from_generated(cls, recording_state_response):

        return cls(
            recording_id=recording_state_response.recording_id,
            recording_state=recording_state_response.recording_state
        )


class PlaySource(object):
    """
    The PlaySource model.

    :ivar play_source_id: Defines the identifier to be used for caching related media.
    :vartype play_source_id: str
    """

    def __init__(
            self,
            **kwargs
    ):
        self.play_source_id = kwargs['play_source_id']


class FileSource(PlaySource):
    """
    The FileSource model.

    :ivar uri: Uri for the audio file to be played.
    :vartype uri: str
    """

    def __init__(
            self,
            **kwargs
    ):
        self.uri = kwargs['uri']
        super().__init__(play_source_id=kwargs.get('play_source_id'))


class CommunicationIdentifierKind(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Communication Identifier Kind."""

    UNKNOWN = "unknown"
    COMMUNICATION_USER = "communication_user"
    PHONE_NUMBER = "phone_number"
    MICROSOFT_TEAMS_USER = "microsoft_teams_user"


class CommunicationCloudEnvironment(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """The cloud environment that the identifier belongs to"""

    PUBLIC = "PUBLIC"
    DOD = "DOD"
    GCCH = "GCCH"


class CommunicationIdentifier(Protocol):
    """Communication Identifier.

    :ivar str raw_id: Optional raw ID of the identifier.
    :ivar kind: The type of identifier.
    :vartype kind: str or CommunicationIdentifierKind
    :ivar Mapping[str, Any] properties: The properties of the identifier.
    """
    raw_id = None  # type: Optional[str]
    kind = None  # type: Optional[Union[CommunicationIdentifierKind, str]]
    properties = {}  # type: Mapping[str, Any]


CommunicationUserProperties = TypedDict(
    'CommunicationUserProperties',
    id=str
)


class CommunicationUserIdentifier(object):
    """Represents a user in Azure Communication Service.

    :ivar str raw_id: Optional raw ID of the identifier.
    :ivar kind: The type of identifier.
    :vartype kind: str or CommunicationIdentifierKind
    :ivar Mapping[str, Any] properties: The properties of the identifier.
     The keys in this mapping include:
        - `id`(str): ID of the Communication user as returned from Azure Communication Identity.

    :param str id: ID of the Communication user as returned from Azure Communication Identity.
    """
    kind = CommunicationIdentifierKind.COMMUNICATION_USER

    def __init__(self, id, **kwargs):
        # type: (str, Any) -> None
        self.raw_id = kwargs.get('raw_id', id)
        self.properties = CommunicationUserProperties(id=id)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


PhoneNumberProperties = TypedDict(
    'PhoneNumberProperties',
    value=str
)


class PhoneNumberIdentifier(object):
    """Represents a phone number.

    :ivar str raw_id: Optional raw ID of the identifier.
    :ivar kind: The type of identifier.
    :vartype kind: str or CommunicationIdentifierKind
    :ivar Mapping properties: The properties of the identifier.
     The keys in this mapping include:
        - `value`(str): The phone number in E.164 format.

    :param str value: The phone number.
    """
    kind = CommunicationIdentifierKind.PHONE_NUMBER

    def __init__(self, value, **kwargs):
        # type: (str, Any) -> None
        self.raw_id = kwargs.get('raw_id')
        self.properties = PhoneNumberProperties(value=value)
        if self.raw_id is None:
            self.raw_id = _phone_number_raw_id(self)


def _phone_number_raw_id(identifier: PhoneNumberIdentifier) -> str:
    value = identifier.properties['value']
    # We just assume correct E.164 format here because
    # validation should only happen server-side, not client-side.
    return f'4:{value}'


class UnknownIdentifier(object):
    """Represents an identifier of an unknown type.

    It will be encountered in communications with endpoints that are not
    identifiable by this version of the SDK.

    :ivar str raw_id: Optional raw ID of the identifier.
    :ivar kind: The type of identifier.
    :vartype kind: str or CommunicationIdentifierKind
    :ivar Mapping properties: The properties of the identifier.
    :param str identifier: The ID of the identifier.
    """
    kind = CommunicationIdentifierKind.UNKNOWN

    def __init__(self, identifier):
        # type: (str) -> None
        self.raw_id = identifier
        self.properties = {}

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


MicrosoftTeamsUserProperties = TypedDict(
    'MicrosoftTeamsUserProperties',
    user_id=str,
    is_anonymous=bool,
    cloud=Union[CommunicationCloudEnvironment, str]
)


class MicrosoftTeamsUserIdentifier(object):
    """Represents an identifier for a Microsoft Teams user.

    :ivar str raw_id: Optional raw ID of the identifier.
    :ivar kind: The type of identifier.
    :vartype kind: str or CommunicationIdentifierKind
    :ivar Mapping properties: The properties of the identifier.
     The keys in this mapping include:
        - `user_id`(str): The id of the Microsoft Teams user. If the user isn't anonymous,
          the id is the AAD object id of the user.
        - `is_anonymous` (bool): Set this to true if the user is anonymous for example when joining
          a meeting with a share link.
        - `cloud` (str): Cloud environment that this identifier belongs to.

    :param str user_id: Microsoft Teams user id.
    :keyword bool is_anonymous: `True` if the identifier is anonymous. Default value is `False`.
    :keyword cloud: Cloud environment that the user belongs to. Default value is `PUBLIC`.
    :paramtype cloud: str or ~azure.communication.chat.CommunicationCloudEnvironment
    """
    kind = CommunicationIdentifierKind.MICROSOFT_TEAMS_USER

    def __init__(self, user_id, **kwargs):
        # type: (str, Any) -> None
        self.raw_id = kwargs.get('raw_id')
        self.properties = MicrosoftTeamsUserProperties(
            user_id=user_id,
            is_anonymous=kwargs.get('is_anonymous', False),
            cloud=kwargs.get('cloud') or CommunicationCloudEnvironment.PUBLIC
        )
        if self.raw_id is None:
            self.raw_id = _microsoft_teams_user_raw_id(self)


def _microsoft_teams_user_raw_id(identifier: MicrosoftTeamsUserIdentifier) -> str:
    user_id = identifier.properties['user_id']
    if identifier.properties['is_anonymous']:
        return '8:teamsvisitor:{}'.format(user_id)
    cloud = identifier.properties['cloud']
    if cloud == CommunicationCloudEnvironment.DOD:
        return '8:dod:{}'.format(user_id)
    elif cloud == CommunicationCloudEnvironment.GCCH:
        return '8:gcch:{}'.format(user_id)
    elif cloud == CommunicationCloudEnvironment.PUBLIC:
        return '8:orgid:{}'.format(user_id)
    return '8:orgid:{}'.format(user_id)


def identifier_from_raw_id(raw_id: str) -> CommunicationIdentifier:
    """
    Creates a CommunicationIdentifier from a given raw ID.

    When storing raw IDs use this function to restore the identifier that was encoded in the raw ID.

    :param str raw_id: A raw ID to construct the CommunicationIdentifier from.
    """
    if raw_id.startswith('4:'):
        return PhoneNumberIdentifier(
            value=raw_id[len('4:'):]
        )

    segments = raw_id.split(':', maxsplit=2)
    if len(segments) < 3:
        return UnknownIdentifier(identifier=raw_id)

    prefix = '{}:{}:'.format(segments[0], segments[1])
    suffix = raw_id[len(prefix):]
    if prefix == '8:teamsvisitor:':
        return MicrosoftTeamsUserIdentifier(
            user_id=suffix,
            is_anonymous=True
        )
    elif prefix == '8:orgid:':
        return MicrosoftTeamsUserIdentifier(
            user_id=suffix,
            is_anonymous=False,
            cloud='PUBLIC'
        )
    elif prefix == '8:dod:':
        return MicrosoftTeamsUserIdentifier(
            user_id=suffix,
            is_anonymous=False,
            cloud='DOD'
        )
    elif prefix == '8:gcch:':
        return MicrosoftTeamsUserIdentifier(
            user_id=suffix,
            is_anonymous=False,
            cloud='GCCH'
        )
    elif prefix in ['8:acs:', '8:spool:', '8:dod-acs:', '8:gcch-acs:']:
        return CommunicationUserIdentifier(
            id=raw_id
        )
    return UnknownIdentifier(
        identifier=raw_id
    )


class Gender(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Voice gender type."""

    MALE = "male"
    FEMALE = "female"


class CallMediaRecognizeOptions(object):
    """
    Options to configure the Recognize operation.

    :ivar input_type: Determines the type of the recognition.
    :vartype input_type: str or ~azure.communication.callautomation.models.RecognizeInputType
    :ivar target_participant: Target participant of DTFM tone recognition.
    :vartype target_participant: ~azure.communication.callautomation.models.CommunicationIdentifierModel
    :ivar initial_silence_timeout: Time to wait for first input after prompt in seconds (if any).
    :vartype initial_silence_timeout: int
    :ivar play_prompt: The source of the audio to be played for recognition.
    :vartype play_prompt: ~azure.communication.callautomation.models.PlaySource
    :ivar interrupt_call_media_operation: If set recognize can barge into other existing queued-up/currently-processing requests.
    :vartype interrupt_call_media_operation: bool
    :ivar operation_context: The value to identify context of the operation.
    :vartype operation_context: str
    :ivar interrupt_prompt: Determines if we interrupt the prompt and start recognizing.
    :vartype interrupt_prompt: bool
    """

    def __init__(
            self,
            input_type,
            target_participant,
            **kwargs
    ):
        self.input_type = input_type
        self.target_participant = target_participant
        self.initial_silence_timeout = 5
        self.play_prompt = kwargs.get('play_prompt')
        self.interrupt_call_media_operation = kwargs.get(
            'interrupt_call_media_operation')
        self.stop_current_operations = kwargs.get('stop_current_operations')
        self.operation_context = kwargs.get('operation_context')
        self.interrupt_prompt = kwargs.get('interrupt_prompt')


class CallMediaRecognizeDtmfOptions(CallMediaRecognizeOptions):
    """
    The recognize configuration specific to Dtmf.

    :ivar max_tones_to_collect: Maximum number of DTMFs to be collected.
    :vartype max_tones_to_collect: int
    :ivar inter_tone_timeout: Time to wait between DTMF inputs to stop recognizing.
    :vartype inter_tone_timeout: int
    :ivar stop_dtmf_tones: List of tones that will stop recognizing.
    :vartype stop_dtmf_tones: list[~azure.communication.callautomation.models.Tone]
    """

    def __init__(
            self,
            target_participant,
            max_tones_to_collect,
            **kwargs
    ):
        self.max_tones_to_collect = max_tones_to_collect
        self.inter_tone_timeout = kwargs.get('inter_tone_timeout')
        self.stop_dtmf_tones = kwargs.get('stop_dtmf_tones')
        super().__init__(RecognizeInputType.DTMF, target_participant, **kwargs)


class DtmfTone(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Tone."""

    ZERO = "zero"
    ONE = "one"
    TWO = "two"
    THREE = "three"
    FOUR = "four"
    FIVE = "five"
    SIX = "six"
    SEVEN = "seven"
    EIGHT = "eight"
    NINE = "nine"
    A = "a"
    B = "b"
    C = "c"
    D = "d"
    POUND = "pound"
    ASTERISK = "asterisk"


class RecognizeCanceled(object):
    """RecognizeCanceled.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also called ChainId for
    skype chain ID.
    :vartype correlation_id: str
    :ivar operation_context: Used by customers when calling mid-call actions to correlate the
    request to the response event.
    :vartype operation_context: str
    """

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        """
        :keyword call_connection_id: Call connection ID.
        :paramtype call_connection_id: str
        :keyword server_call_id: Server call ID.
        :paramtype server_call_id: str
        :keyword correlation_id: Correlation ID for event to call correlation. Also called ChainId for
            skype chain ID.
        :paramtype correlation_id: str
        :keyword operation_context: Used by customers when calling mid-call actions to correlate the
            request to the response event.
        :paramtype operation_context: str
        """
        super().__init__(**kwargs)
        self.call_connection_id = kwargs.get('call_connection_id')
        self.server_call_id = kwargs.get('server_call_id')
        self.correlation_id = kwargs.get('correlation_id')
        self.operation_context = kwargs.get('operation_context')


class RecognizeCompleted(object):
    """RecognizeCompleted.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also called ChainId for
     skype chain ID.
    :vartype correlation_id: str
    :ivar operation_context: Used by customers when calling mid-call actions to correlate the
     request to the response event.
    :vartype operation_context: str
    :ivar result_information: Contains the resulting SIP code/sub-code and message from NGC
     services.
    :vartype result_information: ~azure.communication.callautomation.models.ResultInformation
    :ivar recognition_type: Determines the sub-type of the recognize operation.
     In case of cancel operation the this field is not set and is returned empty. Known values are:
     "dtmf" and "choices".
    :vartype recognition_type: str or ~azure.communication.callautomation.models.RecognitionType
    :ivar collect_tones_result: Defines the result for RecognitionType = Dtmf.
    :vartype collect_tones_result: ~azure.communication.callautomation.models.CollectTonesResult
    :ivar choice_result: Defines the result for RecognitionType = Choices.
    :vartype choice_result: ~azure.communication.callautomation.models.ChoiceResult
    """

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        """
        :keyword call_connection_id: Call connection ID.
        :paramtype call_connection_id: str
        :keyword server_call_id: Server call ID.
        :paramtype server_call_id: str
        :keyword correlation_id: Correlation ID for event to call correlation. Also called ChainId for
         skype chain ID.
        :paramtype correlation_id: str
        :keyword operation_context: Used by customers when calling mid-call actions to correlate the
         request to the response event.
        :paramtype operation_context: str
        :keyword result_information: Contains the resulting SIP code/sub-code and message from NGC
         services.
        :paramtype result_information: ~azure.communication.callautomation.models.ResultInformation
        :keyword recognition_type: Determines the sub-type of the recognize operation.
         In case of cancel operation the this field is not set and is returned empty. Known values are:
         "dtmf" and "choices".
        :paramtype recognition_type: str or ~azure.communication.callautomation.models.RecognitionType
        :keyword collect_tones_result: Defines the result for RecognitionType = Dtmf.
        :paramtype collect_tones_result: ~azure.communication.callautomation.models.CollectTonesResult
        :keyword choice_result: Defines the result for RecognitionType = Choices.
        :paramtype choice_result: ~azure.communication.callautomation.models.ChoiceResult
        """
        super().__init__(**kwargs)
        self.call_connection_id = kwargs.get('call_connection_id')
        self.server_call_id = kwargs.get('server_call_id')
        self.correlation_id = kwargs.get('correlation_id')
        self.operation_context = kwargs.get('operation_context')
        self.result_information = kwargs.get('result_information')
        self.recognition_type = kwargs.get('recognition_type')
        self.collect_tones_result = kwargs.get('collect_tones_result')
        self.choice_result = kwargs.get('choice_result')


class RecognizeFailed(object):
    """RecognizeFailed.

    :ivar call_connection_id: Call connection ID.
    :vartype call_connection_id: str
    :ivar server_call_id: Server call ID.
    :vartype server_call_id: str
    :ivar correlation_id: Correlation ID for event to call correlation. Also called ChainId for
     skype chain ID.
    :vartype correlation_id: str
    :ivar operation_context: Used by customers when calling mid-call actions to correlate the
     request to the response event.
    :vartype operation_context: str
    :ivar result_information: Contains the resulting SIP code/sub-code and message from NGC
     services.
    :vartype result_information: ~azure.communication.callautomation.models.ResultInformation
    """

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        """
        :keyword call_connection_id: Call connection ID.
        :paramtype call_connection_id: str
        :keyword server_call_id: Server call ID.
        :paramtype server_call_id: str
        :keyword correlation_id: Correlation ID for event to call correlation. Also called ChainId for
         skype chain ID.
        :paramtype correlation_id: str
        :keyword operation_context: Used by customers when calling mid-call actions to correlate the
         request to the response event.
        :paramtype operation_context: str
        :keyword result_information: Contains the resulting SIP code/sub-code and message from NGC
         services.
        :paramtype result_information: ~azure.communication.callautomation.models.ResultInformation
        """
        super().__init__(**kwargs)
        self.call_connection_id = kwargs.get('call_connection_id')
        self.server_call_id = kwargs.get('server_call_id')
        self.correlation_id = kwargs.get('correlation_id')
        self.operation_context = kwargs.get('operation_context')
        self.result_information = kwargs.get('result_information')


class CallInvite(object):
    def __init__(
        self,
        *,
        target: CommunicationIdentifier,
        sourceCallIdNumber: Optional[PhoneNumberIdentifier] = None,
        sourceDisplayName: Optional[str] = None,
        sipHeaders: Optional[dict[str, str]] = None,
        voipHeaders: Optional[dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword target: Target's identity. Required.
        :paramtype target: CommunicationIdentifier
        :keyword sourceCallIdNumber: Caller's phone number identifier
        :paramtype sourceCallIdNumber: PhoneNumberIdentifier
        :keyword sourceDisplayName: Set display name for caller
        :paramtype sourceDisplayName: str
        :keyword sipHeaders: Custom context for PSTN
        :paramtype sipHeaders: str
        :keyword voipHeaders: Custom context for VOIP
        :paramtype voipHeaders: str
        """
        super().__init__(**kwargs)
        self.target = target
        self.sourceCallIdNumber = sourceCallIdNumber
        self.sourceDisplayName = sourceDisplayName
        self.sipHeaders = sipHeaders
        self.voipHeaders = voipHeaders


class CallConnectionProperties(object):
    """Properties of a call connection."""

    def __init__(
        self,
        *,
        call_connection_id: Optional[str] = None,
        server_call_id: Optional[str] = None,
        targets: Optional[List[CommunicationIdentifier]] = None,
        call_connection_state: Optional[Union[str,
                                              CallConnectionStateModel]] = None,
        callback_uri: Optional[str] = None,
        media_subscription_id: Optional[str] = None,
        source_caller_id_number: Optional[PhoneNumberIdentifier] = None,
        source_display_name: Optional[str] = None,
        source_identity: Optional[CommunicationIdentifier] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword call_connection_id: The call connection id.
        :paramtype call_connection_id: str
        :keyword server_call_id: The server call id.
        :paramtype server_call_id: str
        :keyword targets: The targets of the call.
        :paramtype targets:
         list[CommunicationIdentifier]
        :keyword call_connection_state: The state of the call connection. Known values are: "unknown",
         "connecting", "connected", "transferring", "transferAccepted", "disconnecting", and
         "disconnected".
        :paramtype call_connection_state: str or CallConnectionStateModel
        :keyword callback_uri: The callback URI.
        :paramtype callback_uri: str
        :keyword media_subscription_id: SubscriptionId for media streaming.
        :paramtype media_subscription_id: str
        :keyword source_caller_id_number: The source caller Id, a phone number, that's shown to the
         PSTN participant being invited.
         Required only when calling a PSTN callee.
        :paramtype source_caller_id_number: PhoneNumberIdentifier
        :keyword source_display_name: Display name of the call if dialing out to a pstn number.
        :paramtype source_display_name: str
        :keyword source_identity: Source identity.
        :paramtype source_identity: CommunicationIdentifier
        """
        super().__init__(**kwargs)
        self.call_connection_id = call_connection_id
        self.server_call_id = server_call_id
        self.targets = targets
        self.call_connection_state = call_connection_state
        self.callback_uri = callback_uri
        self.media_subscription_id = media_subscription_id
        self.source_caller_id_number = source_caller_id_number
        self.source_display_name = source_display_name
        self.source_identity = source_identity

    @classmethod
    def _from_generated(cls, call_connection_properties_generated: CallConnectionPropertiesGenerated):
        target_models = []
        for target in call_connection_properties_generated.targets:
            target_models.append(deserialize_identifier(target))

        return cls(
            call_connection_id=call_connection_properties_generated.call_connection_id,
            server_call_id=call_connection_properties_generated.server_call_id,
            targets=target_models,
            call_connection_state=call_connection_properties_generated.call_connection_state,
            callback_uri=call_connection_properties_generated.callback_uri,
            media_subscription_id=call_connection_properties_generated.media_subscription_id,
            source_caller_id_number=deserialize_phone_identifier(
                call_connection_properties_generated.source_caller_id_number) if call_connection_properties_generated.source_caller_id_number else None,
            source_display_name=call_connection_properties_generated.source_display_name,
            source_identity=deserialize_identifier(call_connection_properties_generated.source_identity) if call_connection_properties_generated.source_identity else None)


class CallParticipant(object):
    """Contract model of an ACS call participant.
    """

    def __init__(
        self,
        *,
        identifier: CommunicationIdentifier,
        is_muted: bool,
        **kwargs: Any
    ) -> None:
        """
        :keyword identifier: Communication identifier of the participant.
        :paramtype identifier: CommunicationIdentifier
        :keyword is_muted: Is participant muted.
        :paramtype is_muted: bool
        """
        super().__init__(**kwargs)
        self.identifier = identifier
        self.is_muted = is_muted

    @classmethod
    def _from_generated(cls, call_participant_generated: CallParticipantGenerated):
        return cls(identifier=deserialize_identifier(call_participant_generated.identifier), is_muted=call_participant_generated.is_muted)


class GetParticipantsResponse(object):
    """The response payload for getting participants of the call."""

    def __init__(
        self,
        *,
        values: Optional[List["_models.CallParticipant"]] = None,
        next_link: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword values: List of the current participants in the call.
        :paramtype values: list[CallParticipant]
        :keyword next_link: Continue of the list of participants.
        :paramtype next_link: str
        """
        super().__init__(**kwargs)
        self.values = values
        self.next_link = next_link

    @classmethod
    def _from_generated(cls, get_participant_response_generated: GetParticipantsResponseGenerated):
        return cls(values=[CallParticipant._from_generated(participant) for participant in get_participant_response_generated.values], next_link=get_participant_response_generated.next_link)


class AddParticipantResponse(object):
    """The response payload for adding participants to the call.
    """

    def __init__(
        self,
        *,
        participant: Optional[CallParticipant] = None,
        operation_context: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword participant: List of current participants in the call.
        :paramtype participant: CallParticipant
        :keyword operation_context: The operation context provided by client.
        :paramtype operation_context: str
        """
        super().__init__(**kwargs)
        self.participant = participant
        self.operation_context = operation_context

    @classmethod
    def _from_generated(cls, add_participant_response_generated: AddParticipantResponseGenerated):
        return cls(participant=CallParticipant._from_generated(add_participant_response_generated.participant), operation_context=add_participant_response_generated.operation_context)
