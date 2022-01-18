# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from devtools_testutils import recorded_by_proxy
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.ai.metricsadvisor import MetricsAdvisorClient, MetricsAdvisorKeyCredential
from base_testcase import TestMetricsAdvisorClientBase


class TestMetricsAdvisorCredential(TestMetricsAdvisorClientBase):

    @recorded_by_proxy
    def test_credential_rotate_both_keys(self):
        credential = MetricsAdvisorKeyCredential(self.subscription_key, self.api_key)
        client = MetricsAdvisorClient(self.service_endpoint, credential)

        # make successful call
        result = client.get_feedback(feedback_id=self.feedback_id)
        assert result

        # rotate both keys
        credential.update_key(subscription_key="xxx")
        assert credential.subscription_key == "xxx"
        credential.update_key(api_key="xxx")
        assert credential.api_key == "xxx"

        # call fails
        with pytest.raises(ClientAuthenticationError):
            result = client.get_feedback(feedback_id=self.feedback_id)

        # rotate back to valid credentials
        credential.update_key(subscription_key=self.subscription_key)
        assert credential.subscription_key == self.subscription_key
        credential.update_key(api_key=self.api_key)
        assert credential.api_key == self.api_key

        # make successful call
        result = client.get_feedback(feedback_id=self.feedback_id)
        assert result

    @recorded_by_proxy
    def test_credential_rotate_sub_key_only(self):
        credential = MetricsAdvisorKeyCredential(self.subscription_key, self.api_key)
        client = MetricsAdvisorClient(self.service_endpoint, credential)

        # make successful call
        result = client.get_feedback(feedback_id=self.feedback_id)
        assert result

        # rotate one key
        credential.update_key(subscription_key="xxx")
        assert credential.subscription_key == "xxx"
        assert credential.api_key == self.api_key

        # call fails
        with pytest.raises(ClientAuthenticationError):
            result = client.get_feedback(feedback_id=self.feedback_id)

        # rotate back to valid credentials
        credential.update_key(subscription_key=self.subscription_key)
        assert credential.subscription_key == self.subscription_key
        assert credential.api_key == self.api_key

        # make successful call
        result = client.get_feedback(feedback_id=self.feedback_id)
        assert result

    @recorded_by_proxy
    def test_credential_rotate_api_key_only(self):
        credential = MetricsAdvisorKeyCredential(self.subscription_key, self.api_key)
        client = MetricsAdvisorClient(self.service_endpoint, credential)

        # make successful call
        result = client.get_feedback(feedback_id=self.feedback_id)
        assert result

        # rotate one key
        credential.update_key(api_key="xxx")
        assert credential.subscription_key == self.subscription_key
        assert credential.api_key == "xxx"

        # call fails
        with pytest.raises(HttpResponseError):
            result = client.get_feedback(feedback_id=self.feedback_id)

        # rotate back to valid credentials
        credential.update_key(api_key=self.api_key)
        assert credential.subscription_key == self.subscription_key
        assert credential.api_key == self.api_key

        # make successful call
        result = client.get_feedback(feedback_id=self.feedback_id)
        assert result

    def test_credential_bad_input(self):
        credential = MetricsAdvisorKeyCredential(self.subscription_key, self.api_key)
        with pytest.raises(TypeError):
            credential.update_key(subscription_key=34)
        with pytest.raises(TypeError):
            credential.update_key(api_key=34)
