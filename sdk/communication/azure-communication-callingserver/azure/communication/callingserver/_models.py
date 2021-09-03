# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._generated.models import EventSubscriptionType, MediaType
from ._shared.models import PhoneNumberIdentifier
from enum import Enum, EnumMeta
from six import with_metaclass
import msrest.serialization

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse # type: ignore

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

    def __init__(
        self,
        *,
        callback_uri: str,
        requested_media_types: MediaType,
        requested_call_events: EventSubscriptionType,
    ):
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

        self.callback_uri = callback_uri
        self.requested_media_types = requested_media_types
        self.requested_call_events = requested_call_events
        self.subject = None

    @property
    def alternate_Caller_Id(self):
        return self._alternate_Caller_Id
    @alternate_Caller_Id.setter
    def alternate_Caller_Id(self, value: PhoneNumberIdentifier):
        self._alternate_Caller_Id = value

    @property
    def subject(self):
        return self._subject
    @subject.setter
    def subject(self, value: str):
        self._subject = value


class JoinCallOptions(object):

    def __init__(
        self,
        *,
        callback_uri: str,
        requested_media_types: MediaType,
        requested_call_events: EventSubscriptionType,
    ):
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

        self._callback_uri = callback_uri
        self._requested_media_types = requested_media_types
        self._requested_call_events = requested_call_events

    @property
    def subject(self):
        return self._subject
    @subject.setter
    def subject(self, value: str):
        self._subject = value


class PlayAudioResult(object):

    def __init__(
        self,
        **kwargs # type: Any
    ):
        # type: (...) -> None
        self.operation_id = kwargs['operation_id']
        self.status = kwargs['status']
        self.operation_context = kwargs['operation_context']
        self.result_info = kwargs['result_info']

    @classmethod
    def _from_generated(cls, play_audio_result):
        if play_audio_result is None:
            return None

        return cls(
            operation_id=play_audio_result.operation_id,
            status=play_audio_result.status,
            operation_context=play_audio_result.operation_context,
            result_info=ResultInfo._from_generated(play_audio_result.result_info)
        )


class ResultInfo(object):
    def __init__(
        self,
        **kwargs # type: Any
    ):
        # type: (...) -> None
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


class CallingServerEventType(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """The calling server event type values.
    """

    CALL_CONNECTION_STATE_CHANGED_EVENT = "Microsoft.Communication.CallConnectionStateChanged"
    ADD_PARTICIPANT_RESULT_EVENT = "Microsoft.Communication.AddParticipantResult"
    CALL_RECORDING_STATE_CHANGED_EVENT = "Microsoft.Communication.CallRecordingStateChanged"
    PLAY_AUDIO_RESULT_EVENT = "Microsoft.Communication.PlayAudioResult"
    PARTICIPANTS_UPDATED_EVENT = "Microsoft.Communication.ParticipantsUpdated"
    TONE_RECEIVED_EVENT = "Microsoft.Communication.DtmfReceived"


class CancelAllMediaOperationsResult(msrest.serialization.Model):
    """The response payload of the cancel all media operations.

    All required parameters must be populated in order to send to Azure.

    :param operation_id: The operation id.
    :type operation_id: str
    :param status: Required. The status of the operation. Possible values include: "notStarted",
     "running", "completed", "failed".
    :type status: str or ~azure.communication.callingserver.models.OperationStatus
    :param operation_context: The operation context provided by client.
    :type operation_context: str
    :param result_info: The result info for the operation.
    :type result_info: ~azure.communication.callingserver.models.ResultInfo
    """

    def __init__(
        self,
        **kwargs
    ):
        self.operation_id = kwargs['operation_id']
        self.status = kwargs['status']
        self.operation_context = kwargs['operation_context']
        self.result_info = kwargs['result_info']

    @classmethod
    def _from_generated(cls, cancel_all_media_operations_result):
        if cancel_all_media_operations_result is None:
            return None

        return cls(
            operation_id=cancel_all_media_operations_result.operation_id,
            status=cancel_all_media_operations_result.status,
            operation_context=cancel_all_media_operations_result.operation_context,
            result_info=cancel_all_media_operations_result.result_info
        )

    
class AddParticipantResult(msrest.serialization.Model):
    """The add participant result.
    :param participant_id: The id of the added participant.
    :type participant_id: str
    """

    def __init__(
        self,
        **kwargs
    ):
        self.participant_id = kwargs['participant_id']

    @classmethod
    def _from_generated(cls, add_participant_result):
        if add_participant_result is None:
            return None

        return cls(
            participant_id=add_participant_result.participant_id
        )


class JoinCallResult(msrest.serialization.Model):
    """The response payload of the join call operation.

    :param call_connection_id: The call connection id.
    :type call_connection_id: str
    """

    def __init__(
        self,
        **kwargs
    ):
        self.call_connection_id = kwargs['call_connection_id']

    @classmethod
    def _from_generated(cls, join_call_result):
        if join_call_result is None:
            return None

        return cls(
            call_connection_id = join_call_result.call_connection_id
        )


class CreateCallResult(msrest.serialization.Model):
    """The response payload of the create call operation.

    :param call_connection_id: The call connection id.
    :type call_connection_id: str
    """

    def __init__(
        self,
        **kwargs
    ):
        self.call_connection_id = kwargs['call_connection_id']

    @classmethod
    def _from_generated(cls, create_call_result):
        if create_call_result is None:
            return None

        return cls(
            call_connection_id = create_call_result.call_connection_id
        )


class StartCallRecordingResult(msrest.serialization.Model):
    """The response payload of start call recording operation.

    :param recording_id: The recording id of the started recording.
    :type recording_id: str
    """

    def __init__(
        self,
        **kwargs
    ):
        self.recording_id = kwargs['recording_id']

    @classmethod
    def _from_generated(cls, start_call_recording_result):
        if start_call_recording_result is None:
            return None

        return cls(
            recording_id = start_call_recording_result.recording_id
        )
