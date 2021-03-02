from azure.core.exceptions import ResourceNotFoundError
from azure.deviceupdate import DeviceUpdateClient
from azure.deviceupdate.models import *
from devtools_testutils import AzureMgmtTestCase
from tests.test_data import *


class DevicesClientTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(DevicesClientTestCase, self).setUp()
        self.test_data = TestData()
        self.client = self.create_basic_client(
            DeviceUpdateClient,
            account_endpoint=self.test_data.account_endpoint,
            instance_id=self.test_data.instance_id)

    def test_get_all_device_classes(self):
        response = self.client.devices.get_all_device_classes()
        self.assertIsNotNone(response)
        providers = list(response)
        self.assertTrue(len(providers) > 0)

    def test_get_device_class(self):
        expected = self.test_data
        response = self.client.devices.get_device_class(expected.device_class_id)
        self.assertIsNotNone(response)
        self.assertEqual(expected.provider, response.manufacturer)
        self.assertEqual(expected.model, response.model)

    def test_get_device_class_not_found(self):
        try:
            _ = self.client.devices.get_device_class("foo")
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    def test_get_device_class_device_ids(self):
        expected = self.test_data
        response = self.client.devices.get_device_class_device_ids(expected.device_class_id)
        self.assertIsNotNone(response)
        providers = list(response)
        self.assertTrue(len(providers) > 0)

    def test_get_device_class_device_ids_not_found(self):
        try:
            response = self.client.devices.get_device_class_device_ids("foo")
            _ = list(response)
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    def test_get_device_class_installable_updates(self):
        expected = self.test_data
        response = self.client.devices.get_device_class_installable_updates(expected.device_class_id)
        self.assertIsNotNone(response)
        providers = list(response)
        self.assertTrue(len(providers) > 0)
        self.assertTrue(UpdateId(provider=expected.provider, name=expected.model, version=expected.version) in providers)

    def test_get_device_class_installable_updates_not_found(self):
        try:
            response = self.client.devices.get_device_class_installable_updates("foo")
            _ = list(response)
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    def test_get_all_devices(self):
        response = self.client.devices.get_all_devices()
        self.assertIsNotNone(response)
        providers = list(response)
        self.assertTrue(len(providers) > 0)

    def test_get_device(self):
        expected = self.test_data
        response = self.client.devices.get_device(expected.device_id)
        self.assertIsNotNone(response)
        self.assertEqual(expected.provider, response.manufacturer)
        self.assertEqual(expected.model, response.model)

    def test_get_device_not_found(self):
        try:
            _ = self.client.devices.get_device("foo")
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    def test_get_update_compliance(self):
        response = self.client.devices.get_update_compliance()
        self.assertIsNotNone(response)
        self.assertTrue(response.total_device_count > 0)

    def test_get_all_device_tags(self):
        response = self.client.devices.get_all_device_tags()
        self.assertIsNotNone(response)
        providers = list(response)
        self.assertTrue(len(providers) > 0)

    def test_get_device_tag(self):
        expected = self.test_data
        tag_name = expected.device_id
        response = self.client.devices.get_device_tag(tag_name)
        self.assertIsNotNone(response)
        self.assertEqual(tag_name, response.tag_name)

    def test_get_device_tag_not_found(self):
        try:
            _ = self.client.devices.get_device_tag("foo")
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    def test_get_all_groups(self):
        response = self.client.devices.get_all_groups()
        self.assertIsNotNone(response)
        providers = list(response)
        self.assertTrue(len(providers) > 0)

    def test_get_group(self):
        expected = self.test_data
        group_id = expected.device_id
        response = self.client.devices.get_group(group_id)
        self.assertIsNotNone(response)
        self.assertEqual(group_id, response.group_id)

    def test_get_group_not_found(self):
        try:
            _ = self.client.devices.get_group("foo")
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    def test_get_group_update_compliance(self):
        expected = self.test_data
        group_id = expected.device_id
        response = self.client.devices.get_group_update_compliance(group_id)
        self.assertIsNotNone(response)
        self.assertTrue(response.total_device_count > 0)

    def test_get_group_update_compliance_not_found(self):
        try:
            _ = self.client.devices.get_group_update_compliance("foo")
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    def test_get_group_best_updates(self):
        expected = self.test_data
        group_id = expected.device_id
        response = self.client.devices.get_group_best_updates(group_id)
        self.assertIsNotNone(response)
        updates = list(response)
        self.assertTrue(len(updates) > 0)

    def test_get_group_best_updates_not_found(self):
        try:
            response = self.client.devices.get_group_best_updates("foo")
            _ = list(response)
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)
