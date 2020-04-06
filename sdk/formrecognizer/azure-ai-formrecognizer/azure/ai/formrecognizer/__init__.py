# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._version import VERSION
from ._form_recognizer_client import FormRecognizerClient
from ._form_training_client import FormTrainingClient

from ._models import (
    LengthUnit,
    TrainStatus,
    ModelStatus,
    FormContentType,
    BoundingBox,
    USReceipt,
    USReceiptType,
    USReceiptItem,
    FormTable,
    FormTableCell,
    CustomModel,
    TrainingInfo,
    FormFields,
    TrainingDocumentInfo,
    FormRecognizerError,
    CustomLabeledModel,
    FieldInfo,
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
    'FormTrainingClient',
    'LengthUnit',
    'TrainStatus',
    'ModelStatus',
    'FormContentType',
    'BoundingBox',
    'USReceipt',
    'USReceiptType',
    'USReceiptItem',
    'FormTable',
    'FormTableCell',
    'CustomModel',
    'TrainingInfo',
    'FormFields',
    'TrainingDocumentInfo',
    'FormRecognizerError',
    'CustomLabeledModel',
    'FieldInfo',
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
