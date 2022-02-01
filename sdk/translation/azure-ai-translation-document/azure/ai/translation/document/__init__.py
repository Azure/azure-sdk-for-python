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
from ._polling import DocumentTranslationLROPoller
from ._models import (
    TranslationTarget,
    TranslationStatus,
    DocumentStatus,
    DocumentTranslationError,
    TranslationGlossary,
    DocumentTranslationInput,
    DocumentTranslationFileFormat,
)

__VERSION__ = VERSION


__all__ = [
    "DocumentTranslationClient",
    "DocumentTranslationApiVersion",
    "DocumentTranslationInput",
    "TranslationGlossary",
    "StorageInputType",
    "DocumentTranslationFileFormat",
    "TranslationTarget",
    "TranslationStatus",
    "DocumentStatus",
    "DocumentTranslationError",
    "DocumentTranslationLROPoller",
]
