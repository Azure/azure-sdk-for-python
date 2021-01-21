# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

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
        credential.update(subscription_key="xxx", api_key="xxx")
        assert credential.subscription_key == "xxx"
        assert credential.api_key == "xxx"

        # call fails
        try:
            result = client.get_feedback(feedback_id=self.feedback_id)
        except ClientAuthenticationError:
            pass

        # rotate back to valid credentials
        credential.update(subscription_key=self.subscription_key, api_key=self.api_key)
        assert credential.subscription_key == self.subscription_key
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
        credential.update(subscription_key="xxx")
        assert credential.subscription_key == "xxx"
        assert credential.api_key == self.api_key

        # call fails
        try:
            result = client.get_feedback(feedback_id=self.feedback_id)
        except ClientAuthenticationError:
            pass

        # rotate back to valid credentials
        credential.update(subscription_key=self.subscription_key)
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
        credential.update(api_key="xxx")
        assert credential.subscription_key == self.subscription_key
        assert credential.api_key == "xxx"

        # call fails
        try:
            result = client.get_feedback(feedback_id=self.feedback_id)
        except HttpResponseError:
            pass

        # rotate back to valid credentials
        credential.update(api_key=self.api_key)
        assert credential.subscription_key == self.subscription_key
        assert credential.api_key == self.api_key

        # make successful call
        result = client.get_feedback(feedback_id=self.feedback_id)
        assert result

    def test_credential_bad_input(self):
        credential = MetricsAdvisorKeyCredential(self.subscription_key, self.api_key)

        try:
            credential.update()
        except ValueError:
            pass

        try:
            credential.update(subscription_key=34)
        except TypeError:
            pass

        try:
            credential.update(api_key=34)
        except TypeError:
            pass
