# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._events import (
    AddParticipantsSucceeded,
    AddParticipantsFailed,
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
    RecognizeFailed
)

_call_automation_event_mapping = {
    "Microsoft.Communication.AddParticipantsSucceeded": AddParticipantsSucceeded,
    "Microsoft.Communication.AddParticipantsFailed": AddParticipantsFailed,
    "Microsoft.Communication.CallConnected": CallConnected,
    "Microsoft.Communication.CallDisconnected": CallDisconnected,
    "Microsoft.Communication.CallTransferAccepted": CallTransferAccepted,
    "Microsoft.Communication.CallTransferFailed": CallTransferFailed,
    "Microsoft.Communication.ParticipantsUpdated": ParticipantsUpdated,
    "Microsoft.Communication.RecordingStateChanged": RecordingStateChanged,
    "Microsoft.Communication.PlayCompleted": PlayCompleted,
    "Microsoft.Communication.PlayFailed": PlayFailed,
    "Microsoft.Communication.PlayCanceled": PlayCanceled,
    "Microsoft.Communication.RecognizeCompleted": RecognizeCompleted,
    "Microsoft.Communication.RecognizeCanceled": RecognizeCanceled,
    "Microsoft.Communication.RecognizeFailed": RecognizeFailed
}

def get_mapping():
    return _call_automation_event_mapping
