# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import sys
import pytest

from azure.communication.callautomation import (
    CallConnectionClient,
)
from azure.communication.callautomation._models import (
    FileSource,
    TextSource,
    SsmlSource,
    PhoneNumberIdentifier,
    Choice
)
from azure.communication.callautomation._generated.models import (
    PlayRequest,
    PlayOptions,
    RecognizeRequest,
    RecognizeOptions,
    DtmfOptions,
    ContinuousDtmfRecognitionRequest,
    SendDtmfRequest,
    StartHoldMusicRequest,
    StopHoldMusicRequest
)
from azure.communication.callautomation._generated.models._enums import (
    RecognizeInputType,
    DtmfTone
)
from unittest.mock import Mock
from azure.core.credentials import AzureKeyCredential
from azure.communication.callautomation._utils import serialize_identifier

class TestCallMediaClient(unittest.TestCase):
    def setUp(self):
        self.call_connection_id = "10000000-0000-0000-0000-000000000000"
        self.url = "https://file_source_url.com/audio_file.wav"
        self.phone_number = "+12345678900"
        self.target_user = PhoneNumberIdentifier(self.phone_number)
        self.tones = [DtmfTone.ONE, DtmfTone.TWO, DtmfTone.THREE, DtmfTone.POUND]
        self.operation_context = "test_operation_context"
        self.call_media_operations = Mock()

        self.call_connection_client = CallConnectionClient(
            endpoint="https://endpoint",
            credential=AzureKeyCredential("fakeCredential=="),
            call_connection_id=self.call_connection_id)

        self.call_connection_client._call_media_client = self.call_media_operations

    def test_play(self):
        mock_play = Mock()
        self.call_media_operations.play = mock_play
        play_source = FileSource(url=self.url)

        self.call_connection_client.play_media(play_source=play_source, play_to=[self.target_user])

        expected_play_request = PlayRequest(
            play_source_info=play_source._to_generated(),
            play_to=[serialize_identifier(self.target_user)],
            play_options=PlayOptions(loop=False)
        )
        mock_play.assert_called_once()
        actual_play_request = mock_play.call_args[0][1]

        self.assertEqual(expected_play_request.play_source_info.source_type, actual_play_request.play_source_info.source_type)
        self.assertEqual(expected_play_request.play_source_info.file_source.uri, actual_play_request.play_source_info.file_source.uri)
        self.assertEqual(expected_play_request.play_source_info.play_source_id, actual_play_request.play_source_info.play_source_id)
        self.assertEqual(expected_play_request.play_to[0]['raw_id'], actual_play_request.play_to[0]['raw_id'])
        self.assertEqual(expected_play_request.play_options, actual_play_request.play_options)

    def test_play_file_to_all_back_compat(self):
        mock_play = Mock()
        self.call_media_operations.play = mock_play
        play_source = FileSource(url=self.url)

        self.call_connection_client.play_media_to_all(play_source=play_source)

        expected_play_request = PlayRequest(
            play_source_info=play_source._to_generated(),
            play_to=[],
            play_options=PlayOptions(loop=False)
        )
        mock_play.assert_called_once()
        actual_play_request = mock_play.call_args[0][1]

        self.assertEqual(expected_play_request.play_source_info.source_type, actual_play_request.play_source_info.source_type)
        self.assertEqual(expected_play_request.play_source_info.file_source.uri, actual_play_request.play_source_info.file_source.uri)
        self.assertEqual(expected_play_request.play_source_info.play_source_id, actual_play_request.play_source_info.play_source_id)
        self.assertEqual(expected_play_request.play_to, actual_play_request.play_to)
        self.assertEqual(expected_play_request.play_options, actual_play_request.play_options)
    
    def test_play_file_to_all(self):
        mock_play = Mock()
        self.call_media_operations.play = mock_play
        play_source = FileSource(url=self.url)

        self.call_connection_client.play_media(play_source=play_source)

        expected_play_request = PlayRequest(
            play_source_info=play_source._to_generated(),
            play_to=[],
            play_options=PlayOptions(loop=False)
        )
        mock_play.assert_called_once()
        actual_play_request = mock_play.call_args[0][1]

        self.assertEqual(expected_play_request.play_source_info.source_type, actual_play_request.play_source_info.source_type)
        self.assertEqual(expected_play_request.play_source_info.file_source.uri, actual_play_request.play_source_info.file_source.uri)
        self.assertEqual(expected_play_request.play_source_info.play_source_id, actual_play_request.play_source_info.play_source_id)
        self.assertEqual(expected_play_request.play_to, actual_play_request.play_to)
        self.assertEqual(expected_play_request.play_options, actual_play_request.play_options)
    
    def test_play_text_to_all(self):
        mock_play = Mock()
        self.call_media_operations.play = mock_play
        play_source = TextSource(text='test test test', custom_voice_endpoint_id="customVoiceEndpointId")

        self.call_connection_client.play_media(play_source=play_source)

        expected_play_request = PlayRequest(
            play_source_info=play_source._to_generated(),
            play_to=[],
            play_options=PlayOptions(loop=False)
        )
        mock_play.assert_called_once()
        actual_play_request = mock_play.call_args[0][1]

        self.assertEqual(expected_play_request.play_source_info.source_type, actual_play_request.play_source_info.source_type)
        self.assertEqual(expected_play_request.play_source_info.text_source.text, actual_play_request.play_source_info.text_source.text)
        self.assertEqual(expected_play_request.play_source_info.play_source_id, actual_play_request.play_source_info.play_source_id)
        self.assertEqual(expected_play_request.play_to, actual_play_request.play_to)
        self.assertEqual(expected_play_request.play_options, actual_play_request.play_options)

    def test_play_ssml_to_all(self):
        mock_play = Mock()
        self.call_media_operations.play = mock_play
        play_source = SsmlSource(
            ssml_text='<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US"><voice name="en-US-JennyNeural">Recognize Choice Completed, played through SSML source.</voice></speak>',
            custom_voice_endpoint_id="customVoiceEndpointId")

        self.call_connection_client.play_media(play_source=play_source)

        expected_play_request = PlayRequest(
            play_source_info=play_source._to_generated(),
            play_to=[],
            play_options=PlayOptions(loop=False)
        )
        mock_play.assert_called_once()
        actual_play_request = mock_play.call_args[0][1]

        self.assertEqual(expected_play_request.play_source_info.source_type, actual_play_request.play_source_info.source_type)
        self.assertEqual(expected_play_request.play_source_info.ssml_source.ssml_text, actual_play_request.play_source_info.ssml_source.ssml_text)
        self.assertEqual(expected_play_request.play_source_info.play_source_id, actual_play_request.play_source_info.play_source_id)
        self.assertEqual(expected_play_request.play_to, actual_play_request.play_to)
        self.assertEqual(expected_play_request.play_options, actual_play_request.play_options)

    def test_recognize_dtmf(self):
        mock_recognize = Mock()
        self.call_media_operations.recognize = mock_recognize

        test_input_type = "dtmf"
        test_max_tones_to_collect = 3
        test_inter_tone_timeout = 10
        test_stop_dtmf_tones = [DtmfTone.FOUR]
        test_interrupt_prompt = True
        test_interrupt_call_media_operation = True
        test_initial_silence_timeout = 5
        test_play_source = FileSource(url=self.url)

        self.call_connection_client.start_recognizing_media(
            target_participant=self.target_user,
            input_type=test_input_type,
            dtmf_max_tones_to_collect=test_max_tones_to_collect,
            dtmf_inter_tone_timeout=test_inter_tone_timeout,
            dtmf_stop_tones=test_stop_dtmf_tones,
            interrupt_prompt=test_interrupt_prompt,
            interrupt_call_media_operation=test_interrupt_call_media_operation,
            initial_silence_timeout=test_initial_silence_timeout,
            play_prompt=test_play_source)

        mock_recognize.assert_called_once()

        actual_recognize_request = mock_recognize.call_args[0][1]

        expected_recognize_request = RecognizeRequest(
            recognize_input_type=test_input_type,
            play_prompt=test_play_source._to_generated(),
            interrupt_call_media_operation=test_interrupt_call_media_operation,
            recognize_options=RecognizeOptions(
                target_participant=serialize_identifier(
                    self.target_user),
                interrupt_prompt=test_interrupt_prompt,
                initial_silence_timeout_in_seconds=test_initial_silence_timeout,
                dtmf_options=DtmfOptions(
                    inter_tone_timeout_in_seconds=test_inter_tone_timeout,
                    max_tones_to_collect=test_max_tones_to_collect,
                    stop_tones=test_stop_dtmf_tones
                )
            )
        )

        self.assertEqual(expected_recognize_request.recognize_input_type, actual_recognize_request.recognize_input_type)
        self.assertEqual(expected_recognize_request.play_prompt.source_type, actual_recognize_request.play_prompt.source_type)
        self.assertEqual(expected_recognize_request.play_prompt.file_source.uri, actual_recognize_request.play_prompt.file_source.uri)
        self.assertEqual(expected_recognize_request.interrupt_call_media_operation, actual_recognize_request.interrupt_call_media_operation)
        self.assertEqual(expected_recognize_request.operation_context, actual_recognize_request.operation_context)
        self.assertEqual(expected_recognize_request.recognize_options.target_participant, actual_recognize_request.recognize_options.target_participant)
        self.assertEqual(expected_recognize_request.recognize_options.interrupt_prompt, actual_recognize_request.recognize_options.interrupt_prompt)
        self.assertEqual(expected_recognize_request.recognize_options.initial_silence_timeout_in_seconds, actual_recognize_request.recognize_options.initial_silence_timeout_in_seconds)
        self.assertEqual(expected_recognize_request.recognize_options.dtmf_options.inter_tone_timeout_in_seconds, actual_recognize_request.recognize_options.dtmf_options.inter_tone_timeout_in_seconds)
        self.assertEqual(expected_recognize_request.recognize_options.dtmf_options.max_tones_to_collect, actual_recognize_request.recognize_options.dtmf_options.max_tones_to_collect)
        self.assertEqual(expected_recognize_request.recognize_options.dtmf_options.stop_tones, actual_recognize_request.recognize_options.dtmf_options.stop_tones)

        with pytest.raises(ValueError) as e:
            self.call_connection_client.start_recognizing_media(
                target_participant=self.target_user,
                input_type="foo"
            )
        assert "'foo' is not supported." in str(e.value)

    def test_recognize_choices(self):
        mock_recognize = Mock()
        self.call_media_operations.recognize = mock_recognize
        test_choice = Choice("choice1", ["pass", "fail"])
        test_input_type = RecognizeInputType.CHOICES
        test_choices = [test_choice]
        test_interrupt_prompt = True
        test_interrupt_call_media_operation = True
        test_initial_silence_timeout = 5
        test_play_source = FileSource(url=self.url)

        self.call_connection_client.start_recognizing_media(
            target_participant=self.target_user,
            input_type=test_input_type,
            choices=test_choices,
            interrupt_prompt=test_interrupt_prompt,
            interrupt_call_media_operation=test_interrupt_call_media_operation,
            initial_silence_timeout=test_initial_silence_timeout,
            play_prompt=test_play_source)

        mock_recognize.assert_called_once()

        actual_recognize_request = mock_recognize.call_args[0][1]

        expected_recognize_request = RecognizeRequest(
            recognize_input_type=test_input_type,
            play_prompt=test_play_source._to_generated(),
            interrupt_call_media_operation=test_interrupt_call_media_operation,
            recognize_options=RecognizeOptions(
                target_participant=serialize_identifier(
                    self.target_user),
                interrupt_prompt=test_interrupt_prompt,
                initial_silence_timeout_in_seconds=test_initial_silence_timeout,
                choices=[test_choice]
            )
        )

        self.assertEqual(expected_recognize_request.recognize_input_type, actual_recognize_request.recognize_input_type)
        self.assertEqual(expected_recognize_request.play_prompt.source_type, actual_recognize_request.play_prompt.source_type)
        self.assertEqual(expected_recognize_request.play_prompt.file_source.uri, actual_recognize_request.play_prompt.file_source.uri)
        self.assertEqual(expected_recognize_request.interrupt_call_media_operation, actual_recognize_request.interrupt_call_media_operation)
        self.assertEqual(expected_recognize_request.operation_context, actual_recognize_request.operation_context)
        self.assertEqual(expected_recognize_request.recognize_options.target_participant, actual_recognize_request.recognize_options.target_participant)
        self.assertEqual(expected_recognize_request.recognize_options.interrupt_prompt, actual_recognize_request.recognize_options.interrupt_prompt)
        self.assertEqual(expected_recognize_request.recognize_options.initial_silence_timeout_in_seconds, actual_recognize_request.recognize_options.initial_silence_timeout_in_seconds)
        self.assertEqual(expected_recognize_request.recognize_options.choices[0].label, actual_recognize_request.recognize_options.choices[0].label)
        self.assertEqual(expected_recognize_request.recognize_options.choices[0].phrases[0], actual_recognize_request.recognize_options.choices[0].phrases[0])

    def test_cancel(self):
        mock_cancel_all = Mock()
        self.call_media_operations.cancel_all_media_operations = mock_cancel_all

        self.call_connection_client.cancel_all_media_operations()

        mock_cancel_all.assert_called_once()
        actual_call_connection_id = mock_cancel_all.call_args[0][0]
        self.assertEqual(self.call_connection_id, actual_call_connection_id)

    def test_start_continuous_dtmf_recognition(self):
        mock_start_continuous_dtmf_recognition = Mock()
        self.call_media_operations.start_continuous_dtmf_recognition = mock_start_continuous_dtmf_recognition
        self.call_connection_client.start_continuous_dtmf_recognition(target_participant=self.target_user)

        expected_continuous_dtmf_recognition_request = ContinuousDtmfRecognitionRequest(
            target_participant=serialize_identifier(self.target_user))

        mock_start_continuous_dtmf_recognition.assert_called_once()
        actual_call_connection_id = mock_start_continuous_dtmf_recognition.call_args[0][0]
        actual_start_continuous_dtmf_recognition = mock_start_continuous_dtmf_recognition.call_args[0][1]

        self.assertEqual(self.call_connection_id, actual_call_connection_id)
        self.assertEqual(expected_continuous_dtmf_recognition_request.target_participant,
                         actual_start_continuous_dtmf_recognition.target_participant)
        self.assertEqual(expected_continuous_dtmf_recognition_request.operation_context,
                         actual_start_continuous_dtmf_recognition.operation_context)

    def test_stop_continuous_dtmf_recognition(self):
        mock_stop_continuous_dtmf_recognition = Mock()
        self.call_media_operations.stop_continuous_dtmf_recognition = mock_stop_continuous_dtmf_recognition
        self.call_connection_client.stop_continuous_dtmf_recognition(target_participant=self.target_user)

        expected_continuous_dtmf_recognition_request = ContinuousDtmfRecognitionRequest(
            target_participant=serialize_identifier(self.target_user))

        mock_stop_continuous_dtmf_recognition.assert_called_once()
        actual_call_connection_id = mock_stop_continuous_dtmf_recognition.call_args[0][0]
        actual_stop_continuous_dtmf_recognition = mock_stop_continuous_dtmf_recognition.call_args[0][1]

        self.assertEqual(self.call_connection_id, actual_call_connection_id)
        self.assertEqual(expected_continuous_dtmf_recognition_request.target_participant,
                         actual_stop_continuous_dtmf_recognition.target_participant)
        self.assertEqual(expected_continuous_dtmf_recognition_request.operation_context,
                         actual_stop_continuous_dtmf_recognition.operation_context)

    def test_send_dtmf(self):
        mock_send_dtmf = Mock()
        self.call_media_operations.send_dtmf = mock_send_dtmf
        self.call_connection_client.send_dtmf(tones=self.tones,
                                              target_participant=self.target_user,
                                              operation_context=self.operation_context)

        expected_send_dtmf_request = SendDtmfRequest(
            tones=self.tones,
            target_participant=serialize_identifier(self.target_user),
            operation_context=self.operation_context)

        mock_send_dtmf.assert_called_once()
        actual_call_connection_id = mock_send_dtmf.call_args[0][0]
        actual_send_dtmf_request = mock_send_dtmf.call_args[0][1]

        self.assertEqual(self.call_connection_id, actual_call_connection_id)
        self.assertEqual(expected_send_dtmf_request.target_participant,
                         actual_send_dtmf_request.target_participant)
        self.assertEqual(expected_send_dtmf_request.tones,
                         actual_send_dtmf_request.tones)
        self.assertEqual(expected_send_dtmf_request.operation_context,
                         actual_send_dtmf_request.operation_context)
        
    def test_start_hold_music(self):
        mock_hold = Mock()
        self.call_media_operations.start_hold_music = mock_hold
        play_source = FileSource(url=self.url)

        self.call_connection_client.start_hold_music(target_participant=self.target_user, play_source=play_source)

        expected_hold_request = StartHoldMusicRequest(
            play_source_info=play_source._to_generated(),
            target_participant=serialize_identifier(self.target_user),
            loop=True
        )
        mock_hold.assert_called_once()
        actual_hold_request = mock_hold.call_args[0][1]

        self.assertEqual(expected_hold_request.play_source_info.source_type, actual_hold_request.play_source_info.source_type)
        self.assertEqual(expected_hold_request.play_source_info.file_source.uri, actual_hold_request.play_source_info.file_source.uri)
        self.assertEqual(expected_hold_request.play_source_info.play_source_id, actual_hold_request.play_source_info.play_source_id)
        self.assertEqual(expected_hold_request.target_participant['raw_id'], actual_hold_request.target_participant['raw_id'])
        self.assertEqual(expected_hold_request.loop, actual_hold_request.loop)
        
    def test_stop_hold_music(self):
        mock_hold = Mock()
        self.call_media_operations.stop_hold_music = mock_hold

        self.call_connection_client.stop_hold_music(target_participant=self.target_user)

        expected_unhold_request = StopHoldMusicRequest(
            target_participant=serialize_identifier(self.target_user),
        )
        mock_hold.assert_called_once()
        actual_unhold_request = mock_hold.call_args[0][1]

        self.assertEqual(expected_unhold_request.target_participant['raw_id'], actual_unhold_request.target_participant['raw_id'])
