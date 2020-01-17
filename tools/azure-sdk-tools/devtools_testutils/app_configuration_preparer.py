# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import azure.mgmt.appconfiguration
import time
import os
from devtools_testutils import AzureMgmtPreparer, ResourceGroupPreparer
from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM
from azure_devtools.scenario_tests.exceptions import AzureTestError
from azure.appconfiguration import AzureAppConfigurationClient
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.authorization import AuthorizationManagementClient
from msrestazure.azure_exceptions import CloudError
try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock
import uuid

class AppConfigurationPreparer(AzureMgmtPreparer):
    def __init__(self,
                 name_prefix="appconfig",
                 aad_mode=False,
                 resource_group_parameter_name=RESOURCE_GROUP_PARAM,
                 disable_recording=True,
                 playback_fake_resource=None,
                 client_kwargs=None):
        super(AppConfigurationPreparer, self).__init__(
            name_prefix,
            24,
            disable_recording=disable_recording,
            playback_fake_resource=playback_fake_resource,
            client_kwargs=client_kwargs,
        )
        self.resource_group_parameter_name = resource_group_parameter_name
        self.aad_mode = aad_mode

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs[self.resource_group_parameter_name]
        except KeyError:
            template = (
                "To create a key vault a resource group is required. Please add "
                "decorator @{} in front of this storage account preparer."
            )
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))

    def create_resource(self, name, **kwargs):
        if not self.is_live:
            return
        BODY = {
            "location": "westus",
            "sku": {
                "name": "Free"
            }
        }
        group = self._get_resource_group(**kwargs).name
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.appconfiguration.AppConfigurationManagementClient
        )
        try:
            result = self.mgmt_client.configuration_stores.get(group, name)
            return
        except:
            pass

        resource = self.mgmt_client.configuration_stores.create(group, name, BODY)

        # ARM may return not found at first even though the resource group has been created
        retries = 4
        for i in range(retries):
            try:
                result = resource.result()
                if result.provisioning_state == "Succeeded":
                    break
            except Exception as ex:
                if i == retries - 1:
                    raise
                time.sleep(3)
        result = self.mgmt_client.configuration_stores.get(group, name)
        subscription_id = self.test_class_instance.get_settings_value("SUBSCRIPTION_ID")
        client_id = self.test_class_instance.get_settings_value("CLIENT_ID")
        client_oid = self.test_class_instance.get_settings_value("CLIENT_OID")
        secret = self.test_class_instance.get_settings_value("CLIENT_SECRET")
        tenant=self.test_class_instance.get_settings_value("TENANT_ID")
        credentials = ServicePrincipalCredentials(client_id=client_id,secret=secret,tenant=tenant)
        authorization_client = AuthorizationManagementClient(credentials, subscription_id)
        role_name = 'App Configuration Data Owner'
        roles = list(authorization_client.role_definitions.list(result.id, filter="roleName eq '{}'".format(role_name)))
        assert len(roles) == 1
        data_reader_role = roles[0]
        try:
            role_assignment = authorization_client.role_assignments.create(
                result.id,
                uuid.uuid4(),
                {
                    'role_definition_id': data_reader_role.id,
                    'principal_id': client_oid
                }
            )
        except CloudError as ex:
            if 'already exists' in ex.message:
                pass

        if self.aad_mode:
            base_url = result.endpoint
            return {"base_url": base_url}
        else:
            result = list(self.mgmt_client.configuration_stores.list_keys(group, name))
            if len(result) > 0:
                connection_string = result[0].connection_string
                return {"connection_str": connection_string}
            else:
                raise
