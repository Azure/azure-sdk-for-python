# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import json
import logging
import websocket
from azure.identity import ManagedIdentityCredential, AzureCliCredential
from azure.keyvault.secrets import SecretClient
from jsonpath_ng import jsonpath, parse
from websocket import WebSocketConnectionClosedException

class AugLoopParams:
    def __init__(
            self,
            url: str,
            authTokenKeyVaultUrl: str,
            authTokenKeyVaultSecretName: str,
            annotationType: str,
            workflowName: str,
            signalType: str,
            signalBaseType: str,
            clientAppName: str,
            pathToMessages: str,
            annotationMessageParamName: str,
            pathToError: str = "",
            signalMessageParamName: str = "message",
            signalOtherParams: str = "",
            flights: str = "",
            cvBase: str = "eAieZY/LoqYfURDv1ao1W3",
            sessionId: str = "1ecf6906-090a-45b1-8d79-88defc62d3cc",
            runtimeVersion: str = "2.34.97",
            scenario: str = "",
            otherTokenKeyVaultSecretNames: list = []
):
        self.url = url
        self.authTokenKeyVaultUrl = authTokenKeyVaultUrl
        self.authTokenKeyVaultSecretName = authTokenKeyVaultSecretName
        self.annotationType = annotationType
        self.workflowName = workflowName
        self.signalType = signalType
        self.signalBaseType = signalBaseType
        self.clientAppName = clientAppName
        self.pathToMessages = pathToMessages
        self.annotationMessageParamName = annotationMessageParamName
        self.pathToError = pathToError
        self.signalMessageParamName = signalMessageParamName
        self.signalOtherParams = signalOtherParams
        self.flights = flights
        self.cvBase = cvBase
        self.sessionId = sessionId
        self.runtimeVersion = runtimeVersion
        self.otherTokenKeyVaultSecretNames = otherTokenKeyVaultSecretNames

        # if signalOtherParams is set, make sure it ends with a ","
        if (self.signalOtherParams != "" and not self.signalOtherParams.endswith(",")):
            self.signalOtherParams = self.signalOtherParams + ","

