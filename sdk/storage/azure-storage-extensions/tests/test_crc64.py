# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.storage.extensions.crc64 import compute_crc64

class TestCrc64:

    def test_compute_crc64():
        data = b''
        crc64 = compute_crc64(data, 0)
        print(crc64)
