# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

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
# SOFTWARE.

import platform
import unittest

import pytest

import azure.cosmos
import azure.cosmos._utils as _utils
import test_config
from azure.cosmos import CosmosClient


@pytest.mark.cosmosEmulator
class TestsUtils(unittest.TestCase):
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
        client: CosmosClient = (azure.cosmos.CosmosClient
                                .from_connection_string(test_config._test_config.connection_str,
                                                        consistency_level="Session"))
        database_id = "connection_string_test"
        db = client.create_database(database_id)
        self.assertTrue(db is not None)
        client.delete_database(db)


if __name__ == "__main__":
    unittest.main()
