from azure.core.exceptions import ResourceNotFoundError
from azure.deviceupdate import DeviceUpdateClient
from azure.deviceupdate.models import *
from devtools_testutils import AzureMgmtTestCase
from tests.test_common import callback
from tests.test_data import *


class UpdatesClientTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(UpdatesClientTestCase, self).setUp()
        self.test_data = TestData()
        self.client = self.create_basic_client(
            DeviceUpdateClient,
            account_endpoint=self.test_data.account_endpoint,
            instance_id=self.test_data.instance_id)

    def test_import_update(self):
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
        response, value, headers = self.client.updates.import_update(content, cls=callback)
        self.assertIsNotNone(response)
        self.assertEqual(202, response.http_response.status_code)
        self.assertIsNone(value)
        self.assertIsNotNone(headers)
        self.assertIsNotNone(headers['Location'])
        self.assertIsNotNone(headers['Operation-Location'])
        self.assertEqual(headers['Location'], headers['Operation-Location'])

    def test_get_update(self):
        expected = self.test_data
        response = self.client.updates.get_update(expected.provider, expected.model, expected.version)
        self.assertIsNotNone(response)
        self.assertEqual(expected.provider, response.update_id.provider)
        self.assertEqual(expected.model, response.update_id.name)
        self.assertEqual(expected.version, response.update_id.version)

    def test_get_update_not_found(self):
        try:
            _ = self.client.updates.get_update("foo", "bar", "0.0.0.1")
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    def test_get_providers(self):
        response = self.client.updates.get_providers()
        self.assertIsNotNone(response)
        providers = list(response)
        self.assertTrue(len(providers) > 0)

    def test_get_names(self):
        expected = self.test_data
        response = self.client.updates.get_names(expected.provider)
        self.assertIsNotNone(response)
        names = list(response)
        self.assertTrue(len(names) > 0)

    def test_get_names_not_found(self):
        try:
            response = self.client.updates.get_names("foo")
            _ = list(response)
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    def test_get_versions(self):
        expected = self.test_data
        response = self.client.updates.get_versions(expected.provider, expected.model)
        self.assertIsNotNone(response)
        versions = list(response)
        self.assertTrue(len(versions) > 0)

    def test_get_versions_not_found(self):
        try:
            response = self.client.updates.get_versions("foo", "bar")
            _ = list(response)
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    def test_get_files(self):
        expected = self.test_data
        response = self.client.updates.get_files(expected.provider, expected.model, expected.version)
        self.assertIsNotNone(response)
        files = list(response)
        self.assertTrue(len(files) > 0)

    def test_get_files_not_found(self):
        try:
            response = self.client.updates.get_files("foo", "bar", "0.0.0.1")
            _ = list(response)
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    def test_get_file(self):
        expected = self.test_data
        response = self.client.updates.get_file(expected.provider, expected.model, expected.version, "00000")
        self.assertIsNotNone(response)
        self.assertEqual("00000", response.file_id)

    def test_get_file_not_found(self):
        expected = self.test_data
        try:
            file = self.client.updates.get_file(expected.provider, expected.model, expected.version, "foobar")
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    def test_get_operation(self):
        response = self.client.updates.get_operation(self.test_data.operation_id)
        self.assertIsNotNone(response)
        self.assertEqual(response.status, OperationStatus.succeeded)

    def test_get_operation_not_found(self):
        try:
            _ = self.client.updates.get_operation("foo")
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    def test_get_operations(self):
        response = self.client.updates.get_operations(None, 1)
        self.assertIsNotNone(response)
