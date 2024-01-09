# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.storage.extensions import crc64

class TestCrc64:

    def test_compute_crc64(self):
        data = b''
        result = crc64.compute_crc64(data, 0)
        assert result == 0
