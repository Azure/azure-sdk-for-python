#--------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved. 
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#--------------------------------------------------------------------------

import unittest
import json
import httpretty
import requests

from msrestazure import azure_cloud

class TestCloud(unittest.TestCase):

    @httpretty.activate
    def test_get_cloud_from_endpoint(self):

        public_azure_dict = {
        	"galleryEndpoint": "https://gallery.azure.com",
	        "graphEndpoint": "https://graph.windows.net/",
	        "portalEndpoint": "https://portal.azure.com",
	        "authentication": {
		        "loginEndpoint": "https://login.windows.net",
		        "audiences": ["https://management.core.windows.net/", "https://management.azure.com/"]
	        }
        }

        httpretty.register_uri(httpretty.GET,
                               "https://management.azure.com/metadata/endpoints?api-version=1.0",
                               body=json.dumps(public_azure_dict),
                               content_type="application/json")

        cloud = azure_cloud.get_cloud_from_metadata_endpoint("https://management.azure.com")
        self.assertEqual("https://management.azure.com", cloud.name)
        self.assertEqual("https://management.azure.com", cloud.endpoints.management)
        self.assertEqual("https://management.azure.com", cloud.endpoints.resource_manager)
        self.assertEqual("https://gallery.azure.com", cloud.endpoints.gallery)
        self.assertEqual("https://graph.windows.net/", cloud.endpoints.active_directory_graph_resource_id)
        self.assertEqual("https://login.windows.net", cloud.endpoints.active_directory)

        session = requests.Session()
        cloud = azure_cloud.get_cloud_from_metadata_endpoint("https://management.azure.com", "Public Azure", session)
        self.assertEqual("Public Azure", cloud.name)
        self.assertEqual("https://management.azure.com", cloud.endpoints.management)
        self.assertEqual("https://management.azure.com", cloud.endpoints.resource_manager)
        self.assertEqual("https://gallery.azure.com", cloud.endpoints.gallery)
        self.assertEqual("https://graph.windows.net/", cloud.endpoints.active_directory_graph_resource_id)
        self.assertEqual("https://login.windows.net", cloud.endpoints.active_directory)

        with self.assertRaises(azure_cloud.MetadataEndpointError):
            azure_cloud.get_cloud_from_metadata_endpoint("https://something.azure.com")

        with self.assertRaises(azure_cloud.CloudEndpointNotSetException):
            cloud.endpoints.batch_resource_id

        with self.assertRaises(azure_cloud.CloudSuffixNotSetException):
            cloud.suffixes.sql_server_hostname

        self.assertIsNotNone(str(cloud))
