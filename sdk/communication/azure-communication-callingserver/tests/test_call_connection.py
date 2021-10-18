# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import utils._test_mock_utils as _mock_utils
import utils._test_constants as _test_constants

from parameterized import parameterized
from typing import List

from azure.communication.callingserver import (
    AudioRoutingMode,
    CommunicationIdentifier,
    PlayAudioOptions
    )

from utils._unit_test_utils import CallConnectionUnitTestUtils

class TestCallConnection(unittest.TestCase):

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_get_call())
    def test_get_call_succeed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        use_managed_identity = False, # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=200,
            payload=_test_constants.GetCallResponsePayload,
            use_managed_identity=use_managed_identity
            )

        result = call_connection.get_call()
        CallConnectionUnitTestUtils.verify_get_call_result(result)

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_get_call())
    def test_get_call_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        use_managed_identity = False, # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.get_call()
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_delete_call())
    def test_delete_call_succeed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        use_managed_identity = False, # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=202,
            payload=_test_constants.GetCallResponsePayload,
            use_managed_identity=use_managed_identity
            )

        call_connection.delete_call()
        assert call_connection.call_connection_id == _test_constants.CALL_ID

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_delete_call())
    def test_delete_call_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        use_managed_identity = False, # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.delete_call()
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_hang_up())
    def test_hang_up_succeed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        use_managed_identity = False, # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=202,
            payload=None,
            use_managed_identity=use_managed_identity
            )

        call_connection.hang_up()
        assert call_connection.call_connection_id == _test_constants.CALL_ID

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_hang_up())
    def test_hang_up_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        use_managed_identity = False, # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.hang_up()
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_keep_alive())
    def test_keep_alive_succeed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        use_managed_identity = False, # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=200,
            payload=None,
            use_managed_identity=use_managed_identity
            )

        call_connection.keep_alive()
        assert call_connection.call_connection_id == _test_constants.CALL_ID

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_keep_alive())
    def test_keep_alive_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        use_managed_identity = False, # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.keep_alive()
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_cancel_all_media_operations())
    def test_cancel_all_media_operations_succeed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=200,
            payload=_test_constants.CancelAllMediaOperaionsResponsePayload,
            use_managed_identity=use_managed_identity
            )

        call_connection.cancel_all_media_operations()
        assert call_connection.call_connection_id == _test_constants.CALL_ID

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_cancel_all_media_operations())
    def test_cancel_all_media_operations_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        operation_context = None, # type: str
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.cancel_all_media_operations(operation_context)
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_play_audio())
    def test_play_audio_succeed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        audio_file_uri, # type: str
        options, # type: PlayAudioOptions
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=202,
            payload=_test_constants.PlayAudioResponsePayload,
            use_managed_identity=use_managed_identity
            )

        result = call_connection.play_audio(audio_file_uri, options)
        CallConnectionUnitTestUtils.verify_play_audio_result(result)

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_play_audio())
    def test_play_audio_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        audio_file_uri, # type: str
        options, # type: PlayAudioOptions
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.play_audio(audio_file_uri, options)
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_play_audio_to_participant())
    def test_play_audio_to_participant_succeed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        participant, # type: CommunicationIdentifier
        audio_file_uri, # type: str
        options, # type: PlayAudioOptions
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=202,
            payload=_test_constants.PlayAudioResponsePayload,
            use_managed_identity=use_managed_identity
            )

        result = call_connection.play_audio_to_participant(participant, audio_file_uri, options)

        CallConnectionUnitTestUtils.verify_play_audio_result(result)

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_play_audio_to_participant())
    def test_play_audio_to_participant_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        participant, # type: CommunicationIdentifier
        audio_file_uri, # type: str
        options, # type: PlayAudioOptions
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.play_audio_to_participant(participant, audio_file_uri, options)
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_add_participant())
    def test_add_participant_succeed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        participant, # type: CommunicationIdentifier
        alternate_caller_id, # type: str
        operation_context, # type: str
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=202,
            payload=_test_constants.AddParticipantResultPayload,
            use_managed_identity=use_managed_identity
            )

        result = call_connection.add_participant(
            participant = participant,
            alternate_caller_id = alternate_caller_id,
            operation_context = operation_context
            )
        CallConnectionUnitTestUtils.verify_add_participant_result(result)

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_add_participant())
    def test_add_participant_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        participant, # type: CommunicationIdentifier
        alternate_caller_id, # type: str
        operation_context, # type: str
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.add_participant(
                participant = participant,
                alternate_caller_id = alternate_caller_id,
                operation_context = operation_context
                )
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_remove_participant())
    def test_remove_participant_succeed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        participant, # type: CommunicationIdentifier
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=202,
            payload=None,
            use_managed_identity=use_managed_identity
            )

        call_connection.remove_participant(
            participant = participant
            )
        assert call_connection.call_connection_id == _test_constants.CALL_ID

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_remove_participant())
    def test_remove_participant_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        participant, # type: CommunicationIdentifier
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.remove_participant(
                participant = participant
                )
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_get_participants())
    def test_get_participants_succeed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=200,
            payload=None,
            use_managed_identity=use_managed_identity
            )

        call_connection.get_participants()
        assert call_connection.call_connection_id == _test_constants.CALL_ID

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_get_participants())
    def test_get_participants_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.get_participants()
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_get_participant())
    def test_get_participant_succeed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        participant, # type: CommunicationIdentifier
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=200,
            payload=None,
            use_managed_identity=use_managed_identity
            )

        call_connection.get_participant(
            participant = participant
            )
        assert call_connection.call_connection_id == _test_constants.CALL_ID

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_get_participant())
    def test_get_participant_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        participant, # type: CommunicationIdentifier
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.get_participant(
                participant = participant
                )
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_cancel_participant_media_operation())
    def test_cancel_participant_media_operation(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        participant, # type: CommunicationIdentifier
        media_operation_id, # type: str
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=200,
            payload=None,
            use_managed_identity=use_managed_identity
            )

        call_connection.cancel_participant_media_operation(
            participant = participant,
            media_operation_id = media_operation_id
            )
        assert call_connection.call_connection_id == _test_constants.CALL_ID

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_cancel_participant_media_operation())
    def test_cancel_participant_media_operation_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        participant, # type: CommunicationIdentifier
        media_operation_id, # type: str
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=None,
            use_managed_identity=use_managed_identity
            )

        raised = False
        try:
             call_connection.cancel_participant_media_operation(
                participant = participant,
                media_operation_id = media_operation_id
                )
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_mute_participant())
    def test_mute_participant(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        participant, # type: CommunicationIdentifier
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=200,
            payload=None,
            use_managed_identity=use_managed_identity
            )

        call_connection.mute_participant(
            participant = participant
            )
        assert call_connection.call_connection_id == _test_constants.CALL_ID

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_mute_participant())
    def test_mute_participant_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        participant, # type: CommunicationIdentifier
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.mute_participant(
                participant = participant,
                media_operation_id = media_operation_id
                )
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_unmute_participant())
    def test_unmute_participant(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        participant, # type: CommunicationIdentifier
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=200,
            payload=None,
            use_managed_identity=use_managed_identity
            )

        call_connection.unmute_participant(
            participant = participant
            )
        assert call_connection.call_connection_id == _test_constants.CALL_ID

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_unmute_participant())
    def test_unmute_participant_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        participant, # type: CommunicationIdentifier
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.unmute_participant(
                participant = participant
                )
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_hold_participant_meeting_audio())
    def test_hold_participant_meeting_audio(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        participant, # type: CommunicationIdentifier
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=200,
            payload=None,
            use_managed_identity=use_managed_identity
            )

        call_connection.hold_participant_meeting_audio(
            participant = participant
            )
        assert call_connection.call_connection_id == _test_constants.CALL_ID

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_hold_participant_meeting_audio())
    def test_hold_participant_meeting_audio_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        participant, # type: CommunicationIdentifier
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.hold_participant_meeting_audio(
                participant = participant
                )
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_resume_participant_meeting_audio())
    def test_resume_participant_meeting_audio(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        participant, # type: CommunicationIdentifier
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=200,
            payload=None,
            use_managed_identity=use_managed_identity
            )

        call_connection.resume_participant_meeting_audio(
            participant = participant
            )
        assert call_connection.call_connection_id == _test_constants.CALL_ID

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_resume_participant_meeting_audio())
    def test_resume_participant_meeting_audio_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        participant, # type: CommunicationIdentifier
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.resume_participant_meeting_audio(
                participant = participant
                )
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_transfer_call())
    def test_transfer_call_succeed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        target_participant, # type: CommunicationIdentifier
        target_call_connection_id, # type: str
        user_to_user_information, # type: str
        operation_context, # type: str
        callback_uri, # type: str
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=202,
            payload=None,
            use_managed_identity=use_managed_identity
            )

        call_connection.transfer_call(
            target_participant = target_participant,
            target_call_connection_id = target_call_connection_id,
            user_to_user_information = user_to_user_information,
            operation_context = operation_context,
            callback_uri = callback_uri
            )
        assert call_connection.call_connection_id == _test_constants.CALL_ID

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_transfer_call())
    def test_transfer_call_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        target_participant, # type: CommunicationIdentifier
        target_call_connection_id, # type: str
        user_to_user_information, # type: str
        operation_context, # type: str
        callback_uri, # type: str
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.transfer_call(
                target_participant = target_participant,
                target_call_connection_id = target_call_connection_id,
                user_to_user_information = user_to_user_information,
                operation_context = operation_context,
                callback_uri = callback_uri
                )
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_create_audio_routing_group())
    def test_create_audio_routing_group_succeed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        audio_routing_mode, # type: AudioRoutingMode
        targets, # type: List[CommunicationIdentifier]
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=201,
            payload=_test_constants.CreateAudioRoutingGroupResponsePayload,
            use_managed_identity=use_managed_identity
            )

        result = call_connection.create_audio_routing_group(
            audio_routing_mode = audio_routing_mode,
            targets = targets
            )
        CallConnectionUnitTestUtils.verify_create_audio_routing_group(result)

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_create_audio_routing_group())
    def test_create_audio_routing_group_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        audio_routing_mode, # type: AudioRoutingMode
        targets, # type: List[CommunicationIdentifier]
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.create_audio_routing_group(
                audio_routing_mode = audio_routing_mode,
                targets = targets
                )
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_get_audio_routing_group())
    def test_get_audio_routing_groups_succeed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        audio_routing_group_id, # type: str
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=200,
            payload=_test_constants.GetAudioRoutingGroupResponsePayload,
            use_managed_identity=use_managed_identity
            )

        result = call_connection.get_audio_routing_groups(
            audio_routing_group_id = audio_routing_group_id
            )
        CallConnectionUnitTestUtils.verify_get_audio_routing_group(result)

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_get_audio_routing_group())
    def test_get_audio_routing_groups_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        audio_routing_group_id, # type: str
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.get_audio_routing_groups(
                audio_routing_group_id = audio_routing_group_id
                )
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_delete_audio_routing_group())
    def test_delete_audio_routing_group_succeed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        audio_routing_group_id, # type: str
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=202,
            payload=None,
            use_managed_identity=use_managed_identity
            )

        call_connection.delete_audio_routing_group(
            audio_routing_group_id = audio_routing_group_id
            )
        assert call_connection.call_connection_id == _test_constants.CALL_ID

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_delete_audio_routing_group())
    def test_delete_audio_routing_group_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        audio_routing_group_id, # type: str
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.delete_audio_routing_group(
                audio_routing_group_id = audio_routing_group_id
                )
        except:
            raised = True
        assert raised == True

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_update_audio_routing_group())
    def test_update_audio_routing_group_succeed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        audio_routing_group_id, # type: str
        targets, # type: List[CommunicationIdentifier]
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=200,
            payload=None,
            use_managed_identity=use_managed_identity
            )

        call_connection.update_audio_routing_group(
            audio_routing_group_id = audio_routing_group_id,
            targets = targets
            )
        assert call_connection.call_connection_id == _test_constants.CALL_ID

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_update_audio_routing_group())
    def test_update_audio_routing_group_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        audio_routing_group_id, # type: str
        targets, # type: List[CommunicationIdentifier]
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=_test_constants.ErrorPayload,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.update_audio_routing_group(
                audio_routing_group_id = audio_routing_group_id,
                targets = targets
                )
        except:
            raised = True
        assert raised == True
