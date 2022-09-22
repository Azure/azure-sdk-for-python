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
import pytest
import azure.cosmos
import azure.cosmos._utils as _utils
import platform
import test_config

pytestmark = pytest.mark.cosmosEmulator

@pytest.mark.usefixtures("teardown")
class UtilsTests(unittest.TestCase):
    """Utils Tests
    """

    def test_user_agent(self):
        user_agent = _utils.get_user_agent()

        expected_user_agent = "azsdk-python-cosmos/{} Python/{} ({})".format(
            azure.cosmos.__version__,
            platform.python_version(),
            platform.platform()
        )
        self.assertEqual(user_agent, expected_user_agent)   

    def test_connection_string(self):
        client = azure.cosmos.CosmosClient.from_connection_string(test_config._test_config.connection_str,
                                                                  consistency_level="Session")
        db = client.create_database_if_not_exists("connection_string_test")
        self.assertTrue(db is not None)

        
if __name__ == "__main__":
    unittest.main()
