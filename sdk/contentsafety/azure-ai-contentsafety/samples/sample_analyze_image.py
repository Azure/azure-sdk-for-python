import os
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety.models import *

class AnalyzeImage(object):
    def analyze_image(self):
        CONTENT_SAFETY_KEY = os.environ["CONTENT_SAFETY_KEY"]
        CONTENT_SAFETY_ENDPOINT = os.environ["CONTENT_SAFETY_ENDPOINT"]
        IMAGE_DATA_PATH = os.path.join("sample_data", "image.jpg")

        # Create an Content Safety client
        client = ContentSafetyClient(CONTENT_SAFETY_ENDPOINT, AzureKeyCredential(CONTENT_SAFETY_KEY))

        # Build request
        with open(IMAGE_DATA_PATH, 'rb') as file:
            request = AnalyzeImageOptions(image=ImageData(content=file.read()))

        # Analyze image
        try:
            response = client.analyze_image(request)
        except Exception as e:
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return

        print(response)

if __name__=="__main__":
    sample = AnalyzeImage()
    sample.analyze_image()
