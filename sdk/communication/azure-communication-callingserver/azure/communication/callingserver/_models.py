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
