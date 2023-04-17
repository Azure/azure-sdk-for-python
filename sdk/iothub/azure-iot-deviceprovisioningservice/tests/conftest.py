import functools
import os

import pytest
import responses
from azure.iot.deviceprovisioningservice import ProvisioningServiceClient
from azure.iot.deviceprovisioningservice._auth import SharedKeyCredentialPolicy
from devtools_testutils import (
    add_body_key_sanitizer,
    EnvironmentVariableLoader,
    add_general_regex_sanitizer,
    add_header_regex_sanitizer,
    test_proxy,
)


from urllib3.util.retry import Retry


# cSpell:disable
mock_dps_target = {}
mock_dps_target["cs"] = "HostName=mydps;SharedAccessKeyName=name;SharedAccessKey=value"
mock_dps_target["entity"] = "mydps.azure-devices-provisioning.net"
mock_dps_target["primarykey"] = "fakekeyfakekeyfakekeyfakekeyfakekeyfakekeyA="
mock_dps_target["secondarykey"] = "fakekeyfakekeyfakekeyfakekeyfakekeyfakekeyA="
mock_dps_target["policy"] = "provisioningserviceowner"
mock_dps_target["subscription"] = "5952cff8-bcd1-4235-9554-af2c0348bf23"
mock_dps_target["endpoint"] = "https://{}".format(mock_dps_target["entity"])
generic_cs_template = "HostName={};SharedAccessKeyName={};SharedAccessKey={}"

GLOBAL_PROVISIONING_HOST = "global.azure-devices-provisioning.net"
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


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    subscription_id = os.environ.get(
        "AZURE_SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000"
    )
    tenant_id = os.environ.get(
        "AZURE_TENANT_ID", "00000000-0000-0000-0000-000000000000"
    )
    client_id = os.environ.get(
        "AZURE_CLIENT_ID", "00000000-0000-0000-0000-000000000000"
    )
    client_secret = os.environ.get(
        "AZURE_CLIENT_SECRET", "00000000-0000-0000-0000-000000000000"
    )
    add_general_regex_sanitizer(
        regex=subscription_id, value="00000000-0000-0000-0000-000000000000"
    )
    add_general_regex_sanitizer(
        regex=tenant_id, value="00000000-0000-0000-0000-000000000000"
    )
    add_general_regex_sanitizer(
        regex=client_id, value="00000000-0000-0000-0000-000000000000"
    )
    add_general_regex_sanitizer(
        regex=client_secret, value="00000000-0000-0000-0000-000000000000"
    )
    add_general_regex_sanitizer(
        regex=r"-----BEGIN CERTIFICATE-----.*-----END CERTIFICATE-----",
        value="certificate",
    )
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")
    add_header_regex_sanitizer(key="Cookie", value="cookie;")
    add_body_key_sanitizer(json_path="$..access_token", value="access_token")
    add_body_key_sanitizer(json_path="$..primaryKey", value="primaryKey")
    add_body_key_sanitizer(json_path="$..secondaryKey", value="secondaryKey")
    add_body_key_sanitizer(json_path="$..sha256Thumbprint", value="thumbprint")
    add_body_key_sanitizer(json_path="$..sha1Thumbprint", value="thumbprint")
    return


@pytest.fixture
def mocked_response():
    with responses.RequestsMock() as mock:
        on_request_with_no_retry = functools.partial(
            mock._on_request,
            retries=Retry(
                0,
                read=False,
            ),
        )
        mock._on_request = on_request_with_no_retry
        yield mock


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


ProvisioningServicePreparer = functools.partial(
    EnvironmentVariableLoader,
    "iothub",
    iothub_dps_endpoint="fake-resource.azure-devices-provisioning.net",
    iothub_dps_conn_str="HostName=mydps;SharedAccessKeyName=name;SharedAccessKey=value",
    iothub_dps_idscope="IDSCOPE",
)
