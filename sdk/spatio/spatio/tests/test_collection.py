import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy

from spatiopackage import AzureOrbitalPlanetaryComputerClient
import json
import random
import os
from test_utils import create_collection,delete_collection

SpatioPreparer = functools.partial(
    EnvironmentVariableLoader,
    'spatio',
    spatio_endpoint="https://micerutest.gkefbud8evgraxeq.uksouth.geocatalog.ppe.spatio.azure-test.net",
    spatio_group="fakegroup",
)

# The test class name needs to start with "Test" to get collected by pytest
class TestAzureOrbitalPlanetaryComputerClient(AzureRecordedTestCase):
    
    #def __init__(self):


    # Start with any helper functions you might need, for example a client creation method:
    def create_aopc_client(self, endpoint):
        credential = self.get_credential(AzureOrbitalPlanetaryComputerClient)
        aopc_client = AzureOrbitalPlanetaryComputerClient(endpoint=endpoint, credential=credential)
        return aopc_client

    # Write your test cases, each starting with "test_":
    @SpatioPreparer()
    @recorded_by_proxy
    def test_create_collection(self, spatio_endpoint):
        collection_id="integration-test-collection-" + str(random.randint(0, 1000))
        
        """
        #Test creating collection
        aopc_client = self.create_aopc_client(spatio_endpoint)
        created_collection = create_collection(aopc_client,collection_id)
        assert created_collection is not None

        #Test getting the collection back
        get_operations_collections = aopc_client.get_operations_collections
        collection = get_operations_collections.collection_api_collections_collection_id_get(collection_id)
        assert collection is not None

        delete_collection(aopc_client,collection_id)
        """
        #geocatalog = createoperations.collection_api_collections_post(stac_collection)
        #
        #assert geocatalog is not None
        # 
        #delete_operations = aopc_client.delete_operations
        #delete_operations.collection_api_collections_collection_id_delete(collection_id)


