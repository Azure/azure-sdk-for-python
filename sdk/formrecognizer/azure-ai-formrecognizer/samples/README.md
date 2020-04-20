---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-ai-formrecognizer
urlFragment: formrecognizer-samples
---

# Samples for Azure Form Recognizer client library for Python

These code samples show common scenario operations with the Azure Form Recognizer client library.
The async versions of the samples require Python 3.5 or later.

These sample programs show common scenarios for the Form Recognizer client's offerings.

All of these samples need the endpoint to your Form Recognizer resource ([instructions on how to get endpoint][get-endpoint-instructions]), and your Form Recognizer API key ([instructions on how to get key][get-key-instructions]).

|**File Name**|**Description**|
|----------------|-------------|
|[sample_recognize_content.py][sample_recognize_content] and [sample_recognize_content_async.py][sample_recognize_content_async]|Recognize text and table structures of a document|
|[sample_recognize_receipts.py][sample_recognize_receipts] and [sample_recognize_receipts_async.py][sample_recognize_receipts_async]|Recognize data from a file of a US sales receipt using a prebuilt model|
|[sample_recognize_receipts_from_url.py][sample_recognize_receipts_from_url] and [sample_recognize_receipts_from_url_async.py][sample_recognize_receipts_from_url_async]|Recognize data from a URL of a US sales receipt using a prebuilt model|
|[sample_recognize_custom_forms.py][sample_recognize_custom_forms] and [sample_recognize_custom_forms_async.py][sample_recognize_custom_forms_async]|Recognize forms with your custom model|
|[sample_train_model_without_labels.py][sample_train_model_without_labels] and [sample_train_model_without_labels_async.py][sample_train_model_without_labels_async]|Train a custom model with unlabeled data|
|[sample_train_model_with_labels.py][sample_train_model_with_labels] and [sample_train_model_with_labels_async.py][sample_train_model_with_labels_async]|Train a custom model with labeled data|
|[sample_manage_custom_models.py][sample_manage_custom_models] and [sample_manage_custom_models_async.py][sample_manage_custom_models_async]|Manage the custom models in your account|

## Prerequisites
* Python 2.7, or 3.5 or later is required to use this package (3.5 or later if using asyncio)
* You must have an [Azure subscription][azure_subscription] and an
[Azure Form Recognizer account][azure_form_recognizer_account] to run these samples.

## Setup

1. Install the Azure Form Recognizer client library for Python with [pip][pip]:

```bash
pip install azure-ai-formrecognizer
```

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_recognize_receipts.py`

## Next steps

Check out the [API reference documentation][python-fr-ref-docs] to learn more about
what you can do with the Azure Form Recognizer client library.

|**Advanced Sample File Name**|**Description**|
|----------------|-------------|
|[sample_get_bounding_boxes.py][sample_get_bounding_boxes] and [sample_get_bounding_boxes_async.py][sample_get_bounding_boxes_async]|Get info to visualize the outlines of form content and fields, which can be used for manual validation|
|[sample_differentiate_output_models_trained_with_and_without_labels.py][sample_differentiate_output_models_trained_with_and_without_labels] and [sample_differentiate_output_models_trained_with_and_without_labels_async.py][sample_differentiate_output_models_trained_with_and_without_labels_async]|See the differences in output when using a custom model trained with labeled data and one trained with unlabeled data|

[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity

[pip]: https://pypi.org/project/pip/
[azure_subscription]: https://azure.microsoft.com/free/
[azure_form_recognizer_account]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=singleservice%2Cwindows
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[python-fr-ref-docs]: https://aka.ms/azsdk-python-formrecognizer-ref-docs
[get-endpoint-instructions]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/formrecognizer/azure-ai-formrecognizer/README.md#looking-up-the-endpoint
[get-key-instructions]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/formrecognizer/azure-ai-formrecognizer/README.md#types-of-credentials

[sample_differentiate_output_models_trained_with_and_without_labels]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_differentiate_output_models_trained_with_and_without_labels.py
[sample_differentiate_output_models_trained_with_and_without_labels_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_differentiate_output_models_trained_with_and_without_labels_async.py
[sample_get_bounding_boxes]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_get_bounding_boxes.py
[sample_get_bounding_boxes_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_get_bounding_boxes_async.py
[sample_manage_custom_models]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_manage_custom_models.py
[sample_manage_custom_models_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_manage_custom_models_async.py
[sample_recognize_content]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_recognize_content.py
[sample_recognize_content_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_recognize_content_async.py
[sample_recognize_custom_forms]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_recognize_custom_forms.py
[sample_recognize_custom_forms_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_recognize_custom_forms_async.py
[sample_recognize_receipts_from_url]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_recognize_receipts_from_url.py
[sample_recognize_receipts_from_url_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_recognize_receipts_from_url_async.py
[sample_recognize_receipts]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_recognize_receipts.py
[sample_recognize_receipts_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_recognize_receipts_async.py
[sample_train_model_with_labels]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_train_model_with_labels.py
[sample_train_model_with_labels_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_train_model_with_labels_async.py
[sample_train_model_without_labels]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_train_model_without_labels.py
[sample_train_model_without_labels_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_train_model_without_labels_async.py
