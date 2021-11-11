# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: skip-file

from typing import List, Mapping, Optional, Union, Any  # pylint: disable=unused-import
from enum import Enum, EnumMeta
from six import with_metaclass
from ._generated.models import CallingEventSubscriptionType, CallMediaType
from ._shared.models import PhoneNumberIdentifier

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse # type: ignore

try:
    from typing import Protocol, TypedDict
except ImportError:
    from typing_extensions import Protocol, TypedDict
from azure.core import CaseInsensitiveEnumMeta

class CallLocatorKind(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Call Locator Kind."""

    GROUP_CALL_LOCATOR = "groupCallLocator"
    SERVER_CALL_LOCATOR = "serverCallLocator"

class CallLocator(Protocol):
    """Call Locator.

    :ivar kind: The type of locator.
    :vartype kind: str or CallLocatorKind
    :ivar Mapping[str, Any] properties: The properties of the locator.
    """
    id = str  # type: str
    kind = None  # type: Union[CallLocatorKind, str]
    properties = {}  # type: Mapping[str, Any]

class GroupCallLocator(CallLocator):
    """The group call locator.

    :ivar kind: The type of locator.
    :vartype kind: str or CallLocatorKind
    :ivar Mapping[str, Any] properties: The properties of the locator.
     The keys in this mapping include:
        - `id`(str): ID of the Call.

    :param str id: ID of the Call.

    :ivar id: Required. The group call id.
    :type id: str
    """
    kind = CallLocatorKind.GROUP_CALL_LOCATOR

    def __init__(self, id):
        # type: (str) -> None
        if not id:
            raise ValueError("id can not be None or empty")
        self.id = id
        self.properties = {}

class ServerCallLocator(CallLocator):
    """The server call locator.

    :ivar kind: The type of locator.
    :vartype kind: str or CallLocatorKind
    :ivar Mapping[str, Any] properties: The properties of the locator.
     The keys in this mapping include:
        - `id`(str): ID of the Call.

    :param str id: ID of the Call.

    :ivar id: Required. The server call id.
    :type id: str
    """
    kind = CallLocatorKind.SERVER_CALL_LOCATOR

    def __init__(self, id):
        # type: (str) -> None
        if not id:
            raise ValueError("id can not be None or empty")
        self.id = id
        self.properties = {}

class CallingServerEventType(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """The calling server event type values.
    """
    CALL_CONNECTION_STATE_CHANGED_EVENT = "Microsoft.Communication.CallConnectionStateChanged"
    ADD_PARTICIPANT_RESULT_EVENT = "Microsoft.Communication.AddParticipantResult"
    CALL_RECORDING_STATE_CHANGED_EVENT = "Microsoft.Communication.CallRecordingStateChanged"
    PLAY_AUDIO_RESULT_EVENT = "Microsoft.Communication.PlayAudioResult"
    PARTICIPANTS_UPDATED_EVENT = "Microsoft.Communication.ParticipantsUpdated"
    TONE_RECEIVED_EVENT = "Microsoft.Communication.DtmfReceived"

class ParallelDownloadOptions(object):
    """The options to configure parallel downloads.
    :ivar max_concurrency: Max number of threads used to download.
    :type max_concurrency: int
    :ivar block_size: Block size to download on each request.
    :type block_size: int
    """
    def __init__(
        self,
        max_concurrency=1, # type: int
        block_size=4*1024*1024, # type: int
    ):  # type: (...) -> None
        self.__max_concurrency = max_concurrency
        self.__block_size = block_size

    @property
    def max_concurrency(self):
        # type: () -> int
        return self.__max_concurrency

    @property
    def block_size(self):
        # type: () -> int
        return self.__block_size
