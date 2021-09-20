# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Any, List, Optional  # pylint: disable=unused-import
from ._generated.models import (EventSubscriptionType,
                                MediaType,
                                CallConnectionStateChangedEvent,
                                ToneReceivedEvent,
                                ToneInfo,
                                PlayAudioResultEvent,
                                PhoneNumberIdentifierModel,
                                CommunicationIdentifierModel,
                                CommunicationUserIdentifierModel,
                                AddParticipantResultEvent,
                                CallConnectionState,
                                OperationStatus,
                                ToneValue,
                                CancelAllMediaOperationsResult,
                                PlayAudioResult,
                                AddParticipantResult)
from ._shared.models import PhoneNumberIdentifier
from enum import Enum, EnumMeta
from six import with_metaclass
import msrest.serialization

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # type: ignore

from typing import Any

class _CaseInsensitiveEnumMeta(EnumMeta):
    def __getitem__(self, name):
        return super().__getitem__(name.upper())

    def __getattr__(cls, name):
        """Return the enum member matching `name`
        We use __getattr__ instead of descriptors or inserting into the enum
        class' __dict__ in order to support `name` and `value` being both
        properties for enum members (which live in the class' __dict__) and
        enum members themselves.
        """
        try:
            return cls._member_map_[name.upper()]
        except KeyError:
            raise AttributeError(name)

class CreateCallOptions(object):
    """The options for creating a call.

    All required parameters must be populated in order to send to Azure.

    :ivar callback_uri: Required. The callback URI.
    :type callback_uri: str
    :ivar requested_media_types: The requested media types.
    :type requested_media_types: list[str or ~azure.communication.callingserver.models.MediaType]
    :ivar requested_call_events: The requested call events to subscribe to.
    :type requested_call_events: list[str or
     ~azure.communication.callingserver.models.EventSubscriptionType]
    """
    def __init__(
        self,
        callback_uri,  # type: str
        requested_media_types,  # type: List[MediaType]
        requested_call_events  # type: List[EventSubscriptionType]
    ):  # type: (...) -> None
        try:
            if not callback_uri.lower().startswith('http'):
                callback_uri = "https://" + callback_uri
        except AttributeError:
            raise ValueError("Host URL must be a string")

        parsed_url = urlparse(callback_uri.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(callback_uri))

        if not requested_media_types:
            raise ValueError("requestedMediaTypes can not be None or empty")

        if not requested_call_events:
            raise ValueError("requestedCallEvents can not be None or empty")

        self.__callback_uri = callback_uri
        self.__requested_media_types = requested_media_types
        self.__requested_call_events = requested_call_events
        self.__alternate_Caller_Id = None
        self.__subject = None

    @property
    def callback_uri(self):
        # type: () -> Optional[str]
        return self.__callback_uri

    @property
    def requested_media_types(self):
        # type: () -> Optional[str]
        return self.__requested_media_types

    @property
    def requested_call_events(self):
        # type: () -> List[EventSubscriptionType]
        return self.__requested_call_events

    @property
    def alternate_Caller_Id(self):
        # type: () -> Optional[PhoneNumberIdentifier]
        return self.__alternate_Caller_Id
    @alternate_Caller_Id.setter
    def alternate_Caller_Id(self, alternate_Caller_Id):
        # type: (PhoneNumberIdentifier) -> None
        self.__alternate_Caller_Id = alternate_Caller_Id

    @property
    def subject(self):
        # type: () -> Optional[str]
        return self.__subject
    @subject.setter
    def subject(self, subject):
        # type: (str) -> None
        self.__subject = subject

