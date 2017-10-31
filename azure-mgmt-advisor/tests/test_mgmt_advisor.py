# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest
import datetime
import re
import time
import azure.mgmt.advisor

from devtools_testutils import (
    AzureMgmtTestCase, ResourceGroupPreparer,
)


class MgmtAdvisorTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtAdvisorTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.advisor.AdvisorManagementClient
        )

    def test_generate_recommendations(self):
        # trigger generate recommendations
        response = self.client.recommendations.generate(raw=True)

        # verify we got a Location header back
        self.assertTrue('Location' in response.headers)
        location = response.headers['Location']

        # extract the operation ID from the Location header
        operation_id = re.findall("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", location)

        # verify it is valid
        self.assertNotEqual(operation_id, None)
        self.assertTrue(len(operation_id), 1)

        status_code = None
        max_attempts = 30
        attempt = 0

        # get generate status until we get back 204 or 30 seconds have passed
        while True:
            response = self.client.recommendations.get_generate_status(
                raw=True,
                operation_id = operation_id[0]
            )
            status_code = response.response.status_code
            if (status_code == 204 or attempt >= max_attempts):
                break
            else:
                time.sleep(60)

        print(attempt)
        self.assertEqual(status_code, 204)

    def test_list(self):
        response = self.client.recommendations.list()
        print(response)
        self.assertNotEqual(response, None)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
