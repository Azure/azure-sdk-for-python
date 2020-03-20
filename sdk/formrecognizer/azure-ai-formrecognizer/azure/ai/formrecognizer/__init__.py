# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._version import VERSION
from ._form_recognizer_client import FormRecognizerClient
from ._custom_form_client import CustomFormClient
from ._credential import FormRecognizerApiKeyCredential

__all__ = [
    'FormRecognizerClient',
    'CustomFormClient',
    'FormRecognizerApiKeyCredential'
]

__VERSION__ = VERSION
