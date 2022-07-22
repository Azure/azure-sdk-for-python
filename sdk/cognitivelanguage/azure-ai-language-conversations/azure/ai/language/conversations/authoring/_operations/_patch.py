# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from ._operations import ConversationAuthoringClientOperationsMixin as ConversationAuthoringClientOperationsMixinGenerated


ConversationAuthoringClientOperationsMixinGenerated.list_projects.__doc__ = \
    """Lists the existing projects.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/list-projects
    for more information.
    
    :keyword top: The maximum number of resources to return from the collection. Default value is
     None.
    :paramtype top: int
    :keyword skip: An offset into the collection of the first resource to be returned. Default
     value is None.
    :paramtype skip: int
    :return: An iterator like instance of JSON object
    :rtype: ~azure.core.paging.ItemPaged[JSON]
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "createdDateTime": "2020-02-20 00:00:00",  # Represents the project creation
                  datetime. Required.
                "description": "str",  # Optional. The project description.
                "language": "str",  # The project language. This is BCP-47 representation of
                  a language. For example, use "en" for English, "en-gb" for English (UK), "es" for
                  Spanish etc. Required.
                "lastDeployedDateTime": "2020-02-20 00:00:00",  # Optional. Represents the
                  project last deployed datetime.
                "lastModifiedDateTime": "2020-02-20 00:00:00",  # Represents the project
                  creation datetime. Required.
                "lastTrainedDateTime": "2020-02-20 00:00:00",  # Optional. Represents the
                  project last trained datetime.
                "multilingual": bool,  # Optional. Whether the project would be used for
                  multiple languages or not.
                "projectKind": "str",  # Represents the project kind. Required. Known values
                  are: "Conversation" and "Orchestration".
                "projectName": "str",  # The new project name. Required.
                "settings": {
                    "confidenceThreshold": 0.0  # The threshold of the intent with the
                      highest confidence, at which the prediction will automatically be changed to
                      "None". Required.
                }
            }
    """


ConversationAuthoringClientOperationsMixinGenerated.create_project.__doc__ = \
    """Creates a new project or updates an existing one.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/create-project
    for more information.
    
    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :param project: The project parameters. Is either a model type or a IO type. Required.
    :type project: JSON or IO
    :keyword content_type: Body Parameter content-type. Known values are:
     'application/merge-patch+json'. Default value is None.
    :paramtype content_type: str
    :return: JSON object
    :rtype: JSON
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python

            # JSON input template you can fill out and use as your body input.
            project = {
                "description": "str",  # Optional. The project description.
                "language": "str",  # The project language. This is BCP-47 representation of
                  a language. For example, use "en" for English, "en-gb" for English (UK), "es" for
                  Spanish etc. Required.
                "multilingual": bool,  # Optional. Whether the project would be used for
                  multiple languages or not.
                "projectKind": "str",  # Represents the project kind. Required. Known values
                  are: "Conversation" and "Orchestration".
                "projectName": "str",  # The new project name. Required.
                "settings": {
                    "confidenceThreshold": 0.0  # The threshold of the intent with the
                      highest confidence, at which the prediction will automatically be changed to
                      "None". Required.
                }
            }

            # response body for status code(s): 200, 201
            response == {
                "createdDateTime": "2020-02-20 00:00:00",  # Represents the project creation
                  datetime. Required.
                "description": "str",  # Optional. The project description.
                "language": "str",  # The project language. This is BCP-47 representation of
                  a language. For example, use "en" for English, "en-gb" for English (UK), "es" for
                  Spanish etc. Required.
                "lastDeployedDateTime": "2020-02-20 00:00:00",  # Optional. Represents the
                  project last deployed datetime.
                "lastModifiedDateTime": "2020-02-20 00:00:00",  # Represents the project
                  creation datetime. Required.
                "lastTrainedDateTime": "2020-02-20 00:00:00",  # Optional. Represents the
                  project last trained datetime.
                "multilingual": bool,  # Optional. Whether the project would be used for
                  multiple languages or not.
                "projectKind": "str",  # Represents the project kind. Required. Known values
                  are: "Conversation" and "Orchestration".
                "projectName": "str",  # The new project name. Required.
                "settings": {
                    "confidenceThreshold": 0.0  # The threshold of the intent with the
                      highest confidence, at which the prediction will automatically be changed to
                      "None". Required.
                }
            }
    """


