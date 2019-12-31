# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.ai.textanalytics import TextAnalyticsClient
from testcase import GlobalTextAnalyticsAccountPreparer
from testcase import TextAnalyticsTest as TestAnalyticsTestCase


class TextAnalyticsTest(TestAnalyticsTestCase):

    @GlobalTextAnalyticsAccountPreparer()
    def test_detect_language(self, resource_group, location, text_analytics_account, text_analytics_account_key):
        text_analytics = TextAnalyticsClient(text_analytics_account, text_analytics_account_key)

        response = text_analytics.detect_languages(
            inputs=[{
                'id': 1,
                'text': 'I had a wonderful experience! The rooms were wonderful and the staff was helpful.'
            }]
        )

        self.assertEqual(response[0].primary_language.name, "English")
