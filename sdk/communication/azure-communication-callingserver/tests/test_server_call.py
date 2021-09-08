# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest
from _test_utils import create_calling_server_client

class TestServerCall(unittest.TestCase):
    def test_start_recording_relative_uri_fails(self):
        server_call_id = "aHR0cHM6Ly9jb252LXVzd2UtMDguY29udi5za3lwZS5jb20vY29udi8tby1FWjVpMHJrS3RFTDBNd0FST1J3P2k9ODgmZT02Mzc1Nzc0MTY4MDc4MjQyOTM"
        server_call = create_calling_server_client().initialize_server_call(server_call_id)
        server_call.start_recording("/not/absolute/uri")
        assert True

if __name__ == '__main__':
    unittest.main()
