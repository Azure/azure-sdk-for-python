# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared live-test preparers for azure-search-documents."""

import functools
import inspect

from devtools_testutils import EnvironmentVariableLoader

FAKE_SEARCH_ENDPOINT = "https://fakesearchendpoint.search.windows.net"
FAKE_SEARCH_SERVICE_NAME = "fakesearchendpoint"
FAKE_STORAGE_CONNECTION_STRING = (
    "DefaultEndpointsProtocol=https;AccountName=fakestoragecs;AccountKey=FAKE;EndpointSuffix=core.windows.net"
)
FAKE_STORAGE_CONTAINER_NAME = "fakestoragecontainer"
FAKE_AZURE_OPENAI_ENDPOINT = "https://fake-openai.openai.azure.com/"
FAKE_AZURE_OPENAI_EMBEDDING_DEPLOYMENT = "text-embedding-3-small"
FAKE_AZURE_OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"

SearchEnvVarPreparer = functools.partial(
    EnvironmentVariableLoader,
    "search",
    search_service_endpoint=FAKE_SEARCH_ENDPOINT,
    search_service_name=FAKE_SEARCH_SERVICE_NAME,
    search_storage_connection_string=FAKE_STORAGE_CONNECTION_STRING,
    search_storage_container_name=FAKE_STORAGE_CONTAINER_NAME,
    search_azure_openai_endpoint=FAKE_AZURE_OPENAI_ENDPOINT,
    search_azure_openai_embedding_deployment=FAKE_AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    search_azure_openai_embedding_model=FAKE_AZURE_OPENAI_EMBEDDING_MODEL,
)


def _trim_kwargs_from_test_function(fn, kwargs):
    if not getattr(fn, "__is_preparer", False):
        spec = inspect.getfullargspec(fn)
        if spec.varkw is None:
            args = set(spec.args)
            for key in [k for k in kwargs if k not in args]:
                del kwargs[key]


def search_decorator():
    def decorator(func):
        def _prepare_test(kwargs):
            """Common setup logic for both sync and async tests."""
            endpoint = kwargs.get("search_service_endpoint")
            # ensure that the names in the test signatures are in the
            # bag of kwargs
            kwargs["endpoint"] = endpoint

            trimmed_kwargs = {k: v for k, v in kwargs.items()}
            _trim_kwargs_from_test_function(func, trimmed_kwargs)
            return trimmed_kwargs

        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                trimmed_kwargs = _prepare_test(kwargs)
                return await func(*args, **trimmed_kwargs)

            return async_wrapper
        else:

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                trimmed_kwargs = _prepare_test(kwargs)
                return func(*args, **trimmed_kwargs)

            return wrapper

    return decorator
