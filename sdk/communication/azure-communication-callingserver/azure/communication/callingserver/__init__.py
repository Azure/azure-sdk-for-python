# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._version import VERSION

from ._call_connection import CallConnection
from ._callingserver_client import CallingServerClient
from ._generated.models import (AudioRoutingMode, AddParticipantResult, CallConnectionProperties,
                                CallRejectReason, CreateCallRequest, PhoneNumberIdentifierModel,
                                PlayAudioRequest, PlayAudioResult, CallParticipant,
                                CallMediaType, CallingEventSubscriptionType,
                                CallingOperationStatus, CallConnectionStateChangedEvent,
                                ToneReceivedEvent, ToneInfo,
                                PlayAudioResultEvent, CommunicationIdentifierModel,
                                CommunicationUserIdentifierModel, AddParticipantResultEvent,
                                CallConnectionState, ToneValue, AnswerCallResult, AudioRoutingGroupResult,
                                CreateAudioRoutingGroupResult)
from ._models import (
    CreateCallOptions,
    JoinCallOptions,
    PlayAudioOptions,
    CallLocator,
    GroupCallLocator,
    ServerCallLocator,
    CallingServerEventType
    )
from ._shared.models import CommunicationIdentifier, CommunicationUserIdentifier, PhoneNumberIdentifier

__all__ = [
    'AudioRoutingMode',
    'AddParticipantResult',
    'CallParticipant',
    'CallRejectReason',
    'CallConnectionProperties',
    'CallConnection',
    'CallingServerClient',
    'CommunicationIdentifier',
    'CommunicationUserIdentifier',
    'CreateCallOptions',
    'CreateCallRequest',
    'CallingEventSubscriptionType',
    'JoinCallOptions',
    'CallMediaType',
    'CallingOperationStatus',
    'PhoneNumberIdentifier',
    'PhoneNumberIdentifierModel',
    'PlayAudioOptions',
    'PlayAudioRequest',
    'PlayAudioResult',
    'CallLocator',
    'GroupCallLocator',
    'ServerCallLocator',
    'CallConnectionStateChangedEvent',
    'ToneReceivedEvent',
    'ToneInfo',
    'PlayAudioResultEvent',
    'CommunicationIdentifierModel',
    'CommunicationUserIdentifierModel',
    'AddParticipantResultEvent',
    'CallConnectionState',
    'ToneValue',
    'CallingServerEventType',
    'AnswerCallResult',
    'AudioRoutingGroupResult',
    'CreateAudioRoutingGroupResult'
]
__version__ = VERSION
