# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from os import environ
from os.path import dirname, realpath, join

import inspect
import json
import requests

from devtools_testutils import AzureTestError, EnvironmentVariableLoader

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

SERVICE_URL_FMT = "https://{}.{}/indexes?api-version=2023-11-01"
TIME_TO_SLEEP = 3
SEARCH_ENDPOINT_SUFFIX = environ.get("SEARCH_ENDPOINT_SUFFIX", "search.windows.net")

SearchEnvVarPreparer = functools.partial(
    EnvironmentVariableLoader,
    "search",
    search_service_endpoint="https://fakesearchendpoint.search.windows.net",
    search_service_api_key="fakesearchapikey",
    search_service_name="fakesearchendpoint",
    search_query_api_key="fakequeryapikey",
    search_storage_connection_string="DefaultEndpointsProtocol=https;AccountName=fakestoragecs;AccountKey=FAKE;EndpointSuffix=core.windows.net",
    search_storage_container_name="fakestoragecontainer",
)


def _load_schema(filename):
    if not filename:
        return None
    cwd = dirname(realpath(__file__))
    return open(join(cwd, filename)).read()


def _load_batch(filename):
    if not filename:
        return None
    cwd = dirname(realpath(__file__))
    try:
        return json.load(open(join(cwd, filename)))
    except UnicodeDecodeError:
        return json.load(open(join(cwd, filename), encoding="utf-8"))


def _clean_up_indexes(endpoint, api_key):
    from azure.search.documents.indexes import SearchIndexClient

    client = SearchIndexClient(endpoint, AzureKeyCredential(api_key), retry_backoff_factor=60)

    # wipe the synonym maps which seem to survive the index
    for map in client.get_synonym_maps():
        client.delete_synonym_map(map.name)

    # # wipe out any existing aliases
    # for alias in client.list_aliases():
    #     client.delete_alias(alias)

    # wipe any existing indexes
    for index in client.list_indexes():
        client.delete_index(index)


def _clean_up_indexers(endpoint, api_key):
    from azure.search.documents.indexes import SearchIndexerClient

    client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key), retry_backoff_factor=60)
    for indexer in client.get_indexers():
        client.delete_indexer(indexer)
    for datasource in client.get_data_source_connection_names():
        client.delete_data_source_connection(datasource)
    try:
        for skillset in client.get_skillset_names():
            client.delete_skillset(skillset)
    except HttpResponseError as ex:
        if "skillset related operations are not enabled in this region" in ex.message.lower():
            pass
        else:
            raise


def _set_up_index(service_name, endpoint, api_key, schema, index_batch):
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient
    from azure.search.documents._generated.models import IndexBatch

    schema = _load_schema(schema)
    index_batch = _load_batch(index_batch)
    if schema:
        index_name = json.loads(schema)["name"]
        response = requests.post(
            SERVICE_URL_FMT.format(service_name, SEARCH_ENDPOINT_SUFFIX),
            headers={"Content-Type": "application/json", "api-key": api_key},
            data=schema,
        )
        if response.status_code != 201:
            raise AzureTestError("Could not create a search index {}".format(response.status_code))

    # optionally load data into the index
    if index_batch and schema:
        batch = IndexBatch.deserialize(index_batch)
        index_client = SearchClient(endpoint, index_name, AzureKeyCredential(api_key))
        results = index_client.index_documents(batch)
        if not all(result.succeeded for result in results):
            raise AzureTestError("Document upload to search index failed")

        # Indexing is asynchronous, so if you get a 200 from the REST API, that only means that the documents are
        # persisted, not that they're searchable yet. The only way to check for searchability is to run queries,
        # and even then things are eventually consistent due to replication. In the Track 1 SDK tests, we "solved"
        # this by using a constant delay between indexing and querying.
        import time

        time.sleep(TIME_TO_SLEEP)


