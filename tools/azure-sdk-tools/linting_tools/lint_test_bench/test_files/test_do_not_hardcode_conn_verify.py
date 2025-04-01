# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# This code violates do-not-harcode-connection-verify


from azure.core.pipeline.transport import RequestsTransport

def create_client():
    transport = RequestsTransport(connection_verify=False)  # Hardcoded to False
    return transport