# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Execute the data-plane definitions supplied by the Bicep deployment script."""

import json
import logging
import os
import re
import time
from urllib.parse import urlsplit

from azure.core.exceptions import AzureError, HttpResponseError
from azure.core.pipeline.policies import RetryPolicy
from azure.identity import AzureCliCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchIndexer,
    SearchIndexerDataSourceConnection,
    SearchIndexerSkillset,
)
from azure.storage.blob import BlobServiceClient, ContentSettings

SEARCH_API_VERSION = "2026-04-01"
WAIT_LIMIT = 600
POLL_INTERVAL = 10
CLIENT_OPTIONS = {
    "permit_redirects": False,
    "connection_timeout": 10,
    "read_timeout": 60,
}


class ThrottlingRetryPolicy(RetryPolicy):
    """Retry only HTTP 429 within the time budget for the request."""

    def __init__(self):
        retry_limit = WAIT_LIMIT // POLL_INTERVAL
        super().__init__(
            retry_total=retry_limit, retry_status=retry_limit, retry_connect=0, retry_read=0, timeout=WAIT_LIMIT
        )

    def configure_retries(self, options):
        settings = super().configure_retries(options)
        settings["deadline"] = time.monotonic() + settings["timeout"]
        return settings

    def is_retry(self, settings, response):
        return response.http_response.status_code == 429 and time.monotonic() + POLL_INTERVAL < settings["deadline"]

    def sleep(self, settings, transport, response=None):
        print("HTTP 429: Azure service throttled the request; retrying.")
        transport.sleep(POLL_INTERVAL)


def validate_endpoint(endpoint, suffix):
    parsed = urlsplit(endpoint)
    if (
        parsed.scheme != "https"
        or not re.fullmatch(r"[a-z0-9][a-z0-9-]*" + re.escape(suffix), parsed.hostname or "")
        or parsed.username is not None
        or parsed.port not in (None, 443)
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Data-plane endpoint does not match its public Azure token audience.")


def wait_for_indexer(client, name):
    deadline = time.monotonic() + WAIT_LIMIT
    while (remaining := deadline - time.monotonic()) > 0:
        status = client.get_indexer_status(name, timeout=remaining)
        result = status.last_result
        if result is not None:
            state = result.status
            if state == "success":
                if result.failed_item_count or result.errors or result.warnings:
                    raise RuntimeError(f"Indexer '{name}' completed with document failures or enrichment warnings.")
                if not result.item_count or result.item_count < 1:
                    raise RuntimeError(f"Indexer '{name}' completed without processing any documents.")
                print(f"Indexer '{name}' succeeded and processed {result.item_count} documents.")
                return
            if state not in ("inProgress", "reset"):
                raise RuntimeError(f"Indexer '{name}' failed with status '{state}'; result details suppressed.")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(POLL_INTERVAL, remaining))
    raise TimeoutError(f"Indexer '{name}' did not finish within ten minutes.")


def upload_document(container, name, content):
    deadline = time.monotonic() + WAIT_LIMIT
    while True:
        try:
            container.upload_blob(
                name,
                content,
                overwrite=True,
                content_settings=ContentSettings(content_type="text/plain; charset=utf-8"),
            )
            return
        except HttpResponseError as error:
            if error.status_code != 429 or time.monotonic() + POLL_INTERVAL >= deadline:
                raise
            print("HTTP 429: Azure Storage throttled the upload; retrying.")
            time.sleep(POLL_INTERVAL)


def provision(configuration, credential):
    search_endpoint = configuration["searchEndpoint"]
    storage_endpoint = configuration["storageEndpoint"]
    validate_endpoint(search_endpoint, ".search.windows.net")
    validate_endpoint(storage_endpoint, ".blob.core.windows.net")

    index = SearchIndex(configuration["index"])
    search_options = {**CLIENT_OPTIONS, "retry_policy": ThrottlingRetryPolicy(), "api_version": SEARCH_API_VERSION}
    # Blob Storage uses a separate SDK retry pipeline; upload_document handles its 429s.
    with (
        BlobServiceClient(storage_endpoint, credential, retry_total=0, **CLIENT_OPTIONS) as storage,
        SearchIndexClient(search_endpoint, credential, **search_options) as indexes,
        SearchIndexerClient(search_endpoint, credential, **search_options) as indexers,
        SearchClient(search_endpoint, index.name, credential, **search_options) as search,
    ):
        container = storage.get_container_client(configuration["containerName"])
        for blob in configuration["blobs"]:
            upload_document(container, blob["name"], blob["content"].encode("utf-8"))
            print(f"Uploaded indexing document '{blob['name']}'.")
        indexes.create_or_update_index(index)
        indexers.create_or_update_data_source_connection(
            SearchIndexerDataSourceConnection(configuration["datasource"]),
        )
        indexers.create_or_update_skillset(
            SearchIndexerSkillset(configuration["skillset"]),
        )
        for definition in configuration["indexers"]:
            indexer = SearchIndexer(definition)
            indexers.create_or_update_indexer(indexer)
            # Fresh indexers start automatically; resetting or running them would race that execution.
            wait_for_indexer(indexers, indexer.name)

        document = next(iter(search.search("*", top=1, select=["chunk"])), None)
        if not document or not document.get("chunk"):
            raise RuntimeError("Search index is empty or has no searchable document content.")
        print("Azure AI Search index is populated and searchable.")


def main():
    # ARM signs Azure CLI in as the deployment script's assigned identity before running this code.
    identity_loggers = [
        logging.getLogger("azure.identity._internal.decorators"),
        logging.getLogger("azure.identity._credentials.azure_cli"),
    ]
    previous_states = [logger.disabled for logger in identity_loggers]
    try:
        # Identity logs raw CLI diagnostics before raising; report only the sanitized error below.
        for logger in identity_loggers:
            logger.disabled = True
        provision(json.loads(os.environ["SEARCH_INDEXING_CONFIGURATION"]), AzureCliCredential())
    except AzureError as error:
        if isinstance(error, HttpResponseError) and error.status_code is not None:
            raise RuntimeError(
                f"Search provisioning failed with HTTP {error.status_code}; response body suppressed."
            ) from None
        raise RuntimeError(f"Search provisioning failed ({type(error).__name__}); details suppressed.") from None
    finally:
        for logger, disabled in zip(identity_loggers, previous_states):
            logger.disabled = disabled


if __name__ == "__main__":
    main()
