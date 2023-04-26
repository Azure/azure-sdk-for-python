import os
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety.models import AnalyzeImageOptions, ImageData

def analyze_image():
    key = os.environ["CONTENT_SAFETY_KEY"]
    endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]
    image_path = os.path.join("sample_data", "image.jpg")

    # Create an Content Safety client
    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

    # Build request
    with open(image_path, "rb") as file:
        request = AnalyzeImageOptions(image=ImageData(content=file.read()))

    # Analyze image
    try:
        response = client.analyze_image(request)
    except Exception as e:
        print("Error code: {}".format(e.error.code))
        print("Error message: {}".format(e.error.message))
        return

    if response.hate_result is not None:
        print("Hate severity: {}".format(response.hate_result.severity))
    if response.self_harm_result is not None:
        print("SelfHarm severity: {}".format(response.self_harm_result.severity))
    if response.sexual_result is not None:
        print("Sexual severity: {}".format(response.sexual_result.severity))
    if response.violence_result is not None:
        print("Violence severity: {}".format(response.violence_result.severity))



if __name__ == "__main__":
    analyze_image()
