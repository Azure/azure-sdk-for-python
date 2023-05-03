# The MIT License (MIT)
# Copyright (c) 2022 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# import unittest
#
# # This class tests the integrated cache, which only works against accounts with the dedicated gateway configured
# # This class tests a PREVIEW FEATURE
#
# pytestmark = pytest.mark.cosmosEmulator
#
#
# @pytest.mark.usefixtures("teardown")
# class TestIntegratedCache(unittest.TestCase):
#
#     # This test only works if run manually, so we will leave it commented out.
#
#     def test_RU_cost(self):
#         if self.host.endswith(":8081/"):
#             print("Skipping; this test only works for accounts with the dedicated gateway configured, or the " +
#                   "emulator running with the proper setup flags, which should run on port 8082.")
#             return
#
#         body = self.get_test_item()
#         self.container.create_item(body)
#         item_id = body['id']
#
#         # Initialize cache for item point read, and verify there is a cost to the read call
#         self.container.read_item(item=item_id, partition_key=item_id, max_integrated_cache_staleness_in_ms=30000)
#         self.assertEqual(self.client.client_connection.last_response_headers[headers.IntegratedCacheHit], 'False')
#         self.assertTrue(float(self.client.client_connection.last_response_headers[headers.RequestCharge]) > 0)
#
#         # Verify that cache is being hit for item read and that there's no RU consumption for this second read
#         self.container.read_item(item=item_id, partition_key=item_id)
#         self.assertEqual(self.client.client_connection.last_response_headers[headers.IntegratedCacheHit], 'True')
#         self.assertTrue(float(self.client.client_connection.last_response_headers[headers.RequestCharge]) == 0)
#
#         body = self.get_test_item()
#         self.container.create_item(body)
#         item_id = body["id"]
#         query = 'SELECT * FROM c'
#
#         # Initialize cache for single partition query read, and verify there is a cost to the query call
#         # Need to iterate over query results in order to properly populate last response headers, so we cast to list
#         list(self.container.query_items(query=query,
#         partition_key=item_id, max_integrated_cache_staleness_in_ms=30000))
#         self.assertEqual(self.client.client_connection.last_response_headers[headers.IntegratedCacheHit], 'False')
#         self.assertTrue(float(self.client.client_connection.last_response_headers[headers.RequestCharge]) > 0)
#
#         # Verify that cache is being hit for item query and that there's no RU consumption for this second query
#         list(self.container.query_items(query=query, partition_key=item_id))
#         self.assertEqual(self.client.client_connection.last_response_headers[headers.IntegratedCacheHit], 'True')
#         self.assertTrue(float(self.client.client_connection.last_response_headers[headers.RequestCharge]) == 0)
#
#         # Verify that reading all items does not have a cost anymore, since all items have been populated into cache
#         self.container.read_all_items()
#         self.assertEqual(self.client.client_connection.last_response_headers[headers.IntegratedCacheHit], 'True')
#         self.assertTrue(float(self.client.client_connection.last_response_headers[headers.RequestCharge]) == 0)
#
#         self.client.delete_database(test_config._test_config.TEST_DATABASE_ID_PLAIN)
#
#     def get_test_item(self):
#         test_item = {
#             'id': 'Item_' + str(uuid.uuid4()),
#             'test_object': True,
#             'lastName': 'Smith',
#             'attr1': random.randint(0, 10)
#         }
#         return test_item
#
#
# if __name__ == "__main__":
#     unittest.main()
