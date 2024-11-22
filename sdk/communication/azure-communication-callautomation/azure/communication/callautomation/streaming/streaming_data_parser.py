# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Union
import json
from azure.communication.callautomation._shared.models import identifier_from_raw_id
from azure.communication.callautomation.streaming.models import (TranscriptionMetadata,TranscriptionData,WordData)

class StreamingDataParser:
    @staticmethod
    def parse(packet_data: Union[str, bytes]) -> Union[TranscriptionMetadata, TranscriptionData]:
        """
        Parse the incoming packets.
        :param packet_data: Transcription packet data.
        :type packet_data: Union[str, bytes]
        :return: Union[TranscriptionMetadata, TranscriptionData]
        :rtype: TranscriptionMetadata, TranscriptionData
        :raises: ValueError
        """
        if isinstance(packet_data, str):
            string_json = packet_data
        elif isinstance(packet_data,bytes):
            string_json = packet_data.decode('utf-8')
        else:
            raise ValueError(packet_data)

        json_object = json.loads(string_json)
        kind = json_object['kind']

        if kind == 'TranscriptionMetadata':
            transcription_metadata = TranscriptionMetadata(**json_object['transcriptionMetadata'])
            return transcription_metadata
        if kind == 'TranscriptionData':
            participant = identifier_from_raw_id(json_object['transcriptionData']['participantRawID'])
            word_data_list = json_object['transcriptionData']['words']
            words = [WordData(entry["text"], entry["offset"], entry["duration"]) for entry in word_data_list]
            transcription_data = TranscriptionData(
                text=json_object['transcriptionData']['text'],
                format=json_object['transcriptionData']['format'],
                confidence=json_object['transcriptionData']['confidence'],
                offset=json_object['transcriptionData']['offset'],
                duration=json_object['transcriptionData']['duration'],
                words=words,
                participant=participant,
                resultStatus=json_object['transcriptionData']['resultStatus']
            )
            return transcription_data
        raise ValueError(string_json)
