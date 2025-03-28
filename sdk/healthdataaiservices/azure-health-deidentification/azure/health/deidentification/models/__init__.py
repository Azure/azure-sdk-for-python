# coding=utf-8
# pylint: disable=wrong-import-position

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._patch import *  # pylint: disable=unused-wildcard-import


from ._models import (  # type: ignore
    DeidentificationContent,
    DeidentificationCustomizationOptions,
    DeidentificationDocumentDetails,
    DeidentificationDocumentLocation,
    DeidentificationJob,
    DeidentificationJobCustomizationOptions,
    DeidentificationJobSummary,
    DeidentificationResult,
    PhiEntity,
    PhiTaggerResult,
    SourceStorageLocation,
    StringIndex,
    TargetStorageLocation,
)

from ._enums import (  # type: ignore
    DeidentificationOperationType,
    OperationState,
    PhiCategory,
)
from ._patch import __all__ as _patch_all
from ._patch import *
from ._patch import patch_sdk as _patch_sdk

__all__ = [
    "DeidentificationContent",
    "DeidentificationCustomizationOptions",
    "DeidentificationDocumentDetails",
    "DeidentificationDocumentLocation",
    "DeidentificationJob",
    "DeidentificationJobCustomizationOptions",
    "DeidentificationJobSummary",
    "DeidentificationResult",
    "PhiEntity",
    "PhiTaggerResult",
    "SourceStorageLocation",
    "StringIndex",
    "TargetStorageLocation",
    "DeidentificationOperationType",
    "OperationState",
    "PhiCategory",
]
__all__.extend([p for p in _patch_all if p not in __all__])  # pyright: ignore
_patch_sdk()
