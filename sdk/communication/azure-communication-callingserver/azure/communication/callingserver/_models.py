# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Any  # pylint: disable=unused-import

from ._generated.models import EventSubscriptionType, MediaType
from ._shared.models import PhoneNumberIdentifier
from enum import Enum, EnumMeta
from six import with_metaclass
import msrest.serialization

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse # type: ignore

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
        self._subject = None

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
        return self._subject
    @subject.setter
    def subject(self, value):
        # type: (str) -> None
        self._subject = value

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

    @property
    def subject(self):
        # type: () -> Optional[str]
        return self._subject
    @subject.setter
    def subject(self, value):
        # type: (str) -> None
        self._subject = value
