# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import test_config
from azure.cosmos import CosmosClient as CosmosSyncClient

cosmos_sync_client = CosmosSyncClient(test_config.TestConfig.host, test_config.TestConfig.masterKey)


def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    config = test_config.TestConfig
    config.create_database_if_not_exist(cosmos_sync_client)
    config.create_single_partition_container_if_not_exist(cosmos_sync_client)
    config.create_multi_partition_container_if_not_exist(cosmos_sync_client)


def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before
    returning the exit status to the system.
    """
    config = test_config.TestConfig
    config.try_delete_database(cosmos_sync_client)


def pytest_unconfigure(config):
    """
    called before test process is exited.
    """
