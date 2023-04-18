import os
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety.models import *
import base64

class AnalyzeImage(object):
    def analyze_image(self):
        SUBSCRIPTION_KEY = "19b54286b8ac49fc8d064eded98dd48e"
        CONTENT_SAFETY_ENDPOINT = "https://cm-carnegie-ppe-use.ppe.cognitiveservices.azure.com/"
        IMAGE_DATA_PATH = os.path.join("sample_data", "image.jpg")

        #create an Content Safety client
        client = ContentSafetyClient(CONTENT_SAFETY_ENDPOINT, AzureKeyCredential(SUBSCRIPTION_KEY))

        #read sample data
        with open(IMAGE_DATA_PATH, "rb") as image_file:
            encoded_bytes = base64.b64encode(image_file.read())
            print(encoded_bytes)
            image = Image(content=base64.b64decode(encoded_bytes))
            print(image)

        #build request
        request = ImageDetectRequest(image=image)

        # analyze image
        try:
            response = client.detect(request)
            print(response)
        except Exception as e:
            print(
                "Error code: {}".format(e.error.code),
                "Error message: {}".format(e.error.message),
            )

if __name__=="__main__":
    sample = AnalyzeImage()
    sample.analyze_image()
