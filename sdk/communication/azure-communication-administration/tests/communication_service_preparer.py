# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import datetime
from os.path import dirname, realpath
import time

try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock

import json
import requests

from devtools_testutils import AzureMgmtPreparer, ResourceGroupPreparer
from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM
from azure_devtools.scenario_tests.exceptions import AzureTestError
from azure.mgmt.communication import CommunicationServiceManagementClient

class CommunicationResourceGroupPreparer(ResourceGroupPreparer):
    def create_resource(self, name, **kwargs):
        result = super(CommunicationResourceGroupPreparer, self).create_resource(name, **kwargs)
        if self.is_live and self._need_creation:
            expiry = datetime.datetime.now() + datetime.timedelta(days=1)
            resource_group_params = dict(tags={'DeleteAfter': expiry.isoformat()}, location=self.location)
            self.client.resource_groups.create_or_update(name, resource_group_params)
        return result

class CommunicationServicePreparer(AzureMgmtPreparer):
    def __init__(
        self,
        schema=None,
        name_prefix="communication",
        resource_group_parameter_name=RESOURCE_GROUP_PARAM,
        disable_recording=True,
        playback_fake_resource=None,
        client_kwargs=None,
    ):
        super(CommunicationServicePreparer, self).__init__(
            name_prefix,
            random_name_length=24,
            disable_recording=disable_recording,
            playback_fake_resource=playback_fake_resource,
            client_kwargs=client_kwargs,
        )
        self.resource_group_parameter_name = resource_group_parameter_name
        self.schema = schema
        self.index_name = None
        self.service_name = "TEST-SERVICE-NAME"

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs[self.resource_group_parameter_name]
        except KeyError:
            template = (
                "To create a communication service a resource group is required. Please add "
                "decorator @{} in front of this preparer."
            )
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))

    def create_resource(self, name, **kwargs):
        if self.schema:
            schema = json.loads(self.schema)
        else:
            schema = None
        self.service_name = self.create_random_name()
        self.endpoint = "https://{}.communication.azure.com".format(self.service_name)

        if not self.is_live:
            return {
                "api_key": "api-key",
            }

        group_name = self._get_resource_group(**kwargs).name

        self.mgmt_client = self.create_mgmt_client(CommunicationServiceManagementClient, connection_verify=False)

        resource = self.mgmt_client.communication_service.begin_create_or_update(
            group_name, self.service_name
        )

        api_key = resource

        return {
            "api_key": api_key,
        }

    def remove_resource(self, name, **kwargs):
        if not self.is_live:
            return

        group_name = self._get_resource_group(**kwargs).name
        self.mgmt_client.services.delete(group_name, self.service_name)