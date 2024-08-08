import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy

from spatiopackage import AzureOrbitalPlanetaryComputerClient
import json
import os
from io import BytesIO
import requests
from test_utils import create_collection,delete_collection
import random

SpatioPreparer = functools.partial(
    EnvironmentVariableLoader,
    'spatio',
    spatio_endpoint="https://micerutest.gkefbud8evgraxeq.uksouth.geocatalog.ppe.spatio.azure-test.net",
    spatio_group="fakegroup",
)

# The test class name needs to start with "Test" to get collected by pytest
class TestAzureOrbitalPlanetaryComputerClient(AzureRecordedTestCase):

    # Start with any helper functions you might need, for example a client creation method:
    def create_aopc_client(self, endpoint):
        credential = self.get_credential(AzureOrbitalPlanetaryComputerClient)
        aopc_client = AzureOrbitalPlanetaryComputerClient(endpoint=endpoint, credential=credential)
        return aopc_client


    # Write your test cases, each starting with "test_":
    @SpatioPreparer()
    @recorded_by_proxy
    def test_create_asset(self, spatio_endpoint):
        collection_id="integration-test-collection-" + str(random.randint(0, 1000))
        
        #create collection
        aopc_client = self.create_aopc_client(spatio_endpoint)
        created_collection = create_collection(aopc_client,collection_id)

        thumbnail_url = "https://ai4edatasetspublicassets.blob.core.windows.net/assets/pc_thumbnails/sentinel-2.png"
        thumbnail_response = requests.get(thumbnail_url)
        thumbnail = ("lulc.png", BytesIO(thumbnail_response.content))
        data_str = '{"key": "thumbnail", "href":"", "type": "image/png", "roles":  ["test_asset"], "title": "test_asset"}'
        aopc_client = self.create_aopc_client(spatio_endpoint)
        createoperations = aopc_client.create_operations_collections
        #collection_id = "integration-test-collection"

        #Test upload thumbnail:
        response = createoperations.collection_asset(collection_id, data=data_str, file = thumbnail)
        assert response is not None

        #Test get thumbnail back:
        get_operations_collections = aopc_client.get_operations_collections
        thumbnail = get_operations_collections.collection_thumbnail_api_collections_collection_id_thumbnail_get(collection_id)
        assert thumbnail is not None



