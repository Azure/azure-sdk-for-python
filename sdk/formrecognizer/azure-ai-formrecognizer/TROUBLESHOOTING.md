# Troubleshoot Azure Form Recognizer client library issues

This troubleshooting guide contains instructions to diagnose frequently encountered issues while using the Azure Form Recognizer client library for Python.

## Table of Contents
* [Troubleshooting Errors](#troubleshooting-errors)
    * [Handling HttpResponseError](#handling-httpresponseerror)
    * [Build model error](#build-model-error)
       * [Invalid training dataset](#invalid-training-data-set)
       * [Invalid SAS URL](#invalid-sas-url)
    * [Generic Error](#generic-error)
* [Unexpected time to build a custom model](#unexpected-time-to-build-a-custom-model)
* [Enable HTTP request/response logging](#enable-http-requestresponse-logging)

## Troubleshooting Errors

### Handling HttpResponseError
The client methods in this SDK raise an [HttpResponseError](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core#httpresponseerror) on request failure.
The HttpResponseError raised by the Azure Form Recognizer client library includes detailed error response information that provides useful insights into what went wrong and includes corrective actions to fix common issues.
This error information can be found inside the `message` property of the `HttpResponseError` instance.

Here is an example of how to catch it:

```python
try:
    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-document", document=f
    )
    result = poller.result()
    # process request result
except HttpResponseError as error:
    # handle the error here
```

### Build model error
Build model errors usually occur when trying to build a custom model. The most common scenarios when this might occur is, if you are building the model with an 
[Invalid data set](#invalid-training-data-set) or an [Invalid SAS Url](#invalid-sas-url).

#### Invalid training data set
This error indicates that the provided data set does not match the training data requirements.
Learn more about building a training data set, [here](https://aka.ms/customModelV3).

Example error output:
```text
azure.core.exceptions.HttpResponseError: (InvalidRequest) Invalid request.
Code: InvalidRequest
Message: Invalid request.
Exception Details:      (ModelBuildError) Could not build the model: Can't find any OCR files for training.
        Code: ModelBuildError
        Message: Could not build the model: Can't find any OCR files for training.
```

#### Invalid SAS URL
This error points to missing permissions on the blob storage SAS URL for the Form Recognizer service to access the training dataset resource. For more information about SAS tokens for Form Recognizer, see [here](https://learn.microsoft.com/azure/applied-ai-services/form-recognizer/create-sas-tokens).

Example error output:
```text
azure.core.exceptions.HttpResponseError: (InvalidArgument) Invalid argument.
Code: InvalidArgument
Message: Invalid argument.
Inner error: {
    "code": "InvalidSasToken",
    "message": "The shared access signature (SAS) is invalid: SAS 'list' authorization is missing. Permissions: racwd"    
}
```

### Generic Error
Seeing a "Generic error" returned from the SDK is most often caused by heavy load on the service. For troubleshooting issues related to service limits, see related information [here](https://learn.microsoft.com/azure/applied-ai-services/form-recognizer/service-limits?tabs=v30).

Example error output:
```text
azure.core.exceptions.HttpResponseError: (3014) Generic error during training.
Invalid model created with ID=<model ID>
```

### Unexpected time to build a custom model
It is common to have a longer completion time than what is expected when building a custom model using the `neural` build mode with `begin_build_document_model()`. Depending on the service load you can usually expect it to take ~10min.

For simpler use-cases, you can use `template` build mode which uses a different model building algorithm that takes less time (typically a few seconds to build). See more about `template` custom models [here](https://aka.ms/custom-template-models). To see more information about `neural` custom models (these models use deep learning to train and build), see documentation [here](https://aka.ms/custom-neural-models).

### Enable HTTP request/response logging
Reviewing the HTTP request sent or response received over the wire to/from the Azure Form Recognizer service can be useful when troubleshooting issues.

For more information about logging with Python Azure SDKs, see [here](https://learn.microsoft.com/azure/developer/python/sdk/azure-sdk-logging).

**NOTE**: When logging the body of request and response, please ensure that they do not contain confidential information.