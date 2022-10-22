# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os.path
from os import PathLike
from typing import Optional, Dict, Union

from .asset_utils import get_snapshot_id
from ...entities._assets import Code


class InternalCode(Code):
    def __init__(
        self,
        *,
        name: str = None,
        version: str = None,
        description: str = None,
        tags: Dict = None,
        properties: Dict = None,
        path: Union[str, PathLike] = None,
        **kwargs,
    ):
        self._name_locked = False
        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            properties=properties,
            path=path,
            **kwargs,
        )

    @classmethod
    def cast_base(cls, code: Code) -> "InternalCode":
        if isinstance(code, InternalCode):
            return code
        if isinstance(code, Code):
            code.__class__ = cls
            code._name_locked = False  # pylint: disable=protected-access
            return code
        raise TypeError(f"Cannot cast {type(code)} to {cls}")

    @property
    def _upload_hash(self) -> Optional[str]:
        # this property will be called in _artifact_utilities._check_and_upload_path
        # before uploading the code to the datastore
        # update self._hash_name on that point so that it will be aligned with the uploaded
        # content and will be used in code creation request
        # self.path will be transformed to an absolute path in super().__init__
        # an error will be raised if the path is not valid
        if self._is_anonymous is True and os.path.isabs(self.path):
            # note that hash name will be calculated in every CodeOperation.create_or_update
            # call, even if the same object is used
            self._name_locked = False
            self.name = get_snapshot_id(self.path)
            self._name_locked = True

        # still return None
        return None  # pylint: disable=useless-return

    def __setattr__(self, key, value):
        if key == "name" and self._name_locked:
            return
        super().__setattr__(key, value)
