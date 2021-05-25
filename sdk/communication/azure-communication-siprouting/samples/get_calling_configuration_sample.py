from ..azure.communication.siprouting import SIPRoutingClient
from ..azure.communication.siprouting import SipConfiguration

class GetCallingSIPSample(object):

    def get_calling_configuration(self):
        test_endpoint = "https://communication-services-test.communication.azure.com/"
        #test_endpoint = "https://communication-services-test.communication.azure.com/identities" 

        calling_configuration_client = SIPRoutingClient(test_endpoint)
        token_holder = ""
        configuration = calling_configuration_client.get_callingsip(token_holder)