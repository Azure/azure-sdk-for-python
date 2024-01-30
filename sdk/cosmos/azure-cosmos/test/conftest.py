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
from azure.cosmos import CosmosClient as CosmosSyncClient
from azure.cosmos.aio import CosmosClient as CosmosAsyncClient

cosmos_sync_client = CosmosSyncClient(test_config.TestConfig.host, test_config.TestConfig.masterKey)
cosmos_async_client = CosmosAsyncClient(test_config.TestConfig.host, test_config.TestConfig.masterKey)


@pytest.fixture(scope="session", autouse=True)
def get_cosmos_sync_client():
    return cosmos_sync_client


@pytest.fixture(scope="session", autouse=True)
def get_cosmos_async_client():
    return cosmos_async_client


@pytest.fixture(scope="session")
def create_test_database():
    config = test_config.TestConfig
    config.create_database_if_not_exist(cosmos_sync_client)


@pytest.fixture(scope="session")
def create_multi_partition_container():
    config = test_config.TestConfig
    config.create_multi_partition_container_if_not_exist(cosmos_sync_client)


@pytest.fixture(scope="session")
def create_single_partition_container():
    config = test_config.TestConfig
    config.create_single_partition_container_if_not_exist(cosmos_sync_client)


@pytest.fixture(scope="session")
def delete_test_database():
    config = test_config.TestConfig
    config.try_delete_database(cosmos_sync_client)


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
