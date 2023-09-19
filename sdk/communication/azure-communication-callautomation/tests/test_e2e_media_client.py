# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import timedelta
from devtools_testutils import recorded_by_proxy
from azure.communication.callautomation import (
    FileSource,
    DtmfTone,
    PhoneNumberIdentifier
)
from callautomation_test_case import CallAutomationRecordedTestCase

class TestMediaAutomatedLiveTest(CallAutomationRecordedTestCase):

    @recorded_by_proxy
    def test_play_media_in_a_call(self):
        # try to establish the call
        caller = self.identity_client.create_user()
        target = self.identity_client.create_user()
        unique_id, call_connection, _ = self.establish_callconnection_voip(caller, target)

        # check returned events
        connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        # play media to all participants
        file_source = FileSource(url=self.file_source_url)
        call_connection.play_media_to_all(
            play_source=file_source,
        )

        # check for PlayCompleted event
        play_completed_event = self.check_for_event('PlayCompleted', call_connection._call_connection_id, timedelta(seconds=30))
        if play_completed_event is None:
            raise ValueError("PlayCompleted event is None")

        self.terminate_call(unique_id)
        return

    @recorded_by_proxy
    def test_dtmf_actions_in_a_call(self):
        # try to establish the call
        purchased_numbers = list(self.phonenumber_client.list_purchased_phone_numbers())
        if len(purchased_numbers) >= 2:
            caller = PhoneNumberIdentifier(purchased_numbers[0].phone_number)
            target = PhoneNumberIdentifier(purchased_numbers[1].phone_number)
        else:
            raise ValueError("Invalid PSTN setup, test needs at least 2 phone numbers")

        unique_id, call_connection, _ = self.establish_callconnection_pstn(caller, target)

        # check returned events
        connected_event = self.check_for_event('CallConnected', call_connection._call_connection_id, timedelta(seconds=15))
        participant_updated_event = self.check_for_event('ParticipantsUpdated', call_connection._call_connection_id, timedelta(seconds=15))

        if connected_event is None:
            raise ValueError("Caller CallConnected event is None")
        if participant_updated_event is None:
            raise ValueError("Caller ParticipantsUpdated event is None")

        call_connection.start_continuous_dtmf_recognition(target_participant=target)

        # send DTMF tones
        call_connection.send_dtmf(tones=[DtmfTone.POUND], target_participant=target)
        send_dtmf_completed_event = self.check_for_event('SendDtmfCompleted', call_connection._call_connection_id, timedelta(seconds=15),)
        if send_dtmf_completed_event is None:
            raise ValueError("SendDtmfCompleted event is None")

        # stop continuous DTMF recognition
        call_connection.stop_continuous_dtmf_recognition(target_participant=target)
        continuous_dtmf_recognition_stopped_event = self.check_for_event('ContinuousDtmfRecognitionStopped', call_connection._call_connection_id, timedelta(seconds=15))
        if continuous_dtmf_recognition_stopped_event is None:
            raise ValueError("ContinuousDtmfRecognitionStopped event is None")

        self.terminate_call(unique_id)
        return
