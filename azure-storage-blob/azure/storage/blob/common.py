# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from enum import Enum


class BlobType(str, Enum):

    BlockBlob = "blockblob"
    PageBlob = "pageblob"
    AppendBlob = "appendblob"