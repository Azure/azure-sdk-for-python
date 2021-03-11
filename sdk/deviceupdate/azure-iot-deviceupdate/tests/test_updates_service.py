# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.iot.deviceupdate import DeviceUpdateClient
from azure.iot.deviceupdate.models import *
from testcase import DeviceUpdateTest, DeviceUpdatePowerShellPreparer, callback


class UpdatesClientTestCase(DeviceUpdateTest):
    @DeviceUpdatePowerShellPreparer()
    def test_import_update(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        manifest = ImportManifestMetadata(
                url="https://adutest.blob.core.windows.net/test/Ak1xigPLmur511bYfCvzeC?sv=2019-02-02&sr=b&sig=L9RZxCUwduStz0m1cj4YnXt6OJCvWSe9SPseum3cclE%3D&se=2020-05-08T20%3A52%3A51Z&sp=r",
                size_in_bytes=453,
                hashes={"SHA256":"Ak1xigPLmur511bYfCvzeCwF6r/QxiBKeEDHOvHPzr4="})
        content = ImportUpdateInput(
            import_manifest=manifest,
            files=[FileImportMetadata(
                filename="setup.exe",
                url="https://adutest.blob.core.windows.net/test/zVknnlx1tyYSMHY28LZVzk?sv=2019-02-02&sr=b&sig=QtS6bAOcHon18wLwIt9uvHIM%2B4M27EoVPNP4RWpMjyw%3D&se=2020-05-08T20%3A52%3A51Z&sp=r")]
        )
        response, value, headers = client.updates.import_update(content, cls=callback)
        self.assertIsNotNone(response)
        self.assertEqual(202, response.http_response.status_code)
        self.assertIsNone(value)
        self.assertIsNotNone(headers)
        self.assertIsNotNone(headers['Location'])
        self.assertIsNotNone(headers['Operation-Location'])
        self.assertEqual(headers['Location'], headers['Operation-Location'])

    @DeviceUpdatePowerShellPreparer()
    def test_get_update(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
        deviceupdate_provider,
        deviceupdate_model,
        deviceupdate_version,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.updates.get_update(deviceupdate_provider, deviceupdate_model, deviceupdate_version)
        self.assertIsNotNone(response)
        self.assertEqual(deviceupdate_provider, response.update_id.provider)
        self.assertEqual(deviceupdate_model, response.update_id.name)
        self.assertEqual(deviceupdate_version, response.update_id.version)

    @DeviceUpdatePowerShellPreparer()
    def test_get_update_not_found(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        try:
            _ = client.updates.get_update("foo", "bar", "0.0.0.1")
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def test_get_providers(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.updates.get_providers()
        self.assertIsNotNone(response)
        providers = list(response)
        self.assertTrue(len(providers) > 0)

    @DeviceUpdatePowerShellPreparer()
    def test_get_names(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
        deviceupdate_provider,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.updates.get_names(deviceupdate_provider)
        self.assertIsNotNone(response)
        names = list(response)
        self.assertTrue(len(names) > 0)

    @DeviceUpdatePowerShellPreparer()
    def test_get_names_not_found(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        try:
            response = client.updates.get_names("foo")
            _ = list(response)
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def test_get_versions(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
        deviceupdate_provider,
        deviceupdate_model,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.updates.get_versions(deviceupdate_provider, deviceupdate_model)
        self.assertIsNotNone(response)
        versions = list(response)
        self.assertTrue(len(versions) > 0)

    @DeviceUpdatePowerShellPreparer()
    def test_get_versions_not_found(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        try:
            response = client.updates.get_versions("foo", "bar")
            _ = list(response)
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def test_get_files(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
        deviceupdate_provider,
        deviceupdate_model,
        deviceupdate_version,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.updates.get_files(deviceupdate_provider, deviceupdate_model, deviceupdate_version)
        self.assertIsNotNone(response)
        files = list(response)
        self.assertTrue(len(files) > 0)

    @DeviceUpdatePowerShellPreparer()
    def test_get_files_not_found(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        try:
            response = client.updates.get_files("foo", "bar", "0.0.0.1")
            _ = list(response)
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def test_get_file(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
        deviceupdate_provider,
        deviceupdate_model,
        deviceupdate_version,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.updates.get_file(deviceupdate_provider, deviceupdate_model, deviceupdate_version, "00000")
        self.assertIsNotNone(response)
        self.assertEqual("00000", response.file_id)

    @DeviceUpdatePowerShellPreparer()
    def test_get_file_not_found(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
        deviceupdate_provider,
        deviceupdate_model,
        deviceupdate_version,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        try:
            file = client.updates.get_file(deviceupdate_provider, deviceupdate_model, deviceupdate_version, "foobar")
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @pytest.mark.live_test_only
    @DeviceUpdatePowerShellPreparer()
    def test_get_operation(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
        deviceupdate_operation_id,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.updates.get_operation(deviceupdate_operation_id)
        self.assertIsNotNone(response)
        self.assertEqual(response.status, OperationStatus.succeeded)

    @DeviceUpdatePowerShellPreparer()
    def test_get_operation_not_found(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        try:
            _ = client.updates.get_operation("foo")
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def test_get_operations(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.updates.get_operations(None, 1)
        self.assertIsNotNone(response)
