# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

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
