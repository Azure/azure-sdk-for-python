# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: send_request_sample.py

DESCRIPTION:
    This sample demonstrates how to make custom HTTP requests through a client pipeline synchronously.

USAGE:
    python send_request_sample.py

    Set the environment variables with your own values before running the sample:
    1) APPCONFIGURATION_CONNECTION_STRING: Connection String used to access the Azure App Configuration.
"""
import os
from azure.appconfiguration import AzureAppConfigurationClient
from azure.core.rest import HttpRequest


def main():
    CONNECTION_STRING = os.environ["APPCONFIGURATION_CONNECTION_STRING"]
    with AzureAppConfigurationClient.from_connection_string(CONNECTION_STRING) as client:
        request = HttpRequest(
            method="GET",
            url="/kv?api-version=2023-10-01",
        )
        response = client.send_request(request)
        print(response.status_code)


if __name__ == "__main__":
    main()
