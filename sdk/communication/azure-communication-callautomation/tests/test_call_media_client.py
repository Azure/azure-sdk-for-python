# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest

from azure.communication.callautomation import (
    CallConnectionClient,
)
from azure.communication.callautomation._models import (
    FileSource,
    TextSource,
    SsmlSource,
    PhoneNumberIdentifier,
    RecognitionChoice,
)
from azure.communication.callautomation._generated.models import (
    PlayRequest,
    PlayOptions,
    RecognizeRequest,
    RecognizeOptions,
    DtmfOptions,
    ContinuousDtmfRecognitionRequest,
    SendDtmfTonesRequest,
    StartTranscriptionRequest,
    StopTranscriptionRequest,
    UpdateTranscriptionRequest,
    HoldRequest,
    UnholdRequest,
    StartMediaStreamingRequest,
    StopMediaStreamingRequest,
    InterruptAudioAndAnnounceRequest
)
from azure.communication.callautomation._generated.models._enums import RecognizeInputType, DtmfTone
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
        self.locale = "en-US"
        self.operation_callback_url = "https://localhost"
        self.call_media_operations = Mock()

        self.call_connection_client = CallConnectionClient(
            endpoint="https://endpoint",
            credential=AzureKeyCredential("fakeCredential=="),
            call_connection_id=self.call_connection_id,
        )

        self.call_connection_client._call_media_client = self.call_media_operations

    def test_play(self):
        mock_play = Mock()
        self.call_media_operations.play = mock_play
        play_source = FileSource(url=self.url)

        self.call_connection_client.play_media(play_source=play_source, play_to=[self.target_user])

        expected_play_request = PlayRequest(
            play_sources=[play_source._to_generated()],
            play_to=[serialize_identifier(self.target_user)],
            play_options=PlayOptions(loop=False)
        )
        mock_play.assert_called_once()
        actual_play_request = mock_play.call_args[0][1]

        self.assertEqual(expected_play_request.play_sources[0].kind, actual_play_request.play_sources[0].kind)
        self.assertEqual(expected_play_request.play_sources[0].file.uri, actual_play_request.play_sources[0].file.uri)
        self.assertEqual(
            expected_play_request.play_sources[0].play_source_cache_id,
            actual_play_request.play_sources[0].play_source_cache_id,
        )
        self.assertEqual(expected_play_request.play_to[0]["raw_id"], actual_play_request.play_to[0]["raw_id"])
        self.assertEqual(expected_play_request.play_options.loop, actual_play_request.play_options.loop)

    def test_play_multiple_play_sources(self):
        mock_play = Mock()
        self.call_media_operations.play = mock_play
        play_sources = [FileSource(url=self.url),  TextSource(text='test test test')]
        self.call_connection_client.play_media(play_source=play_sources, play_to=[self.target_user])

        expected_play_request = PlayRequest(
            play_sources=[play_source._to_generated() for play_source in play_sources],
            play_to=[serialize_identifier(self.target_user)],
            play_options=PlayOptions(loop=False)
        )
        mock_play.assert_called_once()
        actual_play_request = mock_play.call_args[0][1]

        self.assertEqual(expected_play_request.play_sources[0].kind, actual_play_request.play_sources[0].kind)
        self.assertEqual(expected_play_request.play_sources[0].file.uri, actual_play_request.play_sources[0].file.uri)
        self.assertEqual(expected_play_request.play_sources[0].play_source_cache_id, actual_play_request.play_sources[0].play_source_cache_id)
        self.assertEqual(expected_play_request.play_to[0]['raw_id'], actual_play_request.play_to[0]['raw_id'])
        self.assertEqual(expected_play_request.play_options.loop, actual_play_request.play_options.loop)

    def test_play_file_to_all_back_compat(self):
        mock_play = Mock()
        self.call_media_operations.play = mock_play
        play_source = FileSource(url=self.url)

        self.call_connection_client.play_media_to_all(play_source=play_source)

        expected_play_request = PlayRequest(
            play_sources=[play_source._to_generated()],
            play_to=[],
            play_options=PlayOptions(loop=False, interrupt_call_media_operation=False)
        )
        mock_play.assert_called_once()
        actual_play_request = mock_play.call_args[0][1]

        self.assertEqual(expected_play_request.play_sources[0].kind, actual_play_request.play_sources[0].kind)
        self.assertEqual(expected_play_request.play_sources[0].file.uri, actual_play_request.play_sources[0].file.uri)
        self.assertEqual(
            expected_play_request.play_sources[0].play_source_cache_id,
            actual_play_request.play_sources[0].play_source_cache_id,
        )
        self.assertEqual(expected_play_request.play_to, actual_play_request.play_to)
        self.assertEqual(expected_play_request.play_options, actual_play_request.play_options)

    def test_play_file_to_all_back_compat_with_barge_in(self):
        mock_play = Mock()
        self.call_media_operations.play = mock_play
        play_source = FileSource(url=self.url)

        self.call_connection_client.play_media_to_all(play_source=play_source, interrupt_call_media_operation=True)

        expected_play_request = PlayRequest(
            play_sources=[play_source._to_generated()],
            play_to=[],
            play_options=PlayOptions(loop=False, interrupt_call_media_operation=True)
        )
        mock_play.assert_called_once()
        actual_play_request = mock_play.call_args[0][1]

        self.assertEqual(expected_play_request.play_sources[0].kind, actual_play_request.play_sources[0].kind)
        self.assertEqual(expected_play_request.play_sources[0].file.uri, actual_play_request.play_sources[0].file.uri)
        self.assertEqual(
            expected_play_request.play_sources[0].play_source_cache_id,
            actual_play_request.play_sources[0].play_source_cache_id,
        )
        self.assertEqual(expected_play_request.play_to, actual_play_request.play_to)
        self.assertEqual(expected_play_request.play_options.interrupt_call_media_operation, actual_play_request.play_options.interrupt_call_media_operation)

    def test_play_multiple_source_to_all(self):
        mock_play = Mock()
        self.call_media_operations.play = mock_play
        play_sources = [FileSource(url=self.url),  TextSource(text='test test test')]
        self.call_connection_client.play_media_to_all(play_sources)

        expected_play_request = PlayRequest(
            play_sources=[play_source._to_generated() for play_source in play_sources],
            play_to=[],
            play_options=PlayOptions(loop=False)
        )
        mock_play.assert_called_once()
        actual_play_request = mock_play.call_args[0][1]

        self.assertEqual(expected_play_request.play_sources[0].kind, actual_play_request.play_sources[0].kind)
        self.assertEqual(expected_play_request.play_sources[0].file.uri, actual_play_request.play_sources[0].file.uri)
        self.assertEqual(expected_play_request.play_sources[0].play_source_cache_id, actual_play_request.play_sources[0].play_source_cache_id)
        self.assertEqual(expected_play_request.play_to, actual_play_request.play_to)
        self.assertEqual(expected_play_request.play_options.loop, actual_play_request.play_options.loop)

    def test_play_file_to_all(self):
        mock_play = Mock()
        self.call_media_operations.play = mock_play
        play_source = FileSource(url=self.url)

        self.call_connection_client.play_media(play_source=play_source)

        expected_play_request = PlayRequest(
            play_sources=[play_source._to_generated()], play_to=[], play_options=PlayOptions(loop=False)
        )
        mock_play.assert_called_once()
        actual_play_request = mock_play.call_args[0][1]

        self.assertEqual(expected_play_request.play_sources[0].kind, actual_play_request.play_sources[0].kind)
        self.assertEqual(expected_play_request.play_sources[0].file.uri, actual_play_request.play_sources[0].file.uri)
        self.assertEqual(
            expected_play_request.play_sources[0].play_source_cache_id,
            actual_play_request.play_sources[0].play_source_cache_id,
        )
        self.assertEqual(expected_play_request.play_to, actual_play_request.play_to)
        self.assertEqual(expected_play_request.play_options.loop, actual_play_request.play_options.loop)

    def test_play_text_to_all(self):
        mock_play = Mock()
        self.call_media_operations.play = mock_play
        play_source = TextSource(text="test test test", custom_voice_endpoint_id="customVoiceEndpointId")

        self.call_connection_client.play_media(play_source=play_source)

        expected_play_request = PlayRequest(
            play_sources=[play_source._to_generated()], play_to=[], play_options=PlayOptions(loop=False)
        )
        mock_play.assert_called_once()
        actual_play_request = mock_play.call_args[0][1]

        self.assertEqual(expected_play_request.play_sources[0].kind, actual_play_request.play_sources[0].kind)
        self.assertEqual(expected_play_request.play_sources[0].text.text, actual_play_request.play_sources[0].text.text)
        self.assertEqual(
            expected_play_request.play_sources[0].play_source_cache_id,
            actual_play_request.play_sources[0].play_source_cache_id,
        )
        self.assertEqual(expected_play_request.play_to, actual_play_request.play_to)
        self.assertEqual(expected_play_request.play_options.loop, actual_play_request.play_options.loop)

    def test_play_ssml_to_all(self):
        mock_play = Mock()
        self.call_media_operations.play = mock_play
        play_source = SsmlSource(
            ssml_text='<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US"><voice name="en-US-JennyNeural">Recognize Choice Completed, played through SSML source.</voice></speak>',
            custom_voice_endpoint_id="customVoiceEndpointId",
        )

        self.call_connection_client.play_media(play_source=play_source)

        expected_play_request = PlayRequest(
            play_sources=[play_source._to_generated()], play_to=[], play_options=PlayOptions(loop=False)
        )
        mock_play.assert_called_once()
        actual_play_request = mock_play.call_args[0][1]

        self.assertEqual(expected_play_request.play_sources[0].kind, actual_play_request.play_sources[0].kind)
        self.assertEqual(
            expected_play_request.play_sources[0].ssml.ssml_text, actual_play_request.play_sources[0].ssml.ssml_text
        )
        self.assertEqual(
            expected_play_request.play_sources[0].play_source_cache_id,
            actual_play_request.play_sources[0].play_source_cache_id,
        )
        self.assertEqual(expected_play_request.play_to, actual_play_request.play_to)
        self.assertEqual(expected_play_request.play_options.loop, actual_play_request.play_options.loop)

    def test_recognize_dtmf_with_multiple_play_prompts(self):
        mock_recognize = Mock()
        self.call_media_operations.recognize = mock_recognize

        test_input_type = "dtmf"
        test_max_tones_to_collect = 3
        test_inter_tone_timeout = 10
        test_stop_dtmf_tones = [DtmfTone.FOUR]
        test_interrupt_prompt = True
        test_interrupt_call_media_operation = True
        test_initial_silence_timeout = 5
        test_play_sources = [FileSource(url=self.url),  TextSource(text='Testing multiple prompts')]

        self.call_connection_client.start_recognizing_media(
            target_participant=self.target_user,
            input_type=test_input_type,
            dtmf_max_tones_to_collect=test_max_tones_to_collect,
            dtmf_inter_tone_timeout=test_inter_tone_timeout,
            dtmf_stop_tones=test_stop_dtmf_tones,
            interrupt_prompt=test_interrupt_prompt,
            interrupt_call_media_operation=test_interrupt_call_media_operation,
            initial_silence_timeout=test_initial_silence_timeout,
            play_prompt=test_play_sources)

        mock_recognize.assert_called_once()

        actual_recognize_request = mock_recognize.call_args[0][1]

        expected_recognize_request = RecognizeRequest(
            recognize_input_type=test_input_type,
            play_prompts=[test_play_source._to_generated() for test_play_source in test_play_sources],
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
        self.assertEqual(expected_recognize_request.play_prompts, actual_recognize_request.play_prompts)
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
            play_prompt=test_play_source,
        )

        mock_recognize.assert_called_once()

        actual_recognize_request = mock_recognize.call_args[0][1]

        expected_recognize_request = RecognizeRequest(
            recognize_input_type=test_input_type,
            play_prompt=test_play_source._to_generated(),
            interrupt_call_media_operation=test_interrupt_call_media_operation,
            recognize_options=RecognizeOptions(
                target_participant=serialize_identifier(self.target_user),
                interrupt_prompt=test_interrupt_prompt,
                initial_silence_timeout_in_seconds=test_initial_silence_timeout,
                dtmf_options=DtmfOptions(
                    inter_tone_timeout_in_seconds=test_inter_tone_timeout,
                    max_tones_to_collect=test_max_tones_to_collect,
                    stop_tones=test_stop_dtmf_tones,
                ),
            ),
        )

        self.assertEqual(expected_recognize_request.recognize_input_type, actual_recognize_request.recognize_input_type)
        self.assertEqual(expected_recognize_request.play_prompt.kind, actual_recognize_request.play_prompt.kind)
        self.assertEqual(expected_recognize_request.play_prompt.file.uri, actual_recognize_request.play_prompt.file.uri)
        self.assertEqual(
            expected_recognize_request.interrupt_call_media_operation,
            actual_recognize_request.interrupt_call_media_operation,
        )
        self.assertEqual(expected_recognize_request.operation_context, actual_recognize_request.operation_context)
        self.assertEqual(
            expected_recognize_request.recognize_options.target_participant,
            actual_recognize_request.recognize_options.target_participant,
        )
        self.assertEqual(
            expected_recognize_request.recognize_options.interrupt_prompt,
            actual_recognize_request.recognize_options.interrupt_prompt,
        )
        self.assertEqual(
            expected_recognize_request.recognize_options.initial_silence_timeout_in_seconds,
            actual_recognize_request.recognize_options.initial_silence_timeout_in_seconds,
        )
        self.assertEqual(
            expected_recognize_request.recognize_options.dtmf_options.inter_tone_timeout_in_seconds,
            actual_recognize_request.recognize_options.dtmf_options.inter_tone_timeout_in_seconds,
        )
        self.assertEqual(
            expected_recognize_request.recognize_options.dtmf_options.max_tones_to_collect,
            actual_recognize_request.recognize_options.dtmf_options.max_tones_to_collect,
        )
        self.assertEqual(
            expected_recognize_request.recognize_options.dtmf_options.stop_tones,
            actual_recognize_request.recognize_options.dtmf_options.stop_tones,
        )

        with pytest.raises(ValueError) as e:
            self.call_connection_client.start_recognizing_media(target_participant=self.target_user, input_type="foo")
        assert "'foo' is not supported." in str(e.value)

    def test_recognize_choices(self):
        mock_recognize = Mock()
        self.call_media_operations.recognize = mock_recognize
        test_choice = RecognitionChoice(label="choice1", phrases=["pass", "fail"])
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
            play_prompt=test_play_source,
        )

        mock_recognize.assert_called_once()

        actual_recognize_request = mock_recognize.call_args[0][1]

        expected_recognize_request = RecognizeRequest(
            recognize_input_type=test_input_type,
            play_prompt=test_play_source._to_generated(),
            interrupt_call_media_operation=test_interrupt_call_media_operation,
            recognize_options=RecognizeOptions(
                target_participant=serialize_identifier(self.target_user),
                interrupt_prompt=test_interrupt_prompt,
                initial_silence_timeout_in_seconds=test_initial_silence_timeout,
                choices=[test_choice],
            ),
        )

        self.assertEqual(expected_recognize_request.recognize_input_type, actual_recognize_request.recognize_input_type)
        self.assertEqual(expected_recognize_request.play_prompt.kind, actual_recognize_request.play_prompt.kind)
        self.assertEqual(expected_recognize_request.play_prompt.file.uri, actual_recognize_request.play_prompt.file.uri)
        self.assertEqual(
            expected_recognize_request.interrupt_call_media_operation,
            actual_recognize_request.interrupt_call_media_operation,
        )
        self.assertEqual(expected_recognize_request.operation_context, actual_recognize_request.operation_context)
        self.assertEqual(
            expected_recognize_request.recognize_options.target_participant,
            actual_recognize_request.recognize_options.target_participant,
        )
        self.assertEqual(
            expected_recognize_request.recognize_options.interrupt_prompt,
            actual_recognize_request.recognize_options.interrupt_prompt,
        )
        self.assertEqual(
            expected_recognize_request.recognize_options.initial_silence_timeout_in_seconds,
            actual_recognize_request.recognize_options.initial_silence_timeout_in_seconds,
        )
        self.assertEqual(
            expected_recognize_request.recognize_options.choices[0].label,
            actual_recognize_request.recognize_options.choices[0].label,
        )
        self.assertEqual(
            expected_recognize_request.recognize_options.choices[0].phrases[0],
            actual_recognize_request.recognize_options.choices[0].phrases[0],
        )

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
            target_participant=serialize_identifier(self.target_user)
        )

        mock_start_continuous_dtmf_recognition.assert_called_once()
        actual_call_connection_id = mock_start_continuous_dtmf_recognition.call_args[0][0]
        actual_start_continuous_dtmf_recognition = mock_start_continuous_dtmf_recognition.call_args[0][1]

        self.assertEqual(self.call_connection_id, actual_call_connection_id)
        self.assertEqual(
            expected_continuous_dtmf_recognition_request.target_participant,
            actual_start_continuous_dtmf_recognition.target_participant,
        )
        self.assertEqual(
            expected_continuous_dtmf_recognition_request.operation_context,
            actual_start_continuous_dtmf_recognition.operation_context,
        )

    def test_stop_continuous_dtmf_recognition(self):
        mock_stop_continuous_dtmf_recognition = Mock()
        self.call_media_operations.stop_continuous_dtmf_recognition = mock_stop_continuous_dtmf_recognition
        self.call_connection_client.stop_continuous_dtmf_recognition(target_participant=self.target_user)

        expected_continuous_dtmf_recognition_request = ContinuousDtmfRecognitionRequest(
            target_participant=serialize_identifier(self.target_user)
        )

        mock_stop_continuous_dtmf_recognition.assert_called_once()
        actual_call_connection_id = mock_stop_continuous_dtmf_recognition.call_args[0][0]
        actual_stop_continuous_dtmf_recognition = mock_stop_continuous_dtmf_recognition.call_args[0][1]

        self.assertEqual(self.call_connection_id, actual_call_connection_id)
        self.assertEqual(
            expected_continuous_dtmf_recognition_request.target_participant,
            actual_stop_continuous_dtmf_recognition.target_participant,
        )
        self.assertEqual(
            expected_continuous_dtmf_recognition_request.operation_context,
            actual_stop_continuous_dtmf_recognition.operation_context,
        )

    def test_send_dtmf_tones(self):
        mock_send_dtmf_tones = Mock()
        self.call_media_operations.send_dtmf_tones = mock_send_dtmf_tones
        self.call_connection_client.send_dtmf_tones(
            tones=self.tones, target_participant=self.target_user, operation_context=self.operation_context
        )

        expected_send_dtmf_tones_request = SendDtmfTonesRequest(
            tones=self.tones,
            target_participant=serialize_identifier(self.target_user),
            operation_context=self.operation_context,
        )

        mock_send_dtmf_tones.assert_called_once()
        actual_call_connection_id = mock_send_dtmf_tones.call_args[0][0]
        actual_send_dtmf_tones_request = mock_send_dtmf_tones.call_args[0][1]

        self.assertEqual(self.call_connection_id, actual_call_connection_id)
        self.assertEqual(
            expected_send_dtmf_tones_request.target_participant, actual_send_dtmf_tones_request.target_participant
        )
        self.assertEqual(expected_send_dtmf_tones_request.tones, actual_send_dtmf_tones_request.tones)
        self.assertEqual(
            expected_send_dtmf_tones_request.operation_context, actual_send_dtmf_tones_request.operation_context
        )

    def test_start_transcription(self):
        mock_start_transcription = Mock()
        self.call_media_operations.start_transcription = mock_start_transcription
        self.call_connection_client.start_transcription(locale=self.locale, operation_context=self.operation_context)

        expected_start_transcription_request = StartTranscriptionRequest(
            locale=self.locale, operation_context=self.operation_context
        )

        mock_start_transcription.assert_called_once()
        actual_call_connection_id = mock_start_transcription.call_args[0][0]
        actual_start_transcription_request = mock_start_transcription.call_args[0][1]

        self.assertEqual(self.call_connection_id, actual_call_connection_id)
        self.assertEqual(expected_start_transcription_request.locale, actual_start_transcription_request.locale)
        self.assertEqual(
            expected_start_transcription_request.operation_context, actual_start_transcription_request.operation_context
        )

    def test_stop_transcription(self):
        mock_stop_transcription = Mock()
        self.call_media_operations.stop_transcription = mock_stop_transcription
        self.call_connection_client.stop_transcription(operation_context=self.operation_context)

        expected_stop_transcription_request = StopTranscriptionRequest(operation_context=self.operation_context)

        mock_stop_transcription.assert_called_once()
        actual_call_connection_id = mock_stop_transcription.call_args[0][0]
        actual_stop_transcription_request = mock_stop_transcription.call_args[0][1]

        self.assertEqual(self.call_connection_id, actual_call_connection_id)
        self.assertEqual(
            expected_stop_transcription_request.operation_context, actual_stop_transcription_request.operation_context
        )

    def test_update_transcription(self):
        mock_update_transcription = Mock()
        self.call_media_operations.update_transcription = mock_update_transcription
        self.call_connection_client.update_transcription(locale=self.locale)

        expected_update_transcription_request = UpdateTranscriptionRequest(locale=self.locale)

        mock_update_transcription.assert_called_once()
        actual_call_connection_id = mock_update_transcription.call_args[0][0]
        actual_update_transcription_request = mock_update_transcription.call_args[0][1]

        self.assertEqual(self.call_connection_id, actual_call_connection_id)
        self.assertEqual(expected_update_transcription_request.locale, actual_update_transcription_request.locale)

    def test_hold_with_file_source(self):
        mock_hold = Mock()
        self.call_media_operations.hold = mock_hold
        play_source = FileSource(url=self.url)
        operation_context = "context"

        self.call_connection_client.hold(
            target_participant=self.target_user, play_source=play_source, operation_context=operation_context
        )

        expected_hold_request = HoldRequest(
            target_participant=[serialize_identifier(self.target_user)],
            play_source_info=play_source._to_generated(),
            operation_context=operation_context,
        )
        mock_hold.assert_called_once()
        actual_hold_request = mock_hold.call_args[0][1]

        self.assertEqual(expected_hold_request.play_source_info.file.uri, actual_hold_request.play_source_info.file.uri)
        self.assertEqual(expected_hold_request.play_source_info.kind, actual_hold_request.play_source_info.kind)
        self.assertEqual(expected_hold_request.operation_context, actual_hold_request.operation_context)

    def test_hold_with_text_source(self):
        mock_hold = Mock()
        self.call_media_operations.hold = mock_hold
        play_source = TextSource(text="test test test")
        operation_context = "with_operation_context"

        self.call_connection_client.hold(
            target_participant=self.target_user, play_source=play_source, operation_context=operation_context
        )

        expected_hold_request = HoldRequest(
            target_participant=[serialize_identifier(self.target_user)],
            play_source_info=play_source._to_generated(),
            operation_context=operation_context,
        )
        mock_hold.assert_called_once()
        actual_hold_request = mock_hold.call_args[0][1]

        self.assertEqual(
            expected_hold_request.play_source_info.text.text, actual_hold_request.play_source_info.text.text
        )
        self.assertEqual(expected_hold_request.play_source_info.kind, actual_hold_request.play_source_info.kind)
        self.assertEqual(expected_hold_request.operation_context, actual_hold_request.operation_context)

    def test_hold_without_text_source(self):
        mock_hold = Mock()
        self.call_media_operations.hold = mock_hold
        operation_context = "context"

        self.call_connection_client.hold(target_participant=self.target_user, operation_context=operation_context)

        expected_hold_request = HoldRequest(
            target_participant=[serialize_identifier(self.target_user)], operation_context=operation_context
        )
        mock_hold.assert_called_once()
        actual_hold_request = mock_hold.call_args[0][1]

        self.assertEqual(expected_hold_request.operation_context, actual_hold_request.operation_context)
        self.assertEqual(expected_hold_request.play_source_info, actual_hold_request.play_source_info)
        self.assertEqual(expected_hold_request.operation_context, actual_hold_request.operation_context)

    def test_unhold(self):
        mock_unhold = Mock()
        self.call_media_operations.unhold = mock_unhold
        operation_context = "context"

        self.call_connection_client.unhold(target_participant=self.target_user, operation_context=operation_context)

        expected_hold_request = UnholdRequest(
            target_participant=[serialize_identifier(self.target_user)], operation_context=operation_context
        )
        mock_unhold.assert_called_once()
        actual_hold_request = mock_unhold.call_args[0][1]

        self.assertEqual(expected_hold_request.operation_context, actual_hold_request.operation_context)
        
    def test_start_media_streaming(self):
       mock_start_media_streaming = Mock()
       self.call_media_operations.start_media_streaming = mock_start_media_streaming

       self.call_connection_client.start_media_streaming(
           operation_callback_url=self.operation_callback_url,
           operation_context=self.operation_context)

       expected_start_media_streaming_request = StartMediaStreamingRequest(
           operation_callback_uri=self.operation_callback_url,
           operation_context=self.operation_context)

       mock_start_media_streaming.assert_called_once()
       actual_call_connection_id = mock_start_media_streaming.call_args[0][0]
       actual_start_media_streaming_request = mock_start_media_streaming.call_args[0][1]
       self.assertEqual(self.call_connection_id,actual_call_connection_id)
       self.assertEqual(expected_start_media_streaming_request.operation_callback_uri,
                        actual_start_media_streaming_request.operation_callback_uri)
       self.assertEqual(expected_start_media_streaming_request.operation_context,
                        actual_start_media_streaming_request.operation_context)

    def test_start_media_steaming_with_no_param(self):
       mock_start_media_streaming = Mock()
       self.call_media_operations.start_media_streaming = mock_start_media_streaming

       self.call_connection_client.start_media_streaming()

       mock_start_media_streaming.assert_called_once()
       actual_call_connection_id = mock_start_media_streaming.call_args[0][0]
       self.assertEqual(self.call_connection_id,actual_call_connection_id)

    def test_stop_media_streaming(self):
       mock_stop_media_streaming = Mock()
       self.call_media_operations.stop_media_streaming = mock_stop_media_streaming

       self.call_connection_client.stop_media_streaming(
           operation_callback_url=self.operation_callback_url)

       expected_stop_media_streaming_request = StopMediaStreamingRequest(
           operation_callback_uri=self.operation_callback_url)

       mock_stop_media_streaming.assert_called_once()

       actual_call_connection_id = mock_stop_media_streaming.call_args[0][0]
       actual_stop_media_streaming_request = mock_stop_media_streaming.call_args[0][1]
       self.assertEqual(self.call_connection_id,actual_call_connection_id)
       self.assertEqual(expected_stop_media_streaming_request.operation_callback_uri,
                        actual_stop_media_streaming_request.operation_callback_uri)

    def test_stop_media_streaming_with_no_param(self):
       mock_stop_media_streaming = Mock()
       self.call_media_operations.stop_media_streaming = mock_stop_media_streaming

       self.call_connection_client.stop_media_streaming()

       mock_stop_media_streaming.assert_called_once()
       actual_call_connection_id = mock_stop_media_streaming.call_args[0][0]
       self.assertEqual(self.call_connection_id,actual_call_connection_id)

    def test_interrupt_audio_and_announce(self):
        mock_hold = Mock()
        mock_interrupt_audio_and_announce = Mock()
        mock_unhold = Mock()
        self.call_media_operations.hold = mock_hold
        self.call_media_operations.interrupt_audio_and_announce = mock_interrupt_audio_and_announce
        self.call_media_operations.unhold = mock_unhold
        self.call_media_operations.hold = mock_hold
        play_source = FileSource(url=self.url)
        operation_context = "context"

        self.call_connection_client.hold(
            target_participant=self.target_user, play_source=play_source, operation_context=operation_context
        )

        expected_hold_request = HoldRequest(
            target_participant=[serialize_identifier(self.target_user)],
            play_source_info=play_source._to_generated(),
            operation_context=operation_context,
        )
        mock_hold.assert_called_once()
        actual_hold_request = mock_hold.call_args[0][1]

        self.assertEqual(expected_hold_request.play_source_info.file.uri, actual_hold_request.play_source_info.file.uri)
        self.assertEqual(expected_hold_request.play_source_info.kind, actual_hold_request.play_source_info.kind)
        self.assertEqual(expected_hold_request.operation_context, actual_hold_request.operation_context)
        
        play_sources = [FileSource(url=self.url),  TextSource(text='test test test')]
        self.call_connection_client.interrupt_audio_and_announce(target_participant=self.target_user, play_sources=play_sources)

        expected_interrupt_audio_announce_request = InterruptAudioAndAnnounceRequest(
            play_sources=[play_source._to_generated()],
            play_to=serialize_identifier(self.target_user),
            operation_context=operation_context,
        )
        mock_interrupt_audio_and_announce.assert_called_once()
        actual_interrupt_audio_and_announce_request = mock_interrupt_audio_and_announce.call_args[0][1]

        self.assertEqual(expected_interrupt_audio_announce_request.play_sources[0].kind, actual_interrupt_audio_and_announce_request.play_sources[0].kind)
        self.assertEqual(expected_interrupt_audio_announce_request.play_to, actual_interrupt_audio_and_announce_request.play_to)
        
        self.call_connection_client.unhold(target_participant=self.target_user, operation_context=operation_context)

        expected_hold_request = UnholdRequest(
            target_participant=serialize_identifier(self.target_user), operation_context=operation_context
        )
        mock_unhold.assert_called_once()
        actual_hold_request = mock_unhold.call_args[0][1]

        self.assertEqual(expected_hold_request.operation_context, actual_hold_request.operation_context)