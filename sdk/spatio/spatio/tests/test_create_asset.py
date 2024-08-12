import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy

from spatiopackage import AzureOrbitalPlanetaryComputerClient
import json
import os
from io import BytesIO
import requests
from test_utils import create_collection, delete_collection
import random
from devtools_testutils.azure_recorded_testcase import get_credential
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
    #delete_operations.collection_api_collections_collection_id_delete(collection_id)

@pytest.mark.usefixtures("test_fixture")
class TestAzureOrbitalPlanetaryComputerClient(AzureRecordedTestCase):

    # Write your test cases, each starting with "test_":
    @SpatioPreparer()
    @recorded_by_proxy
    def test_create_asset(cls, spatio_endpoint):
        collection_id = "integration-test-collection-" + str(random.randint(0, 1000))


        thumbnail_url = "https://ai4edatasetspublicassets.blob.core.windows.net/assets/pc_thumbnails/sentinel-2.png"
        thumbnail_response = requests.get(thumbnail_url)
        thumbnail = ("lulc.png", BytesIO(thumbnail_response.content))
        data_str = (
            '{"key": "thumbnail", "href":"", "type": "image/png", "roles":  ["test_asset"], "title": "test_asset"}'
        )
        createoperations = cls.client.create_operations_collections
        # collection_id = "integration-test-collection"

        # Test upload thumbnail:
        response = createoperations.collection_asset(cls.collection_id, data=data_str, file=thumbnail)
        assert response is not None

    @recorded_by_proxy
    def test_get_thumbnail(cls):
        # Test get thumbnail back:
        get_operations_collections = cls.client.get_operations_collections
        thumbnail = get_operations_collections.collection_thumbnail_api_collections_collection_id_thumbnail_get(
            cls.collection_id
        )
        assert thumbnail is not None