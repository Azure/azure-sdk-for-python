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

from devtools_testutils import AzureTestError, EnvironmentVariableLoader, get_credential

from azure.core.exceptions import HttpResponseError

SERVICE_URL_FMT = "https://{}.{}/indexes?api-version=2023-11-01"
TIME_TO_SLEEP = 3
SEARCH_ENDPOINT_SUFFIX = environ.get("SEARCH_ENDPOINT_SUFFIX", "search.windows.net")

SearchEnvVarPreparer = functools.partial(
    EnvironmentVariableLoader,
    "search",
    search_service_endpoint="https://fakesearchendpoint.search.windows.net",
    search_service_name="fakesearchendpoint",
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


def _clean_up_indexes(endpoint, cred):
    from azure.search.documents.indexes import SearchIndexClient

    client = SearchIndexClient(endpoint, cred, retry_backoff_factor=60)

    # wipe the synonym maps which seem to survive the index
    for map in client.get_synonym_maps():
        client.delete_synonym_map(map.name)
    # wipe out any existing aliases
    for alias in client.list_aliases():
        client.delete_alias(alias)

    # wipe any existing indexes
    for index in client.list_indexes():
        client.delete_index(index)


def _clean_up_indexers(endpoint, cred):
    from azure.search.documents.indexes import SearchIndexerClient

    client = SearchIndexerClient(endpoint, cred, retry_backoff_factor=60)
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


def _set_up_index(service_name, endpoint, cred, schema, index_batch):
    from azure.search.documents import SearchClient
    from azure.search.documents.indexes.models import SearchIndex
    from azure.search.documents._generated.models import IndexBatch
    from azure.search.documents.indexes import SearchIndexClient

    schema = _load_schema(schema)
    index_batch = _load_batch(index_batch)
    if schema:
        index_json = json.loads(schema)
        index_name = index_json["name"]
        index = SearchIndex.from_dict(index_json)
        index_client = SearchIndexClient(endpoint, cred, retry_backoff_factor=60)
        index_create = index_client.create_index(index)

    # optionally load data into the index
    if index_batch and schema:
        batch = IndexBatch.deserialize(index_batch)
        client = SearchClient(endpoint, index_name, cred)
        results = client.index_documents(batch)
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
            endpoint = kwargs.get("search_service_endpoint")
            service_name = kwargs.get("search_service_name")
            if test.is_live:
                cred = get_credential()
                _clean_up_indexes(endpoint, cred)
                _set_up_index(service_name, endpoint, cred, schema, index_batch)
                _clean_up_indexers(endpoint, cred)
            index_name = json.loads(_load_schema(schema))["name"] if schema else None
            index_batch_data = _load_batch(index_batch) if index_batch else None

            # ensure that the names in the test signatures are in the
            # bag of kwargs
            kwargs["endpoint"] = endpoint
            kwargs["index_name"] = index_name
            kwargs["index_batch"] = index_batch_data

            trimmed_kwargs = {k: v for k, v in kwargs.items()}
            _trim_kwargs_from_test_function(func, trimmed_kwargs)

            return func(*args, **trimmed_kwargs)

        return wrapper

    return decorator
