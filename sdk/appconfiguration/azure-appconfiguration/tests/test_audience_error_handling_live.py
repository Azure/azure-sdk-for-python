# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.core.exceptions import ClientAuthenticationError
from azure.appconfiguration._audience_error_handling_policy import (
    AudienceErrorHandlingPolicy,\
    INCORRECT_AUDIENCE_ERROR_MESSAGE,
)
from testcase import AppConfigTestCase
from preparers import app_config_aad_decorator
from devtools_testutils import recorded_by_proxy\

# cspell:disable-next-line
AZCONFIG_DOMAIN = "azconfig.io" 
CORRECT_AUDIENCE = f"https://{AZCONFIG_DOMAIN}"
VALID_ENDPOINT_SUFFIX = f".{AZCONFIG_DOMAIN}"
# cspell:disable-next-line
INVALID_ENDPOINT_SUFFIX = ".azconfig.sovcloud-api.fr"
# cspell:disable-next-line
INCORRECT_AUDIENCE = "https://login.sovcloud-identity2.fr"


class TestAudienceErrorHandlingLive(AppConfigTestCase):
    """Live and recorded tests for audience error handling with the Azure App Configuration client."""

    @app_config_aad_decorator
    @recorded_by_proxy
    def test_client_has_audience_policy_with_no_audience(self, appconfiguration_endpoint_string):
        """Test that client created without audience has policy with has_audience=False."""
        # Create client without audience
        client = self.create_aad_client(appconfiguration_endpoint_string)

        # Check that audience error handling policy is in the pipeline
        policies = client._impl._client._pipeline._impl_policies
        audience_policy = None
        for policy in policies:
            # Policies are wrapped in _SansIOHTTPPolicyRunner, so we need to access the underlying policy
            underlying_policy = getattr(policy, "_policy", policy)
            if isinstance(underlying_policy, AudienceErrorHandlingPolicy):
                audience_policy = underlying_policy
                break

        assert audience_policy is not None, "AudienceErrorHandlingPolicy should be in pipeline"
        assert audience_policy.has_audience is False, "has_audience should be False when no audience provided"

    @app_config_aad_decorator
    @recorded_by_proxy
    def test_client_has_audience_policy_with_audience(self, appconfiguration_endpoint_string):
        """Test that client created with audience has policy with has_audience=True."""
        # Create client with audience
        client = self.create_aad_client(appconfiguration_endpoint_string, audience=CORRECT_AUDIENCE)

        # Check that audience error handling policy is in the pipeline
        policies = client._impl._client._pipeline._impl_policies
        audience_policy = None
        for policy in policies:
            # Policies are wrapped in _SansIOHTTPPolicyRunner, so we need to access the underlying policy
            underlying_policy = getattr(policy, "_policy", policy)
            if isinstance(underlying_policy, AudienceErrorHandlingPolicy):
                audience_policy = underlying_policy
                break

        assert audience_policy is not None, "AudienceErrorHandlingPolicy should be in pipeline"
        assert audience_policy.has_audience is True, "has_audience should be True when audience provided"

    @app_config_aad_decorator
    @recorded_by_proxy
    def test_error_message_when_incorrect_audience_provided(self, appconfiguration_endpoint_string):
        """Test that correct error message is raised when incorrect audience is provided."""
        # Create client with invalid endpoint to trigger authentication error
        # Replace the endpoint domain with an invalid one to force audience mismatch
        invalid_endpoint = appconfiguration_endpoint_string.replace(VALID_ENDPOINT_SUFFIX, INVALID_ENDPOINT_SUFFIX)
        client = self.create_aad_client(invalid_endpoint, audience=INCORRECT_AUDIENCE)

        # Attempt operation that should fail with audience error
        with pytest.raises(ClientAuthenticationError) as exc_info:
            kv = self.create_config_setting()
            client.set_configuration_setting(kv)

        # Verify the error message indicates incorrect audience
        assert INCORRECT_AUDIENCE_ERROR_MESSAGE in str(exc_info.value)

        # Verify error contains link to documentation
        error_message = str(exc_info.value)
        assert "https://aka.ms/appconfig/client-token-audience" in error_message

        # Verify exception has response attribute from original error
        assert hasattr(exc_info.value, "response")
