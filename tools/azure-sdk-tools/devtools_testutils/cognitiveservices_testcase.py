# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import time
from collections import namedtuple
from azure_devtools.scenario_tests import ReplayableTest
from devtools_testutils import AzureTestCase
from azure_devtools.scenario_tests.exceptions import AzureTestError
from . import AzureMgmtPreparer, ResourceGroupPreparer
from .resource_testcase import RESOURCE_GROUP_PARAM
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from msrest.authentication import CognitiveServicesCredentials

FakeCognitiveServicesAccount = namedtuple("FakeResource", ["endpoint"])


class CognitiveServiceTest(AzureTestCase):
    """Can be used for Track 1 tests"""

    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ["Ocp-Apim-Subscription-Key"]

    def __init__(self, method_name):
        super(CognitiveServiceTest, self).__init__(method_name)


class CognitiveServicesAccountPreparer(AzureMgmtPreparer):
    def __init__(
        self,
        name_prefix="",
        sku="S0",
        location="westus2",
        kind="cognitiveservices",
        parameter_name="cognitiveservices_account",
        legacy=False,
        resource_group_parameter_name=RESOURCE_GROUP_PARAM,
        disable_recording=True,
        playback_fake_resource=None,
        client_kwargs=None,
        random_name_enabled=True,
        **kwargs
    ):
        super(CognitiveServicesAccountPreparer, self).__init__(
            name_prefix,
            24,
            disable_recording=disable_recording,
            playback_fake_resource=playback_fake_resource,
            client_kwargs=client_kwargs,
            random_name_enabled=random_name_enabled,
        )
        self.location = location
        self.sku = sku
        self.kind = kind
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name
        self.cogsci_key = ""
        self.legacy = legacy
        self.custom_subdomain_name = kwargs.pop("custom_subdomain_name", None)

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(CognitiveServicesManagementClient)
            group = self._get_resource_group(**kwargs)
            cogsci_account = self.client.accounts.create(
                group.name,
                name,
                account={
                    "sku": {"name": self.sku},
                    "location": self.location,
                    "kind": self.kind,
                    "properties": {
                        "custom_sub_domain_name": self.custom_subdomain_name
                    },
                },
            )
            time.sleep(
                10
            )  # it takes a few seconds to create a cognitive services account
            self.resource = cogsci_account
            self.cogsci_key = self.client.accounts.list_keys(group.name, name).key1
            # FIXME: LuisAuthoringClient and LuisRuntimeClient need authoring key from ARM API (coming soon-ish)
        else:
            if self.custom_subdomain_name:
                self.resource = FakeCognitiveServicesAccount(
                    "https://{}.cognitiveservices.azure.com".format(
                        self.custom_subdomain_name
                    )
                )
                self.cogsci_key = "ZmFrZV9hY29jdW50X2tleQ=="
            else:
                self.resource = FakeCognitiveServicesAccount(
                    "https://{}.api.cognitive.microsoft.com".format(self.location)
                )
                self.cogsci_key = "ZmFrZV9hY29jdW50X2tleQ=="

        if self.legacy:
            try:
                return {
                    self.parameter_name: self.resource.properties.endpoint,
                    "{}_key".format(self.parameter_name): CognitiveServicesCredentials(
                        self.cogsci_key
                    ),
                }
            except AttributeError:
                return {
                    self.parameter_name: self.resource.endpoint,
                    "{}_key".format(self.parameter_name): CognitiveServicesCredentials(
                        self.cogsci_key
                    ),
                }
        else:
            try:
                return {
                    self.parameter_name: self.resource.properties.endpoint,
                    "{}_key".format(self.parameter_name): self.cogsci_key,
                }
            except AttributeError:
                return {
                    self.parameter_name: self.resource.endpoint,
                    "{}_key".format(self.parameter_name): self.cogsci_key,
                }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            self.client.accounts.delete(group.name, name)

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = (
                "To create a cognitive services account a resource group is required. Please add "
                "decorator @{} in front of this cognitive services account preparer."
            )
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))
