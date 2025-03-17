# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Optional

from ._operations import DatasetOperations as DatasetOperationsGenerated
from ..models._models import (
    DatasetVersion,
    PendingUploadRequest,
    PendingUploadType,
)
from ..models._enums import (
    DatasetType,
)

class DatasetOperations(DatasetOperationsGenerated):

    def __init__(self, outer_instance):
        self._outer_instance = outer_instance

    def create_dataset(
        self,
        *,
        name: str,
        version: Optional[str] = None,
        file: str,
        connection_name: Optional[str] = None, # TODO: Use me.
        **kwargs) -> DatasetVersion:

        pending_upload_response = self._outer_instance.datasets.create_or_get_start_pending_upload(
            name=name,
            version=version,
            pending_upload_request=PendingUploadRequest(
                pending_upload_type=PendingUploadType.TEMPORARY_BLOB_REFERENCE
            ),
            **kwargs
        )

        _ = self._outer_instance.datasets.internal_pub_blob(
            endpoint=pending_upload_response.blob_reference_for_consumption.blob_uri,
            credential=pending_upload_response.blob_reference_for_consumption.credential.sas_token,
            body=
            **kwargs
        )


        dataset_uri="<account>.blob.windows.core.net/<container>/<file_name>"

        dataset_version = self._outer_instance.datasets.create_or_update(
            name=name,
            version=dataset_version, 
            dataset_version=DatasetVersion(
                dataset_uri=dataset_uri,
                dataset_type=DatasetType.URI_FILE
            ),
            **kwargs
        )

        return dataset_version


__all__: List[str] = [DatasetOperations]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
