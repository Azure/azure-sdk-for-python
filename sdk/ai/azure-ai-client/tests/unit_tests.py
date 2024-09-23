# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
import base64
#import azure.ai.client as sdk


# The test class name needs to start with "Test" to get collected by pytest
class TestUnit:

    # **********************************************************************************
    #
    #                               UNIT TESTS
    #
    # **********************************************************************************

    # Unit tests for the SASTokenCredential class
    def test_sas_token_credential_class(self, **kwargs):

        from azure.ai.client import SASTokenCredential

        # Example SAS token. You can parse it on https://jwt.ms/. The "exp" value there is the token expiration time
        # in Linux timestamp format (seconds since 1970-01-01 00:00:00 UTC)
        token = "eyJhbGciOiJFUzI1NiIsImtpZCI6ImtleTEiLCJ0eXAiOiJKV1QifQ.eyJyZWdpb24iOiJlYXN0dXMyZXVhcCIsInN1YnNjcmlwdGlvbi1pZCI6IjQyZjVlYWFjMjc5MDRiMGViMDI4ZTVkZjcyYzg5ZDAxIiwicHJvZHVjdC1pZCI6Ik9wZW5BSS5TMCIsImNvZ25pdGl2ZS1zZXJ2aWNlcy1lbmRwb2ludCI6Imh0dHBzOi8vYXBpLmNvZ25pdGl2ZS5taWNyb3NvZnQuY29tL2ludGVybmFsL3YxLjAvIiwiYXp1cmUtcmVzb3VyY2UtaWQiOiIvc3Vic2NyaXB0aW9ucy84ZjMzOGY2ZS00ZmNlLTQ0YWUtOTY5Yy1mYzdkOGZkYTAzMGUvcmVzb3VyY2VHcm91cHMvYXJncnlnb3JfY2FuYXJ5L3Byb3ZpZGVycy9NaWNyb3NvZnQuQ29nbml0aXZlU2VydmljZXMvYWNjb3VudHMvYXJncnlnb3ItY2FuYXJ5LWFvYWkiLCJzY29wZSI6Imh0dHBzOi8vc3BlZWNoLnBsYXRmb3JtLmJpbmcuY29tIiwiYXVkIjoidXJuOm1zLnNwZWVjaCIsImV4cCI6MTcyNjc4MjI0NiwiaXNzIjoidXJuOm1zLmNvZ25pdGl2ZXNlcnZpY2VzIn0.L7VvsXPzbwHQeMS-o9Za4itkU6uP4-KFMyOpTsYD9tpIJa_qChMHDl8FHy5n7K5L1coKg8sJE6LlJICFdU1ALQ"

        sas_token_credential = SASTokenCredential(
            sas_token = token,
            credential = None,
            subscription_id = None,
            resource_group_name = None,
            workspace_name = None,
            connection_name = None
        )

        print(f"Expiration date: {sas_token_credential._expires_on}")
