#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import unittest
import time
# from types import *

import pytest
import azure.cosmos.cosmos_client as cosmos_client
import test_config

pytestmark = pytest.mark.cosmosEmulator

@pytest.mark.usefixtures("teardown")
class Test_session_container(unittest.TestCase):
    # this test doesn't need real credentials, or connection to server
    host = test_config._test_config.host
    masterkey = test_config._test_config.masterKey
    connectionPolicy = test_config._test_config.connectionPolicy

    def setUp(self):
        self.client = cosmos_client.CosmosClient(self.host, self.masterkey, consistency_level="Session", connection_policy=self.connectionPolicy)
        self.session = self.client.client_connection.Session

    def tearDown(self):
        pass

    def test_create_collection(self):
        #validate session token population after create collection request
        session_token = self.session.get_session_token('')
        assert session_token == ''

        create_collection_response_result = {u'_self': u'dbs/DdAkAA==/colls/DdAkAPS2rAA=/', u'_rid': u'DdAkAPS2rAA=', u'id': u'sample collection'}
        create_collection_response_header = {'x-ms-session-token': '0:0#409#24=-1#12=-1', 'x-ms-alt-content-path': 'dbs/sample%20database'}
        self.session.update_session(create_collection_response_result, create_collection_response_header)

        token = self.session.get_session_token(u'/dbs/sample%20database/colls/sample%20collection')
        assert token == '0:0#409#24=-1#12=-1'

        token = self.session.get_session_token(u'dbs/DdAkAA==/colls/DdAkAPS2rAA=/')
        assert token == '0:0#409#24=-1#12=-1'
        return True

    def test_document_requests(self):
        # validate session token for rid based requests
        create_document_response_result = {u'_self': u'dbs/DdAkAA==/colls/DdAkAPS2rAA=/docs/DdAkAPS2rAACAAAAAAAAAA==/', 
                                           u'_rid': u'DdAkAPS2rAACAAAAAAAAAA==', u'id': u'eb391181-5c49-415a-ab27-848ce21d5d11'}
        create_document_response_header = {'x-ms-session-token': '0:0#406#24=-1#12=-1', 'x-ms-alt-content-path': 'dbs/sample%20database/colls/sample%20collection', 
                                           'x-ms-content-path': 'DdAkAPS2rAA='}
        
        self.session.update_session(create_document_response_result, create_document_response_header)

        token = self.session.get_session_token(u'dbs/DdAkAA==/colls/DdAkAPS2rAA=/docs/DdAkAPS2rAACAAAAAAAAAA==/')
        assert token == '0:0#406#24=-1#12=-1'

        token = self.session.get_session_token(u'dbs/sample%20database/colls/sample%20collection/docs/eb391181-5c49-415a-ab27-848ce21d5d11')
        assert token == '0:0#406#24=-1#12=-1'


if __name__ == '__main__':
    unittest.main()