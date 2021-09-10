# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._generated.models import EventSubscriptionType, MediaType
from ._shared.models import PhoneNumberIdentifier

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse # type: ignore

from typing import Any


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

        self.__callback_uri = callback_uri
        self.__requested_media_types = requested_media_types
        self.__requested_call_events = requested_call_events
        self.__alternate_Caller_Id = None
        self.__subject = None

    @property
    def callback_uri(self):
        return self.__callback_uri

    @property
    def requested_media_types(self):
        return self.__requested_media_types

    @property
    def requested_call_events(self):
        return self.__requested_call_events

    @property
    def alternate_Caller_Id(self):
        return self.__alternate_Caller_Id
    @alternate_Caller_Id.setter
    def alternate_Caller_Id(self, alternate_Caller_Id: PhoneNumberIdentifier):
        self.__alternate_Caller_Id = alternate_Caller_Id

    @property
    def subject(self):
        return self.__subject
    @subject.setter
    def subject(self, subject: str):
        self.__subject = subject

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

        self.__callback_uri = callback_uri
        self.__requested_media_types = requested_media_types
        self.__requested_call_events = requested_call_events

    @property
    def callback_uri(self):
        return self.__callback_uri

    @property
    def requested_media_types(self):
        return self.__requested_media_types

    @property
    def requested_call_events(self):
        return self.__requested_call_events

    @property
    def subject(self):
        return self._subject
    @subject.setter
    def subject(self, value: str):
        self._subject = value

class PlayAudioOptions(object):

    def __init__(
        self,
        *,
        loop: bool,
        operation_context: str,
        audio_file_id: str,
        callback_uri: str,
    ):
        self.loop = loop
        self.operation_context = operation_context
        self.audio_file_id = audio_file_id
        self.callback_uri = callback_uri

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

class CancelAllMediaOperationsResult(object):

    def __init__(
        self,
        **kwargs # type: Any
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
            result_info=ResultInfo._from_generated(cancel_all_media_operations_result.result_info)
        )

class AddParticipantResult(object):

    def __init__(
        self,
        **kwargs # type: Any
    ):
        self.participant_id = kwargs['participant_id']

    @classmethod
    def _from_generated(cls, add_participant_result):
        if add_participant_result is None:
            return None

        return cls(
            participant_id=add_participant_result.participant_id
        )

class ResultInfo(object):
    def __init__(
        self,
        **kwargs # type: Any
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
