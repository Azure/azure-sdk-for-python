# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: images_aoai_quickstart.py

DESCRIPTION:
    This sample demonstrates how to get started generating images with the OpenAI SDK for Python.

USAGE:
    python images_aoai_quickstart.py

    Before running the sample:

    pip install openai
    pip install pillow

    Set the environment variables with your own values:
    1) AZURE_OPENAI_KEY - your Azure OpenAI API key.
    2) AZURE_OPENAI_ENDPOINT - the endpoint to your Azure OpenAI resource.
    3) AZURE_OPENAI_IMAGE_DEPLOYMENT - the deployment name you chose when deploying your model.
"""

import os
os.environ["AZURE_OPENAI_ENDPOINT"] = os.environ["AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT"]
os.environ["AZURE_OPENAI_IMAGE_DEPLOYMENT"] = "dall-e-3"

def images_aoai_quickstart() -> None:
    import os
    import httpx
    from openai import AzureOpenAI
    from PIL import Image
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )

    client = AzureOpenAI(
        azure_ad_token_provider=token_provider,
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=os.environ["API_VERSION_GA"]
    )

    result = client.images.generate(
        model=os.environ["AZURE_OPENAI_IMAGE_DEPLOYMENT"],
        prompt="a close-up of a bear walking through the forest",
        n=1
    )

    # Set the directory for the stored image
    image_dir = os.path.join(os.curdir, 'images')

    # If the directory doesn't exist, create it
    if not os.path.isdir(image_dir):
        os.mkdir(image_dir)

    # Initialize the image path (note the filetype should be png)
    image_path = os.path.join(image_dir, 'generated_image.png')

    # Retrieve the generated image
    image_url = result.data[0].url  # extract image URL from response
    if image_url:
        generated_image = httpx.get(image_url).content  # download the image

        with open(image_path, "wb") as image_file:
            image_file.write(generated_image)

        # Display the image in the default image viewer
        image = Image.open(image_path)
        image.show()

if __name__ == "__main__":
    images_aoai_quickstart()