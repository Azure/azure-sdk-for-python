# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_send_request.py

DESCRIPTION:
    This sample demonstrates how to make custom HTTP requests through a client pipeline.

USAGE:
    python sample_send_request.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os
from azure.core.credentials import AzureKeyCredential
from azure.core.rest import HttpRequest
from azure.ai.formrecognizer import DocumentModelAdministrationClient, FormTrainingClient


def sample_send_request():
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
    response = client.send_request(request)
    response.raise_for_status()
    response_body = response.json()
    print(
        f"Our resource has {response_body['customDocumentModels']['count']} custom models, "
        f"and we can have at most {response_body['customDocumentModels']['limit']} custom models."
        f"The quota limit for custom neural document models is {response_body['customNeuralDocumentModelBuilds']['quota']} and the resource has"
        f"used {response_body['customNeuralDocumentModelBuilds']['used']}. The resource quota will reset on {response_body['customNeuralDocumentModelBuilds']['quotaResetDateTime']}"
    )
    
    # pass with absolute url and override the API version
    request = HttpRequest(method="GET", url=f"{endpoint}/formrecognizer/info?api-version=2022-08-31")
    response = client.send_request(request)
    response.raise_for_status()
    response_body = response.json()
    print(
        f"Our resource has {response_body['customDocumentModels']['count']} custom models, "
        f"and we can have at most {response_body['customDocumentModels']['limit']} custom models."
    )
    
    # override the API version to v2.1
    request = HttpRequest(method="GET", url="v2.1/custom/models?op=summary")
    response = client.send_request(request)
    response.raise_for_status()
    response_body = response.json()
    print(
        f"Our account has {response_body['summary']['count']} custom models, "
        f"and we can have at most {response_body['summary']['limit']} custom models."
    )
    
    # pass with absolute url and override the API version to v2.1
    request = HttpRequest(method="GET", url=f"{endpoint}/formrecognizer/v2.1/custom/models?op=summary")
    response = client.send_request(request)
    response.raise_for_status()
    response_body = response.json()
    print(
        f"Our account has {response_body['summary']['count']} custom models, "
        f"and we can have at most {response_body['summary']['limit']} custom models."
    )


def sample_send_request_v2():
    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    # The default FormTrainingClient API version is v2.1
    client = FormTrainingClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    
    # The `send_request` method can send custom HTTP requests that share the client's existing pipeline,
    # while adding convenience for endpoint construction and service API versioning.
    # Now let's use the `send_request` method to make a resource details fetching request.
    # The URL of the request can be relative (your endpoint is the default base URL),
    # and the API version of your client will automatically be used for the request.
    request = HttpRequest(method="GET", url="custom/models?op=summary")
    response = client.send_request(request)
    response.raise_for_status()
    response_body = response.json()
    print(
        f"Our account has {response_body['summary']['count']} custom models, "
        f"and we can have at most {response_body['summary']['limit']} custom models."
    )
    
    # pass with absolute url and override the API version
    request = HttpRequest(method="GET", url=f"{endpoint}/formrecognizer/v2.0/custom/models?op=summary")
    response = client.send_request(request)
    response.raise_for_status()
    response_body = response.json()
    print(
        f"Our account has {response_body['summary']['count']} custom models, "
        f"and we can have at most {response_body['summary']['limit']} custom models."
    )
    
    # override the API version to 2023-07-31
    request = HttpRequest(method="GET", url=f"{endpoint}/formrecognizer/info?api-version=2023-07-31")
    response = client.send_request(request)
    response.raise_for_status()
    response_body = response.json()
    print(
        f"Our resource has {response_body['customDocumentModels']['count']} custom models, "
        f"and we can have at most {response_body['customDocumentModels']['limit']} custom models."
        f"The quota limit for custom neural document models is {response_body['customNeuralDocumentModelBuilds']['quota']} and the resource has"
        f"used {response_body['customNeuralDocumentModelBuilds']['used']}. The resource quota will reset on {response_body['customNeuralDocumentModelBuilds']['quotaResetDateTime']}"
    )


if __name__ == "__main__":
    from azure.core.exceptions import HttpResponseError

    try:
        sample_send_request()
        sample_send_request_v2()
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
