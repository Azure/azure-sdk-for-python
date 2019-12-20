# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.ai.textanalytics import TextAnalyticsClient
from devtools_testutils import ResourceGroupPreparer
from devtools_testutils.cognitiveservices_testcase import CognitiveServiceTest, CognitiveServicesAccountPreparer


class TextAnalyticsTest(CognitiveServiceTest):

    @ResourceGroupPreparer(random_name_enabled=True)
    @CognitiveServicesAccountPreparer(name_prefix="pycog")
    def test_detect_language(self, resource_group, location, cognitiveservices_account, cognitiveservices_account_key):
        text_analytics = TextAnalyticsClient(cognitiveservices_account, cognitiveservices_account_key)

        response = text_analytics.detect_languages(
            inputs=[{
                'id': 1,
                'text': 'I had a wonderful experience! The rooms were wonderful and the staff was helpful.'
            }]
        )

        self.assertEqual(response[0].detected_languages[0].name, "English")
