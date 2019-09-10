# The MIT License (MIT)
# Copyright (c) 2017 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE

# pytest fixture 'teardown' is called at the end of a test run to clean up resources

import pytest
import test_config
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
from azure.cosmos.http_constants import StatusCodes

database_ids_to_delete = []

@pytest.fixture(scope="session")
def teardown(request):

    def delete_database():
        print("Cleaning up test resources...")
        config = test_config._test_config
        host = config.host
        masterKey = config.masterKey
        connectionPolicy = config.connectionPolicy
        try:
            client = cosmos_client.CosmosClient(host, masterKey, "Session", connection_policy=connectionPolicy)
         # This is to soft-fail the teardown while cosmos tests are not running automatically
        except Exception:
            pass
        else:
            database_ids_to_delete.append(config.TEST_DATABASE_ID)
            for database_id in database_ids_to_delete:
                try:
                    client.delete_database(database_id)
                except errors.CosmosResourceNotFoundError:
                    pass
            del database_ids_to_delete[:]
        print("Clean up completed!")

    request.addfinalizer(delete_database)
    return None
