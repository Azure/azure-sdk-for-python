# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import datetime

from azure.mgmt.communication import CommunicationServiceManagementClient
from azure.mgmt.communication.models import CommunicationServiceResource
from devtools_testutils import AzureMgmtPreparer, ResourceGroupPreparer
from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM
from azure_devtools.scenario_tests.exceptions import AzureTestError

class CommunicationServicePreparer(AzureMgmtPreparer):
    """Communication Service Preparer.
       Creating and destroying test resources on demand
    """
    def __init__(
            self,
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
        self.random_name_enabled = True
        self.service_name = "TEST-SERVICE-NAME"
        self.mgmt_client = None

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
        self.service_name = self.create_random_name()

        if not self.is_live:
            return {
                "connection_string": "endpoint=https://fake-resource.communication.azure.com/;accesskey=fake===",
            }

        group_name = self._get_resource_group(**kwargs).name

        self.mgmt_client = self.create_mgmt_client(CommunicationServiceManagementClient, polling_interval=30)

        resource = self.mgmt_client.communication_service.begin_create_or_update(
            group_name,
            self.service_name,
            CommunicationServiceResource(location="global", data_location="UnitedStates")
        ).result()

        primary_connection_string = self.mgmt_client.communication_service.list_keys(
            group_name,
            resource.name).primary_connection_string

        return {
            "connection_string": primary_connection_string,
        }

    def remove_resource(self, name, **kwargs):
        if not self.is_live:
            return

        group_name = self._get_resource_group(**kwargs).name
        self.mgmt_client.communication_service.begin_delete(group_name, self.service_name).wait()
