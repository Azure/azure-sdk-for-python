# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import platform
import unittest
import uuid

import azure.cosmos
import azure.cosmos._utils as _utils
import test_config
from azure.cosmos import CosmosClient


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
                                .from_connection_string(test_config.TestConfig.connection_str,
                                                        consistency_level="Session"))
        database_id = "connection_string_test" + str(uuid.uuid4())
        db = client.create_database(database_id)
        self.assertTrue(db is not None)
        client.delete_database(db.id)


if __name__ == "__main__":
    unittest.main()
