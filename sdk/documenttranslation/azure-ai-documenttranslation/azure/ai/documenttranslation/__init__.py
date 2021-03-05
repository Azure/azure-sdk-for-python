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
from ._api_version import DocumentTranslationVersion
from ._models import (
    StorageTarget,
    JobStatusDetail,
    DocumentStatusDetail,
    DocumentTranslationError,
    TranslationGlossary,
    BatchDocumentInput,
    FileFormat
)

__VERSION__ = VERSION


__all__ = [
    "DocumentTranslationClient",
    "DocumentTranslationVersion",
    "BatchDocumentInput",
    "TranslationGlossary",
    "StorageInputType",
    "FileFormat",
    "StorageTarget",
    "JobStatusDetail",
    "DocumentStatusDetail",
    "DocumentTranslationError",
]
