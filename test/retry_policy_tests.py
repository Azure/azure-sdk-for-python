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

import pydocumentdb.document_client as document_client
import pydocumentdb.documents as documents
import pydocumentdb.errors as errors
import pydocumentdb.retry_options as retry_options
from pydocumentdb.http_constants import HttpHeaders, StatusCodes, SubStatusCodes
import pydocumentdb.retry_utility as retry_utility
import test.test_config as test_config


#IMPORTANT NOTES: 
  
#  	Most test cases in this file create collections in your DocumentDB account.
#  	Collections are billing entities.  By running these test cases, you may incur monetary costs on your account.
  
#  	To Run the test, replace the two member fields (masterKey and host) with values 
#   associated with your DocumentDB account.

class Test_retry_policy_tests(unittest.TestCase):

    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    test_db_name = 'sample database' 
    test_coll_name = 'sample collection'

    def __AssertHTTPFailureWithStatus(self, status_code, func, *args, **kwargs):
        """Assert HTTP failure with status.

        :Parameters:
            - `status_code`: int
            - `func`: function
        """
        try:
            func(*args, **kwargs)
            self.assertFalse(True, 'function should fail.')
        except errors.HTTPFailure as inst:
            self.assertEqual(inst.status_code, status_code)

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure DocumentDB account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    @classmethod
    def tearDownClass(cls):
        client = document_client.DocumentClient(cls.host, 
                                                {'masterKey': cls.masterKey})
        query_iterable = client.QueryDatabases('SELECT * FROM root r WHERE r.id=\'' + cls.test_db_name + '\'')
        it = iter(query_iterable)
        
        test_db = next(it, None)
        if test_db is not None:
            client.DeleteDatabase(test_db['_self'])

    def setUp(self):
        self.client = document_client.DocumentClient(Test_retry_policy_tests.host, {'masterKey': Test_retry_policy_tests.masterKey})

        # Create the test database only when it's not already present
        query_iterable = self.client.QueryDatabases('SELECT * FROM root r WHERE r.id=\'' + Test_retry_policy_tests.test_db_name + '\'')
        it = iter(query_iterable)
        
        self.created_db = next(it, None)
        if self.created_db is None:
            self.created_db = self.client.CreateDatabase({'id' : Test_retry_policy_tests.test_db_name})

        # Create the test collection only when it's not already present
        query_iterable = self.client.QueryCollections(self.created_db['_self'], 'SELECT * FROM root r WHERE r.id=\'' + Test_retry_policy_tests.test_coll_name + '\'')
        it = iter(query_iterable)
        
        self.created_collection = next(it, None)
        if self.created_collection is None:
            self.created_collection = self.client.CreateCollection(self.created_db['_self'], {'id' : Test_retry_policy_tests.test_coll_name})

        self.retry_after_in_milliseconds = 1000

    def test_resource_throttle_retry_policy_default_retry_after(self):
        connection_policy = documents.ConnectionPolicy()
        connection_policy.RetryOptions = retry_options.RetryOptions(5)

        client = document_client.DocumentClient(Test_retry_policy_tests.host, {'masterKey': Test_retry_policy_tests.masterKey}, connection_policy)

        self.OriginalExecuteFunction = retry_utility._ExecuteFunction
        retry_utility._ExecuteFunction = self._MockExecuteFunction

        document_definition = { 'id': 'doc',
                                'name': 'sample document',
                                'key': 'value'} 

        try:
            client.CreateDocument(self.created_collection['_self'], document_definition)
        except errors.HTTPFailure as e:
            self.assertEqual(e.status_code, StatusCodes.TOO_MANY_REQUESTS)
            self.assertEqual(connection_policy.RetryOptions.MaxRetryAttemptCount, client.last_response_headers[HttpHeaders.ThrottleRetryCount])
            self.assertGreaterEqual(client.last_response_headers[HttpHeaders.ThrottleRetryWaitTimeInMs], connection_policy.RetryOptions.MaxRetryAttemptCount * self.retry_after_in_milliseconds)

        retry_utility._ExecuteFunction = self.OriginalExecuteFunction

    def test_resource_throttle_retry_policy_fixed_retry_after(self):
        connection_policy = documents.ConnectionPolicy()
        connection_policy.RetryOptions = retry_options.RetryOptions(5, 2000)

        client = document_client.DocumentClient(Test_retry_policy_tests.host, {'masterKey': Test_retry_policy_tests.masterKey}, connection_policy)

        
        self.OriginalExecuteFunction = retry_utility._ExecuteFunction
        retry_utility._ExecuteFunction = self._MockExecuteFunction

        document_definition = { 'id': 'doc',
                                'name': 'sample document',
                                'key': 'value'} 

        try:
            client.CreateDocument(self.created_collection['_self'], document_definition)
        except errors.HTTPFailure as e:
            self.assertEqual(e.status_code, StatusCodes.TOO_MANY_REQUESTS)
            self.assertEqual(connection_policy.RetryOptions.MaxRetryAttemptCount, client.last_response_headers[HttpHeaders.ThrottleRetryCount])
            self.assertGreaterEqual(client.last_response_headers[HttpHeaders.ThrottleRetryWaitTimeInMs], connection_policy.RetryOptions.MaxRetryAttemptCount * connection_policy.RetryOptions.FixedRetryIntervalInMilliseconds)

        retry_utility._ExecuteFunction = self.OriginalExecuteFunction

    def test_resource_throttle_retry_policy_max_wait_time(self):
        connection_policy = documents.ConnectionPolicy()
        connection_policy.RetryOptions = retry_options.RetryOptions(5, 2000, 3)

        client = document_client.DocumentClient(Test_retry_policy_tests.host, {'masterKey': Test_retry_policy_tests.masterKey}, connection_policy)

        
        self.OriginalExecuteFunction = retry_utility._ExecuteFunction
        retry_utility._ExecuteFunction = self._MockExecuteFunction

        document_definition = { 'id': 'doc',
                                'name': 'sample document',
                                'key': 'value'} 

        try:
            client.CreateDocument(self.created_collection['_self'], document_definition)
        except errors.HTTPFailure as e:
            self.assertEqual(e.status_code, StatusCodes.TOO_MANY_REQUESTS)
            self.assertGreaterEqual(client.last_response_headers[HttpHeaders.ThrottleRetryWaitTimeInMs], connection_policy.RetryOptions.MaxWaitTimeInSeconds * 1000)

        retry_utility._ExecuteFunction = self.OriginalExecuteFunction

    def test_resource_throttle_retry_policy_query(self):
        connection_policy = documents.ConnectionPolicy()
        connection_policy.RetryOptions = retry_options.RetryOptions(5)

        client = document_client.DocumentClient(Test_retry_policy_tests.host, {'masterKey': Test_retry_policy_tests.masterKey}, connection_policy)
        
        document_definition = { 'id': 'doc',
                                'name': 'sample document',
                                'key': 'value'} 

        client.CreateDocument(self.created_collection['_self'], document_definition)

        self.OriginalExecuteFunction = retry_utility._ExecuteFunction
        retry_utility._ExecuteFunction = self._MockExecuteFunction

        try:
            list(client.QueryDocuments(
            self.created_collection['_self'],
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    { 'name':'@id', 'value':document_definition['id'] }
                ]
            }))
        except errors.HTTPFailure as e:
            self.assertEqual(e.status_code, StatusCodes.TOO_MANY_REQUESTS)
            self.assertEqual(connection_policy.RetryOptions.MaxRetryAttemptCount, client.last_response_headers[HttpHeaders.ThrottleRetryCount])
            self.assertGreaterEqual(client.last_response_headers[HttpHeaders.ThrottleRetryWaitTimeInMs], connection_policy.RetryOptions.MaxRetryAttemptCount * self.retry_after_in_milliseconds)

        retry_utility._ExecuteFunction = self.OriginalExecuteFunction

    def _MockExecuteFunction(self, function, *args, **kwargs):
        raise errors.HTTPFailure(StatusCodes.TOO_MANY_REQUESTS, "Request rate is too large", {HttpHeaders.RetryAfterInMilliseconds: self.retry_after_in_milliseconds})

if __name__ == '__main__':
    unittest.main()
