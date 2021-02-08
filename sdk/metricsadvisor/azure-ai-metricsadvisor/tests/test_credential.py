# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.ai.metricsadvisor import MetricsAdvisorClient, MetricsAdvisorKeyCredential
from base_testcase import TestMetricsAdvisorClientBase


class TestMetricsAdvisorCredential(TestMetricsAdvisorClientBase):

    def __init__(self, method_name):
        super(TestMetricsAdvisorCredential, self).__init__(method_name)
        if self.is_live:
            self.service_endpoint = self.get_settings_value("METRICS_ADVISOR_ENDPOINT")
            self.subscription_key = self.get_settings_value("METRICS_ADVISOR_SUBSCRIPTION_KEY")
            self.api_key = self.get_settings_value("METRICS_ADVISOR_API_KEY")
        else:
            self.service_endpoint = "https://endpointname.cognitiveservices.azure.com"
            self.subscription_key = "METRICS_ADVISOR_SUBSCRIPTION_KEY"
            self.api_key = "METRICS_ADVISOR_API_KEY"

    def test_credential_rotate_both_keys(self):
        credential = MetricsAdvisorKeyCredential(self.subscription_key, self.api_key)
        client = MetricsAdvisorClient(self.service_endpoint, credential)

        # make successful call
        result = client.get_feedback(feedback_id=self.feedback_id)
        assert result

        # rotate both keys
        credential.update_subscription_key("xxx")
        assert credential.subscription_key == "xxx"
        credential.update_api_key("xxx")
        assert credential.api_key == "xxx"

        # call fails
        with pytest.raises(ClientAuthenticationError):
            result = client.get_feedback(feedback_id=self.feedback_id)

        # rotate back to valid credentials
        credential.update_subscription_key(self.subscription_key)
        assert credential.subscription_key == self.subscription_key
        credential.update_api_key(self.api_key)
        assert credential.api_key == self.api_key

        # make successful call
        result = client.get_feedback(feedback_id=self.feedback_id)
        assert result

    def test_credential_rotate_sub_key_only(self):
        credential = MetricsAdvisorKeyCredential(self.subscription_key, self.api_key)
        client = MetricsAdvisorClient(self.service_endpoint, credential)

        # make successful call
        result = client.get_feedback(feedback_id=self.feedback_id)
        assert result

        # rotate one key
        credential.update_subscription_key("xxx")
        assert credential.subscription_key == "xxx"
        assert credential.api_key == self.api_key

        # call fails
        with pytest.raises(ClientAuthenticationError):
            result = client.get_feedback(feedback_id=self.feedback_id)

        # rotate back to valid credentials
        credential.update_subscription_key(self.subscription_key)
        assert credential.subscription_key == self.subscription_key
        assert credential.api_key == self.api_key

        # make successful call
        result = client.get_feedback(feedback_id=self.feedback_id)
        assert result

    def test_credential_rotate_api_key_only(self):
        credential = MetricsAdvisorKeyCredential(self.subscription_key, self.api_key)
        client = MetricsAdvisorClient(self.service_endpoint, credential)

        # make successful call
        result = client.get_feedback(feedback_id=self.feedback_id)
        assert result

        # rotate one key
        credential.update_api_key("xxx")
        assert credential.subscription_key == self.subscription_key
        assert credential.api_key == "xxx"

        # call fails
        with pytest.raises(HttpResponseError):
            result = client.get_feedback(feedback_id=self.feedback_id)

        # rotate back to valid credentials
        credential.update_api_key(self.api_key)
        assert credential.subscription_key == self.subscription_key
        assert credential.api_key == self.api_key

        # make successful call
        result = client.get_feedback(feedback_id=self.feedback_id)
        assert result

    def test_credential_bad_input(self):
        credential = MetricsAdvisorKeyCredential(self.subscription_key, self.api_key)

        with pytest.raises(ValueError):
            credential.update_subscription_key(None)
        with pytest.raises(ValueError):
            credential.update_api_key(None)
        with pytest.raises(TypeError):
            credential.update_subscription_key(subscription_key=34)
        with pytest.raises(TypeError):
            credential.update_api_key(api_key=34)
