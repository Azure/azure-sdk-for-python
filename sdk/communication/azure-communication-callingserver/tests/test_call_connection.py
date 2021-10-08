# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import utils._test_mock_utils as _mock_utils
import utils._test_constants as _test_constants

from parameterized import parameterized

from azure.communication.callingserver import (
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

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_cancel_all_media_operations())
    def test_cancel_all_media_operations_succeed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        operation_context = None, # type: str
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=200,
            payload=_test_constants.CancelAllMediaOperaionsResponsePayload,
            use_managed_identity=use_managed_identity
            )

        result = call_connection.cancel_all_media_operations(operation_context)
        CallConnectionUnitTestUtils.verify_cancel_all_media_operations_result(result)

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

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_transfer_call())
    def test_transfer_call_succeed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        participant, # type: CommunicationIdentifier
        user_to_user_information, # type: str
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=202,
            payload=None,
            use_managed_identity=use_managed_identity
            )

        call_connection.transfer_call(
            target_participant = participant,
            user_to_user_information = user_to_user_information
            )
        assert call_connection.call_connection_id == _test_constants.CALL_ID

    @parameterized.expand(CallConnectionUnitTestUtils.data_source_test_transfer_call())
    def test_transfer_call_failed(
        self,
        test_name, # type: str
        call_connection_id, # type: str
        participant, # type: CommunicationIdentifier
        user_to_user_information, # type: str
        use_managed_identity = False # type: bool
        ):

        call_connection = _mock_utils.create_mock_call_connection(
            call_connection_id,
            status_code=404,
            payload=None,
            use_managed_identity = use_managed_identity
            )

        raised = False
        try:
            call_connection.transfer_call(
                target_participant = participant,
                user_to_user_information = user_to_user_information
                )
        except:
            raised = True
        assert raised == True