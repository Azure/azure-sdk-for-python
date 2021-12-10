# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import uuid
import os
import pytest
import utils._test_constants as CONST

from azure.communication.callingserver import (
    CallingServerClient,
    PhoneNumberIdentifier,
    CallMediaType,
    CallingEventSubscriptionType,
    CommunicationUserIdentifier
    )
from azure.communication.callingserver._shared.utils import parse_connection_str
from azure.identity import DefaultAzureCredential
from _shared.testcase import (
    CommunicationTestCase,
    BodyReplacerProcessor,
    ResponseReplacerProcessor
)
from devtools_testutils import is_live
from _shared.utils import get_http_logging_policy
from utils._live_test_utils import CallingServerLiveTestUtils, RequestReplacerProcessor
from utils._test_mock_utils import FakeTokenCredential

class CallConnectionTest(CommunicationTestCase):

    def setUp(self):
        super(CallConnectionTest, self).setUp()

        if self.is_playback():
            self.from_phone_number = "+15551234567"
            self.to_phone_number = "+15551234567"
            self.recording_processors.extend([
                BodyReplacerProcessor(keys=["alternateCallerId", "targets", "source", "callbackUri", "identity", "communicationUser", "rawId", "callConnectionId", "phoneNumber", "serverCallId"])])
        else:
            self.to_phone_number = os.getenv("AZURE_PHONE_NUMBER")
            self.from_phone_number = os.getenv("ALTERNATE_CALLERID")
            self.partcipant_guid = os.getenv("PARTICIPANT_GUID")
            self.recording_processors.extend([
                BodyReplacerProcessor(keys=["alternateCallerId", "targets", "source", "callbackUri", "identity", "communicationUser", "rawId", "callConnectionId", "phoneNumber", "serverCallId"]),
                BodyReplacerProcessor(keys=["audioFileUri"], replacement = "https://dummy.ngrok.io/audio/sample-message.wav"),
                ResponseReplacerProcessor(keys=[self._resource_name]),
                RequestReplacerProcessor()])

        # create CallingServerClient
        endpoint, _ = parse_connection_str(self.connection_str)
        endpoint = endpoint

        if not is_live():
            credential = FakeTokenCredential()
        else:
            credential = DefaultAzureCredential()

        self.callingserver_client = CallingServerClient(
            endpoint,
            credential,
            http_logging_policy=get_http_logging_policy()
        )

        self.from_user = CallingServerLiveTestUtils.get_new_user_id(self.connection_str)
        self.to_user = CallingServerLiveTestUtils.get_new_user_id(self.connection_str)

    def test_create_play_cancel_hangup_scenario(self):
        # create call option and establish a call
        call_connection = self.callingserver_client.create_call_connection(
                    source=CommunicationUserIdentifier(self.from_user),
                    targets=[PhoneNumberIdentifier(self.to_phone_number)],
                    callback_uri=CONST.AppCallbackUrl,
                    requested_media_types=[CallMediaType.AUDIO],
                    requested_call_events=[CallingEventSubscriptionType.PARTICIPANTS_UPDATED],
                    alternate_caller_id=PhoneNumberIdentifier(self.from_phone_number)
                    )   
        CallingServerLiveTestUtils.validate_callconnection(call_connection)

        try:
            # Get Call
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            get_call_result = call_connection.get_call()
            assert get_call_result.call_connection_id is not None

            # Play Audio
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            OperationContext = str(uuid.uuid4())
            AudioFileId = str(uuid.uuid4())
            play_audio_result = call_connection.play_audio(
                CONST.AUDIO_FILE_URL,
                is_looped = True,
                audio_file_id = AudioFileId,
                operation_context = OperationContext
                )
            CallingServerLiveTestUtils.validate_play_audio_result(play_audio_result)

            # Cancel All Media Operations
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            call_connection.cancel_all_media_operations()
        except Exception as ex:
            print(str(ex))
        finally:
            # Hang up
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            call_connection.hang_up()

    def test_create_add_remove_hangup_scenario(self):
        # create option and establish a call
        call_connection = self.callingserver_client.create_call_connection(
                    source=CommunicationUserIdentifier(self.from_user),
                    targets=[PhoneNumberIdentifier(self.to_phone_number)],
                    callback_uri=CONST.AppCallbackUrl,
                    requested_media_types=[CallMediaType.AUDIO],
                    requested_call_events=[CallingEventSubscriptionType.PARTICIPANTS_UPDATED],
                    alternate_caller_id=PhoneNumberIdentifier(self.from_phone_number)
                    )   

        CallingServerLiveTestUtils.validate_callconnection(call_connection)

        try:
            # Add Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            added_participant = CallingServerLiveTestUtils.get_fixed_user_id(self.partcipant_guid)
            add_participant_result = call_connection.add_participant(
                participant=CommunicationUserIdentifier(added_participant)
                )
            CallingServerLiveTestUtils.validate_add_participant(add_participant_result)  
           
            #list_participants 
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            list_participants_result = call_connection.list_participants()
            assert len(list_participants_result) > 2

            # Remove Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            call_connection.remove_participant(CommunicationUserIdentifier(added_participant))
        except Exception as ex:
            print(str(ex))
        finally:
            # Hang up
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            call_connection.hang_up()

    def test_test_create_add_play_audio_to_participant_remove_hangup_scenario(self):
        # create option and establish a call
        call_connection = self.callingserver_client.create_call_connection(
                    source=CommunicationUserIdentifier(self.from_user),
                    targets=[PhoneNumberIdentifier(self.to_phone_number)],
                    callback_uri=CONST.AppCallbackUrl,
                    requested_media_types=[CallMediaType.AUDIO],
                    requested_call_events=[CallingEventSubscriptionType.PARTICIPANTS_UPDATED],
                    alternate_caller_id=PhoneNumberIdentifier(self.from_phone_number)
                    )   
        CallingServerLiveTestUtils.validate_callconnection(call_connection)

        try:
           # Add Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            added_participant = CallingServerLiveTestUtils.get_fixed_user_id(self.partcipant_guid)
            add_participant_result = call_connection.add_participant(
                participant=CommunicationUserIdentifier(added_participant)
                )
            CallingServerLiveTestUtils.validate_add_participant(add_participant_result)   

            # Play Audio To Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            play_audio_to_participant_result = call_connection.play_audio_to_participant(
             participant=CommunicationUserIdentifier(added_participant), 
             audio_url = CONST.AUDIO_FILE_URL,
             is_looped=True,
             audio_file_id=str(uuid.uuid4()))    
             
            assert play_audio_to_participant_result.operation_id is not None   

            # Cancel Participant Media Operation 
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            call_connection.cancel_participant_media_operation(
                participant=CommunicationUserIdentifier(added_participant),
                media_operation_id=play_audio_to_participant_result.operation_id
            )

            # Remove Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            call_connection.remove_participant(CommunicationUserIdentifier(added_participant))

        except Exception as ex:
            print( str(ex))
        finally:
            # Hang up
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            call_connection.hang_up()

    def test_create_add_participant_mute_unmute_hangup_scenario(self):
        # Establish a call
        call_connection = self.callingserver_client.create_call_connection(
                    source=CommunicationUserIdentifier(self.from_user),
                    targets=[PhoneNumberIdentifier(self.to_phone_number)],
                    callback_uri=CONST.AppCallbackUrl,
                    requested_media_types=[CallMediaType.AUDIO],
                    requested_call_events=[CallingEventSubscriptionType.PARTICIPANTS_UPDATED],
                    alternate_caller_id=PhoneNumberIdentifier(self.from_phone_number)
                    )   
        CallingServerLiveTestUtils.validate_callconnection(call_connection)

        try:
           # Add Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            OperationContext = str(uuid.uuid4())
            added_participant = CallingServerLiveTestUtils.get_fixed_user_id(self.partcipant_guid)
            add_participant_result = call_connection.add_participant(
                participant=CommunicationUserIdentifier(added_participant),
                operation_context=OperationContext
                )
            CallingServerLiveTestUtils.validate_add_participant(add_participant_result)

            # Mute Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            call_connection.mute_participant(CommunicationUserIdentifier(added_participant))

            # Get Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            muted_participant = call_connection.get_participant(CommunicationUserIdentifier(added_participant))
            assert muted_participant.is_muted == True

            # Unmute Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            call_connection.unmute_participant(CommunicationUserIdentifier(added_participant))

            # Get Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            unmuted_participant = call_connection.get_participant(CommunicationUserIdentifier(added_participant))
            assert unmuted_participant.is_muted == False
           
            # Remove Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            call_connection.remove_participant(CommunicationUserIdentifier(added_participant))
        except Exception as ex:
            print(ex)
        finally:
            # Hang up
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            call_connection.hang_up()  

    def test_hold_resume_participant_audio_scenario(self):
        # Establish a call
        call_connection = self.callingserver_client.create_call_connection(
                    source=CommunicationUserIdentifier(self.from_user),
                    targets=[PhoneNumberIdentifier(self.to_phone_number)],
                    callback_uri=CONST.AppCallbackUrl,
                    requested_media_types=[CallMediaType.AUDIO],
                    requested_call_events=[CallingEventSubscriptionType.PARTICIPANTS_UPDATED],
                    alternate_caller_id=PhoneNumberIdentifier(self.from_phone_number)
                    ) 

        CallingServerLiveTestUtils.validate_callconnection(call_connection)

        try:
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            OperationContext = str(uuid.uuid4())
            added_participant = CallingServerLiveTestUtils.get_fixed_user_id(self.partcipant_guid)
            participant=CommunicationUserIdentifier(added_participant)
            add_participant_result = call_connection.add_participant(
                participant=participant,
                operation_context=OperationContext
                )
            CallingServerLiveTestUtils.validate_add_participant(
                add_participant_result)

            # Hold Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            call_connection.hold_participant_meeting_audio(participant)

            # Resume Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            call_connection.resume_participant_meeting_audio(participant)

            # Remove Participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            call_connection.remove_participant(participant)
        except Exception as ex:
            print(ex)
        finally:
            # Hang up
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            call_connection.hang_up()

    @pytest.mark.skip("Skip test as it is not working now")
    def test_transfer_to_call_scenario(self):
        # create option and establish a call
        call_connection = self.callingserver_client.create_call_connection(
                    source=CommunicationUserIdentifier(self.from_user),
                    targets=[PhoneNumberIdentifier(self.to_phone_number)],
                    callback_uri=CONST.AppCallbackUrl,
                    requested_media_types=[CallMediaType.AUDIO],
                    requested_call_events=[CallingEventSubscriptionType.PARTICIPANTS_UPDATED],
                    alternate_caller_id=PhoneNumberIdentifier(self.from_phone_number)
                    )   
        CallingServerLiveTestUtils.validate_callconnection(call_connection)

        try:
            # Transfer to call
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            OperationContext = str(uuid.uuid4())
            transfer_call_result = call_connection.transfer_to_call(
                target_call_connection_id = os.getenv("TARGET_CALL_CONNECTION_ID"),
                user_to_user_information='test information',
                operation_context=OperationContext
                )
            CallingServerLiveTestUtils.validate_transfer_call_participant(transfer_call_result)

        except Exception as ex:
            print(str(ex))

    def test_transfer_to_participant_scenario(self):
        # create option and establish a call
        call_connection = self.callingserver_client.create_call_connection(
                    source=CommunicationUserIdentifier(self.from_user),
                    targets=[PhoneNumberIdentifier(self.to_phone_number)],
                    callback_uri=CONST.AppCallbackUrl,
                    requested_media_types=[CallMediaType.AUDIO],
                    requested_call_events=[CallingEventSubscriptionType.PARTICIPANTS_UPDATED],
                    alternate_caller_id=PhoneNumberIdentifier(self.from_phone_number)
                    )   
        CallingServerLiveTestUtils.validate_callconnection(call_connection)

        try:
            # Transfer to participant
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            OperationContext = str(uuid.uuid4())
            target_participant = CallingServerLiveTestUtils.get_fixed_user_id(self.partcipant_guid)
            transfer_call_result = call_connection.transfer_to_participant(
                target_participant=CommunicationUserIdentifier(target_participant),
                user_to_user_information='test information',
                operation_context=OperationContext
                )
            CallingServerLiveTestUtils.validate_transfer_call_participant(transfer_call_result)

        except Exception as ex:
            print(str(ex))

    def test_create_delete_keep_alive_scenario(self):
        # Establish a call
        call_connection = self.callingserver_client.create_call_connection(
                    source=CommunicationUserIdentifier(self.from_user),
                    targets=[PhoneNumberIdentifier(self.to_phone_number)],
                    callback_uri=CONST.AppCallbackUrl,
                    requested_media_types=[CallMediaType.AUDIO],
                    requested_call_events=[CallingEventSubscriptionType.PARTICIPANTS_UPDATED],
                    alternate_caller_id=PhoneNumberIdentifier(self.from_phone_number)
                    )   

        CallingServerLiveTestUtils.validate_callconnection(call_connection)

        # Check Keep Alive
        CallingServerLiveTestUtils.sleep_if_in_live_mode()
        call_connection.keep_alive()

        # Delete the call
        CallingServerLiveTestUtils.sleep_if_in_live_mode()
        call_connection.delete()   # notice that call got disconnected
        try:
            CallingServerLiveTestUtils.sleep_if_in_live_mode()
            call_connection.keep_alive()
        except Exception as ex:
            assert '8522' in str(ex)