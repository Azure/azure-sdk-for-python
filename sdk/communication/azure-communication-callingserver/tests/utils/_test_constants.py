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

CALL_ID = "cad9df7b-f3ac-4c53-96f7-c76e7437b3c1"
SERVER_CALL_ID = "0d11d342-297f-4584-bb92-13fcbb3ae3bd"
FAKE_ENDPOINT = "https://endpoint"
FAKE_TOKEN = "Fake Token"
CALL_SUBJECT = "testsubject"
OPERATION_ID = "dummyId"
TIMEOUT_IN_SECONDS = 1

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

# Common
PHONE_NUMBER = "+14255550123"
OPERATION_CONTEXT = "dummyOperationContext"
INCOMING_CALL_CONTEXT = "dummyIncomingCallContext"
AUDIO_ROUTING_GROUP_ID = "0e54921f-69db-4bd4-b99a-790538ab9708"
COMMUNICATION_USER_Id_01 = "8:acs:b9612345-fd0b-480c-8fd2-cb58b70eab9f_acacdeb5-dba7-479b-ab45-5e76469d87b2"
COMMUNICATION_USER_Id_02 = "8:acs:b9612345-fd0b-480c-8fd2-cb58b70eab9f_f95c7b38-6c4e-4898-93b3-2553402304d6"
RESOURCE_SOURCE = "8:acs:6dbaf0ca-ec52-4202-a2ca-71fd2e09e5cd_4488bddf-549b-46f6-afd8-2e1fcd598c20"
RESOURCE_TARGET = "8:acs:f6b516eb-7787-4eee-ada5-00d3ad16038c_7664814d-78a7-440c-9f44-3b5d2c746c11"
PARTICIPANT_ID_01 = "d114c51f-03f1-4dcf-84ed-0a5bb56f17a7"
PARTICIPANT_ID_02 = "321a1144-ba7c-4a3d-af45-017bb6c52706"
MEDIA_OPERATION_ID = "dummyMediaOperationId"
USER_TO_USER_INFORMATION = "dummyUserToUserInformation"

# CreateOrJoinCallPayload
CreateOrJoinCallPayload={
    "callLegId": CALL_ID,
    "callConnectionId": CALL_ID,
    }

# AnswerCallPayload
AnswerCallResponsePayload={
    "callConnectionId": CALL_ID
    }

# GetParticipantsPayload
GetParticipantsResponsePayload=[
    {
    "identifier": {
        "communicationUser": {
                "id": COMMUNICATION_USER_Id_01
            }
        },
    "participantId": PARTICIPANT_ID_01,
    "isMuted": "false"
    },
    {
    "identifier": {
        "phoneNumber": {
                "value": PHONE_NUMBER
            }
        },
    "participantId": PARTICIPANT_ID_02,
    "isMuted": "true"
    }
    ]

# GetParticipantPayload
GetParticipantResponsePayload=[{
    "identifier": {
        "communicationUser": {
                "id": COMMUNICATION_USER_Id_01
            }
        },
    "participantId": PARTICIPANT_ID_01,
    "isMuted": "false"
    }]

ErrorPayload={
    "operationId": OPERATION_ID,
    "status": "failed",
    "operationContext": OPERATION_CONTEXT,
    "resultInfo": {
        "code": 404,
        "subcode": 404,
        "message": "Resource not found on the server."
        }
    }
ClientType_ConnectionString = "use connectionString"
ClientType_ManagedIdentity = "use managedIdentity"
CALLBACK_URI = "https://bot.contoso.io/callback"
CONNECTION_STRING = "endpoint=https://REDACTED.communication.azure.com/;accesskey=eyJhbG=="


SEVERCALL_ID = "aHKW9HM6Ly9jb252ZXJzYXRpb24tc2VydmljZS11cmwvYXBpL3YyL2VwL2NvbnYvc2Rjc3NlaVdiUV8wLVNCTE9peG1NWHRRP2k9OSZlPTYzNzU1MDY4NDM3MDUzNTAwMQ=="
GROUPCALL_ID = "507ad2dc-5a40-4d85-b2d9-cf214d469638"

SERVER_CALL_LOCATOR = "serverCallLocator"
GROUP_CALL_LOCATOR = "groupCallLocator"

COMMUNICATION_USER_KIND = "communication_user"
PHONE_NUMBER_KIND = "phone_number"

AUDIOROUTINGMODE_ONE_TO_ONE = "oneToOne"
AUDIOROUTINGMODE_MULTICAST = "multicast"

CALL_STATE_CONNECTED = "connected"
MEDIA_TYPES_AUDIO = "audio"
MEDIA_TYPES_VIDEO = "video"
CALLEVENTS_DTMFRECEIVED = "dtmfReceived"
CALLEVENTS_PARTICIPANTSUPDATED = "participantsUpdated"

# GetCallResponsePayload
GetCallResponsePayload = {
    "callConnectionId": CALL_ID,
    "source": {
          "communicationUser": {
            "id": COMMUNICATION_USER_Id_01
          }
        },
    "targets": [
        {
        "communicationUser": {
            "id": COMMUNICATION_USER_Id_02
        }
        },
        {
        "phoneNumber": {
            "value": PHONE_NUMBER
        }
        }
    ],
    "callConnectionState": CALL_STATE_CONNECTED,
    "subject": CALL_SUBJECT,
    "callbackUri": AppCallbackUrl,
    "requestedMediaTypes": [
        MEDIA_TYPES_AUDIO,
        MEDIA_TYPES_VIDEO
    ],
    "requestedCallEvents": [
        CALLEVENTS_DTMFRECEIVED,
        CALLEVENTS_PARTICIPANTSUPDATED
    ],
    "callLocator": {
          "serverCallId": SEVERCALL_ID,
          "kind": SERVER_CALL_LOCATOR
        }
    }

# CancelAllMediaOperaionsPayload
CancelAllMediaOperaionsResponsePayload = {
    "operationId": OPERATION_ID,
    "status": "completed",
    "operationContext": OPERATION_CONTEXT,
    }

# PlayAudioPayload
AUDIO_FILE_URI = "https://bot.contoso.io/audio/sample-message.wav"
AUDIO_FILE_ID = "sampleAudioFileId"
PlayAudioResponsePayload = {
    "operationId": OPERATION_ID,
    "status": "running",
    "operationContext": OPERATION_CONTEXT
    }

# AddParticipantPayload
AddParticipantResultPayload = {
    "participantId": PARTICIPANT_ID_01
    }

# CreateAudioRoutingGroupPayload
AUDIO_FILE_URI = "https://bot.contoso.io/audio/sample-message.wav"
AUDIO_FILE_ID = "sampleAudioFileId"
CreateAudioRoutingGroupResponsePayload = {
    "audioRoutingGroupId": AUDIO_ROUTING_GROUP_ID,
    }

# GetAudioRoutingGroupPayload
AUDIO_FILE_URI = "https://bot.contoso.io/audio/sample-message.wav"
AUDIO_FILE_ID = "sampleAudioFileId"
GetAudioRoutingGroupResponsePayload = {
    "audioRoutingMode": "oneToOne",
        "targets": [
          {
            "communicationUser": {
              "id": RESOURCE_SOURCE
            }
          }
        ]
      }
