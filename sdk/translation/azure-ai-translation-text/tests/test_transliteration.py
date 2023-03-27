# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import recorded_by_proxy, AzureRecordedTestCase, PowerShellPreparer
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
from tests.preparer import TextTranslationPreparer
from tests.test_helper import TestHelper
from tests.testcase import TextTranslationTest
 
class TestTransliteration(TextTranslationTest, TestHelper):

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_transliteration(self, **kwargs):      
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        input_text_elements = [ InputTextItem(text = "这里怎么一回事?") ]
        response = client.transliterate(content = input_text_elements, language="zh-Hans", from_script="Hans", to_script="Latn")
        
        assert response is not None
        assert response[0].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_multiple_inputs(self, **kwargs):      
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        input_text_elements = [ InputTextItem(text = "यहएककसौटीहैयहएककसौटीहै"), InputTextItem(text = "यहएककसौटीहै") ]
        response = client.transliterate(content = input_text_elements, language="hi", from_script="Deva", to_script="Latn")
        
        assert response is not None
        assert response[0].text is not None
        assert response[1].text is not None

    @TextTranslationPreparer()
    @recorded_by_proxy
    def test_edit_distance(self, **kwargs):      
        endpoint = kwargs.get("text_translation_endpoint")
        apikey = kwargs.get("text_translation_apikey")
        region = kwargs.get("text_translation_region")
        client = self.create_client(endpoint, apikey, region)

        input_text_elements = [ InputTextItem(text = "gujarat"), InputTextItem(text = "hadman"), InputTextItem(text = "hukkabar") ]
        response = client.transliterate(content = input_text_elements, language="gu", from_script="Latn", to_script="Gujr")
        
        assert response is not None
        assert response[0].text is not None
        assert response[1].text is not None
        assert response[2].text is not None

        expectedText = [ "ગુજરાત", "હદમાં", "હુક્કાબાર" ]
        editDistance = 0
        for i in range(len(expectedText)):
            editDistance = editDistance + self.edit_distance(expectedText[i], response[i].text)
        assert editDistance < 6