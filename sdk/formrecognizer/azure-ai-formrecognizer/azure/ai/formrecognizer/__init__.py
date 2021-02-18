# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._version import VERSION
from ._form_recognizer_client import FormRecognizerClient
from ._form_training_client import FormTrainingClient
from ._models import (
    FormElement,
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
    FieldData,
    FormPage,
    FormLine,
    FormWord,
    CustomFormModel,
    CustomFormSubmodel,
    CustomFormModelField,
    FieldValueType,
    CustomFormModelProperties,
    FormSelectionMark,
    TextAppearance,
    TextStyle,
)
from ._api_versions import FormRecognizerApiVersion


__all__ = [
    "FormRecognizerApiVersion",
    "FormRecognizerClient",
    "FormTrainingClient",
    "LengthUnit",
    "TrainingStatus",
    "CustomFormModelStatus",
    "FormContentType",
    "FormElement",
    "FormTable",
    "FormTableCell",
    "TrainingDocumentInfo",
    "FormRecognizerError",
    "CustomFormModelInfo",
    "AccountProperties",
    "Point",
    "FormPageRange",
    "RecognizedForm",
    "FormField",
    "FieldData",
    "FormPage",
    "FormLine",
    "FormWord",
    "CustomFormModel",
    "CustomFormSubmodel",
    "CustomFormModelField",
    "FieldValueType",
    "CustomFormModelProperties",
    "FormSelectionMark",
    "TextAppearance",
    "TextStyle",
]

__VERSION__ = VERSION
