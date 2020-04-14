# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._version import VERSION
from ._form_recognizer_client import FormRecognizerClient
from ._form_training_client import FormTrainingClient

from ._models import (
    FormContent,
    LengthUnit,
    TrainingStatus,
    CustomFormModelStatus,
    FormContentType,
    USReceipt,
    USReceiptType,
    USReceiptItem,
    FormTable,
    FormTableCell,
    TrainingDocumentInfo,
    FormRecognizerError,
    CustomFormModelInfo,
    AccountProperties,
    Point,
    PageRange,
    RecognizedForm,
    FormField,
    FieldText,
    FormPage,
    FormLine,
    FormWord,
    CustomFormModel,
    CustomFormSubModel,
    CustomFormModelField
)


__all__ = [
    'FormRecognizerClient',
    'FormTrainingClient',
    'LengthUnit',
    'TrainingStatus',
    'CustomFormModelStatus',
    'FormContentType',
    'FormContent',
    'USReceipt',
    'USReceiptType',
    'USReceiptItem',
    'FormTable',
    'FormTableCell',
    'TrainingDocumentInfo',
    'FormRecognizerError',
    'CustomFormModelInfo',
    'AccountProperties',
    'Point',
    'PageRange',
    'RecognizedForm',
    'FormField',
    'FieldText',
    'FormPage',
    'FormLine',
    'FormWord',
    'CustomFormModel',
    'CustomFormSubModel',
    'CustomFormModelField'
]

__VERSION__ = VERSION
