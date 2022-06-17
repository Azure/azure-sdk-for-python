import os
import sys
import pytest
try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore

from devtools_testutils import AzureTestCase
from azure.core.pipeline.transport import HttpTransport, HttpResponse
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.maps.render import MapsRenderClient
from azure.maps.render.models import LatLon


# cSpell:disable
class MockTransport(HttpTransport):
    def __init__(self, status_code, body, **kwargs):
        self.status_code = status_code
        self.body = body.encode("utf-8-sig") if body != None else None
        self.kwargs = kwargs
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def close(self):
        pass
    def open(self):
        pass
    def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
        response = HttpResponse(request, None)
        response.status_code = self.status_code
        response.headers["content-type"] = "application/json"
        response.body = lambda: self.body
        for key, val in self.kwargs.items():
            setattr(response, key, val)
        return response

def create_mock_client(status_code=0, body=None, **kwargs):
    return RenderClient(credential="NotUsed",
                        authentication_policy = Mock(AzureKeyCredentialPolicy),
                        transport=MockTransport(status_code, body, **kwargs))

class AzureMapsRenderClientUnitTest(AzureTestCase):
    def __init__(self, *args, **kwargs):
        super(AzureMapsRenderClientUnitTest, self).__init__(*args, **kwargs)

    def setUp(self):
        super(AzureMapsRenderClientUnitTest, self).setUp()





if __name__ == "__main__" :
    testArgs = [ "-v" , "-s" ] if len(sys.argv) == 1 else sys.argv[1:]
    #testArgs = [ "-s" , "-n" , "auto" , "--dist=loadscope" ] if len(sys.argv) == 1 else sys.argv[1:]
    #pytest-xdist: -n auto --dist=loadscope
    #pytest-parallel: --tests-per-worker auto
    #print( "testArgs={}".format(testArgs) )

    pytest.main(args=testArgs)

    print("main() Leave")