def _trim_kwargs_from_test_function(fn, kwargs):
    # the next function is the actual test function. the kwargs need to be trimmed so
    # that parameters which are not required will not be passed to it.
    if not getattr(fn, "__is_preparer", False):
        try:
            args, _, kw, _, _, _, _ = inspect.getfullargspec(fn)
        except AttributeError:
            args, _, kw, _ = inspect.getargspec(fn)  # pylint: disable=deprecated-method
        if kw is None:
            args = set(args)
            for key in [k for k in kwargs if k not in args]:
                del kwargs[key]


def search_decorator(*, schema, index_batch):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # set up hotels search index
            test = args[0]
            api_key = kwargs.get("search_service_api_key")
            endpoint = kwargs.get("search_service_endpoint")
            service_name = kwargs.get("search_service_name")
            if test.is_live:
                _clean_up_indexes(endpoint, api_key)
                _set_up_index(service_name, endpoint, api_key, schema, index_batch)
                _clean_up_indexers(endpoint, api_key)
            index_name = json.loads(_load_schema(schema))["name"] if schema else None
            index_batch_data = _load_batch(index_batch) if index_batch else None

            # ensure that the names in the test signatures are in the
            # bag of kwargs
            kwargs["endpoint"] = endpoint
            kwargs["api_key"] = AzureKeyCredential(api_key)
            kwargs["index_name"] = index_name
            kwargs["index_batch"] = index_batch_data

            trimmed_kwargs = {k: v for k, v in kwargs.items()}
            _trim_kwargs_from_test_function(func, trimmed_kwargs)

            return func(*args, **trimmed_kwargs)

        return wrapper

    return decorator


# FIXME: DELETE EVERYTHING AFTER THIS LINE BEFORE MERGING

from devtools_testutils import ResourceGroupPreparer, AzureMgmtPreparer
from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM
import datetime


# TODO: Remove this
class SearchResourceGroupPreparer(ResourceGroupPreparer):
    def create_resource(self, name, **kwargs):
        result = super(SearchResourceGroupPreparer, self).create_resource(name, **kwargs)
        if self.is_live and self._need_creation:
            expiry = datetime.datetime.now() + datetime.timedelta(days=1)
            resource_group_params = dict(tags={"DeleteAfter": expiry.isoformat()}, location=self.location)
            self.client.resource_groups.create_or_update(name, resource_group_params)
        return result


# TODO: Remove this
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
        self.service_name = "TEST-SERVICE-NAME"

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
        self.service_name = self.create_random_name()
        self.endpoint = "https://{}.{}".format(self.service_name, SEARCH_ENDPOINT_SUFFIX)

        if not self.is_live:
            return {
                "api_key": "api-key",
                "index_name": schema["name"] if schema else None,
                "endpoint": self.endpoint,
            }

        group_name = self._get_resource_group(**kwargs).name

        from azure.mgmt.search import SearchManagementClient
        from azure.mgmt.search.models import ProvisioningState

        self.mgmt_client = self.create_mgmt_client(SearchManagementClient)

        # create the search service
        from azure.mgmt.search.models import SearchService, Sku

        service_config = SearchService(location="West US", sku=Sku(name="basic"))
        resource = self.mgmt_client.services.begin_create_or_update(group_name, self.service_name, service_config)

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

        api_key = self.mgmt_client.admin_keys.get(group_name, self.service_name).primary_key

        if self.schema:
            response = requests.post(
                SERVICE_URL_FMT.format(self.service_name, SEARCH_ENDPOINT_SUFFIX),
                headers={"Content-Type": "application/json", "api-key": api_key},
                data=self.schema,
            )
            if response.status_code != 201:
                raise AzureTestError("Could not create a search index {}".format(response.status_code))
            self.index_name = schema["name"]

        # optionally load data into the index
        if self.index_batch and self.schema:
            from azure.core.credentials import AzureKeyCredential
            from azure.search.documents import SearchClient
            from azure.search.documents._generated.models import IndexBatch

            batch = IndexBatch.deserialize(self.index_batch)
            index_client = SearchClient(self.endpoint, self.index_name, AzureKeyCredential(api_key))
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

        group_name = self._get_resource_group(**kwargs).name
        self.mgmt_client.services.delete(group_name, self.service_name)


