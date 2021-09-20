 # -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from devtools_testutils import is_live
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

RESOURCE_SOURCE = "8:acs:resource_source"
RESOURCE_TARGET = "8:acs:resource_target"
CALL_ID = "cad9df7b-f3ac-4c53-96f7-c76e7437b3c1"
SERVER_CALL_ID = "0d11d342-297f-4584-bb92-13fcbb3ae3bd"
FAKE_ENDPOINT = "https://endpoint"
FAKE_TOKEN = "Fake Token"
CALL_SUBJECT = "testsubject"

# System Environment Variables
# Live Test Variables
RESOURCE_IDENTIFIER = os.getenv(
    "COMMUNICATION_LIVETEST_STATIC_RESOURCE_IDENTIFIER",
    "016a7064-0581-40b9-be73-6dde64d69d72" # From ACS Resource "immutableResourceId".
    )
AZURE_TENANT_ID = RESOURCE_IDENTIFIER
SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS = is_live() or os.getenv("SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS", "false") == "true"
CALLINGSERVER_INTERACTION_LIVE_TESTS_SKIP_REASON = "SKIP_CALLINGSERVER_INTERACTION_LIVE_TESTS skips certain callingserver tests that required human interaction"

IncomingRequestSecret = "helloworld"
AppBaseUrl = "https://dummy.ngrok.io"
AppCallbackUrl = "{}/api/incident/callback?SecretKey={}".format(AppBaseUrl,quote(IncomingRequestSecret))
AudioFileName = "sample-message.wav"
AudioFileUrl = "{}/audio/{}".format(AppBaseUrl,AudioFileName)

# CreateOrJoinCall
CreateOrJoinCallPayload={
    "callLegId": CALL_ID,
    "callConnectionId": CALL_ID,
    }

# Common
PHONE_NUMBER = "+14255550123"
OPERATION_CONTEXT = "dummyOperationContext"
ErrorPayload={"msg": "some error"}
ClientType_ConnectionString = "use connectionString"
ClientType_ManagedIdentity = "use managedIdentity"
CALLBACK_URI = "https://bot.contoso.io/callback"
CONNECTION_STRING = "endpoint=https://REDACTED.communication.azure.com/;accesskey=eyJhbG=="
PARTICIPANT_ID = "dummyParticipantId"
MEDIA_OPERATION_ID = "dummyMediaOperationId"
USER_TO_USER_INFORMATION = "dummyUserToUserInformation"

# CancelAllMediaOperaions
CancelAllMediaOperaionsResponsePayload = {
    "operationId": "dummyId",
    "status": "completed",
    "operationContext": OPERATION_CONTEXT,
    "resultInfo": {
        "code": 200,
        "subcode": 200,
        "message": "dummyMessage"
        }
    }

SEVERCALL_ID = "b3ba87f4-9daf-4d0b-b95a-53d955a40577"

# PlayAudio
AUDIO_FILE_URI = "https://bot.contoso.io/audio/sample-message.wav"
AUDIO_FILE_ID = "sampleAudioFileId"
PlayAudioResponsePayload = {
    "operationId": "dummyId",
    "status": "running",
    "operationContext": OPERATION_CONTEXT,
    "resultInfo": {
        "code": 200,
        "subcode": 200,
        "message": "dummyMessage"
        }
    }

# AddParticipant
AddParticipantResultPayload = {
    "participantId": PARTICIPANT_ID
    }

