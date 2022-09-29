# # coding: utf-8
#
# # -------------------------------------------------------------------------
# # Copyright (c) Microsoft Corporation. All rights reserved.
# # Licensed under the MIT License. See License.txt in the project root for
# # license information.
# # --------------------------------------------------------------------------
# from contextlib import suppress
#
# import pytest
#
# from azure.mgmt.security.v2022_07_01_preview import SecurityCenter
# import azure.mgmt.security.models
# from azure.core.exceptions import HttpResponseError
# from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy
#
# AZURE_LOCATION = "eastus"
#
#
# class TestMgmtSecurity(AzureMgmtRecordedTestCase):
#     def setup_method(self, method):
#         self.mgmt_client = self.create_mgmt_client(SecurityCenter)
#
#     @recorded_by_proxy
#     def test_security_operations_list(self):
#         # it proves that we can normally send request but maybe needs additional parameters
#         with suppress(HttpResponseError):
#             result = self.mgmt_client.applications.list()
#             assert list(result) is not None