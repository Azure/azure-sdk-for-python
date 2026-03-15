# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from unittest import mock

import pytest
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.storage.blob import ContainerClient
from azure.storage.blob._list_blobs_helper import BlobPrefix

from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer


class TestContainerClientGapBranches(StorageRecordedTestCase):

    def _get_container_client(self, storage_account_name, storage_account_key):
        return ContainerClient(
            self.account_url(storage_account_name, "blob"),
            self.get_resource_name("container"),
            credential=storage_account_key.secret,
        )

    @BlobPreparer()
    def test_get_container_access_policy_when_generated_call_fails_propagates_processed_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        container = self._get_container_client(storage_account_name, storage_account_key)
        http_error = HttpResponseError(message="boom")
        processed_error = ResourceNotFoundError(message="processed")

        with mock.patch.object(container._client.container, "get_access_policy", side_effect=http_error):
            with mock.patch("azure.storage.blob._container_client.process_storage_error", side_effect=processed_error) as process_error:
                with pytest.raises(ResourceNotFoundError) as exc:
                    container.get_container_access_policy()

        assert exc.value is processed_error
        process_error.assert_called_once_with(http_error)

    @BlobPreparer()
    def test_list_blobs_when_prefix_kwarg_provided_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        container = self._get_container_client(storage_account_name, storage_account_key)

        with pytest.raises(ValueError) as exc:
            container.list_blobs(prefix="foo")

        assert str(exc.value) == (
            "Passing 'prefix' has no effect on filtering, "
            "please use the 'name_starts_with' parameter instead."
        )

    @BlobPreparer()
    def test_list_blob_names_when_prefix_kwarg_provided_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        container = self._get_container_client(storage_account_name, storage_account_key)

        with pytest.raises(ValueError) as exc:
            container.list_blob_names(prefix="foo")

        assert str(exc.value) == (
            "Passing 'prefix' has no effect on filtering, "
            "please use the 'name_starts_with' parameter instead."
        )

    @BlobPreparer()
    def test_walk_blobs_when_prefix_kwarg_provided_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        container = self._get_container_client(storage_account_name, storage_account_key)

        with pytest.raises(ValueError) as exc:
            container.walk_blobs(prefix="foo")

        assert str(exc.value) == (
            "Passing 'prefix' has no effect on filtering, "
            "please use the 'name_starts_with' parameter instead."
        )

    @BlobPreparer()
    def test_walk_blobs_when_include_is_string_wraps_include_in_list(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        container = self._get_container_client(storage_account_name, storage_account_key)

        result = container.walk_blobs(
            name_starts_with="alpha/",
            include="metadata",
            delimiter="/",
            results_per_page=5,
        )

        assert isinstance(result, BlobPrefix)
        assert result.prefix == "alpha/"
        assert result.delimiter == "/"
        assert result.results_per_page == 5
        assert result._args[0].keywords["include"] == ["metadata"]
