# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_send_request_async.py

DESCRIPTION:
    This sample demonstrates how to make custom HTTP requests through a client pipeline.

USAGE:
    python sample_send_request_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os
from azure.core.credentials import AzureKeyCredential
from azure.core.rest import HttpRequest
from azure.ai.formrecognizer.aio import DocumentModelAdministrationClient


async def sample_send_request():
    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    client = DocumentModelAdministrationClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    
    # The `send_request` method can send custom HTTP requests that share the client's existing pipeline,
    # while adding convenience for endpoint construction and service API versioning.
    # Now let's use the `send_request` method to make a resource details fetching request.
    # The URL of the request can be relative (your endpoint is the default base URL),
    # and the API version of your client will automatically be used for the request.
    request = HttpRequest(method="GET", url="info")
    async with client:
        response = await client.send_request(request)
    response.raise_for_status()
    
    response_body = response.json()
    print(
        f"Our resource has {response_body['customDocumentModels']['count']} custom models, "
        f"and we can have at most {response_body['customDocumentModels']['limit']} custom models."
        f"The quota limit for custom neural document models is {response_body['customNeuralDocumentModelBuilds']['quota']} and the resource has"
        f"used {response_body['customNeuralDocumentModelBuilds']['used']}. The resource quota will reset on {response_body['customNeuralDocumentModelBuilds']['quotaResetDateTime']}"
    )


async def main():
    await sample_send_request()


if __name__ == "__main__":
    import sys
    from azure.core.exceptions import HttpResponseError

    try:
        asyncio.run(main())
    except HttpResponseError as error:
        print(
            "For more information about troubleshooting errors, see the following guide: "
            "https://aka.ms/azsdk/python/formrecognizer/troubleshooting"
        )
        # Examples of how to check an HttpResponseError
        # Check by error code:
        if error.error is not None:
            if error.error.code == "InvalidImage":
                print(f"Received an invalid image error: {error.error}")
            if error.error.code == "InvalidRequest":
                print(f"Received an invalid request error: {error.error}")
            # Raise the error again after printing it
            raise
        # If the inner error is None and then it is possible to check the message to get more information:
        if "Invalid request".casefold() in error.message.casefold():
            print(f"Uh-oh! Seems there was an invalid request: {error}")
        # Raise the error again
        raise
