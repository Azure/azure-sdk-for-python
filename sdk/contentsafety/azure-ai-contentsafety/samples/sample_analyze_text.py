import os
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety.models import *


class AnalyzeText(object):
    def analyze_text(self):
        CONTENT_SAFETY_KEY = os.environ["CONTENT_SAFETY_KEY"]
        CONTENT_SAFETY_ENDPOINT = os.environ["CONTENT_SAFETY_ENDPOINT"]
        TEXT_DATA_PATH = os.path.join("sample_data", "text.txt")

        # Create an Content Safety client
        client = ContentSafetyClient(CONTENT_SAFETY_ENDPOINT, AzureKeyCredential(CONTENT_SAFETY_KEY))

        # Read sample data
        with open(TEXT_DATA_PATH) as f:
            text = f.readline()

        # Build request
        request = AnalyzeTextOptions(text=text, categories=[TextCategory.HATE, TextCategory.SELF_HARM])

        # Analyze text
        try:
            response = client.analyze_text(request)
        except Exception as e:
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return

        print(response.hate_result)
        print(response.self_harm_result)

if __name__=="__main__":
    sample = AnalyzeText()
    sample.analyze_text()