ConversationAuthoringClientOperationsMixinGenerated.get_project.__doc__ = \
    """Gets the details of a project.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/get-project for
    more information.

    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :return: JSON object
    :rtype: JSON
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "createdDateTime": "2020-02-20 00:00:00",  # Represents the project creation
                  datetime. Required.
                "description": "str",  # Optional. The project description.
                "language": "str",  # The project language. This is BCP-47 representation of
                  a language. For example, use "en" for English, "en-gb" for English (UK), "es" for
                  Spanish etc. Required.
                "lastDeployedDateTime": "2020-02-20 00:00:00",  # Optional. Represents the
                  project last deployed datetime.
                "lastModifiedDateTime": "2020-02-20 00:00:00",  # Represents the project
                  creation datetime. Required.
                "lastTrainedDateTime": "2020-02-20 00:00:00",  # Optional. Represents the
                  project last trained datetime.
                "multilingual": bool,  # Optional. Whether the project would be used for
                  multiple languages or not.
                "projectKind": "str",  # Represents the project kind. Required. Known values
                  are: "Conversation" and "Orchestration".
                "projectName": "str",  # The new project name. Required.
                "settings": {
                    "confidenceThreshold": 0.0  # The threshold of the intent with the
                      highest confidence, at which the prediction will automatically be changed to
                      "None". Required.
                }
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.begin_delete_project.__doc__ = \
    """Deletes a project.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/delete-project
    for more information.

    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :keyword str continuation_token: A continuation token to restart a poller from a saved state.
    :keyword polling: By default, your polling method will be LROBasePolling. Pass in False for
     this operation to not poll, or pass in your own initialized polling object for a personal
     polling strategy.
    :paramtype polling: bool or ~azure.core.polling.PollingMethod
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    :return: An instance of LROPoller that returns JSON object
    :rtype: ~azure.core.polling.LROPoller[JSON]
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "createdDateTime": "2020-02-20 00:00:00",  # The creation date time of the
                  job. Required.
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
                "expirationDateTime": "2020-02-20 00:00:00",  # Optional. The expiration date
                  time of the job.
                "jobId": "str",  # The job ID. Required.
                "lastUpdatedDateTime": "2020-02-20 00:00:00",  # The last date time the job
                  was updated. Required.
                "status": "str",  # The job status. Required. Known values are: "notStarted",
                  "running", "succeeded", "failed", "cancelled", "cancelling", and
                  "partiallyCompleted".
                "warnings": [
                    {
                        "code": "str",  # The warning code. Required.
                        "message": "str"  # The warning message. Required.
                    }
                ]
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.begin_export_project.__doc__ = \
    """Triggers a job to export a project's data.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/export for more
    information.
    
    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :keyword string_index_type: Specifies the method used to interpret string offsets. For
     additional information see https://aka.ms/text-analytics-offsets. "Utf16CodeUnit" Required.
    :paramtype string_index_type: str
    :keyword exported_project_format: The format of the exported project file to use. Known values
     are: "Conversation" and "Luis". Default value is None.
    :paramtype exported_project_format: str
    :keyword asset_kind: Kind of asset to export. Default value is None.
    :paramtype asset_kind: str
    :keyword str continuation_token: A continuation token to restart a poller from a saved state.
    :keyword polling: By default, your polling method will be LROBasePolling. Pass in False for
     this operation to not poll, or pass in your own initialized polling object for a personal
     polling strategy.
    :paramtype polling: bool or ~azure.core.polling.PollingMethod
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    :return: An instance of LROPoller that returns JSON object
    :rtype: ~azure.core.polling.LROPoller[JSON]
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "createdDateTime": "2020-02-20 00:00:00",  # The creation date time of the
                  job. Required.
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
                "expirationDateTime": "2020-02-20 00:00:00",  # Optional. The expiration date
                  time of the job.
                "jobId": "str",  # The job ID. Required.
                "lastUpdatedDateTime": "2020-02-20 00:00:00",  # The last date time the job
                  was updated. Required.
                "resultUrl": "str",  # Optional. The URL to use in order to download the
                  exported project.
                "status": "str",  # The job status. Required. Known values are: "notStarted",
                  "running", "succeeded", "failed", "cancelled", "cancelling", and
                  "partiallyCompleted".
                "warnings": [
                    {
                        "code": "str",  # The warning code. Required.
                        "message": "str"  # The warning message. Required.
                    }
                ]
            }
    """