# FIXME: DELETE EVERYTHING AFTER THIS LINE BEFORE MERGING

from devtools_testutils import ResourceGroupPreparer, AzureMgmtPreparer
from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM
import datetime


# TODO: Remove this
class SearchResourceGroupPreparer(ResourceGroupPreparer):
    def create_resource(self, name, **kwargs):
        result = super(SearchResourceGroupPreparer, self).create_resource(name, **kwargs)
        if self.is_live and self._need_creation:
            expiry = datetime.datetime.now() + datetime.timedelta(days=1)
            resource_group_params = dict(tags={"DeleteAfter": expiry.isoformat()}, location=self.location)
            self.client.resource_groups.create_or_update(name, resource_group_params)
        return result


# TODO: Remove this
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
        self.service_name = "TEST-SERVICE-NAME"

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
        self.service_name = self.create_random_name()
        self.endpoint = "https://{}.{}".format(self.service_name, SEARCH_ENDPOINT_SUFFIX)

        if not self.is_live:
            return {
                "api_key": "api-key",
                "index_name": schema["name"] if schema else None,
                "endpoint": self.endpoint,
            }

        group_name = self._get_resource_group(**kwargs).name

        from azure.mgmt.search import SearchManagementClient
        from azure.mgmt.search.models import ProvisioningState

        self.mgmt_client = self.create_mgmt_client(SearchManagementClient)

        # create the search service
        from azure.mgmt.search.models import SearchService, Sku

        service_config = SearchService(location="West US", sku=Sku(name="basic"))
        resource = self.mgmt_client.services.begin_create_or_update(group_name, self.service_name, service_config)

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

        api_key = self.mgmt_client.admin_keys.get(group_name, self.service_name).primary_key

        if self.schema:
            response = requests.post(
                SERVICE_URL_FMT.format(self.service_name, SEARCH_ENDPOINT_SUFFIX),
                headers={"Content-Type": "application/json", "api-key": api_key},
                data=self.schema,
            )
            if response.status_code != 201:
                raise AzureTestError("Could not create a search index {}".format(response.status_code))
            self.index_name = schema["name"]

        # optionally load data into the index
        if self.index_batch and self.schema:
            from azure.core.credentials import AzureKeyCredential
            from azure.search.documents import SearchClient
            from azure.search.documents._generated.models import IndexBatch

            batch = IndexBatch.deserialize(self.index_batch)
            index_client = SearchClient(self.endpoint, self.index_name, AzureKeyCredential(api_key))
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

        group_name = self._get_resource_group(**kwargs).name
        self.mgmt_client.services.delete(group_name, self.service_name)


# FIXME: DELETE EVERYTHING AFTER THIS LINE BEFORE MERGING

from devtools_testutils import ResourceGroupPreparer, AzureMgmtPreparer
from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM
import datetime


# TODO: Remove this
class SearchResourceGroupPreparer(ResourceGroupPreparer):
    def create_resource(self, name, **kwargs):
        result = super(SearchResourceGroupPreparer, self).create_resource(name, **kwargs)
        if self.is_live and self._need_creation:
            expiry = datetime.datetime.now() + datetime.timedelta(days=1)
            resource_group_params = dict(tags={"DeleteAfter": expiry.isoformat()}, location=self.location)
            self.client.resource_groups.create_or_update(name, resource_group_params)
        return result


