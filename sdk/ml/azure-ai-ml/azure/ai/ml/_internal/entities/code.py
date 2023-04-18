# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional

from ...entities._assets import Code


class InternalCode(Code):
    @property
    def _upload_hash(self) -> Optional[str]:
        # This property will be used to identify the uploaded content when trying to
        # upload to datastore. The tracebacks will be as below:
        #   Traceback (most recent call last):
        #     _artifact_utilities._check_and_upload_path
        #     _artifact_utilities._upload_to_datastore
        #     _artifact_utilities.upload_artifact
        #     _blob_storage_helper.upload
        # where asset id will be calculated based on the upload hash.

        if self._is_anonymous is True:
            # Name of an anonymous internal code is the same as its snapshot id
            # in ml-component, use it as the upload hash to avoid duplicate hash
            # calculation with _asset_utils.get_object_hash.
            return self.name

        return getattr(super(InternalCode, self), "_upload_hash")

    def __setattr__(self, key, value):
        if key == "name" and hasattr(self, key) and self._is_anonymous is True and value != self.name:
            raise AttributeError(
                "InternalCode name are calculated based on its content and cannot "
                "be changed: current name is {} and new value is {}".format(self.name, value)
            )
        super().__setattr__(key, value)
