import os
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety.models import *


class AnalyzeText(object):
    def analyze_text(self):
        SUBSCRIPTION_KEY = "19b54286b8ac49fc8d064eded98dd48e"
        CONTENT_SAFETY_ENDPOINT = "https://cm-carnegie-ppe-use.ppe.cognitiveservices.azure.com/"
        TEXT_DATA_PATH = os.path.join("sample_data", "text.txt")

        #create an Content Safety client
        client = ContentSafetyClient(CONTENT_SAFETY_ENDPOINT, AzureKeyCredential(SUBSCRIPTION_KEY))

        #read sample data
        with open(TEXT_DATA_PATH) as f:
            text = f.readline()

        #build request
        request = TextDetectRequest(text=text, categories=[TextCategory.HATE, TextCategory.SELF_HARM])

        # analyze text
        try:
            response = client.analyze(request)
            print(response.hate_result)
            print(response.self_harm_result)
        except Exception as e:
            print(
                "Error code: {}".format(e.error.code),
                "Error message: {}".format(e.error.message),
            )

if __name__=="__main__":
    sample = AnalyzeText()
    sample.analyze_text()
