# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_raw_response.py

DESCRIPTION:
    This sample demonstrates how to get raw response via "raw_response_hook".

USAGE:
    python sample_get_raw_response.py

    Set the environment variables with your own values before running the sample:
    1) DOCUMENTINTELLIGENCE_ENDPOINT - the endpoint to your Document Intelligence resource.
    2) DOCUMENTINTELLIGENCE_API_KEY - your Document Intelligence API key.
"""

def sample_raw_response_hook():
    # [START raw_response_hook]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documentintelligence import DocumentIntelligenceAdministrationClient
    endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
    key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]

    client = DocumentIntelligenceAdministrationClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    responses = []

    def callback(response):
        response_status_code = response.http_response.status_code
        response_body = response.http_response.json()
        responses.append(response_status_code)
        responses.append(response_body)

    with client:
        client.get_resource_info(raw_response_hook=callback)

    print(f"Response status code is: {responses[0]}")
    print(f"Response body is: {responses[1]}")
    # [END raw_response_hook]


if __name__ == "__main__":
    from azure.core.exceptions import HttpResponseError
    from dotenv import find_dotenv, load_dotenv

    try:
        load_dotenv(find_dotenv())
        sample_raw_response_hook()
    except HttpResponseError as error:
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
