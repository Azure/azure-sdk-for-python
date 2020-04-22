# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import sys

import pytest

from devtools_testutils import FakeResource

from search_service_preparer import GlobalResourceGroupPreparer

def pytest_unconfigure(config):
    if not isinstance(GlobalResourceGroupPreparer.GLOBAL_GROUP, FakeResource):
        group_name = GlobalResourceGroupPreparer.GLOBAL_GROUP.name
        GlobalResourceGroupPreparer._preparer.client.resource_groups.delete(group_name, polling=False)

        # group_name = search_service_preparer.GLOBAL_GROUP.name
        # service_name = SearchServicePreparer.service_name
        # client = search_service_preparer.SearchServicePreparer.mgmt_client
        # client.services.delete(group_name, service_name)

# Ignore async tests for Python < 3.5
collect_ignore = []
if sys.version_info < (3, 5):
    collect_ignore.append("async_tests")
