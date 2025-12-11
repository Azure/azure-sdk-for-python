# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.exceptions import ClientAuthenticationError
from azure.appconfiguration._audience_policy import AudienceErrorHandlingPolicy
import pytest

NO_AUDIENCE_ERROR_MESSAGE = (
    "Unable to authenticate to Azure App Configuration. No authentication token audience was provided. Please set the "
    "audience via credential_scopes when constructing AzureAppConfigurationClient for the target cloud. For details on "
    "how to configure the authentication token audience visit https://aka.ms/appconfig/client-token-audience."
)
INCORRECT_AUDIENCE_ERROR_MESSAGE = (
    "Unable to authenticate to Azure App Configuration. An incorrect token audience was provided. Please set the "
    "audience via credential_scopes when constructing AzureAppConfigurationClient to the appropriate audience for this "
    "cloud. For details on how to configure the authentication token audience visit "
    "https://aka.ms/appconfig/client-token-audience."
)
AAD_AUDIENCE_ERROR_CODE = "AADSTS500011"


def test_on_exception_no_audience():
    policy = AudienceErrorHandlingPolicy(False)
    try:
        raise ClientAuthenticationError(message=f"{AAD_AUDIENCE_ERROR_CODE} some error", response=None)
    except ClientAuthenticationError:
        with pytest.raises(ClientAuthenticationError) as exc_info:
            policy.on_exception(None)
            assert NO_AUDIENCE_ERROR_MESSAGE in str(exc_info.value)


def test_on_exception_incorrect_audience():
    policy = AudienceErrorHandlingPolicy(True)
    try:
        raise ClientAuthenticationError(message=f"{AAD_AUDIENCE_ERROR_CODE} some error", response=None)
    except ClientAuthenticationError:
        with pytest.raises(ClientAuthenticationError) as exc_info:
            policy.on_exception(None)
            assert INCORRECT_AUDIENCE_ERROR_MESSAGE in str(exc_info.value)


def test_on_exception_non_audience_error():
    policy = AudienceErrorHandlingPolicy(False)
    try:
        raise ClientAuthenticationError(message="Some other error", response=None)
    except ClientAuthenticationError as ex:
        result = policy.on_exception(None)
        assert result is ex
