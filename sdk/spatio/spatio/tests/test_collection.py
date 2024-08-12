import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from devtools_testutils.azure_recorded_testcase import get_credential

from spatiopackage import AzureOrbitalPlanetaryComputerClient
import json
import random
import os
from test_utils import create_collection, delete_collection
import pytest

SpatioPreparer = functools.partial(
    EnvironmentVariableLoader,
    "spatio",
    spatio_endpoint="https://micerutest.gkefbud8evgraxeq.uksouth.geocatalog.ppe.spatio.azure-test.net",
    spatio_group="fakegroup",
)


@pytest.fixture(scope="class")
def test_fixture(request):
    credential = get_credential()
    endpoint = os.environ.get('SPATIO_ENDPOINT')
    aopc_client = AzureOrbitalPlanetaryComputerClient(endpoint, credential)
    collection_id = "integration-test-collection-" + str(random.randint(0, 1000))
    created_collection = create_collection(aopc_client,collection_id)

    # Set attributes on the request object
    request.cls.credential = credential
    request.cls.client = AzureOrbitalPlanetaryComputerClient(endpoint=endpoint, credential=credential)
    request.cls.collection_id = collection_id

    # Set up resources with the client, then yield to tests
    yield  # <-- Tests run here, and execution resumes after they finish
    # Clean up resources after tests are run
    delete_operations = aopc_client.delete_operations
    delete_operations.collection_api_collections_collection_id_delete(collection_id)


@pytest.mark.usefixtures("test_fixture")
class TestAzureOrbitalPlanetaryComputerClient(AzureRecordedTestCase):

    # Start with any helper functions you might need, for example a client creation method:
    def create_aopc_client(self, endpoint):
        credential = test_fixture.credentia        
        aopc_client = self.client
        #AzureOrbitalPlanetaryComputerClient(endpoint=endpoint, credential=credential)
        return aopc_client

    # Write your test cases, each starting with "test_":
    @SpatioPreparer()
    @recorded_by_proxy
    def test_create_collection(cls, spatio_endpoint):
        #collection_id = "integration-test-collection-" + str(random.randint(0, 1000))
        
        get_operations_collections=cls.client.get_operations_collections
        collection = get_operations_collections.collection_api_collections_collection_id_get(cls.collection_id)
        assert collection is not None

        credential = cls.credential
        client = cls.client
        
        # Your test code here
        assert client is not None
        assert credential is not None
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
        # geocatalog = createoperations.collection_api_collections_post(stac_collection)
        #
        # assert geocatalog is not None
        #
        # delete_operations = aopc_client.delete_operations
        # delete_operations.collection_api_collections_collection_id_delete(collection_id)