class JoinCallOptions(object):
    """The options for joining a call.

    All required parameters must be populated in order to send to Azure.

    :ivar callback_uri: Required. The callback URI.
    :type callback_uri: str
    :ivar requested_media_types: The requested media types.
    :type requested_media_types: list[str or ~azure.communication.callingserver.models.MediaType]
    :ivar requested_call_events: The requested call events to subscribe to.
    :type requested_call_events: list[str or
     ~azure.communication.callingserver.models.EventSubscriptionType]
    """
    def __init__(
        self,
        callback_uri,  # type: str
        requested_media_types,  # type: List[MediaType]
        requested_call_events  # type: List[EventSubscriptionType]
    ):  # type: (...) -> None
        try:
            if not callback_uri.lower().startswith('http'):
                callback_uri = "https://" + callback_uri
        except AttributeError:
            raise ValueError("Host URL must be a string")

        parsed_url = urlparse(callback_uri.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(callback_uri))

        if not requested_media_types:
            raise ValueError("requestedMediaTypes can not be None or empty")

        if not requested_call_events:
            raise ValueError("requestedCallEvents can not be None or empty")

        self.__callback_uri = callback_uri
        self.__requested_media_types = requested_media_types
        self.__requested_call_events = requested_call_events
        self.__subject = None

    @property
    def callback_uri(self):
        # type: () -> str
        return self.__callback_uri

    @property
    def requested_media_types(self):
        # type: () -> List[MediaType]
        return self.__requested_media_types

    @property
    def requested_call_events(self):
        # type: () -> List[EventSubscriptionType]
        return self.__requested_call_events

    @property
    def subject(self):
        # type: () -> Optional[str]
        return self.__subject
    @subject.setter
    def subject(self, subject):
        # type: (str) -> None
        self.__subject = subject

class PlayAudioOptions(object):
    """The options for playing audio.

    All required parameters must be populated in order to send to Azure.

    :ivar loop: Required. The flag indicating whether audio file needs to be played in loop or not.
    :type loop: bool
    :ivar operation_context: Required. The value to identify context of the operation.
    :type operation_context: str
    :ivar audio_file_id: Required. An id for the media in the AudioFileUri, using which we cache the media resource.
    :type audio_file_id: str
    :ivar callback_uri: Required. The callback Uri to receive PlayAudio status notifications.
    :type callback_uri: str
    """
    def __init__(
        self,
        loop,  # type: bool
        operation_context,  # type: str
        audio_file_id,  # type: str
        callback_uri  # type: str
    ):  # type: (...) -> None
        self.loop = loop
        self.operation_context = operation_context
        self.audio_file_id = audio_file_id
        self.callback_uri = callback_uri
        self.__subject = None

    @property
    def subject(self):
        # type: () -> Optional[str]
        return self.__subject
    @subject.setter
    def subject(self, subject):
        # type: (str) -> None
        self.__subject = subject

class PlayAudioResult(object):
    def __init__(
        self,
        **kwargs  # type: Any
    ):
        self.__operation_id = kwargs['operation_id']
        self.__status = kwargs['status']
        self.__operation_context = kwargs['operation_context']
        self.__result_info = kwargs['result_info']

    @classmethod
    def _from_generated(cls, play_audio_result):
        if play_audio_result is None:
            return None

        return cls(
            operation_id=play_audio_result.operation_id,
            status=play_audio_result.status,
            operation_context=play_audio_result.operation_context,
            result_info=ResultInfo._from_generated(
                play_audio_result.result_info)
        )

    @property
    def operation_id(self):
        # type: () -> List[MediaType]
        return self.__operation_id

    @property
    def status(self):
        # type: () -> List[MediaType]
        return self.__status

    @property
    def operation_context(self):
        # type: () -> List[MediaType]
        return self.__operation_context

    @property
    def result_info(self):
        # type: () -> List[MediaType]
        return self.__result_info

class CancelAllMediaOperationsResult(object):
    def __init__(
        self,
        **kwargs  # type: Any
    ):
        self.__operation_id = kwargs['operation_id']
        self.__status = kwargs['status']
        self.__operation_context = kwargs['operation_context']
        self.__result_info = kwargs['result_info']

    @classmethod
    def _from_generated(cls, cancel_all_media_operations_result):
        if cancel_all_media_operations_result is None:
            return None

        return cls(
            operation_id=cancel_all_media_operations_result.operation_id,
            status=cancel_all_media_operations_result.status,
            operation_context=cancel_all_media_operations_result.operation_context,
            result_info=ResultInfo._from_generated(
                cancel_all_media_operations_result.result_info)
        )

    @property
    def operation_id(self):
        # type: () -> List[MediaType]
        return self.__operation_id

    @property
    def status(self):
        # type: () -> List[MediaType]
        return self.__status

    @property
    def operation_context(self):
        # type: () -> List[MediaType]
        return self.__operation_context

    @property
    def result_info(self):
        # type: () -> List[MediaType]
        return self.__result_info

