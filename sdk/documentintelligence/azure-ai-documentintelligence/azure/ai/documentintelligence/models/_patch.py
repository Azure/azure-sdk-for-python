# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Optional
from ._models import (
    AnalyzeDocumentRequest as GeneratedAnalyzeDocumentRequest,
    ClassifyDocumentRequest as GeneratedClassifyDocumentRequest,
)
from .._model_base import rest_field


class AnalyzeDocumentRequest(GeneratedAnalyzeDocumentRequest):
    """Document analysis parameters.

    :ivar url_source: Document URL to analyze.  Either url_source or bytes_source must be specified.
    :vartype url_source: str
    :ivar bytes_source: Document bytes to analyze.  Either url_source or bytes_source must be specified.
    :vartype bytes_source: bytes
    """

    bytes_source: Optional[bytes] = rest_field(name="base64Source", format="base64")
    """Document bytes to analyze.  Either url_source or bytes_source must be specified."""


class ClassifyDocumentRequest(GeneratedClassifyDocumentRequest):
    """Document classification parameters.

    :ivar url_source: Document URL to classify.  Either url_source or bytes_source must be
     specified.
    :vartype url_source: str
    :ivar bytes_source: Document bytes to classify.  Either url_source or bytes_source must be specified.
    :vartype bytes_source: bytes
    """

    bytes_source: Optional[bytes] = rest_field(name="base64Source", format="base64")
    """Document bytes to classify.  Either url_source or bytes_source must be specified."""


__all__: List[str] = [
    "AnalyzeDocumentRequest",
    "ClassifyDocumentRequest",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
