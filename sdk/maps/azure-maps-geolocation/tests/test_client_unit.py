import sys
import pytest
from unittest.mock import Mock
from devtools_testutils import AzureTestCase
from azure.core.exceptions import ServiceRequestError
from azure.core.credentials import AzureKeyCredential
from azure.maps.geolocation import MapsGeolocationClient


# cSpell:disable
def create_mock_client():
    return MapsGeolocationClient(credential= Mock(AzureKeyCredential))

class AzureMapsGeolocationClientUnitTest(AzureTestCase):
    def test_get_country_code(self):
        client = create_mock_client()
        with pytest.raises(ServiceRequestError):
            client.get_country_code(ip_address="12345123")


if __name__ == "__main__" :
    testArgs = [ "-v" , "-s" ] if len(sys.argv) == 1 else sys.argv[1:]
    #testArgs = [ "-s" , "-n" , "auto" , "--dist=loadscope" ] if len(sys.argv) == 1 else sys.argv[1:]
    #pytest-xdist: -n auto --dist=loadscope
    #pytest-parallel: --tests-per-worker auto
    #print( "testArgs={}".format(testArgs) )

    pytest.main(args=testArgs)

    print("main() Leave")