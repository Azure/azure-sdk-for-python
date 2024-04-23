# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from enum import Enum
from typing import List
from azure.communication.callautomation._shared.models import CommunicationIdentifier

class ResultStatus(Enum):
    """
    The status of the result of transcription.
    """
    INTERMEDIATE = "intermediate"
    FINAL = "final"

class TextFormat(Enum):
    """
    The format of transcription text.
    """
    DISPLAY = "display"

class WordData:
    """
    Text in the phrase.

    :keyword text: Text in the phrase.
    :paramtype text: str
    :keyword offset: The word's position within the phrase.
    :paramtype offset: int
    :keyword duration: Duration in ticks. 1 tick = 100 nanoseconds.
    :paramtype duration: int
    """
    text:str
    """ Text in the phrase. """
    offset:int
    """ The word's position within the phrase. """
    duration:int
    """ Duration in ticks. 1 tick = 100 nanoseconds. """
    def __init__(self, text: str, offset: int, duration: int):
        self.text = text
        self.offset = offset
        self.duration = duration

class TranscriptionMetadata:
    """
    Metadata for Transcription Streaming.

    :keyword subscriptionId: Transcription Subscription Id.
    :paramtype subscriptionId: str
    :keyword locale: The target locale in which the translated text needs to be.
    :paramtype locale: str
    :keyword callConnectionId: call connection Id.
    :paramtype callConnectionId: str
    :keyword correlationId: correlation Id.
    :paramtype correlationId: str
    """

    subscriptionId: str
    """ Transcription Subscription Id. """
    locale: str
    """ The target locale in which the translated text needs to be. """
    callConnectionId: str
    """ call connection Id. """
    correlationId: str
    """ correlation Id. """
    def __init__(self, subscriptionId: str, locale: str, callConnectionId: str, correlationId: str):
        self.subscriptionId = subscriptionId
        self.locale = locale
        self.callConnectionId = callConnectionId
        self.correlationId = correlationId

class TranscriptionData:
    """
    Streaming Transcription.
    :keyword  text: The display form of the recognized word.
    :paramtype  text: str
    :keyword format: The format of text.
    :paramtype format: TextFormat
    :keyword confidence: Confidence of recognition of the whole phrase.
    :paramtype confidence: float
    :keyword offset: The position of this payload.
    :paramtype offset: int
    :keyword duration: Duration in ticks. 1 tick = 100 nanoseconds.
    :paramtype duration: int
    :keyword words: The result for each word of the phrase.
    :paramtype words: List[WordData]
    :keyword participant: The identified speaker based on participant raw ID.
    :paramtype participant: CommunicationIdentifier
    :keyword resultStatus: Status of the result of transcription.
    :paramtype resultStatus: ResultStatus
    """
    text: str
    """ The display form of the recognized word. """
    format: TextFormat
    """ The format of text. """
    confidence: float
    """ Confidence of recognition of the whole phrase, from 0.0 (no confidence) to 1.0 (full confidence). """
    offset: int
    """ The position of this payload. """
    duration: int
    """ Duration in ticks. 1 tick = 100 nanoseconds. """
    words: List[WordData]
    """ The result for each word of the phrase. """
    participant: CommunicationIdentifier
    """ The identified speaker based on participant raw ID. """
    resultStatus: ResultStatus
    """ Status of the result of transcription. """
    def __init__(self, text: str, format: TextFormat, confidence: float, offset: int, duration: int,
    words: List[WordData], participant: CommunicationIdentifier, resultStatus: ResultStatus):
        self.text = text
        self.format = format
        self.confidence = confidence
        self.offset = offset
        self.duration = duration
        self.words = words
        self.participant = participant
        self.resultStatus = resultStatus
