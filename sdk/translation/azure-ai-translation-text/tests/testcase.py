# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import AzureRecordedTestCase
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
import requests, datetime
from azure.core.credentials import AccessToken

from tests.staticAccessTokenCredential import StaticAccessTokenCredential

class TextTranslationTest(AzureRecordedTestCase):    
    def create_getlanguage_client(self, endpoint):
        client = TextTranslationClient(endpoint=endpoint, credential=None)
        return client
    
    def create_client(self, endpoint, apikey, region):
        credential = TranslatorCredential(apikey, region) 
        client = TextTranslationClient(endpoint=endpoint, credential=credential)
        return client
    
    def create_client_token(self, endpoint, apikey, region):
        accessToken = self.GetAzureAuthorizationToken(apikey, region)
        credential = StaticAccessTokenCredential(accessToken)        
        client = TextTranslationClient(endpoint=endpoint, credential=credential)
        return client
    
    def GetAzureAuthorizationToken(self, apikey, region):
       request_url = "https://{0}.api.cognitive.microsoft.com/sts/v1.0/issueToken?Subscription-Key={1}".format(region, apikey)        
       response = requests.post(request_url)
       print(response.content)
       print(datetime.datetime.now() + datetime.timedelta(days=1))
       return AccessToken(response.content, datetime.datetime.now() + datetime.timedelta(days=1))   

   