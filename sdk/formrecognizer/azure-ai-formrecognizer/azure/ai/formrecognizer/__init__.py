# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._version import VERSION
from ._form_recognizer_client import FormRecognizerClient
from ._custom_form_client import CustomFormClient

from ._models import (
    LengthUnit,
    TrainStatus,
    ModelStatus,
    BoundingBox,
    USReceipt,
    FieldValue,
    USReceiptType,
    USReceiptItem,
    ExtractedLine,
    ExtractedWord,
    PageMetadata,
    ExtractedLayoutPage,
    ExtractedTable,
    TableCell,
    CustomModel,
    TrainingInfo,
    FormFields,
    TrainingDocumentInfo,
    FormRecognizerError,
    CustomLabeledModel,
    FieldInfo,
    ExtractedPage,
    ExtractedField,
    ExtractedText,
    ExtractedLabeledForm,
    ModelInfo,
    ModelsSummary,
    Point,
    PageRange,
    RecognizedForm,
    FormField,
    FieldText,
    FormPage,
    FormLine,
    FormWord
)


__all__ = [
    'FormRecognizerClient',
    'CustomFormClient',
    'LengthUnit',
    'TrainStatus',
    'ModelStatus',
    'BoundingBox',
    'USReceipt',
    'FieldValue',
    'USReceiptType',
    'USReceiptItem',
    'ExtractedLine',
    'ExtractedWord',
    'PageMetadata',
    'ExtractedLayoutPage',
    'ExtractedTable',
    'TableCell',
    'CustomModel',
    'TrainingInfo',
    'FormFields',
    'TrainingDocumentInfo',
    'FormRecognizerError',
    'CustomLabeledModel',
    'FieldInfo',
    'ExtractedPage',
    'ExtractedField',
    'ExtractedText',
    'ExtractedLabeledForm',
    'ModelInfo',
    'ModelsSummary',
    'Point',
    'PageRange',
    'RecognizedForm',
    'FormField',
    'FieldText',
    'FormPage',
    'FormLine',
    'FormWord'
]

__VERSION__ = VERSION
