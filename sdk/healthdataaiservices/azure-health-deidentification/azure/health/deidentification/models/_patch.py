# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import TYPE_CHECKING, List, Optional, Union
from ._models import DeidentificationContent as DeidentificationContentGenerated
from models import StringIndexType

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from .. import models as _models


class DeidentificationContent(DeidentificationContentGenerated):
    def __init__(
        self,
        *,
        input_text: str,
        operation: Union[str, "_models.OperationType"],
        data_type: Union[str, "_models.DocumentDataType"],
        redaction_format: Optional[str] = None,
    ):
        super(DeidentificationContent, self).__init__(
            input_text=input_text,
            operation=operation,
            data_type=data_type,
            string_index_type=StringIndexType.UNICODE_CODE_POINT,
            redaction_format=redaction_format,
        )


__all__: List[str] = [
    "DeidentificationContent"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
