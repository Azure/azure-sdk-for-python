# coding=utf-8
# pylint: disable=wrong-import-position

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._patch import *  # pylint: disable=unused-wildcard-import


from ._models import (  # type: ignore
    BatchOptions,
    DocumentBatch,
    DocumentFilter,
    DocumentStatus,
    DocumentTranslateContent,
    DocumentTranslationError,
    DocumentTranslationFileFormat,
    InnerTranslationError,
    SourceInput,
    StartTranslationDetails,
    TranslationErrorResponse,
    TranslationGlossary,
    TranslationStatus,
    TranslationStatusSummary,
    TranslationTarget,
)

from ._enums import (  # type: ignore
    FileFormatType,
    Status,
    StorageInputType,
    TranslationErrorCode,
    TranslationStorageSource,
)
from ._patch import __all__ as _patch_all
from ._patch import *
from ._patch import patch_sdk as _patch_sdk

__all__ = [
    "BatchOptions",
    "DocumentBatch",
    "DocumentFilter",
    "DocumentStatus",
    "DocumentTranslateContent",
    "DocumentTranslationError",
    "DocumentTranslationFileFormat",
    "InnerTranslationError",
    "SourceInput",
    "StartTranslationDetails",
    "TranslationErrorResponse",
    "TranslationGlossary",
    "TranslationStatus",
    "TranslationStatusSummary",
    "TranslationTarget",
    "FileFormatType",
    "Status",
    "StorageInputType",
    "TranslationErrorCode",
    "TranslationStorageSource",
]
__all__.extend([p for p in _patch_all if p not in __all__])  # pyright: ignore
_patch_sdk()
