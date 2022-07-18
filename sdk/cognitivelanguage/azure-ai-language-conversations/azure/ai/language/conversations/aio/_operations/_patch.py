# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from ._operations import ConversationAnalysisClientOperationsMixin as ConversationAnalysisClientOperationsMixinGenerated


ConversationAnalysisClientOperationsMixinGenerated.analyze_conversation.__doc__ = \
    """Analyzes the input conversation utterance.

    See https://docs.microsoft.com/rest/api/language/conversation-analysis-runtime/analyze-conversation
    for more information.

    :param task: A single conversational task to execute. Is either a model type or a IO type.
     Required.
    :type task: JSON or IO
    :keyword content_type: Body Parameter content-type. Known values are: 'application/json'.
     Default value is None.
    :paramtype content_type: str
    :return: JSON object
    :rtype: JSON
    :raises ~azure.core.exceptions.HttpResponseError:

    Example:
        .. code-block:: python

            # JSON input template you can fill out and use as your body input.
            task = {
                "kind": "str", # Required. Enumeration of supported Conversation tasks. Known values are: "Conversation".
                "analysisInput": {
                    "conversationItem": {
                        "id": "str", # Required. The ID of a conversation item.
                        "participantId": "str", # Required. The participant ID of a conversation item.
                        "modality": "string", # Required, Enumeration of supported conversational modalities. Known values are: "text", and "transcript".
                        "language": "str", # Optional. The override language of a conversation item in BCP 47 language representation.
                        "text": "str", # Required. The text input.
                        "role": "str"  # Optional. The role of the participant. Known values are: "agent", "customer", and "generic".
                    }
                },
                "parameters": {
                    "projectName": "str", # Required. The name of the project to use.
                    "deploymentName": "str", # Required. The name of the deployment to use.
                    "stringIndexType": "str",  # Optional. Default value is
                      "TextElements_v8". Specifies the method used to interpret string offsets. Set
                      to "UnicodeCodePoint" for Python strings. Known values are:
                      "TextElements_v8", "UnicodeCodePoint", and "Utf16CodeUnit".
                    "verbose": "bool", # Optional. If true, the service will return more detailed information in the response.
                    "isLoggingEnabled": "bool", # Optional. If true, the service will keep the query for further review.
                    "directTarget": "str", # Optional. The name of a target project to forward the request to.
                    "targetProjectParameters": "dict" # Optional. A dictionary representing the parameters for each target project.
                }
            }

            # The response is polymorphic. The following are possible polymorphic responses based
            off discriminator "kind":

            # response body for status code(s): 200
            response.json() == {
                "kind": "str", # Required. Enumeration of supported conversational task results. Known values are: "ConversationResult".
                "result": {
                    "query": "str", # Required. The conversation utterance given by the caller.
                    "detectedLanguage": "str", # Optional. The system detected language for the query in BCP 47 language representation.
                    "prediction": {
                        "topIntent": "str", # Required. The intent with the highest score.
                        "projectKind": "str", # Required. The type of the project. Known values are: "Conversation" and "Orchestration".
                    }
                }
            }
    """

