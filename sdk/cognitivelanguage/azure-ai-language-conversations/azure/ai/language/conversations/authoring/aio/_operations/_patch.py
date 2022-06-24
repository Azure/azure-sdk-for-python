# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from ._operations import \
    ConversationAuthoringClientOperationsMixin as ConversationAuthoringClientOperationsMixinGenerated


ConversationAuthoringClientOperationsMixinGenerated.create_project.__doc__ = \
    """Creates a new project or updates an existing one.

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

ConversationAuthoringClientOperationsMixinGenerated.begin_import_project.__doc__ = \
    """Triggers a job to import a project. If a project with the same name already exists, the data of
    that project is replaced.

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
    :keyword polling: By default, your polling method will be AsyncLROBasePolling. Pass in False
     for this operation to not poll, or pass in your own initialized polling object for a personal
     polling strategy.
    :paramtype polling: bool or ~azure.core.polling.AsyncPollingMethod
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    :return: An instance of AsyncLROPoller that returns JSON object
    :rtype: ~azure.core.polling.AsyncLROPoller[JSON]
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

    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :param configuration: The training input parameters. Is either a model type or a IO type.
     Required.
    :type configuration: JSON or IO
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

ConversationAuthoringClientOperationsMixinGenerated.begin_swap_deployments.__doc__ = \
    """Swaps two existing deployments with each other.

    :param project_name: The name of the project to use. Required.
    :type project_name: str
    :param deployments: The job object to swap two deployments. Is either a model type or a IO
     type. Required.
    :type deployments: JSON or IO
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

ConversationAuthoringClientOperationsMixinGenerated.begin_deploy_project.__doc__ = \
    """Creates a new deployment or replaces an existing one.

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
    :keyword polling: By default, your polling method will be AsyncLROBasePolling. Pass in False
     for this operation to not poll, or pass in your own initialized polling object for a personal
     polling strategy.
    :paramtype polling: bool or ~azure.core.polling.AsyncPollingMethod
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    :return: An instance of AsyncLROPoller that returns JSON object
    :rtype: ~azure.core.polling.AsyncLROPoller[JSON]
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


class ConversationAuthoringClientOperationsMixin(ConversationAuthoringClientOperationsMixinGenerated):
    ...


__all__: List[str] = ["ConversationAuthoringClientOperationsMixin"]  # Add all objects you want publicly available to users at this package level

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
