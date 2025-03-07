# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable
import datetime
import jwt
import time

from azure.ai.projects.models import SASTokenCredential
from azure.core.credentials import TokenCredential, AccessToken
from azure.core.exceptions import HttpResponseError
from connection_test_base import ConnectionsTestBase
from azure.ai.projects.models import ConnectionProperties
from azure.ai.projects.models._models import GetConnectionResponse
from unittest.mock import MagicMock, patch


class FakeTokenCredential(TokenCredential):
    def get_token(self, *scopes, **kwargs):
        # Create a fake token with an expiration time
        token = "fake_token"
        expires_on = datetime.datetime.now() + datetime.timedelta(hours=1)
        return AccessToken(token, expires_on.timestamp())


# The test class name needs to start with "Test" to get collected by pytest
class TestConnectionsUnitTests(ConnectionsTestBase):

    # **********************************************************************************
    #
    #                               UNIT TESTS
    #
    # **********************************************************************************

    def test_sas_token_credential_class_mocked(self, **kwargs):
        # Create a simple JWT with 10 seconds expiration time
        secret_key = "my_secret_key"
        token_duration_sec = 5
        sas_token_expiration: datetime = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            seconds=token_duration_sec
        )
        sas_token_expiration = sas_token_expiration.replace(microsecond=0)
        payload = {"exp": sas_token_expiration}
        sas_token = jwt.encode(payload, secret_key)

        # You can parse the token string on https://jwt.ms/. The "exp" value there is the
        # token expiration time in Unix timestamp format (seconds since 1970-01-01 00:00:00 UTC).
        # See https://www.epochconverter.com/ to convert Unix time to readable date & time.
        # The base64 decoded string will look something like this:
        # {
        #  "alg": "HS256",
        #  "typ": "JWT"
        # }.{
        #  "exp": 1727208894
        # }.[Signature]
        print(f"Generated JWT token: {sas_token}")

        sas_token_credential = SASTokenCredential(
            sas_token=sas_token,
            credential=FakeTokenCredential(),
            subscription_id="fake_subscription_id",
            resource_group_name="fake_resource_group",
            project_name="fake_project_name",
            connection_name="fake_connection_name",
        )
        assert sas_token_credential._expires_on == sas_token_expiration

        exception_caught = False
        try:
            for _ in range(token_duration_sec + 2):
                print("Looping...")
                time.sleep(1)
                sas_token_credential.get_token()
        except HttpResponseError as e:
            exception_caught = True
            print(e)
        assert exception_caught

    def _get_fake_token(self, exiration):
        """Return the fake sas token."""
        secret_key = "my_secret_key"
        payload = {"exp": exiration}
        sas_token = jwt.encode(payload, secret_key)
        return SASTokenCredential(
            sas_token=sas_token,
            credential=FakeTokenCredential(),
            subscription_id="fake_subscription_id",
            resource_group_name="fake_resource_group",
            project_name="fake_project_name",
            connection_name="fake_connection_name",
        )

    def test_mock_subscription_refresh_token(self):
        """Test refreshing token with mock subscription"""
        token_duration_sec = 5
        # Let our token be already expired.
        sas_token_expiration: datetime = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
            seconds=token_duration_sec
        )
        sas_token_expiration = sas_token_expiration.replace(microsecond=0)
        sas_token_credential = self._get_fake_token(sas_token_expiration)
        assert sas_token_credential._expires_on == sas_token_expiration
        new_expiration: datetime = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            seconds=token_duration_sec
        )
        new_token_credential = self._get_fake_token(new_expiration)

        mock_properties = MagicMock()
        mock_properties.auth_type = "sas_token"
        mock_properties.category = "fake_category"
        mock_properties.target = "microsoft.com"
        mock_properties.credentials.key = "very secret key"
        conn_resp = GetConnectionResponse(id="12334", name="Fake_connection", properties=mock_properties)
        conn = ConnectionProperties(connection=conn_resp, token_credential=new_token_credential)
        with patch("azure.ai.projects.operations.ConnectionsOperations.get", return_value=conn):
            new_token = sas_token_credential.get_token()
        assert new_token.expires_on == int(new_expiration.timestamp())

    # Unit tests for the SASTokenCredential class
    def test_sas_token_credential_class_real(self, **kwargs):

        # Example of real SAS token for AOAI service. You can parse it on https://jwt.ms/. The "exp" value there is the
        # token expiration time in Unix timestamp format (seconds since 1970-01-01 00:00:00 UTC)
        token = "eyJhbGciOiJFUzI1NiIsImtpZCI6ImtleTEiLCJ0eXAiOiJKV1QifQ.eyJyZWdpb24iOiJlYXN0dXMyZXVhcCIsInN1YnNjcmlwdGlvbi1pZCI6IjQyZjVlYWFjMjc5MDRiMGViMDI4ZTVkZjcyYzg5ZDAxIiwicHJvZHVjdC1pZCI6Ik9wZW5BSS5TMCIsImNvZ25pdGl2ZS1zZXJ2aWNlcy1lbmRwb2ludCI6Imh0dHBzOi8vYXBpLmNvZ25pdGl2ZS5taWNyb3NvZnQuY29tL2ludGVybmFsL3YxLjAvIiwiYXp1cmUtcmVzb3VyY2UtaWQiOiIvc3Vic2NyaXB0aW9ucy84ZjMzOGY2ZS00ZmNlLTQ0YWUtOTY5Yy1mYzdkOGZkYTAzMGUvcmVzb3VyY2VHcm91cHMvYXJncnlnb3JfY2FuYXJ5L3Byb3ZpZGVycy9NaWNyb3NvZnQuQ29nbml0aXZlU2VydmljZXMvYWNjb3VudHMvYXJncnlnb3ItY2FuYXJ5LWFvYWkiLCJzY29wZSI6Imh0dHBzOi8vc3BlZWNoLnBsYXRmb3JtLmJpbmcuY29tIiwiYXVkIjoidXJuOm1zLnNwZWVjaCIsImV4cCI6MTcyNjc4MjI0NiwiaXNzIjoidXJuOm1zLmNvZ25pdGl2ZXNlcnZpY2VzIn0.L7VvsXPzbwHQeMS-o9Za4itkU6uP4-KFMyOpTsYD9tpIJa_qChMHDl8FHy5n7K5L1coKg8sJE6LlJICFdU1ALQ"
        expiration_date_linux_time = 1726782246  # Value of "exp" field in the token. See https://www.epochconverter.com/ to convert to date & time
        expiration_datatime_utc = datetime.datetime.fromtimestamp(expiration_date_linux_time, datetime.timezone.utc)
        print(f"\n[TEST] Expected expiration date: {expiration_datatime_utc}")

        sas_token_credential = SASTokenCredential(
            sas_token=token,
            credential=None,
            subscription_id=None,
            resource_group_name=None,
            project_name=None,
            connection_name=None,
        )

        print(f"[TEST]   Actual expiration date: {sas_token_credential._expires_on}")
        assert sas_token_credential._expires_on == expiration_datatime_utc