ConversationAnalysisClientOperationsMixinGenerated.begin_conversation_analysis.__doc__ = \
    """Submit analysis job for conversations.
    
    Submit a collection of conversations for analysis. Specify one or more unique tasks to be
    executed.
    
    :param task: The collection of conversations to analyze and one or more tasks to execute. Is
     either a model type or a IO type. Required.
    :type task: JSON or IO
    :keyword content_type: Body Parameter content-type. Known values are: 'application/json'.
     Default value is None.
    :paramtype content_type: str
    :keyword str continuation_token: A continuation token to restart a poller from a saved state.
    :keyword polling: By default, your polling method will be AsyncLROBasePolling. Pass in False
     for this operation to not poll, or pass in your own initialized polling object for a personal
     polling strategy.
    :paramtype polling: bool or ~azure.core.polling.AsyncPollingMethod
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    :return: An instance of AsyncLROPoller that returns JSON object
    :rtype: ~azure.core.polling.AsyncLROPoller[JSON]
    :raises ~azure.core.exceptions.HttpResponseError:

    .. versionadded:: 2022-05-15-preview
        The *begin_conversation_analysis* client method.

    Example:
        .. code-block:: python

            # JSON input template you can fill out and use as your body input.
            task = {
              "displayName": "str",  # Optional. Display name for the analysis job.
              "analysisInput": {
                "conversations": [
                    ... # A list of text_conversation or transcript_conversation (see below)
                ]
              },
              "tasks": [
                {
                  "taskName": "str",  # Optional. Associate a name with the task.
                  "kind": "str",  # Required. Known values are "ConversationalPIITask" and "ConversationalSummarizationTask".
                  "parameters": {
                    ... # summarization_task_parameters or pii_task_parameters (see below)
                  }
                }
              ]
            }

            text_conversation = {
              "id": "str",  # Required. Unique identifier for the conversation.
              "language": "str",  # Required. The language of the conversation item in BCP-47 format.
              "modality": "str",  # Required. Known values are: "transcript" and "text".
              "domain": "str",  # Optional. Known values are "finance", "healthcare", and "generic".
              "conversationItems": [  # Ordered list of text conversation items in the conversation.
                {
                  "id": "str", # Required. The ID of a conversation item.
                  "participantId": "str", # Required. The participant ID of a conversation item.
                  "modality": "string", # Required. Enumeration of supported conversational modalities.
                    Known values are: "text", and "transcript".
                  "language": "str", # Optional. The override language of a conversation item in BCP 47 language
                    representation.
                  "role": "str",  # Optional. The role of the participant. Known values are: "agent", "customer",
                    and "generic".
                  "text": "str"  # Required. The text input
                }
              ]
            }

            transcript_conversation = {
                "id": "str",  # Required. Unique identifier for the conversation.
                "language": "str",  # Required. The language of the conversation item in BCP-47 format.
                "modality": "str",  # Required. Known values are: "transcript" and "text".
                "domain": "str",  # Optional. Known values are "finance", "healthcare", and "generic".
                "conversationItems": [  # Ordered list of transcript conversation items in the conversation.
                    {
                        "id": "str",  # Required. The ID of a conversation item.
                        "participantId": "str",  # Required. The participant ID of a conversation item.
                        "modality": "string",  # Required. Enumeration of supported conversational modalities.
                          Known values are: "text", and "transcript".
                        "language": "str",  # Optional. The override language of a conversation item in BCP 47 language
                          representation.
                        "role": "str",  # Optional. The role of the participant. Known values are: "agent", "customer",
                          and "generic".
                        "text": "str",  # Optional. The display form of the recognized text from speech to text API,
                          with punctuation and capitalization added.
                        "itn": "str",  # Optional. Inverse Text Normalization representation of input. The inverse -
                          text - normalized form is the recognized text from Microsoft's Speech to Text API, with
                          phone numbers, numbers, abbreviations, and other transformations applied.
                        "maskedItn": "str",  # Optional. The Inverse Text Normalized format with profanity masking applied.
                        "lexical": "str",  # Optional. The lexical form of the recognized text from speech to text
                          API with the actual words recognized.
                        "audioTimings": [  # Optional. The list of word level audio timing information.
                            {
                                "word": "str",  # Optional. The word recognized.
                                "offset": "int",  # Optional. Offset from start of speech audio, in ticks. 1 tick = 100 ns.
                                "duration": "int"  # Optional. Duration of word articulation, in ticks. 1 tick = 100 ns.
                            }
                        ]
                    }
                ]
            }

            summarization_task_parameters = {
              "modelVersion": "str",  # Optional. The model version to use. Defaults to "latest".
              "loggingOptOut": "bool",  # Optional. Defaults to false.
              "summaryAspects": "array"  # Required. A list of summary aspects. Known values are
                "issue" and "resolution".
            }

            pii_task_parameters = {
              "modelVersion": "str",  # Optional. The model version to use. Defaults to "latest".
              "loggingOptOut": "bool",  # Optional. Defaults to false.
              "piiCategories": "array",  # Optional. Describes the PII categories to return for detection.
                If not provided, 'default' categories will be returned which will vary with the language. Known values
                are "Address", "CreditCard", "Email", "Name", "NumericIdentifier", "PhoneNumber", "All", "Default".
              "redactionSource": "str",  # Optional. Supported content types. Known values are "lexical", "itn",
                "maskedItn", and "text".
              "includeAudioRedaction": "bool" # Optional. Defaults to false. Flag to indicate if audio redaction
                is requested. By default audio redaction will not be performed.
            }

            # The response is polymorphic. The following are possible polymorphic responses based
            off discriminator "kind":

            # response body for status code(s): 200
            response == {
                "createdDateTime": "2020-02-20 00:00:00",  # Required.
                "displayName": "str",  # Optional.
                "errors": [
                    {
                        "code": "str",  # One of a server-defined set of error codes.
                          Required. Known values are: "InvalidRequest", "InvalidArgument",
                          "Unauthorized", "Forbidden", "NotFound", "ProjectNotFound",
                          "OperationNotFound", "AzureCognitiveSearchNotFound",
                          "AzureCognitiveSearchIndexNotFound", "TooManyRequests",
                          "AzureCognitiveSearchThrottling",
                          "AzureCognitiveSearchIndexLimitReached", "InternalServerError",
                          "ServiceUnavailable", "Timeout", "QuotaExceeded", "Conflict", and
                          "Warning".
                        "details": [
                            ...
                        ],
                        "innererror": {
                            "code": "str",  # One of a server-defined set of
                              error codes. Required. Known values are: "InvalidRequest",
                              "InvalidParameterValue", "KnowledgeBaseNotFound",
                              "AzureCognitiveSearchNotFound", "AzureCognitiveSearchThrottling",
                              "ExtractionFailure", "InvalidRequestBodyFormat", "EmptyRequest",
                              "MissingInputDocuments", "InvalidDocument", "ModelVersionIncorrect",
                              "InvalidDocumentBatch", "UnsupportedLanguageCode", and
                              "InvalidCountryHint".
                            "details": {
                                "str": "str"  # Optional. Error details.
                            },
                            "innererror": ...,
                            "message": "str",  # Error message. Required.
                            "target": "str"  # Optional. Error target.
                        },
                        "message": "str",  # A human-readable representation of the
                          error. Required.
                        "target": "str"  # Optional. The target of the error.
                    }
                ],
                "expirationDateTime": "2020-02-20 00:00:00",  # Optional.
                "jobId": "str",  # Required.
                "lastUpdatedDateTime": "2020-02-20 00:00:00",  # Required.
                "nextLink": "str",  # Optional.
                "statistics": {
                    "conversationsCount": 0,  # Number of conversations submitted in the
                      request. Required.
                    "erroneousConversationsCount": 0,  # Number of invalid documents.
                      This includes empty, over-size limit or non-supported languages documents.
                      Required.
                    "transactionsCount": 0,  # Number of transactions for the request.
                      Required.
                    "validConversationsCount": 0  # Number of conversations documents.
                      This excludes empty, over-size limit or non-supported languages documents.
                      Required.
                },
                "status": "str",  # Required. Known values are: "notStarted", "running",
                  "succeeded", "partiallyCompleted", "failed", "cancelled", and "cancelling".
                "tasks": {
                    "completed": 0,  # Count of tasks completed successfully. Required.
                    "failed": 0,  # Count of tasks that failed. Required.
                    "inProgress": 0,  # Count of tasks in progress currently. Required.
                    "items": [
                        {
                          "kind": "str", # Required. Enumeration of supported Conversation Analysis task results.
                            Known values are: "conversationalSummarizationResults" and "conversationalPIIResults". 
                          "taskName": "str", # Optional. Associated name with the task.
                          "lastUpdateDateTime": "str", # Required. The last updated time in UTC for the task.
                          "status": "str", # Required. The status of the task at the mentioned last update time.
                            Known values are: "notStarted", "running", "succeeded", "failed", "cancelled", "cancelling".
                          "results": [ 
                              ... 
                           ]  # Optional. List of results from tasks (if available).
                        }
                    ],
                    "total": 0  # Total count of tasks submitted as part of the job.
                      Required.
                }
            }
    """


class ConversationAnalysisClientOperationsMixin(ConversationAnalysisClientOperationsMixinGenerated):
    ...


__all__: List[str] = [
    "ConversationAnalysisClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
