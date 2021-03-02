from azure.core.exceptions import ResourceNotFoundError
from azure.iot.deviceupdate import DeviceUpdateClient
from azure.iot.deviceupdate.models import *
from devtools_testutils import AzureMgmtTestCase
from tests.test_common import callback
from tests.test_data import *
import uuid


class DeploymentsClientTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(DeploymentsClientTestCase, self).setUp()
        self.test_data = TestData()
        self.client = self.create_basic_client(
            DeviceUpdateClient,
            account_endpoint=self.test_data.account_endpoint,
            instance_id=self.test_data.instance_id)

    def test_get_all_deployments(self):
        response = self.client.deployments.get_all_deployments()
        self.assertIsNotNone(response)
        providers = list(response)
        self.assertTrue(len(providers) > 0)

    def test_get_deployment(self):
        expected = self.test_data
        response = self.client.deployments.get_deployment(expected.deployment_id)
        self.assertIsNotNone(response)
        self.assertEqual(expected.deployment_id, response.deployment_id)
        self.assertEqual(DeploymentType.complete, response.deployment_type)
        self.assertEqual(DeviceGroupType.DEVICE_GROUP_DEFINITIONS, response.device_group_type)
        self.assertEqual(expected.provider, response.update_id.provider)
        self.assertEqual(expected.model, response.update_id.name)
        self.assertEqual(expected.version, response.update_id.version)

    def test_get_deployment_not_found(self):
        try:
            _ = self.client.deployments.get_deployment("foo")
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    def test_create_cancel_and_delete_deployment(self):
        # The following test works *ONLY* when run LIVE -> not recorded
        if self.is_live is not True:
            return

        expected = self.test_data
        deployment_id = uuid.uuid4().hex
        response = self.client.deployments.create_or_update_deployment(
            deployment_id=deployment_id,
            deployment=Deployment(
                deployment_id=deployment_id,
                deployment_type=DeploymentType.complete,
                start_date_time=datetime(2020, 1, 1, 0, 0, 0, 0, timezone.utc),
                device_group_type=DeviceGroupType.DEVICE_GROUP_DEFINITIONS,
                device_group_definition=[expected.device_id],
                update_id=UpdateId(provider=expected.provider, name=expected.model, version=expected.version)))
        self.assertIsNotNone(response)
        self.assertEqual(deployment_id, response.deployment_id)

        response = self.client.deployments.get_deployment(deployment_id)
        self.assertIsNotNone(response)
        self.assertEqual(deployment_id, response.deployment_id)

        response = self.client.deployments.get_deployment_status(deployment_id)
        self.assertIsNotNone(response)
        self.assertEqual(DeploymentState.ACTIVE, response.deployment_state)

        response, value, _ = self.client.deployments.cancel_deployment(deployment_id, cls=callback)
        self.assertIsNotNone(response)
        self.assertEqual(200, response.http_response.status_code)
        self.assertIsNotNone(value)
        self.assertEqual(deployment_id, value.deployment_id)
        self.assertTrue(value.is_canceled)

        response, _, _ = self.client.deployments.delete_deployment(deployment_id, cls=callback)
        self.assertIsNotNone(response)
        self.assertEqual(200, response.http_response.status_code)

        try:
            _ = self.client.deployments.get_deployment(deployment_id)
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    def test_get_deployment_status(self):
        expected = self.test_data
        response = self.client.deployments.get_deployment_status(expected.deployment_id)
        self.assertIsNotNone(response)
        self.assertEqual(DeploymentState.ACTIVE, response.deployment_state)

    def test_get_deployment_status_not_found(self):
        try:
            _ = self.client.deployments.get_deployment_status("foo")
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    def test_get_deployment_devices(self):
        expected = self.test_data
        response = self.client.deployments.get_deployment_devices(expected.deployment_id)
        self.assertIsNotNone(response)
        providers = list(response)
        self.assertTrue(len(providers) > 0)

    def test_get_deployment_devices_not_found(self):
        try:
            response = self.client.deployments.get_deployment_devices("foo")
            _ = list(response)
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)
