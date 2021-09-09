 # -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

RESOURCE_SOURCE = "8:acs:resource_source"
RESOURCE_TARGET = "8:acs:resource_target"
Phone_Number = "+14255550123"
CALL_ID = "cad9df7b-f3ac-4c53-96f7-c76e7437b3c1"
CALLBACK_URI = "callBackUri"
CONNECTION_STRING = "endpoint=https://REDACTED.communication.azure.com/;accesskey=eyJhbG=="
FAKE_ENDPOINT = "https://endpoint"
FAKE_TOKEN = "Fake Token"
CALL_SUBJECT = "testsubject"
CreateOrJoinCallPayload={
            "callLegId": CALL_ID,
            "callConnectionId": CALL_ID,
            }
ErrorPayload={"msg": "some error"}

ClientType_ConnectionString = "use connectionString"
ClientType_ManagedIdentity = "use managedIdentity"

SEVERCALL_ID = "b3ba87f4-9daf-4d0b-b95a-53d955a40577"