# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._version import VERSION
from ._client import DocumentTranslationClient
from ._generated.models import (
    StorageInputType,
)
from ._api_version import DocumentTranslationApiVersion
from ._models import (
    TranslationTarget,
    JobStatusResult,
    DocumentStatusResult,
    DocumentTranslationError,
    TranslationGlossary,
    DocumentTranslationInput,
    FileFormat
)

__VERSION__ = VERSION


__all__ = [
    "DocumentTranslationClient",
    "DocumentTranslationApiVersion",
    "DocumentTranslationInput",
    "TranslationGlossary",
    "StorageInputType",
    "FileFormat",
    "TranslationTarget",
    "JobStatusResult",
    "DocumentStatusResult",
    "DocumentTranslationError",
]
