# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.core.exceptions import ClientAuthenticationError
from azure.appconfiguration._audience_error_handling_policy import (
    AudienceErrorHandlingPolicy,
    INCORRECT_AUDIENCE_ERROR_MESSAGE,
)
from testcase import AppConfigTestCase
from preparers import app_config_aad_decorator
from devtools_testutils import recorded_by_proxy

# cspell:disable-next-line
CORRECT_AUDIENCE = "https://azconfig.io"
# cspell:disable-next-line
VALID_ENDPOINT_SUFFIX = ".azconfig.io"
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