ConversationAuthoringClientOperationsMixinGenerated.begin_import_project.__doc__ = \
    """Triggers a job to import a project. If a project with the same name already exists, the data of
    that project is replaced.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/import for more
    information.
    
    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :param project: The project data to import. Is either a model type or a IO type. Required.
    :type project: JSON or IO
    :keyword exported_project_format: The format of the exported project file to use. Known values
     are: "Conversation" and "Luis". Default value is None.
    :paramtype exported_project_format: str
    :keyword content_type: Body Parameter content-type. Known values are: 'application/json'.
     Default value is None.
    :paramtype content_type: str
    :keyword str continuation_token: A continuation token to restart a poller from a saved state.
    :keyword polling: By default, your polling method will be LROBasePolling. Pass in False for
     this operation to not poll, or pass in your own initialized polling object for a personal
     polling strategy.
    :paramtype polling: bool or ~azure.core.polling.PollingMethod
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    :return: An instance of LROPoller that returns JSON object
    :rtype: ~azure.core.polling.LROPoller[JSON]
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python

            # JSON input template you can fill out and use as your body input.
            project = {
                "assets": exported_project_assets,
                "metadata": {
                    "description": "str",  # Optional. The project description.
                    "language": "str",  # The project language. This is BCP-47
                      representation of a language. For example, use "en" for English, "en-gb" for
                      English (UK), "es" for Spanish etc. Required.
                    "multilingual": bool,  # Optional. Whether the project would be used
                      for multiple languages or not.
                    "projectKind": "str",  # Represents the project kind. Required. Known
                      values are: "Conversation" and "Orchestration".
                    "projectName": "str",  # The new project name. Required.
                    "settings": {
                        "confidenceThreshold": 0.0  # The threshold of the intent
                          with the highest confidence, at which the prediction will automatically
                          be changed to "None". Required.
                    }
                },
                "projectFileVersion": "str",  # The version of the exported file. Required.
                "stringIndexType": "str"  # Specifies the method used to interpret string
                  offsets. For additional information see https://aka.ms/text-analytics-offsets.
                  Required. "Utf16CodeUnit"
            }

            # response body for status code(s): 200
            response == {
                "createdDateTime": "2020-02-20 00:00:00",  # The creation date time of the
                  job. Required.
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
                "expirationDateTime": "2020-02-20 00:00:00",  # Optional. The expiration date
                  time of the job.
                "jobId": "str",  # The job ID. Required.
                "lastUpdatedDateTime": "2020-02-20 00:00:00",  # The last date time the job
                  was updated. Required.
                "status": "str",  # The job status. Required. Known values are: "notStarted",
                  "running", "succeeded", "failed", "cancelled", "cancelling", and
                  "partiallyCompleted".
                "warnings": [
                    {
                        "code": "str",  # The warning code. Required.
                        "message": "str"  # The warning message. Required.
                    }
                ]
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.begin_train.__doc__ = \
    """Triggers a training job for a project.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/train for more
    information.

    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :param configuration: The training input parameters. Is either a model type or a IO type.
     Required.
    :type configuration: JSON or IO
    :keyword content_type: Body Parameter content-type. Known values are: 'application/json'.
     Default value is None.
    :paramtype content_type: str
    :keyword str continuation_token: A continuation token to restart a poller from a saved state.
    :keyword polling: By default, your polling method will be LROBasePolling. Pass in False for
     this operation to not poll, or pass in your own initialized polling object for a personal
     polling strategy.
    :paramtype polling: bool or ~azure.core.polling.PollingMethod
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    :return: An instance of LROPoller that returns JSON object
    :rtype: ~azure.core.polling.LROPoller[JSON]
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python

            # JSON input template you can fill out and use as your body input.
            configuration = {
                "evaluationOptions": {
                    "kind": "str",  # Optional. Represents the evaluation kind. By
                      default, the evaluation kind is set to percentage. Known values are:
                      "percentage" and "manual".
                    "testingSplitPercentage": 0,  # Optional. Represents the testing
                      dataset split percentage. Only needed in case the evaluation kind is
                      percentage.
                    "trainingSplitPercentage": 0  # Optional. Represents the training
                      dataset split percentage. Only needed in case the evaluation kind is
                      percentage.
                },
                "modelLabel": "str",  # Represents the output model label. Required.
                "trainingConfigVersion": "str",  # Optional. Represents training config
                  version. By default, "latest" value is used which uses the latest released
                  training config version.
                "trainingMode": "str"  # Represents the mode of the training operation.
                  Required. Known values are: "advanced" and "standard".
            }

            # response body for status code(s): 200
            response == {
                "createdDateTime": "2020-02-20 00:00:00",  # The creation date time of the
                  job. Required.
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
                "expirationDateTime": "2020-02-20 00:00:00",  # Optional. The expiration date
                  time of the job.
                "jobId": "str",  # The job ID. Required.
                "lastUpdatedDateTime": "2020-02-20 00:00:00",  # The last date time the job
                  was updated. Required.
                "result": {
                    "estimatedEndDateTime": "2020-02-20 00:00:00",  # Optional.
                      Represents the estimated end date time for training and evaluation.
                    "evaluationStatus": {
                        "endDateTime": "2020-02-20 00:00:00",  # Optional. Represents
                          the end date time.
                        "percentComplete": 0,  # Represents progress percentage.
                          Required.
                        "startDateTime": "2020-02-20 00:00:00",  # Optional.
                          Represents the start date time.
                        "status": "str"  # Represents the status of the
                          sub-operation. Required. Known values are: "notStarted", "running",
                          "succeeded", "failed", "cancelled", "cancelling", and
                          "partiallyCompleted".
                    },
                    "modelLabel": "str",  # Represents trained model label. Required.
                    "trainingConfigVersion": "str",  # Represents training config
                      version. Required.
                    "trainingMode": "str",  # Optional. Represents the mode of the
                      training operation. Known values are: "advanced" and "standard".
                    "trainingStatus": {
                        "endDateTime": "2020-02-20 00:00:00",  # Optional. Represents
                          the end date time.
                        "percentComplete": 0,  # Represents progress percentage.
                          Required.
                        "startDateTime": "2020-02-20 00:00:00",  # Optional.
                          Represents the start date time.
                        "status": "str"  # Represents the status of the
                          sub-operation. Required. Known values are: "notStarted", "running",
                          "succeeded", "failed", "cancelled", "cancelling", and
                          "partiallyCompleted".
                    }
                },
                "status": "str",  # The job status. Required. Known values are: "notStarted",
                  "running", "succeeded", "failed", "cancelled", "cancelling", and
                  "partiallyCompleted".
                "warnings": [
                    {
                        "code": "str",  # The warning code. Required.
                        "message": "str"  # The warning message. Required.
                    }
                ]
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.list_deployments.__doc__ = \
    """Lists the deployments belonging to a project.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/list-deployments
    for more information.

    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :keyword top: The maximum number of resources to return from the collection. Default value is
     None.
    :paramtype top: int
    :keyword skip: An offset into the collection of the first resource to be returned. Default
     value is None.
    :paramtype skip: int
    :return: An iterator like instance of JSON object
    :rtype: ~azure.core.paging.ItemPaged[JSON]
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "deploymentExpirationDate": "2020-02-20",  # Represents deployment expiration
                  date in the runtime. Required.
                "deploymentName": "str",  # Represents deployment name. Required.
                "lastDeployedDateTime": "2020-02-20 00:00:00",  # Represents deployment last
                  deployed time. Required.
                "lastTrainedDateTime": "2020-02-20 00:00:00",  # Represents deployment last
                  trained time. Required.
                "modelId": "str",  # Represents deployment modelId. Required.
                "modelTrainingConfigVersion": "str"  # Represents model training config
                  version. Required.
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.begin_swap_deployments.__doc__ = \
    """Swaps two existing deployments with each other.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/swap-deployments
    for more information.

    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :param deployments: The job object to swap two deployments. Is either a model type or a IO
     type. Required.
    :type deployments: JSON or IO
    :keyword content_type: Body Parameter content-type. Known values are: 'application/json'.
     Default value is None.
    :paramtype content_type: str
    :keyword str continuation_token: A continuation token to restart a poller from a saved state.
    :keyword polling: By default, your polling method will be LROBasePolling. Pass in False for
     this operation to not poll, or pass in your own initialized polling object for a personal
     polling strategy.
    :paramtype polling: bool or ~azure.core.polling.PollingMethod
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    :return: An instance of LROPoller that returns JSON object
    :rtype: ~azure.core.polling.LROPoller[JSON]
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python

            # JSON input template you can fill out and use as your body input.
            deployments = {
                "firstDeploymentName": "str",  # Represents the first deployment name.
                  Required.
                "secondDeploymentName": "str"  # Represents the second deployment name.
                  Required.
            }

            # response body for status code(s): 200
            response == {
                "createdDateTime": "2020-02-20 00:00:00",  # The creation date time of the
                  job. Required.
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
                "expirationDateTime": "2020-02-20 00:00:00",  # Optional. The expiration date
                  time of the job.
                "jobId": "str",  # The job ID. Required.
                "lastUpdatedDateTime": "2020-02-20 00:00:00",  # The last date time the job
                  was updated. Required.
                "status": "str",  # The job status. Required. Known values are: "notStarted",
                  "running", "succeeded", "failed", "cancelled", "cancelling", and
                  "partiallyCompleted".
                "warnings": [
                    {
                        "code": "str",  # The warning code. Required.
                        "message": "str"  # The warning message. Required.
                    }
                ]
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.get_deployment.__doc__ = \
    """Gets the details of a deployment.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/get-deployment
    for more information.

    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :param deployment_name: The name of the specific deployment of the project to use. Required.
    :type deployment_name: str
    :return: JSON object
    :rtype: JSON
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "deploymentExpirationDate": "2020-02-20",  # Represents deployment expiration
                  date in the runtime. Required.
                "deploymentName": "str",  # Represents deployment name. Required.
                "lastDeployedDateTime": "2020-02-20 00:00:00",  # Represents deployment last
                  deployed time. Required.
                "lastTrainedDateTime": "2020-02-20 00:00:00",  # Represents deployment last
                  trained time. Required.
                "modelId": "str",  # Represents deployment modelId. Required.
                "modelTrainingConfigVersion": "str"  # Represents model training config
                  version. Required.
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.begin_deploy_project.__doc__ = \
    """Creates a new deployment or replaces an existing one.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/deploy-project
    for more information.

    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :param deployment_name: The name of the specific deployment of the project to use. Required.
    :type deployment_name: str
    :param deployment: The new deployment info. Is either a model type or a IO type. Required.
    :type deployment: JSON or IO
    :keyword content_type: Body Parameter content-type. Known values are: 'application/json'.
     Default value is None.
    :paramtype content_type: str
    :keyword str continuation_token: A continuation token to restart a poller from a saved state.
    :keyword polling: By default, your polling method will be LROBasePolling. Pass in False for
     this operation to not poll, or pass in your own initialized polling object for a personal
     polling strategy.
    :paramtype polling: bool or ~azure.core.polling.PollingMethod
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    :return: An instance of LROPoller that returns JSON object
    :rtype: ~azure.core.polling.LROPoller[JSON]
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python

            # JSON input template you can fill out and use as your body input.
            deployment = {
                "trainedModelLabel": "str"  # Represents the trained model label. Required.
            }

            # response body for status code(s): 200
            response == {
                "deploymentExpirationDate": "2020-02-20",  # Represents deployment expiration
                  date in the runtime. Required.
                "deploymentName": "str",  # Represents deployment name. Required.
                "lastDeployedDateTime": "2020-02-20 00:00:00",  # Represents deployment last
                  deployed time. Required.
                "lastTrainedDateTime": "2020-02-20 00:00:00",  # Represents deployment last
                  trained time. Required.
                "modelId": "str",  # Represents deployment modelId. Required.
                "modelTrainingConfigVersion": "str"  # Represents model training config
                  version. Required.
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.begin_delete_deployment.__doc__ = \
    """Deletes a project deployment.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/delete-deployment
    for more information.
    
    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :param deployment_name: The name of the specific deployment of the project to use. Required.
    :type deployment_name: str
    :keyword str continuation_token: A continuation token to restart a poller from a saved state.
    :keyword polling: By default, your polling method will be LROBasePolling. Pass in False for
     this operation to not poll, or pass in your own initialized polling object for a personal
     polling strategy.
    :paramtype polling: bool or ~azure.core.polling.PollingMethod
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    :return: An instance of LROPoller that returns JSON object
    :rtype: ~azure.core.polling.LROPoller[JSON]
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "createdDateTime": "2020-02-20 00:00:00",  # The creation date time of the
                  job. Required.
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
                "expirationDateTime": "2020-02-20 00:00:00",  # Optional. The expiration date
                  time of the job.
                "jobId": "str",  # The job ID. Required.
                "lastUpdatedDateTime": "2020-02-20 00:00:00",  # The last date time the job
                  was updated. Required.
                "status": "str",  # The job status. Required. Known values are: "notStarted",
                  "running", "succeeded", "failed", "cancelled", "cancelling", and
                  "partiallyCompleted".
                "warnings": [
                    {
                        "code": "str",  # The warning code. Required.
                        "message": "str"  # The warning message. Required.
                    }
                ]
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.get_deployment_job_status.__doc__ = \
    """Gets the status of an existing deployment job.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/get-deployment-status
    for more information.
    
    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :param deployment_name: The name of the specific deployment of the project to use. Required.
    :type deployment_name: str
    :param job_id: The job ID. Required.
    :type job_id: str
    :return: JSON object
    :rtype: JSON
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "createdDateTime": "2020-02-20 00:00:00",  # The creation date time of the
                  job. Required.
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
                "expirationDateTime": "2020-02-20 00:00:00",  # Optional. The expiration date
                  time of the job.
                "jobId": "str",  # The job ID. Required.
                "lastUpdatedDateTime": "2020-02-20 00:00:00",  # The last date time the job
                  was updated. Required.
                "status": "str",  # The job status. Required. Known values are: "notStarted",
                  "running", "succeeded", "failed", "cancelled", "cancelling", and
                  "partiallyCompleted".
                "warnings": [
                    {
                        "code": "str",  # The warning code. Required.
                        "message": "str"  # The warning message. Required.
                    }
                ]
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.get_swap_deployments_job_status.__doc__ = \
    """Gets the status of an existing swap deployment job.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/get-swap-deployments-status
    for more information.

    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :param job_id: The job ID. Required.
    :type job_id: str
    :return: JSON object
    :rtype: JSON
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "createdDateTime": "2020-02-20 00:00:00",  # The creation date time of the
                  job. Required.
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
                "expirationDateTime": "2020-02-20 00:00:00",  # Optional. The expiration date
                  time of the job.
                "jobId": "str",  # The job ID. Required.
                "lastUpdatedDateTime": "2020-02-20 00:00:00",  # The last date time the job
                  was updated. Required.
                "status": "str",  # The job status. Required. Known values are: "notStarted",
                  "running", "succeeded", "failed", "cancelled", "cancelling", and
                  "partiallyCompleted".
                "warnings": [
                    {
                        "code": "str",  # The warning code. Required.
                        "message": "str"  # The warning message. Required.
                    }
                ]
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.get_export_project_job_status.__doc__ = \
    """Gets the status of an export job. Once job completes, returns the project metadata, and assets.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/get-export-status
    for more information.

    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :param job_id: The job ID. Required.
    :type job_id: str
    :return: JSON object
    :rtype: JSON
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "createdDateTime": "2020-02-20 00:00:00",  # The creation date time of the
                  job. Required.
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
                "expirationDateTime": "2020-02-20 00:00:00",  # Optional. The expiration date
                  time of the job.
                "jobId": "str",  # The job ID. Required.
                "lastUpdatedDateTime": "2020-02-20 00:00:00",  # The last date time the job
                  was updated. Required.
                "resultUrl": "str",  # Optional. The URL to use in order to download the
                  exported project.
                "status": "str",  # The job status. Required. Known values are: "notStarted",
                  "running", "succeeded", "failed", "cancelled", "cancelling", and
                  "partiallyCompleted".
                "warnings": [
                    {
                        "code": "str",  # The warning code. Required.
                        "message": "str"  # The warning message. Required.
                    }
                ]
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.get_import_project_job_status.__doc__ = \
    """Gets the status for an import.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/get-import-status
    for more information.

    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :param job_id: The job ID. Required.
    :type job_id: str
    :return: JSON object
    :rtype: JSON
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "createdDateTime": "2020-02-20 00:00:00",  # The creation date time of the
                  job. Required.
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
                "expirationDateTime": "2020-02-20 00:00:00",  # Optional. The expiration date
                  time of the job.
                "jobId": "str",  # The job ID. Required.
                "lastUpdatedDateTime": "2020-02-20 00:00:00",  # The last date time the job
                  was updated. Required.
                "status": "str",  # The job status. Required. Known values are: "notStarted",
                  "running", "succeeded", "failed", "cancelled", "cancelling", and
                  "partiallyCompleted".
                "warnings": [
                    {
                        "code": "str",  # The warning code. Required.
                        "message": "str"  # The warning message. Required.
                    }
                ]
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.list_trained_models.__doc__ = \
    """Lists the trained models belonging to a project.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/list-trained-models
    for more information.

    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :keyword top: The maximum number of resources to return from the collection. Default value is
     None.
    :paramtype top: int
    :keyword skip: An offset into the collection of the first resource to be returned. Default
     value is None.
    :paramtype skip: int
    :return: An iterator like instance of JSON object
    :rtype: ~azure.core.paging.ItemPaged[JSON]
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "label": "str",  # The trained model label. Required.
                "lastTrainedDateTime": "2020-02-20 00:00:00",  # The last trained date time
                  of the model. Required.
                "lastTrainingDurationInSeconds": 0,  # The duration of the model's last
                  training request in seconds. Required.
                "modelExpirationDate": "2020-02-20",  # The model expiration date. Required.
                "modelId": "str",  # The model ID. Required.
                "modelTrainingConfigVersion": "str"  # The model training config version.
                  Required.
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.get_trained_model.__doc__ = \
    """Gets the details of a trained model.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/get-trained-model
    for more information.

    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :param trained_model_label: The trained model label. Required.
    :type trained_model_label: str
    :return: JSON object
    :rtype: JSON
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "label": "str",  # The trained model label. Required.
                "lastTrainedDateTime": "2020-02-20 00:00:00",  # The last trained date time
                  of the model. Required.
                "lastTrainingDurationInSeconds": 0,  # The duration of the model's last
                  training request in seconds. Required.
                "modelExpirationDate": "2020-02-20",  # The model expiration date. Required.
                "modelId": "str",  # The model ID. Required.
                "modelTrainingConfigVersion": "str"  # The model training config version.
                  Required.
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.delete_trained_model.__doc__ = \
    """Deletes an existing trained model.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/delete-trained-model
    for more information.

    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :param trained_model_label: The trained model label. Required.
    :type trained_model_label: str
    :return: None
    :rtype: None
    :raises ~azure.core.exceptions.HttpResponseError:
    """

ConversationAuthoringClientOperationsMixinGenerated.list_model_evaluation_results.__doc__ = \
    """Gets the detailed results of the evaluation for a trained model. This includes the raw
    inference results for the data included in the evaluation process.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/get-model-evaluation-results
    for more information.

    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :param trained_model_label: The trained model label. Required.
    :type trained_model_label: str
    :keyword string_index_type: Specifies the method used to interpret string offsets. For
     additional information see https://aka.ms/text-analytics-offsets. "Utf16CodeUnit" Required.
    :paramtype string_index_type: str
    :keyword top: The maximum number of resources to return from the collection. Default value is
     None.
    :paramtype top: int
    :keyword skip: An offset into the collection of the first resource to be returned. Default
     value is None.
    :paramtype skip: int
    :return: An iterator like instance of JSON object
    :rtype: ~azure.core.paging.ItemPaged[JSON]
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "entitiesResult": {
                    "expectedEntities": [
                        {
                            "category": "str",  # Represents the entity category.
                              Required.
                            "length": 0,  # Represents the entity length.
                              Required.
                            "offset": 0  # Represents the entity offset index
                              relative to the original text. Required.
                        }
                    ],
                    "predictedEntities": [
                        {
                            "category": "str",  # Represents the entity category.
                              Required.
                            "length": 0,  # Represents the entity length.
                              Required.
                            "offset": 0  # Represents the entity offset index
                              relative to the original text. Required.
                        }
                    ]
                },
                "intentsResult": {
                    "expectedIntent": "str",  # Represents the utterance's expected
                      intent. Required.
                    "predictedIntent": "str"  # Represents the utterance's predicted
                      intent. Required.
                },
                "language": "str",  # Represents the utterance language. This is BCP-47
                  representation of a language. For example, use "en" for English, "en-gb" for
                  English (UK), "es" for Spanish etc. Required.
                "text": "str"  # Represents the utterance text. Required.
            }
    """


ConversationAuthoringClientOperationsMixinGenerated.get_model_evaluation_summary.__doc__ = \
    """Gets the evaluation summary of a trained model. The summary includes high level performance
    measurements of the model e.g., F1, Precision, Recall, etc.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/get-model-evaluation-summary
    for more information.
    
    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :param trained_model_label: The trained model label. Required.
    :type trained_model_label: str
    :return: JSON object
    :rtype: JSON
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "entitiesEvaluation": {
                    "confusionMatrix": {
                        "str": {
                            "str": {
                                "normalizedValue": 0.0,  # Represents
                                  normalized value in percentages. Required.
                                "rawValue": 0.0  # Represents raw value.
                                  Required.
                            }
                        }
                    },
                    "entities": {
                        "str": {
                            "f1": 0.0,  # Represents the model precision.
                              Required.
                            "falseNegativeCount": 0,  # Represents the count of
                              false negative. Required.
                            "falsePositiveCount": 0,  # Represents the count of
                              false positive. Required.
                            "precision": 0.0,  # Represents the model recall.
                              Required.
                            "recall": 0.0,  # Represents the model F1 score.
                              Required.
                            "trueNegativeCount": 0,  # Represents the count of
                              true negative. Required.
                            "truePositiveCount": 0  # Represents the count of
                              true positive. Required.
                        }
                    },
                    "macroF1": 0.0,  # Represents the macro F1. Required.
                    "macroPrecision": 0.0,  # Represents the macro precision. Required.
                    "macroRecall": 0.0,  # Represents the macro recall. Required.
                    "microF1": 0.0,  # Represents the micro F1. Required.
                    "microPrecision": 0.0,  # Represents the micro precision. Required.
                    "microRecall": 0.0  # Represents the micro recall. Required.
                },
                "evaluationOptions": {
                    "kind": "str",  # Optional. Represents the evaluation kind. By
                      default, the evaluation kind is set to percentage. Known values are:
                      "percentage" and "manual".
                    "testingSplitPercentage": 0,  # Optional. Represents the testing
                      dataset split percentage. Only needed in case the evaluation kind is
                      percentage.
                    "trainingSplitPercentage": 0  # Optional. Represents the training
                      dataset split percentage. Only needed in case the evaluation kind is
                      percentage.
                },
                "intentsEvaluation": {
                    "confusionMatrix": {
                        "str": {
                            "str": {
                                "normalizedValue": 0.0,  # Represents
                                  normalized value in percentages. Required.
                                "rawValue": 0.0  # Represents raw value.
                                  Required.
                            }
                        }
                    },
                    "intents": {
                        "str": {
                            "f1": 0.0,  # Represents the model precision.
                              Required.
                            "falseNegativeCount": 0,  # Represents the count of
                              false negative. Required.
                            "falsePositiveCount": 0,  # Represents the count of
                              false positive. Required.
                            "precision": 0.0,  # Represents the model recall.
                              Required.
                            "recall": 0.0,  # Represents the model F1 score.
                              Required.
                            "trueNegativeCount": 0,  # Represents the count of
                              true negative. Required.
                            "truePositiveCount": 0  # Represents the count of
                              true positive. Required.
                        }
                    },
                    "macroF1": 0.0,  # Represents the macro F1. Required.
                    "macroPrecision": 0.0,  # Represents the macro precision. Required.
                    "macroRecall": 0.0,  # Represents the macro recall. Required.
                    "microF1": 0.0,  # Represents the micro F1. Required.
                    "microPrecision": 0.0,  # Represents the micro precision. Required.
                    "microRecall": 0.0  # Represents the micro recall. Required.
                }
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.list_training_jobs.__doc__ = \
    """Lists the non-expired training jobs created for a project.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/list-training-jobs
    for more information.

    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :keyword top: The maximum number of resources to return from the collection. Default value is
     None.
    :paramtype top: int
    :keyword skip: An offset into the collection of the first resource to be returned. Default
     value is None.
    :paramtype skip: int
    :return: An iterator like instance of JSON object
    :rtype: ~azure.core.paging.ItemPaged[JSON]
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "createdDateTime": "2020-02-20 00:00:00",  # The creation date time of the
                  job. Required.
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
                "expirationDateTime": "2020-02-20 00:00:00",  # Optional. The expiration date
                  time of the job.
                "jobId": "str",  # The job ID. Required.
                "lastUpdatedDateTime": "2020-02-20 00:00:00",  # The last date time the job
                  was updated. Required.
                "result": {
                    "estimatedEndDateTime": "2020-02-20 00:00:00",  # Optional.
                      Represents the estimated end date time for training and evaluation.
                    "evaluationStatus": {
                        "endDateTime": "2020-02-20 00:00:00",  # Optional. Represents
                          the end date time.
                        "percentComplete": 0,  # Represents progress percentage.
                          Required.
                        "startDateTime": "2020-02-20 00:00:00",  # Optional.
                          Represents the start date time.
                        "status": "str"  # Represents the status of the
                          sub-operation. Required. Known values are: "notStarted", "running",
                          "succeeded", "failed", "cancelled", "cancelling", and
                          "partiallyCompleted".
                    },
                    "modelLabel": "str",  # Represents trained model label. Required.
                    "trainingConfigVersion": "str",  # Represents training config
                      version. Required.
                    "trainingMode": "str",  # Optional. Represents the mode of the
                      training operation. Known values are: "advanced" and "standard".
                    "trainingStatus": {
                        "endDateTime": "2020-02-20 00:00:00",  # Optional. Represents
                          the end date time.
                        "percentComplete": 0,  # Represents progress percentage.
                          Required.
                        "startDateTime": "2020-02-20 00:00:00",  # Optional.
                          Represents the start date time.
                        "status": "str"  # Represents the status of the
                          sub-operation. Required. Known values are: "notStarted", "running",
                          "succeeded", "failed", "cancelled", "cancelling", and
                          "partiallyCompleted".
                    }
                },
                "status": "str",  # The job status. Required. Known values are: "notStarted",
                  "running", "succeeded", "failed", "cancelled", "cancelling", and
                  "partiallyCompleted".
                "warnings": [
                    {
                        "code": "str",  # The warning code. Required.
                        "message": "str"  # The warning message. Required.
                    }
                ]
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.get_training_job_status.__doc__ = \
    """Gets the status for a training job.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/get-training-status
    for more information.

    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :param job_id: The job ID. Required.
    :type job_id: str
    :return: JSON object
    :rtype: JSON
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "createdDateTime": "2020-02-20 00:00:00",  # The creation date time of the
                  job. Required.
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
                "expirationDateTime": "2020-02-20 00:00:00",  # Optional. The expiration date
                  time of the job.
                "jobId": "str",  # The job ID. Required.
                "lastUpdatedDateTime": "2020-02-20 00:00:00",  # The last date time the job
                  was updated. Required.
                "result": {
                    "estimatedEndDateTime": "2020-02-20 00:00:00",  # Optional.
                      Represents the estimated end date time for training and evaluation.
                    "evaluationStatus": {
                        "endDateTime": "2020-02-20 00:00:00",  # Optional. Represents
                          the end date time.
                        "percentComplete": 0,  # Represents progress percentage.
                          Required.
                        "startDateTime": "2020-02-20 00:00:00",  # Optional.
                          Represents the start date time.
                        "status": "str"  # Represents the status of the
                          sub-operation. Required. Known values are: "notStarted", "running",
                          "succeeded", "failed", "cancelled", "cancelling", and
                          "partiallyCompleted".
                    },
                    "modelLabel": "str",  # Represents trained model label. Required.
                    "trainingConfigVersion": "str",  # Represents training config
                      version. Required.
                    "trainingMode": "str",  # Optional. Represents the mode of the
                      training operation. Known values are: "advanced" and "standard".
                    "trainingStatus": {
                        "endDateTime": "2020-02-20 00:00:00",  # Optional. Represents
                          the end date time.
                        "percentComplete": 0,  # Represents progress percentage.
                          Required.
                        "startDateTime": "2020-02-20 00:00:00",  # Optional.
                          Represents the start date time.
                        "status": "str"  # Represents the status of the
                          sub-operation. Required. Known values are: "notStarted", "running",
                          "succeeded", "failed", "cancelled", "cancelling", and
                          "partiallyCompleted".
                    }
                },
                "status": "str",  # The job status. Required. Known values are: "notStarted",
                  "running", "succeeded", "failed", "cancelled", "cancelling", and
                  "partiallyCompleted".
                "warnings": [
                    {
                        "code": "str",  # The warning code. Required.
                        "message": "str"  # The warning message. Required.
                    }
                ]
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.begin_cancel_training_job.__doc__ = \
    """Triggers a cancellation for a running training job.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/cancel-training-job
    for more information.

    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :param job_id: The job ID. Required.
    :type job_id: str
    :keyword str continuation_token: A continuation token to restart a poller from a saved state.
    :keyword polling: By default, your polling method will be LROBasePolling. Pass in False for
     this operation to not poll, or pass in your own initialized polling object for a personal
     polling strategy.
    :paramtype polling: bool or ~azure.core.polling.PollingMethod
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    :return: An instance of LROPoller that returns JSON object
    :rtype: ~azure.core.polling.LROPoller[JSON]
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "createdDateTime": "2020-02-20 00:00:00",  # The creation date time of the
                  job. Required.
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
                "expirationDateTime": "2020-02-20 00:00:00",  # Optional. The expiration date
                  time of the job.
                "jobId": "str",  # The job ID. Required.
                "lastUpdatedDateTime": "2020-02-20 00:00:00",  # The last date time the job
                  was updated. Required.
                "result": {
                    "estimatedEndDateTime": "2020-02-20 00:00:00",  # Optional.
                      Represents the estimated end date time for training and evaluation.
                    "evaluationStatus": {
                        "endDateTime": "2020-02-20 00:00:00",  # Optional. Represents
                          the end date time.
                        "percentComplete": 0,  # Represents progress percentage.
                          Required.
                        "startDateTime": "2020-02-20 00:00:00",  # Optional.
                          Represents the start date time.
                        "status": "str"  # Represents the status of the
                          sub-operation. Required. Known values are: "notStarted", "running",
                          "succeeded", "failed", "cancelled", "cancelling", and
                          "partiallyCompleted".
                    },
                    "modelLabel": "str",  # Represents trained model label. Required.
                    "trainingConfigVersion": "str",  # Represents training config
                      version. Required.
                    "trainingMode": "str",  # Optional. Represents the mode of the
                      training operation. Known values are: "advanced" and "standard".
                    "trainingStatus": {
                        "endDateTime": "2020-02-20 00:00:00",  # Optional. Represents
                          the end date time.
                        "percentComplete": 0,  # Represents progress percentage.
                          Required.
                        "startDateTime": "2020-02-20 00:00:00",  # Optional.
                          Represents the start date time.
                        "status": "str"  # Represents the status of the
                          sub-operation. Required. Known values are: "notStarted", "running",
                          "succeeded", "failed", "cancelled", "cancelling", and
                          "partiallyCompleted".
                    }
                },
                "status": "str",  # The job status. Required. Known values are: "notStarted",
                  "running", "succeeded", "failed", "cancelled", "cancelling", and
                  "partiallyCompleted".
                "warnings": [
                    {
                        "code": "str",  # The warning code. Required.
                        "message": "str"  # The warning message. Required.
                    }
                ]
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.get_project_deletion_job_status.__doc__ = \
    """Gets the status for a project deletion job.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/get-project-deletion-status
    for more information.

    :param job_id: The job ID. Required.
    :type job_id: str
    :return: JSON object
    :rtype: JSON
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "createdDateTime": "2020-02-20 00:00:00",  # The creation date time of the
                  job. Required.
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
                "expirationDateTime": "2020-02-20 00:00:00",  # Optional. The expiration date
                  time of the job.
                "jobId": "str",  # The job ID. Required.
                "lastUpdatedDateTime": "2020-02-20 00:00:00",  # The last date time the job
                  was updated. Required.
                "status": "str",  # The job status. Required. Known values are: "notStarted",
                  "running", "succeeded", "failed", "cancelled", "cancelling", and
                  "partiallyCompleted".
                "warnings": [
                    {
                        "code": "str",  # The warning code. Required.
                        "message": "str"  # The warning message. Required.
                    }
                ]
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.list_supported_languages.__doc__ = \
    """Lists the supported languages for the given project type. 

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/get-supported-languages
    for more information.

    :keyword project_kind: The project kind. Known values are: "Conversation" and "Orchestration".
     Required.
    :paramtype project_kind: str
    :keyword top: The maximum number of resources to return from the collection. Default value is
     None.
    :paramtype top: int
    :keyword skip: An offset into the collection of the first resource to be returned. Default
     value is None.
    :paramtype skip: int
    :return: An iterator like instance of JSON object
    :rtype: ~azure.core.paging.ItemPaged[JSON]
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "languageCode": "str",  # The language code. This is BCP-47 representation of
                  a language. For example, "en" for English, "en-gb" for English (UK), "es" for
                  Spanish etc. Required.
                "languageName": "str"  # The language name. Required.
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.list_supported_prebuilt_entities.__doc__ = \
    """Lists the supported prebuilt entities that can be used while creating composed entities.

    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/get-supported-prebuilt-entities
    for more information.
    
    :keyword language: The language to get supported prebuilt entities for. Required if
     multilingual is false. This is BCP-47 representation of a language. For example, use "en" for
     English, "en-gb" for English (UK), "es" for Spanish etc. Default value is None.
    :paramtype language: str
    :keyword multilingual: Whether to get the support prebuilt entities for multilingual or
     monolingual projects. If true, the language parameter is ignored. Default value is None.
    :paramtype multilingual: bool
    :keyword top: The maximum number of resources to return from the collection. Default value is
     None.
    :paramtype top: int
    :keyword skip: An offset into the collection of the first resource to be returned. Default
     value is None.
    :paramtype skip: int
    :return: An iterator like instance of JSON object
    :rtype: ~azure.core.paging.ItemPaged[JSON]
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "category": "str",  # The prebuilt entity category. Required.
                "description": "str",  # The description. Required.
                "examples": "str"  # English examples for the entity. Required.
            }
    """

ConversationAuthoringClientOperationsMixinGenerated.list_training_config_versions.__doc__ = \
    """Lists the support training config version for a given project type.
    
    See https://docs.microsoft.com/rest/api/language/conversational-analysis-authoring/list-training-config-versions
    for more information.

    :keyword project_kind: The project kind. Known values are: "Conversation" and "Orchestration".
     Required.
    :paramtype project_kind: str
    :keyword top: The maximum number of resources to return from the collection. Default value is
     None.
    :paramtype top: int
    :keyword skip: An offset into the collection of the first resource to be returned. Default
     value is None.
    :paramtype skip: int
    :return: An iterator like instance of JSON object
    :rtype: ~azure.core.paging.ItemPaged[JSON]
    :raises ~azure.core.exceptions.HttpResponseError:
    
    Example:
        .. code-block:: python
    
            # response body for status code(s): 200
            response == {
                "modelExpirationDate": "2020-02-20",  # Represents the training config
                  version expiration date. Required.
                "trainingConfigVersion": "str"  # Represents the version of the config.
                  Required.
            }
    """


class ConversationAuthoringClientOperationsMixin(ConversationAuthoringClientOperationsMixinGenerated):
    ...


__all__: List[str] = ["ConversationAuthoringClientOperationsMixin"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
