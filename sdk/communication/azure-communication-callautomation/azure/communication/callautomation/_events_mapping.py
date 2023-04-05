# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._events import (
    AddParticipantSucceeded,
    AddParticipantFailed,
    CallConnected,
    CallDisconnected,
    CallTransferAccepted,
    CallTransferFailed,
    ParticipantsUpdated,
    RecordingStateChanged,
    PlayCompleted,
    PlayFailed,
    PlayCanceled,
    RecognizeCompleted,
    RecognizeCanceled,
    RecognizeFailed,
    RemoveParticipantSucceeded,
    RemoveParticipantFailed
)

_call_automation_event_mapping = {
    "AddParticipantSucceeded": AddParticipantSucceeded,
    "AddParticipantFailed": AddParticipantFailed,
    "CallConnected": CallConnected,
    "CallDisconnected": CallDisconnected,
    "CallTransferAccepted": CallTransferAccepted,
    "CallTransferFailed": CallTransferFailed,
    "ParticipantsUpdated": ParticipantsUpdated,
    "RecordingStateChanged": RecordingStateChanged,
    "PlayCompleted": PlayCompleted,
    "PlayFailed": PlayFailed,
    "PlayCanceled": PlayCanceled,
    "RecognizeCompleted": RecognizeCompleted,
    "RecognizeCanceled": RecognizeCanceled,
    "RecognizeFailed": RecognizeFailed,
    "RemoveParticipantSucceeded": RemoveParticipantSucceeded,
    "RemoveParticipantFailed": RemoveParticipantFailed
}

def get_mapping():
    return _call_automation_event_mapping
