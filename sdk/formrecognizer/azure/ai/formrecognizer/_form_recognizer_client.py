# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import (  # pylint: disable=unused-import
    Union,
    Optional,
    Any,
    List,
    Dict,
    TYPE_CHECKING,
)

from ._generated.models import ErrorResponseException
from ._generated._form_recognizer_client import FormRecognizerClient as FormRecognizer
from ._base_client import FormRecognizerClientBase


if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential



class FormRecognizerClient(FormRecognizerClientBase):


    def __init__(self, endpoint, credential, **kwargs):
        super(FormRecognizerClient, self).__init__(credential=credential, **kwargs)
        self._client = FormRecognizer(
            endpoint=endpoint, credentials=credential, pipeline=self._pipeline
        )
