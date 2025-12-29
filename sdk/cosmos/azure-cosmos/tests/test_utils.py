# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import platform
import unittest
import uuid

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
                                .from_connection_string(test_config.TestConfig.connection_str,
                                                        consistency_level="Session"))
        database_id = "connection_string_test" + str(uuid.uuid4())
        db = client.create_database(database_id)
        self.assertTrue(db is not None)
        client.delete_database(db.id)

    def test_add_args_to_kwargs(self):
        arg_names = ["arg1", "arg2", "arg3", "arg4"]
        args = ("arg1_val", "arg2_val", "arg3_val", "arg4_val")
        kwargs = {}

        # Test any number of positional arguments less than or equals to the number of argument names
        for num_args in range(len(arg_names)):
            args = tuple(f"arg{i+1}_val" for i in range(num_args))
            kwargs = {}
            _utils.add_args_to_kwargs(arg_names, args, kwargs)

            assert len(kwargs.keys()) == len(args)
            for arg_name, arg in zip(arg_names, args):
                assert arg_name in kwargs
                assert kwargs[arg_name] == arg

        # test if arg_name already in kwargs
        with pytest.raises(ValueError) as e:
            _utils.add_args_to_kwargs(arg_names, args, kwargs)
        assert str(e.value) == f"{arg_names[0]} cannot be used as positional and keyword argument at the same time."

        # Test if number of positional argument greater than expected argument names
        args = ("arg1_val", "arg2_val", "arg3_val", "arg4_val", "arg5_val")
        with pytest.raises(ValueError) as e:
            _utils.add_args_to_kwargs(arg_names, args, kwargs)
        assert str(e.value) == (f"Positional argument is out of range. Expected {len(arg_names)} arguments, "
                         f"but got {len(args)} instead. Please review argument list in API documentation.")

    def test_verify_exclusive_arguments(self):
        exclusive_keys = ["key1", "key2", "key3", "key4"]

        ## Test valid cases
        kwargs = {}
        assert _utils.verify_exclusive_arguments(exclusive_keys, **kwargs) is None

        kwargs = {"key1": "test_value"}
        assert _utils.verify_exclusive_arguments(exclusive_keys, **kwargs) is None

        kwargs = {"key1": "test_value", "key9": "test_value"}
        assert _utils.verify_exclusive_arguments(exclusive_keys, **kwargs) is None

        # Even if some keys are in exclusive_keys list, if the values were 'None' we ignore them
        kwargs = {"key1": "test_value", "key2": None, "key3": None}
        assert _utils.verify_exclusive_arguments(exclusive_keys, **kwargs) is None

        ## Test invalid cases
        kwargs = {"key1": "test_value", "key2": "test_value"}
        expected_error_message = "'key1' and 'key2' are exclusive parameters, please only set one of them."
        with pytest.raises(ValueError) as e:
            _utils.verify_exclusive_arguments(exclusive_keys, **kwargs)
        assert str(e.value) == expected_error_message

        kwargs = {"key1": "test_value", "key2": "test_value", "key3": "test_value"}
        expected_error_message = "'key1', 'key2', and 'key3' are exclusive parameters, please only set one of them."
        with pytest.raises(ValueError) as e:
            _utils.verify_exclusive_arguments(exclusive_keys, **kwargs)
        assert str(e.value) == expected_error_message

