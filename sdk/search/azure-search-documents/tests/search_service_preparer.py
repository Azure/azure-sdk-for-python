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

from devtools_testutils import AzureMgmtPreparer, AzureMgmtTestCase, FakeResource, ResourceGroupPreparer
from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM
from azure_devtools.scenario_tests.exceptions import AzureTestError

CREATE_INDEX_URL_FMT = "https://{}.search.windows.net/indexes?api-version=2019-05-06"
DELETE_INDEX_URL_FMT = "https://{}.search.windows.net/indexes/{}?api-version=2019-05-06"
TIME_TO_SLEEP = 3


class GlobalResourceGroupPreparer(AzureMgmtPreparer):

    GLOBAL_GROUP = None
    _preparer = ResourceGroupPreparer(random_name_enabled=True, name_prefix='pysearchdoc')

    def __init__(self):
        super(GlobalResourceGroupPreparer, self).__init__(
            name_prefix='',
            random_name_length=42
        )

    def create_resource(self, name, **kwargs):
        if GlobalResourceGroupPreparer.GLOBAL_GROUP is None:
            if self.is_live:
                test_case = AzureMgmtTestCase("__init__")
                rg_name, rg_kwargs = self._preparer._prepare_create_resource(test_case)
                GlobalResourceGroupPreparer.GLOBAL_GROUP = rg_kwargs['resource_group']
                self.test_class_instance.scrubber.register_name_pair(
                    GlobalResourceGroupPreparer.GLOBAL_GROUP.name,
                    "rgname"
                )
            else:
                GlobalResourceGroupPreparer.GLOBAL_GROUP = FakeResource(
                    name="rgname",
                    id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rgname"
                )

        return {
            'location': 'westus',
            'resource_group': GlobalResourceGroupPreparer.GLOBAL_GROUP,
        }

class SearchServicePreparer(AzureMgmtPreparer):

    endpoint = None
    service_name = None
    mgmt_client = None

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
        if self.schema:
            schema = json.loads(self.schema)
        else:
            schema = None

        if SearchServicePreparer.endpoint is None:

            service_name = self.create_random_name()
            endpoint = "https://{}.search.windows.net".format(service_name)

            SearchServicePreparer.service_name = service_name
            SearchServicePreparer.endpoint = endpoint

            if not self.is_live:
                return {
                    "api_key": "api-key",
                    "index_name": schema["name"] if schema else None,
                    "endpoint": endpoint,
                }

            group_name = self._get_resource_group(**kwargs).name

            from azure.mgmt.search import SearchManagementClient
            from azure.mgmt.search.models import ProvisioningState

            SearchServicePreparer.mgmt_client = self.create_mgmt_client(SearchManagementClient)

            # create the search service
            from azure.mgmt.search.models import SearchService, Sku

            service_config = SearchService(location="West US", sku=Sku(name="free"))
            resource = self.mgmt_client.services.create_or_update(
                group_name, self.service_name, service_config
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
                    time.sleep(TIME_TO_SLEEP)
                time.sleep(TIME_TO_SLEEP)

            # note the for/else here: will raise an error if we *don't* break
            # above i.e. if result.provisioning state was never "Succeeded"
            else:
                raise AzureTestError("Could not create a search service")

        if not self.is_live:
            return {
                "api_key": "api-key",
                "index_name": schema["name"] if schema else None,
                "endpoint": self.endpoint,
            }

        group_name = self._get_resource_group(**kwargs).name

        api_key = self.mgmt_client.admin_keys.get(
            group_name, self.service_name
        ).primary_key

        if self.schema:
            response = requests.post(
                CREATE_INDEX_URL_FMT.format(self.service_name),
                headers={"Content-Type": "application/json", "api-key": api_key},
                data=self.schema,
            )
            if response.status_code != 201:
                raise AzureTestError(
                    "Could not create a search index {}".format(response.status_code)
                )
            self.index_name = schema["name"]

        # optionally load data into the index
        if self.index_batch and self.schema:
            from azure.core.credentials import AzureKeyCredential
            from azure.search.documents import SearchIndexClient
            from azure.search.documents._index._generated.models import IndexBatch

            batch = IndexBatch.deserialize(self.index_batch)
            index_client = SearchIndexClient(
                self.endpoint, self.index_name, AzureKeyCredential(api_key)
            )
            results = index_client.index_documents(batch)
            if not all(result.succeeded for result in results):
                raise AzureTestError("Document upload to search index failed")

            # Indexing is asynchronous, so if you get a 200 from the REST API, that only means that the documents are
            # persisted, not that they're searchable yet. The only way to check for searchability is to run queries,
            # and even then things are eventually consistent due to replication. In the Track 1 SDK tests, we "solved"
            # this by using a constant delay between indexing and querying.
            import time

            time.sleep(TIME_TO_SLEEP)

        return {
            "api_key": api_key,
            "index_name": self.index_name,
            "endpoint": self.endpoint,
        }

    def remove_resource(self, name, **kwargs):
        if not self.is_live:
            return

        if self.schema:
            group_name = self._get_resource_group(**kwargs).name
            api_key = self.mgmt_client.admin_keys.get(
                group_name, self.service_name
            ).primary_key
            response = requests.delete(
                DELETE_INDEX_URL_FMT.format(self.service_name, self.index_name),
                headers={"Content-Type": "application/json", "api-key": api_key},
            )
            if response.status_code != 204:
                raise AzureTestError(
                    "Could not delete a search index {}".format(response.status_code)
                )
