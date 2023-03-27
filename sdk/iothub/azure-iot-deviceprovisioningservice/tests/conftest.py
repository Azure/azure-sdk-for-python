from functools import partial

import pytest
import responses
from azure.iot.deviceprovisioningservice import ProvisioningServiceClient
from azure.iot.deviceprovisioningservice.auth import SharedKeyCredentialPolicy
from urllib3.util.retry import Retry

# TODO - Tests
#   1. Create DPS before running test if connection string is not given
#   2. Convert DPS creation / cleanup to setup/teardown fixtures
#   3. Figure out automated IoT Hub linkage for device registration tests


mock_dps_target = {}
mock_dps_target["cs"] = "HostName=mydps;SharedAccessKeyName=name;SharedAccessKey=value"
mock_dps_target["entity"] = "mydps.azure-devices-provisioning.net"
mock_dps_target["primarykey"] = "rJx/6rJ6rmG4ak890+eW5MYGH+A0uzRvjGNjg3Ve8sfo="
mock_dps_target["secondarykey"] = "aCd/6rJ6rmG4ak890+eW5MYGH+A0uzRvjGNjg3Ve8sfo="
mock_dps_target["policy"] = "provisioningserviceowner"
mock_dps_target["subscription"] = "5952cff8-bcd1-4235-9554-af2c0348bf23"
mock_dps_target["endpoint"] = "https://{}".format(mock_dps_target["entity"])
generic_cs_template = "HostName={};SharedAccessKeyName={};SharedAccessKey={}"

IOTDPS_PROVISIONING_HOST = "global.azure-devices-provisioning.net"
WEBHOOK_URL = "https://www.test.test"
TEST_ENDORSEMENT_KEY = (
    "AToAAQALAAMAsgAgg3GXZ0SEs/gakMyNRqXXJP1S124GUgtk8qHaGzMUaaoABgCAAEMAEAgAAAAAAAEAibym9HQP9vxCGF5dVc1Q"
    "QsAGe021aUGJzNol1/gycBx3jFsTpwmWbISRwnFvflWd0w2Mc44FAAZNaJOAAxwZvG8GvyLlHh6fGKdh+mSBL4iLH2bZ4Ry22cB3"
    "CJVjXmdGoz9Y/j3/NwLndBxQC+baNvzvyVQZ4/A2YL7vzIIj2ik4y+ve9ir7U0GbNdnxskqK1KFIITVVtkTIYyyFTIR0BySjPrRI"
    "Dj7r7Mh5uF9HBppGKQCBoVSVV8dI91lNazmSdpGWyqCkO7iM4VvUMv2HT/ym53aYlUrau+Qq87Tu+uQipWYgRdF11KDfcpMHqqzB"
    "QQ1NpOJVhrsTrhyJzO7KNw=="
)
API_VERSION = "2019-03-31"
CUSTOM_ALLOCATION = {"webhookUrl": WEBHOOK_URL, "apiVersion": API_VERSION}
TEST_DICT = {"hello": "world"}
DEVICE_INFO = {"additionalProperties": TEST_DICT}
CERT_FOLDER = "./test_certs"
# reprovision policy models
REPROVISION_MIGRATE = {"migrateDeviceData": True, "updateHubAssignment": True}

REPROVISION_RESET = {"migrateDeviceData": False, "updateHubAssignment": True}

REPROVISION_NEVER = {"migrateDeviceData": False, "updateHubAssignment": False}


@pytest.fixture
def mocked_response():
    with responses.RequestsMock() as rsps:
        on_request_with_no_retry = partial(
            rsps._on_request,
            retries=Retry(
                0,
                read=False,
            ),
        )
        rsps._on_request = on_request_with_no_retry
        yield rsps


@pytest.fixture
def sdk_client() -> ProvisioningServiceClient:
    host_name, policy_name, key = (
        mock_dps_target["entity"],
        mock_dps_target["policy"],
        mock_dps_target["primarykey"],
    )
    creds = SharedKeyCredentialPolicy(host_name, policy_name, key)
    client = ProvisioningServiceClient(
        endpoint=f"https://{host_name}", credential=creds, authentication_policy=creds
    )
    return client
