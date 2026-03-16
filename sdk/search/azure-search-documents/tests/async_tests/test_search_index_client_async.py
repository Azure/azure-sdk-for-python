# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import functools
import pytest
from unittest import mock
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import ApiVersion
from azure.search.documents.aio import SearchClient
from azure.search.documents.indexes.aio import SearchIndexClient, SearchIndexerClient
from devtools_testutils import trim_kwargs_from_test_function

CREDENTIAL = AzureKeyCredential(key="test_api_key")


def await_prepared_test(test_fn):
    """Synchronous wrapper for async test methods. Used to avoid making changes
    upstream to AbstractPreparer (which doesn't await the functions it wraps)
    """

    @functools.wraps(test_fn)
    def run(test_class_instance, *args, **kwargs):
        trim_kwargs_from_test_function(test_fn, kwargs)

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            owns_loop = True
        else:
            owns_loop = False

        try:
            return loop.run_until_complete(test_fn(test_class_instance, **kwargs))
        finally:
            if owns_loop:
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.close()
                asyncio.set_event_loop(None)

    return run
