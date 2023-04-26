import os
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety.models import AnalyzeTextOptions, TextCategory


def analyze_text():
    key = os.environ["CONTENT_SAFETY_KEY"]
    endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]
    text_path = os.path.join("sample_data", "text.txt")

    # Create an Content Safety client
    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

    # Read sample data
    with open(text_path) as f:
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

    if response.hate_result is not None:
        print("Hate severity: {}".format(response.hate_result.severity))
    if response.self_harm_result is not None:
        print("SelfHarm severity: {}".format(response.self_harm_result.severity))


if __name__ == "__main__":
    analyze_text()
