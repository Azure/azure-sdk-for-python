# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
import json
import os
import time

from azure.identity import (
    AzureAuthorityHosts,
    DeviceCodeCredential,
    UsernamePasswordCredential,
    InteractiveBrowserCredential,
)
from azure.identity._constants import DEVELOPER_SIGN_ON_CLIENT_ID
from azure.mgmt.resource.subscriptions import SubscriptionClient
from devtools_testutils import AzureRecordedTestCase, is_live, recorded_by_proxy
import pytest

class CaePreparer(object):
    def __init__(self):
        if is_live():
            if "CAE_TENANT_ID" not in os.environ:
                pytest.skip("Missing a tenant ID for CAE tests")
            if "CAE_ARM_URL" not in os.environ:
                pytest.skip("Missing an ARM URL for CAE tests")

            self.cae_settings = {
                "arm_scope": os.environ.get("CAE_ARM_SCOPE", "https://management.azure.com/.default"),
                "arm_url": os.environ["CAE_ARM_URL"],
                "authority": os.environ.get("CAE_AUTHORITY", AzureAuthorityHosts.AZURE_PUBLIC_CLOUD),
                "graph_url": os.environ.get("CAE_GRAPH_URL", "https://graph.microsoft.com"),
                "password": os.environ.get("CAE_PASSWORD"),
                "tenant_id": os.environ["CAE_TENANT_ID"],
                "username": os.environ.get("CAE_USERNAME"),
            }
        else:
            self.cae_settings = {
                "arm_scope": "https://management.azure.com/.default",
                "arm_url": "https://management.azure.com/",
                "authority": AzureAuthorityHosts.AZURE_PUBLIC_CLOUD,
                "password": "password",
                "tenant_id": "tenant",
                "username": "username",
            }

    def __call__(self, fn):
        def _preparer_wrapper(test_class):
            fn(test_class, cae_settings=self.cae_settings)
        return _preparer_wrapper

@pytest.mark.skip("these tests require support in azure-core")
class TestCae(AzureRecordedTestCase):
    def cae_test(self, credential):
        client = SubscriptionClient(credential, base_url=self.cae_settings["arm_url"])

        # get an access token for ARM
        list(client.subscriptions.list())
        first_token = credential.get_token(self.cae_settings["arm_scope"])

        if is_live():
            validate_ssm_token(first_token.token)

            # revoking sessions revokes access and refresh tokens
            self.disable_recording = True
            graph_token = credential.get_token("User.ReadWrite")
            response = credential._client.post(
                self.cae_settings["graph_url"].rstrip("/") + "/v1.0/me/revokeSignInSessions",
                headers={"Authorization": "Bearer " + graph_token.token},
            )
            self.disable_recording = False
            assert 200 <= response.status_code < 300, "session revocation failed: " + response.text()

            # wait for the resource provider to observe the revocation event
            time.sleep(400)

        # The client should authorize this request with a revoked token, and receive a challenge.
        # Silent authentication will fail because the refresh token has been revoked.
        list(client.subscriptions.list())

        # the credential should have reauthenticated the user and acquired a new access token
        second_token = credential.get_token(self.cae_settings["arm_scope"])
        assert second_token.token != first_token.token

    @pytest.mark.manual
    def test_browser(self):
        self.load_settings()
        credential = InteractiveBrowserCredential(
            authority=self.cae_settings["authority"], tenant_id=self.cae_settings["tenant_id"]
        )
        self.cae_test(credential, cae_settings=self.cae_settings)

    @pytest.mark.manual
    @recorded_by_proxy
    def test_device_code(self):
        self.load_settings()
        credential = DeviceCodeCredential(
            authority=self.cae_settings["authority"], tenant_id=self.cae_settings["tenant_id"]
        )
        self.cae_test(credential)

    @pytest.mark.manual
    @recorded_by_proxy
    def test_username_password(self):
        self.load_settings()
        if is_live() and not ("username" in self.cae_settings and "password" in self.cae_settings):
            pytest.skip("Missing a username or password for CAE test")

        credential = UsernamePasswordCredential(
            DEVELOPER_SIGN_ON_CLIENT_ID,
            authority=self.cae_settings["authority"],
            tenant_id=self.cae_settings["tenant_id"],
            username=self.cae_settings["username"],
            password=self.cae_settings["password"],
        )
        self.cae_test(credential)

    def load_settings(self):
        if is_live():
            if "CAE_TENANT_ID" not in os.environ:
                pytest.skip("Missing a tenant ID for CAE tests")
            if "CAE_ARM_URL" not in os.environ:
                pytest.skip("Missing an ARM URL for CAE tests")

            self.cae_settings = {
                "arm_scope": os.environ.get("CAE_ARM_SCOPE", "https://management.azure.com/.default"),
                "arm_url": os.environ["CAE_ARM_URL"],
                "authority": os.environ.get("CAE_AUTHORITY", AzureAuthorityHosts.AZURE_PUBLIC_CLOUD),
                "graph_url": os.environ.get("CAE_GRAPH_URL", "https://graph.microsoft.com"),
                "password": os.environ.get("CAE_PASSWORD"),
                "tenant_id": os.environ["CAE_TENANT_ID"],
                "username": os.environ.get("CAE_USERNAME"),
            }
        else:
            self.cae_settings = {
                "arm_scope": "https://management.azure.com/.default",
                "arm_url": "https://management.azure.com/",
                "authority": AzureAuthorityHosts.AZURE_PUBLIC_CLOUD,
                "password": "password",
                "tenant_id": "tenant",
                "username": "username",
            }


def validate_ssm_token(access_token):
    """Ensure an access token is enabled for smart session management i.e. it is subject to CAE"""

    _, payload, _ = access_token.split(".")
    decoded_payload = base64.urlsafe_b64decode(payload + "==").decode()
    parsed_payload = json.loads(decoded_payload)

    assert (
        "xms_cc" in parsed_payload and "CP1" in parsed_payload["xms_cc"]
    ), 'the token request did not include client capability "CP1"'

    assert "xms_ssm" in parsed_payload and parsed_payload["xms_ssm"] == "1", "CAE isn't enabled for the user"
