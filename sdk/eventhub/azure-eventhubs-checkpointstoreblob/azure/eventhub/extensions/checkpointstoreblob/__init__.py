# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

__version__ = "1.0.0b5"

from .blobstoragecs import BlobCheckpointStore

__all__ = [
    "BlobCheckpointStore",
]