class AddParticipantResult(object):
    def __init__(
        self,
        **kwargs  # type: Any
    ):
        self.__participant_id = kwargs['participant_id']

    @classmethod
    def _from_generated(cls, add_participant_result):
        if add_participant_result is None:
            return None

        return cls(
            participant_id=add_participant_result.participant_id
        )

    @property
    def participant_id(self):
        # type: () -> List[MediaType]
        return self.__participant_id

class ResultInfo(object):
    def __init__(
        self,
        **kwargs  # type: Any
    ):
        self.code = kwargs['code']
        self.subcode = kwargs['subcode']
        self.message = kwargs['message']

    @classmethod
    def _from_generated(cls, result_info):
        if result_info is None:
            return None

        return cls(
            code=result_info.code,
            subcode=result_info.subcode,
            message=result_info.message,
        )

class CreateCallResult(object):
    """The response payload of the create call operation.

    :param call_connection_id: The call connection id.
    :type call_connection_id: str
    """
    def __init__(
        self,
        **kwargs  # type: Any
    ):  # type: (...) -> None
        self.__call_connection_id = kwargs['call_connection_id']

    @classmethod
    def _from_generated(cls, create_call_result):
        if create_call_result is None:
            return None

        return cls(
            __call_connection_id=create_call_result.call_connection_id
        )

    @property
    def call_connection_id(self):
        # type: () -> List[MediaType]
        return self.__call_connection_id

class JoinCallResult(object):
    """The response payload of the join call operation.

    :param call_connection_id: The call connection id.
    :type call_connection_id: str
    """
    def __init__(
        self,
        **kwargs  # type: Any
    ):
        self.__call_connection_id = kwargs['call_connection_id']

    @classmethod
    def _from_generated(cls, join_call_result):
        if join_call_result is None:
            return None

        return cls(
            __call_connection_id=join_call_result.call_connection_id
        )

    @property
    def call_connection_id(self):
        # type: () -> List[MediaType]
        return self.__call_connection_id

class StartCallRecordingResult(object):
    """The response payload of start call recording operation.

    :param recording_id: The recording id of the started recording.
    :type recording_id: str
    """
    def __init__(
        self,
        **kwargs  # type: Any
    ):
        self.__recording_id = kwargs['recording_id']

    @classmethod
    def _from_generated(cls, start_call_recording_result):
        if start_call_recording_result is None:
            return None

        return cls(
            recording_id=start_call_recording_result.recording_id
        )

    @property
    def recording_id(self):
        # type: () -> List[MediaType]
        return self.__recording_id

class CallRecordingProperties(object):
    """The response payload of get call recording properties operation.

    All required parameters must be populated in order to send to Azure.

    :param recording_state: Required. The state of the recording. Possible values include:
     "active", "inactive".
    :type recording_state: str or ~azure.communication.callingserver.models.CallRecordingState
    """
    _validation = {
        'recording_state': {'required': True},
    }

    _attribute_map = {
        'recording_state': {'key': 'recordingState', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs  # type: Any
    ):
        self.recording_state = kwargs['recording_state']

    @classmethod
    def _from_generated(cls, call_recording_state_result):
        if call_recording_state_result is None:
            return None

        return cls(
            recording_state=call_recording_state_result.recording_state
        )

class CallingServerEventType(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """The calling server event type values.
    """
    CALL_CONNECTION_STATE_CHANGED_EVENT = "Microsoft.Communication.CallConnectionStateChanged"
    ADD_PARTICIPANT_RESULT_EVENT = "Microsoft.Communication.AddParticipantResult"
    CALL_RECORDING_STATE_CHANGED_EVENT = "Microsoft.Communication.CallRecordingStateChanged"
    PLAY_AUDIO_RESULT_EVENT = "Microsoft.Communication.PlayAudioResult"
    PARTICIPANTS_UPDATED_EVENT = "Microsoft.Communication.ParticipantsUpdated"
    TONE_RECEIVED_EVENT = "Microsoft.Communication.DtmfReceived"