# TODO: Remove this
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
        self.service_name = "TEST-SERVICE-NAME"

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
        self.service_name = self.create_random_name()
        self.endpoint = "https://{}.{}".format(self.service_name, SEARCH_ENDPOINT_SUFFIX)

        if not self.is_live:
            return {
                "api_key": "api-key",
                "index_name": schema["name"] if schema else None,
                "endpoint": self.endpoint,
            }

        group_name = self._get_resource_group(**kwargs).name

        from azure.mgmt.search import SearchManagementClient
        from azure.mgmt.search.models import ProvisioningState

        self.mgmt_client = self.create_mgmt_client(SearchManagementClient)

        # create the search service
        from azure.mgmt.search.models import SearchService, Sku

        service_config = SearchService(location="West US", sku=Sku(name="basic"))
        resource = self.mgmt_client.services.begin_create_or_update(group_name, self.service_name, service_config)

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

        api_key = self.mgmt_client.admin_keys.get(group_name, self.service_name).primary_key

        if self.schema:
            response = requests.post(
                SERVICE_URL_FMT.format(self.service_name, SEARCH_ENDPOINT_SUFFIX),
                headers={"Content-Type": "application/json", "api-key": api_key},
                data=self.schema,
            )
            if response.status_code != 201:
                raise AzureTestError("Could not create a search index {}".format(response.status_code))
            self.index_name = schema["name"]

        # optionally load data into the index
        if self.index_batch and self.schema:
            from azure.core.credentials import AzureKeyCredential
            from azure.search.documents import SearchClient
            from azure.search.documents._generated.models import IndexBatch

            batch = IndexBatch.deserialize(self.index_batch)
            index_client = SearchClient(self.endpoint, self.index_name, AzureKeyCredential(api_key))
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

        group_name = self._get_resource_group(**kwargs).name
        self.mgmt_client.services.delete(group_name, self.service_name)


# FIXME: DELETE EVERYTHING AFTER THIS LINE BEFORE MERGING

from devtools_testutils import ResourceGroupPreparer, AzureMgmtPreparer
from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM
import datetime


# TODO: Remove this
class SearchResourceGroupPreparer(ResourceGroupPreparer):
    def create_resource(self, name, **kwargs):
        result = super(SearchResourceGroupPreparer, self).create_resource(name, **kwargs)
        if self.is_live and self._need_creation:
            expiry = datetime.datetime.now() + datetime.timedelta(days=1)
            resource_group_params = dict(tags={"DeleteAfter": expiry.isoformat()}, location=self.location)
            self.client.resource_groups.create_or_update(name, resource_group_params)
        return result


# TODO: Remove this
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
        self.service_name = "TEST-SERVICE-NAME"

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
        self.service_name = self.create_random_name()
        self.endpoint = "https://{}.{}".format(self.service_name, SEARCH_ENDPOINT_SUFFIX)

        if not self.is_live:
            return {
                "api_key": "api-key",
                "index_name": schema["name"] if schema else None,
                "endpoint": self.endpoint,
            }

        group_name = self._get_resource_group(**kwargs).name

        from azure.mgmt.search import SearchManagementClient
        from azure.mgmt.search.models import ProvisioningState

        self.mgmt_client = self.create_mgmt_client(SearchManagementClient)

        # create the search service
        from azure.mgmt.search.models import SearchService, Sku

        service_config = SearchService(location="West US", sku=Sku(name="basic"))
        resource = self.mgmt_client.services.begin_create_or_update(group_name, self.service_name, service_config)

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

        api_key = self.mgmt_client.admin_keys.get(group_name, self.service_name).primary_key

        if self.schema:
            response = requests.post(
                SERVICE_URL_FMT.format(self.service_name, SEARCH_ENDPOINT_SUFFIX),
                headers={"Content-Type": "application/json", "api-key": api_key},
                data=self.schema,
            )
            if response.status_code != 201:
                raise AzureTestError("Could not create a search index {}".format(response.status_code))
            self.index_name = schema["name"]

        # optionally load data into the index
        if self.index_batch and self.schema:
            from azure.core.credentials import AzureKeyCredential
            from azure.search.documents import SearchClient
            from azure.search.documents._generated.models import IndexBatch

            batch = IndexBatch.deserialize(self.index_batch)
            index_client = SearchClient(self.endpoint, self.index_name, AzureKeyCredential(api_key))
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

        group_name = self._get_resource_group(**kwargs).name
        self.mgmt_client.services.delete(group_name, self.service_name)
