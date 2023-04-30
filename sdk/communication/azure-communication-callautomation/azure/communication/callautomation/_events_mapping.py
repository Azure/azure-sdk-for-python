# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ._events import (
    AddParticipantSucceededEventData,
    AddParticipantFailedEventData,
    CallConnectedEventData,
    CallDisconnectedEventData,
    CallTransferAcceptedEventData,
    CallTransferFailedEventData,
    ParticipantsUpdatedEventData,
    RecordingStateChangedEventData,
    PlayCompletedEventData,
    PlayFailedEventData,
    PlayCanceledEventData,
    RecognizeCompletedEventData,
    RecognizeCanceledEventData,
    RecognizeFailedEventData,
    RemoveParticipantSucceededEventData,
    RemoveParticipantFailedEventData,
    ContinuousDtmfRecognitionToneReceivedEventData,
    ContinuousDtmfRecognitionToneFailedEventData,
    ContinuousDtmfRecognitionStoppedEventData,
    SendDtmfCompletedEventData,
    SendDtmfFailedEventData
)

_call_automation_event_mapping = {
    "AddParticipantSucceeded": AddParticipantSucceededEventData,
    "AddParticipantFailed": AddParticipantFailedEventData,
    "CallConnected": CallConnectedEventData,
    "CallDisconnected": CallDisconnectedEventData,
    "CallTransferAccepted": CallTransferAcceptedEventData,
    "CallTransferFailed": CallTransferFailedEventData,
    "ParticipantsUpdated": ParticipantsUpdatedEventData,
    "RecordingStateChanged": RecordingStateChangedEventData,
    "PlayCompleted": PlayCompletedEventData,
    "PlayFailed": PlayFailedEventData,
    "PlayCanceled": PlayCanceledEventData,
    "RecognizeCompleted": RecognizeCompletedEventData,
    "RecognizeCanceled": RecognizeCanceledEventData,
    "RecognizeFailed": RecognizeFailedEventData,
    "RemoveParticipantSucceeded": RemoveParticipantSucceededEventData,
    "RemoveParticipantFailed": RemoveParticipantFailedEventData,
    "ContinuousDtmfRecognitionToneReceived": ContinuousDtmfRecognitionToneReceivedEventData,
    "ContinuousDtmfRecognitionToneFailed": ContinuousDtmfRecognitionToneFailedEventData,
    "ContinuousDtmfRecognitionStopped": ContinuousDtmfRecognitionStoppedEventData,
    "SendDtmfCompleted": SendDtmfCompletedEventData,
    "SendDtmfFailed": SendDtmfFailedEventData
}

def get_mapping():
    return _call_automation_event_mapping
