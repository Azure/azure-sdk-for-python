# coding: utf-8


# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


def analyze_text_with_aad_auth():
    # [START analyze_text]

    import os
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.ai.contentsafety.models import TextCategory
    from azure.core.exceptions import HttpResponseError
    from azure.ai.contentsafety.models import AnalyzeTextOptions
    from azure.identity import ClientSecretCredential

    tenant_id = os.environ["CONTENT_SAFETY_TENANT_ID"]
    client_id = os.environ["CONTENT_SAFETY_CLIENT_ID"]
    client_secret = os.environ["CONTENT_SAFETY_CLIENT_SECRET"]
    endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]

    # Create a Content Safety client
    client = ContentSafetyClient(
        endpoint,
        ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        ),
    )

    # Construct a request
    request = AnalyzeTextOptions(text="You are an idiot")

    # Analyze text
    try:
        response = client.analyze_text(request)
    except HttpResponseError as e:
        print("Analyze text failed.")
        if e.error:
            print(f"Error code: {e.error.code}")
            print(f"Error message: {e.error.message}")
            raise
        print(e)
        raise

    hate_result = next(item for item in response.categories_analysis if item.category == TextCategory.HATE)
    self_harm_result = next(item for item in response.categories_analysis if item.category == TextCategory.SELF_HARM)
    sexual_result = next(item for item in response.categories_analysis if item.category == TextCategory.SEXUAL)
    violence_result = next(item for item in response.categories_analysis if item.category == TextCategory.VIOLENCE)

    if hate_result:
        print(f"Hate severity: {hate_result.severity}")
    if self_harm_result:
        print(f"SelfHarm severity: {self_harm_result.severity}")
    if sexual_result:
        print(f"Sexual severity: {sexual_result.severity}")
    if violence_result:
        print(f"Violence severity: {violence_result.severity}")

    # [END analyze_text]


if __name__ == "__main__":
    analyze_text_with_aad_auth()
