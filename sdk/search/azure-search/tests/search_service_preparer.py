# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

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

from consts import SERVICE_URL, TEST_SERVICE_NAME


class SearchServicePreparer(AzureMgmtPreparer):
    def __init__(
        self,
        schema=None,
        index_batch=None,
        name_prefix="search",
        resource_group_parameter_name=RESOURCE_GROUP_PARAM,
        disable_recording=True,
        playback_fake_resource=None,
        client_kwargs=None,
    ):
        super(SearchServicePreparer, self).__init__(
            name_prefix,
            random_name_length=24,
            disable_recording=disable_recording,
            playback_fake_resource=playback_fake_resource,
            client_kwargs=client_kwargs,
        )
        self.resource_group_parameter_name = resource_group_parameter_name
        self.schema = schema
        self.index_name = None
        self.index_batch = index_batch

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs[self.resource_group_parameter_name]
        except KeyError:
            template = (
                "To create a search service a resource group is required. Please add "
                "decorator @{} in front of this preparer."
            )
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))

    def create_resource(self, name, **kwargs):
        if not self.is_live:
            return

        group_name = self._get_resource_group(**kwargs).name

        from azure.mgmt.search import SearchManagementClient
        from azure.mgmt.search.models import ProvisioningState

        self.mgmt_client = self.create_mgmt_client(SearchManagementClient)

        # create the search service
        from azure.mgmt.search.models import SearchService, Sku

        service_config = SearchService(location="West US", sku=Sku(name="free"))
        resource = self.mgmt_client.services.create_or_update(
            group_name, TEST_SERVICE_NAME, service_config
        )

        retries = 4
        for i in range(retries):
            try:
                result = resource.result()
                if result.provisioning_state == ProvisioningState.succeeded:
                    break
            except Exception as ex:
                if i == retries - 1:
                    raise
                time.sleep(3)
            time.sleep(3)

        # note the for/else here: will raise an error if we *don't* break
        # above i.e. if result.provisioning state was never "Succeeded"
        else:
            raise AzureTestError("Could not create a search service")

        api_key = self.mgmt_client.admin_keys.get(
            group_name, TEST_SERVICE_NAME
        ).primary_key

        # optionally create an index in the service
        if self.schema:
            response = requests.post(
                SERVICE_URL,
                headers={"Content-Type": "application/json", "api-key": api_key},
                data=self.schema,
            )
            if response.status_code != 201:
                raise AzureTestError(
                    "Could not create a search index {}".format(response.status_code)
                )
            schema = json.loads(self.schema)
            self.index_name = schema["name"]

        # optionally load data into the index
        if self.schema and self.index_batch:
            from azure.search import SearchIndexClient, SearchApiKeyCredential
            from azure.search.index._generated.models import IndexBatch

            batch = IndexBatch.deserialize(self.index_batch)
            index_client = SearchIndexClient(
                TEST_SERVICE_NAME, self.index_name, SearchApiKeyCredential(api_key)
            )
            results = index_client.index_batch(batch)
            if not all(result.succeeded for result in results):
                raise AzureTestError("Document upload to search index failed")

        return {"api_key": api_key, "index_name": self.index_name}

    def remove_resource(self, name, **kwargs):
        if not self.is_live:
            return

        group_name = self._get_resource_group(**kwargs).name
        self.mgmt_client.services.delete(group_name, TEST_SERVICE_NAME)
