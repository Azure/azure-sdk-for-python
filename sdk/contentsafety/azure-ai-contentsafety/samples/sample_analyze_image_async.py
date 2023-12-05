# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio


async def analyze_image_async():
    # [START analyze_image_async]

    import os
    from azure.ai.contentsafety.aio import ContentSafetyClient
    from azure.ai.contentsafety.models import ImageCategory
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError
    from azure.ai.contentsafety.models import AnalyzeImageOptions, ImageData

    key = os.environ["CONTENT_SAFETY_KEY"]
    endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]
    image_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./sample_data/image.jpg"))

    # Create a Content Safety client
    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

    async with client:
        # Build request
        with open(image_path, "rb") as file:
            request = AnalyzeImageOptions(image=ImageData(content=file.read()))

        # Analyze image
        try:
            response = await client.analyze_image(request)
        except HttpResponseError as e:
            print("Analyze image failed.")
            if e.error:
                print(f"Error code: {e.error.code}")
                print(f"Error message: {e.error.message}")
                raise
            print(e)
            raise

    hate_result = next(item for item in response.categories_analysis if item.category == ImageCategory.HATE)
    self_harm_result = next(item for item in response.categories_analysis if item.category == ImageCategory.SELF_HARM)
    sexual_result = next(item for item in response.categories_analysis if item.category == ImageCategory.SEXUAL)
    violence_result = next(item for item in response.categories_analysis if item.category == ImageCategory.VIOLENCE)

    if hate_result:
        print(f"Hate severity: {hate_result.severity}")
    if self_harm_result:
        print(f"SelfHarm severity: {self_harm_result.severity}")
    if sexual_result:
        print(f"Sexual severity: {sexual_result.severity}")
    if violence_result:
        print(f"Violence severity: {violence_result.severity}")

    # [END analyze_image_async]


async def main():
    await analyze_image_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