class AugLoopClient:
    def __init__(
        self,
        augLoopParams: AugLoopParams,
    ):
        self.augLoopParams = augLoopParams
        self.sequence = 0

        self.logger = logging.getLogger(repr(self))

        self.logger.info(f"Connecting Websocket")
        self.websocket = websocket.create_connection(self.augLoopParams.url)

        # send session init
        self.send_message_to_al(f'{{"protocolVersion":2,"clientMetadata":{{"appName":"{self.augLoopParams.clientAppName}","appPlatform":"Client","sessionId":"{self.augLoopParams.sessionId}","flights":"{self.augLoopParams.flights}","appVersion":"","uiLanguage":"","roamingServiceAppId":0,"runtimeVersion":"{self.augLoopParams.runtimeVersion}","docSessionId":"{self.augLoopParams.sessionId}"}},"extensionConfigs":[],"returnWorkflowInputTypes":false,"enableRemoteExecutionNotification":false,"H_":{{"T_":"AugLoop_Session_Protocol_SessionInitMessage","B_":["AugLoop_Session_Protocol_Message"]}},"cv":"{self.augLoopParams.cvBase}.{self.sequence}","messageId":"c{self.sequence}"}}')
        message = self.websocket.recv()
        self.logger.info(f"SessionInit Response: {message}")

        sessionInitResponse = json.loads(message)
        self.sessionKey = sessionInitResponse["sessionKey"]
        self.origin = sessionInitResponse["origin"]
        self.anonToken = sessionInitResponse["anonymousToken"]

        self.setup_session_after_init()

    # Deleting (Calling destructor)
    def __del__(self):
        self.logger.info(f"Closing Websocket")
        self.websocket.close()

    def send_signal_and_wait_for_annotation(self, message: str, isInRecursiveCall: bool = False):
        try:
            self.send_signal_message(message)

            responseMessage = None
            while True:
                responseMessage = self.websocket.recv()
                self.logger.info(f"Received message: {responseMessage}")

                if (responseMessage != None and self.augLoopParams.annotationType in responseMessage and self.augLoopParams.workflowName in responseMessage):
                    break

            if (responseMessage != None):
                response_json = json.loads(responseMessage)

                if (self.augLoopParams.pathToError != ""):
                    error_expr = parse(self.augLoopParams.pathToError)

                    self.logger.warn("Checking for error in response")
                    errorMessages = []
                    for errMatch in error_expr.find(response_json):
                        errorMessages.append(f'{errMatch.value["category"]}: {errMatch.value["message"]}')

                    if (errorMessages != None and len(errorMessages) > 0):
                        self.logger.warn("Found Error in response")
                        return { "id": response_json["cv"], "messages": errorMessages, "success": True, "full_message": response_json }

                self.logger.info("No error in response")
                
                response_expr = parse(self.augLoopParams.pathToMessages)
                responseMessages = []
                for match in response_expr.find(response_json):
                    if type(match.value) is str:
                        match_value =  json.loads(match.value)
                    else:
                        match_value = match.value

                    if self.augLoopParams.annotationMessageParamName not in match_value:
                        continue

                    if (("author" not in match_value or match_value["author"] != "user") and "messageType" not in match_value):
                        responseMessages.append(match_value[self.augLoopParams.annotationMessageParamName])

                return { "id": response_json["cv"], "messages": responseMessages, "success": True, "full_message": response_json }

            return { "success": False }
        except WebSocketConnectionClosedException:
            self.logger.info("Websocket is closed. Re-attempting connection")
            if (isInRecursiveCall == False):
                self.reconnect_and_attempt_session_init()

                return self.send_signal_and_wait_for_annotation(message = message, isInRecursiveCall = True)
            else:
                return { "success": False }
        except Exception as e:
            self.logger.error(f"Error: {str(e)}")
            # TODO: adding detailed message is not working, e disappears
            # if 'Expecting value: line 1 column 1 (char 0)' in str(e):
            #     self.logger.error(f"Check that augloop_bot_path_to_message param points to a JSON in the response")
            return { "success": False }


    def send_message_to_al(self, message: str):
        self.sequence += 1

        # make sure message does not have any new line characters
        lines = message.split('\n')

        for line in lines:
            line = line.lstrip()
            line = line.rstrip()

        message = ' '.join(lines)

        if ("authToken" not in message):
            self.logger.info(f"Sending message to AL: {message}")

        self.websocket.send(message)

    def send_signal_message(self, message: str):
        self.id = f'id{self.sequence}'
        message = message.replace('"', '\\"')
        self.send_message_to_al(f'{{"cv":"{self.augLoopParams.cvBase}.{self.sequence}","seq":{self.sequence},"ops":[{{"parentPath":["session","doc"],"prevId":"{self.prevId}","items":[{{"id":"{self.id}","body":{{"{self.augLoopParams.signalMessageParamName}":"{message}", {self.augLoopParams.signalOtherParams} "H_":{{"T_":"{self.augLoopParams.signalType}","B_":["{self.augLoopParams.signalBaseType}"]}}}},"contextId":"C{self.sequence}"}}],"H_":{{"T_":"AugLoop_Core_AddOperation","B_":["AugLoop_Core_OperationWithSiblingContext","AugLoop_Core_Operation"]}}}}],"H_":{{"T_":"AugLoop_Session_Protocol_SyncMessage","B_":["AugLoop_Session_Protocol_Message"]}},"messageId":"c{self.sequence}"}}')
        self.prevId = self.id

    def reconnect_and_attempt_session_init(self):
        if (self.sessionKey == None or self.sessionKey == ""):
            raise Exception("SessionKey Not Found!!")

        self.logger.info(f"Connecting Websocket again")
        self.websocket = websocket.create_connection(self.augLoopParams.url)

        # send session init
        self.send_message_to_al(f'{{"protocolVersion":2,"clientMetadata":{{"appName":"{self.augLoopParams.clientAppName}","appPlatform":"Client","sessionKey":"{self.sessionKey}","origin":"{self.origin}","anonymousToken":"{self.anonToken}","sessionId":"{self.augLoopParams.sessionId}","flights":"{self.augLoopParams.flights}","appVersion":"","uiLanguage":"","roamingServiceAppId":0,"runtimeVersion":"{self.augLoopParams.runtimeVersion}","docSessionId":"{self.augLoopParams.sessionId}"}},"extensionConfigs":[],"returnWorkflowInputTypes":false,"enableRemoteExecutionNotification":false,"H_":{{"T_":"AugLoop_Session_Protocol_SessionInitMessage","B_":["AugLoop_Session_Protocol_Message"]}},"cv":"{self.augLoopParams.cvBase}.{self.sequence}","messageId":"c{self.sequence}"}}')

        maxRetry=3
        while True:
            message = self.websocket.recv()
            self.logger.info(f"Re-SessionInit Response: {message}")

            if (message == None or message.find("AugLoop_Session_Protocol_SessionInitResponse") == -1):
                maxRetry = maxRetry -1
                if (maxRetry == 0):
                    raise Exception("SessionInit response not found!!")
                else:
                    self.logger.info(f"This is not session init, response so waiting on next response")
                    continue

            sessionInitResponse = json.loads(message)
            oldSessionKey = self.sessionKey
            self.sessionKey = sessionInitResponse["sessionKey"]
            self.origin = sessionInitResponse["origin"]
            self.anonToken = sessionInitResponse["anonymousToken"]
            break

        if self.sessionKey != oldSessionKey:
            self.logger.warn(f"Connected to a different session, previous: {self.sessionKey}, new: {sessionInitResponse['sessionKey']}")

            self.setup_session_after_init()


    def setup_session_after_init(self):
        # Activate annotation
        self.send_message_to_al(f'{{"annotationType":"{self.augLoopParams.annotationType}","token":"{self.augLoopParams.annotationType}-1","ignoreExistingAnnotations":false,"H_":{{"T_":"AugLoop_Session_Protocol_AnnotationActivationMessage","B_":["AugLoop_Session_Protocol_Message"]}},"cv":"{self.augLoopParams.cvBase}.{self.sequence}","messageId":"c{self.sequence}"}}')
        message = self.websocket.recv()
        self.logger.info(f"Ack for activate annotation: {message}")

        # auth token message
        token = self.get_auth_token()
        self.send_message_to_al(f'{{"authToken":"{token}","H_":{{"T_":"AugLoop_Session_Protocol_TokenProvisionMessage","B_":["AugLoop_Session_Protocol_Message"]}},"cv":"{self.augLoopParams.cvBase}.{self.sequence}","messageId":"c{self.sequence}"}}')
        message = self.websocket.recv()
        self.logger.info(f"Ack for auth token message: {message}")

        # add doc container to session
        self.send_message_to_al(f'{{"cv":"{self.augLoopParams.cvBase}.{self.sequence}","seq":{self.sequence},"ops":[{{"parentPath":["session"],"prevId":"#head","items":[{{"id":"doc","body":{{"isReadonly":false,"H_":{{"T_":"AugLoop_Core_Document","B_":["AugLoop_Core_TileGroup"]}}}},"contextId":"C{self.sequence}"}}],"H_":{{"T_":"AugLoop_Core_AddOperation","B_":["AugLoop_Core_OperationWithSiblingContext","AugLoop_Core_Operation"]}}}}],"H_":{{"T_":"AugLoop_Session_Protocol_SyncMessage","B_":["AugLoop_Session_Protocol_Message"]}},"messageId":"c{self.sequence}"}}')
        message = self.websocket.recv()
        self.logger.info(f"Ack for seed doc: {message}")

        self.prevId = "#head"


    def get_auth_token(self):
        # get augloop auth token
        identity_client_id = os.environ.get("DEFAULT_IDENTITY_CLIENT_ID", None)
        if identity_client_id is not None:
            self.logger.info(f"Using DEFAULT_IDENTITY_CLIENT_ID: {identity_client_id}")
            credential = ManagedIdentityCredential(client_id=identity_client_id)
        else:
            # Good for local testing.
            self.logger.info("Environment variable DEFAULT_IDENTITY_CLIENT_ID is not set, using DefaultAzureCredential")
            credential = AzureCliCredential()

        secret_client = SecretClient(vault_url=self.augLoopParams.authTokenKeyVaultUrl, credential=credential)
        auth_token = secret_client.get_secret(self.augLoopParams.authTokenKeyVaultSecretName).value
        self.logger.info(f"Obtained augloop auth token using AzureCliCredential: {auth_token and not auth_token.isspace()}")
        return auth_token
    
    def get_other_tokens(self):
        # get augloop auth token
        identity_client_id = os.environ.get("DEFAULT_IDENTITY_CLIENT_ID", None)
        if identity_client_id is not None:
            self.logger.info(f"Using DEFAULT_IDENTITY_CLIENT_ID: {identity_client_id}")
            credential = ManagedIdentityCredential(client_id=identity_client_id)
        else:
            # Good for local testing.
            self.logger.info("Environment variable DEFAULT_IDENTITY_CLIENT_ID is not set, using DefaultAzureCredential")
            credential = AzureCliCredential()

        secret_client = SecretClient(vault_url=self.augLoopParams.authTokenKeyVaultUrl, credential=credential)
        tokens = {}
        for name in self.augLoopParams.otherTokenKeyVaultSecretNames:
            tokens[name] = secret_client.get_secret(name).value
        self.logger.info(f"Obtained token '{name}' using AzureCliCredential: {tokens[name] and not tokens[name].isspace()}")
        return tokens