# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from unittest.mock import MagicMock

from azure.core.credentials import AzureNamedKeyCredential
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.storage.filedatalake import (
    AnalyticsLogging,
    CorsRule,
    DataLakeDirectoryClient,
    DataLakeFileClient,
    DataLakeServiceClient,
    FileSystemClient,
    Metrics,
    RetentionPolicy,
    StaticWebsite)

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import DataLakePreparer

# ------------------------------------------------------------------------------
TEST_FILE_SYSTEM_PREFIX = 'filesystem'
# ------------------------------------------------------------------------------


class TestDatalakeService(StorageRecordedTestCase):
    # --Helpers-----------------------------------------------------------------
    def _setup(self, account_name, account_key):
        url = self.account_url(account_name, 'dfs')
        self.dsc = DataLakeServiceClient(url, account_key)
        self.config = self.dsc._config

    def _assert_properties_default(self, prop):
        assert prop is not None
        self._assert_logging_equal(prop['analytics_logging'], AnalyticsLogging())
        self._assert_metrics_equal(prop['hour_metrics'], Metrics())
        self._assert_metrics_equal(prop['minute_metrics'], Metrics())
        self._assert_cors_equal(prop['cors'], list())

    def _assert_logging_equal(self, log1, log2):
        if log1 is None or log2 is None:
            assert log1 == log2
            return

        assert log1.version == log2.version
        assert log1.read == log2.read
        assert log1.write == log2.write
        assert log1.delete == log2.delete
        self._assert_retention_equal(log1.retention_policy, log2.retention_policy)

    def _assert_delete_retention_policy_equal(self, policy1, policy2):
        if policy1 is None or policy2 is None:
            assert policy1 == policy2
            return

        assert policy1.enabled == policy2.enabled
        assert policy1.days == policy2.days

    def _assert_static_website_equal(self, prop1, prop2):
        if prop1 is None or prop2 is None:
            assert prop1 == prop2
            return

        assert prop1.enabled == prop2.enabled
        assert prop1.index_document == prop2.index_document
        assert prop1.error_document404_path == prop2.error_document404_path
        assert prop1.default_index_document_path == prop2.default_index_document_path

    def _assert_delete_retention_policy_not_equal(self, policy1, policy2):
        if policy1 is None or policy2 is None:
            assert policy1 != policy2
            return

        assert not (policy1.enabled == policy2.enabled and policy1.days == policy2.days)

    def _assert_metrics_equal(self, metrics1, metrics2):
        if metrics1 is None or metrics2 is None:
            assert metrics1 == metrics2
            return

        assert metrics1.version == metrics2.version
        assert metrics1.enabled == metrics2.enabled
        assert metrics1.include_apis == metrics2.include_apis
        self._assert_retention_equal(metrics1.retention_policy, metrics2.retention_policy)

    def _assert_cors_equal(self, cors1, cors2):
        if cors1 is None or cors2 is None:
            assert cors1 == cors2
            return

        assert len(cors1) == len(cors2)

        for i in range(0, len(cors1)):
            rule1 = cors1[i]
            rule2 = cors2[i]
            assert len(rule1.allowed_origins) == len(rule2.allowed_origins)
            assert len(rule1.allowed_methods) == len(rule2.allowed_methods)
            assert rule1.max_age_in_seconds == rule2.max_age_in_seconds
            assert len(rule1.exposed_headers) == len(rule2.exposed_headers)
            assert len(rule1.allowed_headers) == len(rule2.allowed_headers)

    def _assert_retention_equal(self, ret1, ret2):
        assert ret1.enabled == ret2.enabled
        assert ret1.days == ret2.days

    # --Test cases per service ---------------------------------------
    @DataLakePreparer()
    @recorded_by_proxy
    def test_datalake_service_properties(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        # Act
        resp = self.dsc.set_service_properties(
            analytics_logging=AnalyticsLogging(),
            hour_metrics=Metrics(),
            minute_metrics=Metrics(),
            cors=list(),
            target_version='2014-02-14'
        )

        # Assert
        assert resp is None
        props = self.dsc.get_service_properties()
        self._assert_properties_default(props)
        assert '2014-02-14' == props['target_version']

    @DataLakePreparer()
    @recorded_by_proxy
    def test_empty_set_service_properties_exception(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        with pytest.raises(ValueError):
            self.dsc.set_service_properties()

    @DataLakePreparer()
    @recorded_by_proxy
    def test_set_default_service_version(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        # Act
        self.dsc.set_service_properties(target_version='2014-02-14')

        # Assert
        received_props = self.dsc.get_service_properties()
        assert received_props['target_version'] == '2014-02-14'

    @DataLakePreparer()
    @recorded_by_proxy
    def test_set_delete_retention_policy(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        delete_retention_policy = RetentionPolicy(enabled=True, days=2)

        # Act
        self.dsc.set_service_properties(delete_retention_policy=delete_retention_policy)

        # Assert
        received_props = self.dsc.get_service_properties()
        self._assert_delete_retention_policy_equal(received_props['delete_retention_policy'], delete_retention_policy)

    @DataLakePreparer()
    @recorded_by_proxy
    def test_set_delete_retention_policy_edge_cases(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        delete_retention_policy = RetentionPolicy(enabled=True, days=1)
        self.dsc.set_service_properties(delete_retention_policy=delete_retention_policy)

        # Assert
        received_props = self.dsc.get_service_properties()
        self._assert_delete_retention_policy_equal(received_props['delete_retention_policy'], delete_retention_policy)

        # Should work with maximum settings
        delete_retention_policy = RetentionPolicy(enabled=True, days=365)
        self.dsc.set_service_properties(delete_retention_policy=delete_retention_policy)

        # Assert
        received_props = self.dsc.get_service_properties()
        self._assert_delete_retention_policy_equal(received_props['delete_retention_policy'], delete_retention_policy)

        # Should not work with 0 days
        delete_retention_policy = RetentionPolicy(enabled=True, days=0)

        with pytest.raises(HttpResponseError):
            self.dsc.set_service_properties(delete_retention_policy=delete_retention_policy)

        # Assert
        received_props = self.dsc.get_service_properties()
        self._assert_delete_retention_policy_not_equal(
            received_props['delete_retention_policy'], delete_retention_policy)

        # Should not work with 366 days
        delete_retention_policy = RetentionPolicy(enabled=True, days=366)

        with pytest.raises(HttpResponseError):
            self.dsc.set_service_properties(delete_retention_policy=delete_retention_policy)

        # Assert
        received_props = self.dsc.get_service_properties()
        self._assert_delete_retention_policy_not_equal(
            received_props['delete_retention_policy'], delete_retention_policy)

    @DataLakePreparer()
    @recorded_by_proxy
    def test_set_static_website_properties(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        static_website = StaticWebsite(
            enabled=True,
            index_document="index.html",
            error_document404_path="errors/error/404error.html")

        # Act
        self.dsc.set_service_properties(static_website=static_website)

        # Assert
        received_props = self.dsc.get_service_properties()
        self._assert_static_website_equal(received_props['static_website'], static_website)

    @DataLakePreparer()
    @recorded_by_proxy
    def test_disabled_static_website_properties(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        static_website = StaticWebsite(enabled=False, index_document="index.html",
                                       error_document404_path="errors/error/404error.html")

        # Act
        self.dsc.set_service_properties(static_website=static_website)

        # Assert
        received_props = self.dsc.get_service_properties()
        self._assert_static_website_equal(received_props['static_website'], StaticWebsite(enabled=False))

    @DataLakePreparer()
    @recorded_by_proxy
    def test_set_static_website_props_dont_impact_other_props(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        cors_rule1 = CorsRule(['www.xyz.com'], ['GET'])

        allowed_origins = ['www.xyz.com', "www.ab.com", "www.bc.com"]
        allowed_methods = ['GET', 'PUT']
        max_age_in_seconds = 500
        exposed_headers = ["x-ms-meta-data*", "x-ms-meta-source*", "x-ms-meta-abc", "x-ms-meta-bcd"]
        allowed_headers = ["x-ms-meta-data*", "x-ms-meta-target*", "x-ms-meta-xyz", "x-ms-meta-foo"]
        cors_rule2 = CorsRule(
            allowed_origins,
            allowed_methods,
            max_age_in_seconds=max_age_in_seconds,
            exposed_headers=exposed_headers,
            allowed_headers=allowed_headers)

        cors = [cors_rule1, cors_rule2]

        # Act to set cors
        self.dsc.set_service_properties(cors=cors)

        # Assert cors is updated
        received_props = self.dsc.get_service_properties()
        self._assert_cors_equal(received_props['cors'], cors)

        # Arrange to set static website properties
        static_website = StaticWebsite(enabled=True, index_document="index.html",
                                       error_document404_path="errors/error/404error.html")

        # Act to set static website
        self.dsc.set_service_properties(static_website=static_website)

        # Assert static website was updated was cors was unchanged
        received_props = self.dsc.get_service_properties()
        self._assert_static_website_equal(received_props['static_website'], static_website)
        self._assert_cors_equal(received_props['cors'], cors)

    @DataLakePreparer()
    @recorded_by_proxy
    def test_set_logging(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        logging = AnalyticsLogging(read=True, write=True, delete=True,
                                   retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        self.dsc.set_service_properties(analytics_logging=logging)

        # Assert
        received_props = self.dsc.get_service_properties()
        self._assert_logging_equal(received_props['analytics_logging'], logging)

    @DataLakePreparer()
    @recorded_by_proxy
    def test_set_hour_metrics(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        hour_metrics = Metrics(
            include_apis=False, enabled=True, retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        self.dsc.set_service_properties(hour_metrics=hour_metrics)

        # Assert
        received_props = self.dsc.get_service_properties()
        self._assert_metrics_equal(received_props['hour_metrics'], hour_metrics)

    @DataLakePreparer()
    @recorded_by_proxy
    def test_set_minute_metrics(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        minute_metrics = Metrics(enabled=True, include_apis=True,
                                 retention_policy=RetentionPolicy(enabled=True, days=5))

        # Act
        self.dsc.set_service_properties(minute_metrics=minute_metrics)

        # Assert
        received_props = self.dsc.get_service_properties()
        self._assert_metrics_equal(received_props['minute_metrics'], minute_metrics)

    @DataLakePreparer()
    @recorded_by_proxy
    def test_set_cors(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        cors_rule1 = CorsRule(['www.xyz.com'], ['GET'])

        allowed_origins = ['www.xyz.com', "www.ab.com", "www.bc.com"]
        allowed_methods = ['GET', 'PUT']
        max_age_in_seconds = 500
        exposed_headers = ["x-ms-meta-data*", "x-ms-meta-source*", "x-ms-meta-abc", "x-ms-meta-bcd"]
        allowed_headers = ["x-ms-meta-data*", "x-ms-meta-target*", "x-ms-meta-xyz", "x-ms-meta-foo"]
        cors_rule2 = CorsRule(
            allowed_origins,
            allowed_methods,
            max_age_in_seconds=max_age_in_seconds,
            exposed_headers=exposed_headers,
            allowed_headers=allowed_headers)

        cors = [cors_rule1, cors_rule2]

        # Act
        self.dsc.set_service_properties(cors=cors)

        # Assert
        received_props = self.dsc.get_service_properties()
        self._assert_cors_equal(received_props['cors'], cors)

    @DataLakePreparer()
    def test_connectionstring_without_secondary(self):
        test_conn_str = "DefaultEndpointsProtocol=https;AccountName=foo;AccountKey=bar"
        client = DataLakeServiceClient.from_connection_string(test_conn_str)
        assert client.url == 'https://foo.dfs.core.windows.net/'
        assert client.primary_hostname == 'foo.dfs.core.windows.net'
        assert not client.secondary_hostname

        client = FileSystemClient.from_connection_string(test_conn_str, "fsname")
        assert client.url == 'https://foo.dfs.core.windows.net/fsname'
        assert client.primary_hostname == 'foo.dfs.core.windows.net'
        assert not client.secondary_hostname

        client = DataLakeFileClient.from_connection_string(test_conn_str, "fsname", "fpath")
        assert client.url == 'https://foo.dfs.core.windows.net/fsname/fpath'
        assert client.primary_hostname == 'foo.dfs.core.windows.net'
        assert not client.secondary_hostname

        client = DataLakeDirectoryClient.from_connection_string(test_conn_str, "fsname", "dname")
        assert client.url == 'https://foo.dfs.core.windows.net/fsname/dname'
        assert client.primary_hostname == 'foo.dfs.core.windows.net'
        assert not client.secondary_hostname

    @DataLakePreparer()
    @recorded_by_proxy
    def test_azure_named_key_credential_access(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        named_key = AzureNamedKeyCredential(datalake_storage_account_name, datalake_storage_account_key)
        dsc = DataLakeServiceClient(self.account_url(datalake_storage_account_name, "blob"), named_key)

        # Act
        props = dsc.get_service_properties()

        # Assert
        assert props is not None

    @DataLakePreparer()
    def test_datalake_clients_properly_close(self, **kwargs):
        account_name = "adlsstorage"
        account_key = "adlskey"

        self._setup(account_name, account_key)
        file_system_client = self.dsc.get_file_system_client(file_system='testfs')
        dir_client = self.dsc.get_directory_client(file_system='testfs', directory='testdir')
        file_client = dir_client.get_file_client(file='testfile')

        # Mocks
        self.dsc._blob_service_client.close = MagicMock()
        self.dsc._client.__exit__ = MagicMock()
        file_system_client._client.__exit__ = MagicMock()
        file_system_client._datalake_client_for_blob_operation.close = MagicMock()
        dir_client._client.__exit__ = MagicMock()
        dir_client._datalake_client_for_blob_operation.close = MagicMock()
        file_client._client.__exit__ = MagicMock()
        file_client._datalake_client_for_blob_operation.close = MagicMock()

        # Act
        with self.dsc as dsc:
            pass
            with file_system_client as fsc:
                pass
                with dir_client as dc:
                    pass
                    with file_client as fc:
                        pass

        # Assert
        self.dsc._blob_service_client.close.assert_called_once()
        self.dsc._client.__exit__.assert_called_once()
        file_system_client._client.__exit__.assert_called_once()
        file_system_client._datalake_client_for_blob_operation.close.assert_called_once()
        dir_client._client.__exit__.assert_called_once()
        dir_client._datalake_client_for_blob_operation.close.assert_called_once()
        file_client._client.__exit__.assert_called_once()
        file_client._datalake_client_for_blob_operation.close.assert_called_once()

    @DataLakePreparer()
    @recorded_by_proxy
    def test_storage_account_audience_service_client(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        self.dsc.create_file_system('testfs1')

        # Act
        token_credential = self.get_credential(DataLakeServiceClient)
        dsc = DataLakeServiceClient(
            self.account_url(datalake_storage_account_name, "blob"),
            credential=token_credential,
            audience=f'https://{datalake_storage_account_name}.blob.core.windows.net/'
        )

        # Assert
        response1 = dsc.list_file_systems()
        response2 = dsc.create_file_system('testfs11')
        assert response1 is not None
        assert response2 is not None

    @DataLakePreparer()
    @recorded_by_proxy
    def test_bad_audience_service_client(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        self.dsc.create_file_system('testfs2')

        # Act
        token_credential = self.get_credential(DataLakeServiceClient)
        dsc = DataLakeServiceClient(
            self.account_url(datalake_storage_account_name, "blob"),
            credential=token_credential,
            audience=f'https://badaudience.blob.core.windows.net/'
        )

        # Will not raise ClientAuthenticationError despite bad audience due to Bearer Challenge
        dsc.list_file_systems()
        dsc.create_file_system('testfs22')
