# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer, AzureMgmtTestCase
from azure_devtools.scenario_tests import create_random_name
from testcase import StorageTestCase

import pytest


@pytest.fixture(scope="session")
def storage_account():
    test_case = AzureMgmtTestCase("__init__")
    rg_preparer = ResourceGroupPreparer()
    storage_preparer = StorageAccountPreparer(name_prefix='pyacrstorage')

    # Set what the decorator is supposed to set for us
    for prep in [rg_preparer, storage_preparer]:
        prep.live_test = False
        prep.test_class_instance = test_case

    # Create
    rg_name = create_random_name("pystorage", 24)
    storage_name = create_random_name("pyacrstorage", 24)
    try:
        rg = rg_preparer.create_resource(rg_name)
        StorageTestCase._RESOURCE_GROUP = rg['resource_group']
        try:
            storage_dict = storage_preparer.create_resource(
                storage_name,
                resource_group=rg['resource_group']
            )
            # Now the magic begins
            StorageTestCase._STORAGE_ACCOUNT = storage_dict['storage_account']
            StorageTestCase._STORAGE_KEY = storage_dict['storage_account_key']
            yield
        finally:
            storage_preparer.remove_resource(
                storage_name,
                resource_group=rg['resource_group']
            )
            StorageTestCase._STORAGE_ACCOUNT = None
            StorageTestCase._STORAGE_KEY = None
    finally:
        rg_preparer.remove_resource(rg_name)
        StorageTestCase._RESOURCE_GROUP = None
