# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import RoomsTest, RoomsPowerShellPreparer

class RoomsSmokeTest(RoomsTest):


    @RoomsPowerShellPreparer()
    def test_smoke(self, rooms_endpoint):
        client = self.create_client(endpoint=rooms_endpoint)
        # test your code here, for example:
        # result = client.xxx.xx(...)
        # assert result is not None
