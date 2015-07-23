#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import json
import os.path
import time
import azure.mgmt.resource
from azure.common import (
    AzureHttpError,
    SubscriptionCloudCredentials,
)
from testutils.common_recordingtestcase import (
    RecordingTestCase,
    TestMode,
)
import tests.mgmt_settings_fake as fake_settings


class HttpStatusCode(object):
    OK = 200
    Created = 201
    Accepted = 202
    NoContent = 204
    NotFound = 404


class AzureMgmtTestCase(RecordingTestCase):

    def setUp(self):
        self.working_folder = os.path.dirname(__file__)

        super(AzureMgmtTestCase, self).setUp()

        self.fake_settings = fake_settings
        if TestMode.is_playback(self.test_mode):
            self.settings = self.fake_settings
        else:
            import tests.mgmt_settings_real as real_settings
            self.settings = real_settings

        self.resource_client = self.create_mgmt_client(azure.mgmt.resource.ResourceManagementClient)

        # Every test uses a different resource group name calculated from its
        # qualified test name.
        #
        # When running all tests serially, this allows us to delete
        # the resource group in teardown without waiting for the delete to
        # complete. The next test in line will use a different resource group,
        # so it won't have any trouble creating its resource group even if the
        # previous test resource group hasn't finished deleting.
        #
        # When running tests individually, if you try to run the same test
        # multiple times in a row, it's possible that the delete in the previous
        # teardown hasn't completed yet (because we don't wait), and that
        # would make resource group creation fail.
        # To avoid that, we also delete the resource group in the
        # setup, and we wait for that delete to complete.
        self.group_name = self.get_resource_name(
            self.qualified_test_name.replace('.', '_')
        )
        self.region = 'westus'

        if not self.is_playback():
            self.delete_resource_group(wait_timeout=600)

    def tearDown(self):
        if not self.is_playback():
            self.delete_resource_group(wait_timeout=None)
        return super(AzureMgmtTestCase, self).tearDown()

    def create_mgmt_client(self, client_class):
        creds = SubscriptionCloudCredentials(
            self.settings.SUBSCRIPTION_ID,
            self.settings.get_token(),
        )
        client = client_class(creds)
        if self.is_playback():
            client.long_running_operation_initial_timeout = 0
            client.long_running_operation_retry_timeout = 0
        return client

    def _scrub(self, val):
        val = super(AzureMgmtTestCase, self)._scrub(val)
        real_to_fake_dict = {
            self.settings.SUBSCRIPTION_ID: self.fake_settings.SUBSCRIPTION_ID,
        }
        val = self._scrub_using_dict(val, real_to_fake_dict)
        return val

    def create_resource_group(self):
        group = azure.mgmt.resource.ResourceGroup()
        group.location = self.region
        result = self.resource_client.resource_groups.create_or_update(
            self.group_name,
            group,
        )

    def delete_resource_group(self, wait_timeout):
        try:
            self.resource_client.resource_groups.delete(self.group_name)
        except AzureHttpError:
            pass

        if wait_timeout:
            while wait_timeout > 0:
                try:
                    result = self.resource_client.resource_groups.get(self.group_name)
                    if result.resource_group.provisioning_state != azure.mgmt.resource.ProvisioningState.deleting:
                        return
                except AzureHttpError as e:
                    if e.status_code == HttpStatusCode.NotFound:
                        return
                    raise
                time.sleep(10)
                wait_timeout -= 10
            self.assertTrue(False, 'Timed out waiting for resource group to be deleted.')
