# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, List, Optional, Union

from ._operations import (
    DirectoryOperations,
    FileOperations as _GeneratedFileOperations,
    ServiceOperations,
    ShareOperations,
)
from .. import models as _models


class FileOperations(_GeneratedFileOperations):  # pylint: disable=too-many-public-methods

    def upload_range(  # pylint: disable=arguments-differ
        self,
        optional_body: Optional[bytes] = None,
        *,
        file_range_write: Union[str, "_models.FileRangeWriteType"] = "update",
        **kwargs: Any,
    ) -> None:
        return super().upload_range(optional_body, file_range_write=file_range_write, **kwargs)


__all__: List[str] = ["FileOperations"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
