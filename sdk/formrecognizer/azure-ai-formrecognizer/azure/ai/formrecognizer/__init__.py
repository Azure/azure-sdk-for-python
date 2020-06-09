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
    FormTable,
    FormTableCell,
    TrainingDocumentInfo,
    FormRecognizerError,
    CustomFormModelInfo,
    AccountProperties,
    Point,
    FormPageRange,
    RecognizedForm,
    FormField,
    FieldText,
    FormPage,
    FormLine,
    FormWord,
    CustomFormModel,
    CustomFormSubmodel,
    CustomFormModelField,
    RecognizedReceipt
)


__all__ = [
    'FormRecognizerClient',
    'FormTrainingClient',
    'LengthUnit',
    'TrainingStatus',
    'CustomFormModelStatus',
    'FormContentType',
    'FormContent',
    'FormTable',
    'FormTableCell',
    'TrainingDocumentInfo',
    'FormRecognizerError',
    'CustomFormModelInfo',
    'AccountProperties',
    'Point',
    'FormPageRange',
    'RecognizedForm',
    'FormField',
    'FieldText',
    'FormPage',
    'FormLine',
    'FormWord',
    'CustomFormModel',
    'CustomFormSubmodel',
    'CustomFormModelField',
    'RecognizedReceipt'
]

__VERSION__ = VERSION
