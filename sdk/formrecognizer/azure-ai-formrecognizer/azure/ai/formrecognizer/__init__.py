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
    ExtractedReceipt,
    FieldValue,
    ReceiptType,
    ReceiptItem,
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
    PageRange
)


__all__ = [
    'FormRecognizerClient',
    'CustomFormClient',
    'LengthUnit',
    'TrainStatus',
    'ModelStatus',
    'BoundingBox',
    'ExtractedReceipt',
    'FieldValue',
    'ReceiptType',
    'ReceiptItem',
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
    'PageRange'
]

__VERSION__ = VERSION
