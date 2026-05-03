# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared live-test preparers for azure-search-documents."""

import functools
import inspect

from devtools_testutils import EnvironmentVariableLoader, get_credential

from azure.core.exceptions import HttpResponseError

FAKE_SEARCH_ENDPOINT = "https://fakesearchendpoint.search.windows.net"
FAKE_SEARCH_SERVICE_NAME = "fakesearchendpoint"
FAKE_STORAGE_CONNECTION_STRING = (
    "DefaultEndpointsProtocol=https;AccountName=fakestoragecs;AccountKey=FAKE;EndpointSuffix=core.windows.net"
)
FAKE_STORAGE_CONTAINER_NAME = "fakestoragecontainer"
SKILLSET_NOT_ENABLED_MESSAGE = "skillset related operations are not enabled in this region"

SearchEnvVarPreparer = functools.partial(
    EnvironmentVariableLoader,
    "search",
    search_service_endpoint=FAKE_SEARCH_ENDPOINT,
    search_service_name=FAKE_SEARCH_SERVICE_NAME,
    search_storage_connection_string=FAKE_STORAGE_CONNECTION_STRING,
    search_storage_container_name=FAKE_STORAGE_CONTAINER_NAME,
)


def _clean_up_indexes(endpoint, cred):
    from azure.search.documents.indexes import SearchIndexClient

    client = SearchIndexClient(endpoint, cred, retry_backoff_factor=60)
    try:
        try:
            for knowledge_base in client.list_knowledge_bases():
                client.delete_knowledge_base(knowledge_base.name)
        except HttpResponseError:
            pass

        try:
            for knowledge_source in client.list_knowledge_sources():
                client.delete_knowledge_source(knowledge_source.name)
        except HttpResponseError:
            pass

        for synonym_map in client.get_synonym_maps():
            client.delete_synonym_map(synonym_map.name)

        try:
            for alias in client.list_aliases():
                client.delete_alias(alias)
        except HttpResponseError:
            pass

        for index in client.list_indexes():
            try:
                client.delete_index(index)
            except HttpResponseError:
                pass
    finally:
        client.close()


def _clean_up_indexers(endpoint, cred):
    from azure.search.documents.indexes import SearchIndexerClient

    client = SearchIndexerClient(endpoint, cred, retry_backoff_factor=60)
    try:
        for indexer in client.get_indexers():
            client.delete_indexer(indexer)
        for data_source_name in client.get_data_source_connection_names():
            client.delete_data_source_connection(data_source_name)
        try:
            for skillset_name in client.get_skillset_names():
                client.delete_skillset(skillset_name)
        except HttpResponseError as ex:
            if SKILLSET_NOT_ENABLED_MESSAGE in ex.message.lower():
                pass
            else:
                raise
    finally:
        client.close()


def _trim_kwargs_from_test_function(fn, kwargs):
    if not getattr(fn, "__is_preparer", False):
        spec = inspect.getfullargspec(fn)
        if spec.varkw is None:
            args = set(spec.args)
            for key in [k for k in kwargs if k not in args]:
                del kwargs[key]


def search_decorator():
    def decorator(func):
        def _prepare_test(test, kwargs):
            """Common setup logic for both sync and async tests."""
            endpoint = kwargs.get("search_service_endpoint")
            if test.is_live:
                cred = get_credential()
                _clean_up_indexes(endpoint, cred)
                _clean_up_indexers(endpoint, cred)

            # ensure that the names in the test signatures are in the
            # bag of kwargs
            kwargs["endpoint"] = endpoint

            trimmed_kwargs = {k: v for k, v in kwargs.items()}
            _trim_kwargs_from_test_function(func, trimmed_kwargs)
            return trimmed_kwargs

        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                test = args[0]
                trimmed_kwargs = _prepare_test(test, kwargs)
                return await func(*args, **trimmed_kwargs)

            return async_wrapper
        else:

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                test = args[0]
                trimmed_kwargs = _prepare_test(test, kwargs)
                return func(*args, **trimmed_kwargs)

            return wrapper

    return decorator
