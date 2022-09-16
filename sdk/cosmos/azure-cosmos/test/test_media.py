import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos._synchronized_request as synchronized_request
import unittest
import test_config

#  TODO: Check if this test is needed - not sure what is being tested here other than account names?

class FakePipelineResponse:
    def __init__(
        self,
        http_response,
    ):
        self.http_response = http_response


class FakeHttpResponse:
    def __init__(
        self,
        content,
        headers,
        status_code
    ):
        self.content = content
        self.headers = headers
        self.status_code = status_code

    def body(self):
        return self.content


class MediaTests(unittest.TestCase):
    database_account_string = b'''{"_self": "",
    "id": "fake-media",
    "_rid": "fake-media.documents.azure.com",
    "media": "//media/",
    "addresses": "//addresses/",
    "_dbs": "//dbs/",
    "writableLocations": [
        {"name": "UK South", "databaseAccountEndpoint": "https://fake-media-uksouth.documents.azure.com:443/"}],
     "readableLocations": [
         {"name": "UK South", "databaseAccountEndpoint": "https://fake-media-uksouth.documents.azure.com:443/"},
         {"name": "UK West", "databaseAccountEndpoint": "https://fake-media-ukwest.documents.azure.com:443/"}],
     "enableMultipleWriteLocations": false,
     "userReplicationPolicy": {"asyncReplication": false, "minReplicaSetSize": 3, "maxReplicasetSize": 4},
     "userConsistencyPolicy": {"defaultConsistencyLevel": "Session"},
     "systemReplicationPolicy": {"minReplicaSetSize": 3, "maxReplicasetSize": 4},
     "readPolicy": {"primaryReadCoefficient": 1, "secondaryReadCoefficient": 1}}'''

    response = FakePipelineResponse(FakeHttpResponse(database_account_string, {}, 200))

    def test_account_name_with_media(self):
        host = "https://fake-media.documents.azure.com:443/"
        master_key = test_config._test_config.masterKey
        try:
            original_execute_function = synchronized_request._PipelineRunFunction
            synchronized_request._PipelineRunFunction = self._MockRunFunction
            cosmos_client.CosmosClient(host, master_key, consistency_level="Session")
        finally:
            synchronized_request._PipelineRunFunction = original_execute_function

    def _MockRunFunction(self, pipeline_client, request, **kwargs):
        return self.response

