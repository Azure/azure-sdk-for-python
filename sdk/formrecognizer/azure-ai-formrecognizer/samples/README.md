---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-cognitive-services
  - azure-form-recognizer
urlFragment: formrecognizer-samples
---

# Samples for Azure Form Recognizer client library for Python

> Note: Starting with version 2021-09-30-preview, a new set of clients were introduced to leverage the newest features
> of the Form Recognizer service. Please see the [Migration Guide][migration-guide] for detailed instructions on how to update application
> code from client library version 3.1.X or lower to the latest version. Additionally, see the [Changelog][changelog] for more detailed information.

These code samples show common scenario operations with the Azure Form Recognizer client library.
The async versions of the samples require Python 3.6 or later.

These sample programs show common scenarios for the Form Recognizer client's offerings.

All of these samples need the endpoint to your Form Recognizer resource ([instructions on how to get endpoint][get-endpoint-instructions]), and your Form Recognizer API key ([instructions on how to get key][get-key-instructions]).

## Samples for client library versions 3.2.0b1 and later

|**File Name**|**Description**|
|----------------|-------------|
|[sample_authentication.py][sample_auth] and [sample_authentication_async.py][sample_auth_async]|Authenticate the client|
|[sample_analyze_layout.py][sample_analyze_layout] and [sample_analyze_layout_async.py][sample_analyze_layout_async]|Extract text, selection marks, and table structures in a document|
|[sample_analyze_general_documents.py][sample_analyze_general_documents] and [sample_analyze_general_documents_async.py][sample_analyze_general_documents_async]|Analyze document key-value pairs, tables, and selection marks using a prebuilt model|
|[sample_analyze_read.py][sample_analyze_read] and [sample_analyze_read_async.py][sample_analyze_read_async]|Read document elements, such as pages and detected languages|
|[sample_analyze_invoices.py][sample_analyze_invoices] and [sample_analyze_invoices_async.py][sample_analyze_invoices_async]|Analyze document text, selection marks, tables, and pre-trained fields and values pertaining to English invoices using a prebuilt model|
|[sample_analyze_business_cards.py][sample_analyze_business_cards] and [sample_analyze_business_cards_async.py][sample_analyze_business_cards_async]|Analyze document text and pre-trained fields and values pertaining to English business cards using a prebuilt model|
|[sample_analyze_identity_documents.py][sample_analyze_identity_documents] and [sample_analyze_identity_documents_async.py][sample_analyze_identity_documents_async]|Analyze document text and pre-trained fields and values pertaining to US driver licenses and international passports using a prebuilt model|
|[sample_analyze_receipts.py][sample_analyze_receipts] and [sample_analyze_receipts_async.py][sample_analyze_receipts_async]|Analyze document text and pre-trained fields and values pertaining to English sales receipts using a prebuilt model|
|[sample_analyze_tax_us_w2.py][sample_analyze_tax_us_w2] and [sample_analyze_tax_us_w2_async.py][sample_analyze_tax_us_w2_async]|Analyze document text and pre-trained fields and values pertaining to US tax W-2 forms using a prebuilt model|
|[sample_analyze_custom_documents.py][sample_analyze_custom_documents] and [sample_analyze_custom_documents_async.py][sample_analyze_custom_documents_async]|Analyze custom documents with your custom model to extract text, field values, selection marks, and table data from documents|
|[sample_build_model.py][sample_build_model] and [sample_build_model_async.py][sample_build_model_async]|Build a custom model|
|[sample_create_composed_model.py][sample_composed_model] and [sample_create_composed_model_async.py][sample_composed_model_async]|Create a composed model from a collection of existing models to be called with a single model ID|
|[sample_manage_models.py][sample_manage_models] and [sample_manage_models_async.py][sample_manage_models_async]|Manage the models in your account|
|[sample_get_operations.py][sample_get_operations] and [sample_get_operations_async.py][sample_get_operations_async]|Get and list the document model operations created within the past 24 hours|
|[sample_copy_model_to.py][sample_copy] and [sample_copy_model_to_async.py][sample_copy_async]|Copy a custom model from one Form Recognizer resource to another|
|[sample_get_words_on_document_line.py][sample_get_words_on_document_line] and [sample_get_words_on_document_line_async.py][sample_get_words_on_document_line_async]|Get the words in a DocumentLine|
|[sample_convert_to_and_from_dict.py][sample_convert_to_and_from_dict_v3_2] and [sample_convert_to_and_from_dict_async.py][sample_convert_to_and_from_dict_async_v3_2]|Convert model types to a dictionary that can be used to create JSON content, then convert the same dictionary back to the original model type|
|[sample_get_elements_with_spans.py][sample_get_elements_with_spans] and [sample_get_elements_with_spans_async.py][sample_get_elements_with_spans_async]|Get elements, such as words, lines, and styles, in the result of an analyze operation by searching with spans|

## Samples for client library versions 3.1.X

|**File Name**|**Description**|
|----------------|-------------|
|[sample_authentication.py][sample_authentication] and [sample_authentication_async.py][sample_authentication_async]|Authenticate the client|
|[sample_recognize_content.py][sample_recognize_content] and [sample_recognize_content_async.py][sample_recognize_content_async]|Recognize text, selection marks, and table structures in a document|
|[sample_recognize_receipts.py][sample_recognize_receipts] and [sample_recognize_receipts_async.py][sample_recognize_receipts_async]|Recognize data from a file of a sales receipt using a prebuilt model|
|[sample_recognize_receipts_from_url.py][sample_recognize_receipts_from_url] and [sample_recognize_receipts_from_url_async.py][sample_recognize_receipts_from_url_async]|Recognize data from a URL of a sales receipt using a prebuilt model|
|[sample_recognize_business_cards.py][sample_recognize_business_cards] and [sample_recognize_business_cards_async.py][sample_recognize_business_cards_async]|Recognize data from a file of a business card using a prebuilt model|
|[sample_recognize_identity_documents.py][sample_recognize_identity_documents] and [sample_recognize_identity_documents_async.py][sample_recognize_identity_documents_async]|Recognize data from a file of an ID document using a prebuilt model|
|[sample_recognize_invoices.py][sample_recognize_invoices] and [sample_recognize_invoices_async.py][sample_recognize_invoices_async]|Recognize data from a file of an invoice using a prebuilt model|
|[sample_recognize_custom_forms.py][sample_recognize_custom_forms] and [sample_recognize_custom_forms_async.py][sample_recognize_custom_forms_async]|Recognize forms with your custom model|
|[sample_train_model_without_labels.py][sample_train_model_without_labels] and [sample_train_model_without_labels_async.py][sample_train_model_without_labels_async]|Train a custom model with unlabeled data|
|[sample_train_model_with_labels.py][sample_train_model_with_labels] and [sample_train_model_with_labels_async.py][sample_train_model_with_labels_async]|Train a custom model with labeled data|
|[sample_manage_custom_models.py][sample_manage_custom_models] and [sample_manage_custom_models_async.py][sample_manage_custom_models_async]|Manage the custom models in your account|
|[sample_copy_model.py][sample_copy_model] and [sample_copy_model_async.py][sample_copy_model_async]|Copy a custom model from one Form Recognizer resource to another|
|[sample_create_composed_model.py][sample_create_composed_model] and [sample_create_composed_model_async.py][sample_create_composed_model_async]|Create a composed model from a collection of existing models trained with labels|
|[sample_strongly_typing_recognized_form.py][sample_strongly_typing_recognized_form] and [sample_strongly_typing_recognized_form_async.py][sample_strongly_typing_recognized_form_async]|Use the fields in your recognized forms to create an object with strongly-typed fields|
|[sample_get_bounding_boxes.py][sample_get_bounding_boxes] and [sample_get_bounding_boxes_async.py][sample_get_bounding_boxes_async]|Get info to visualize the outlines of form content and fields, which can be used for manual validation|
|[sample_differentiate_output_models_trained_with_and_without_labels.py][sample_differentiate_output_models_trained_with_and_without_labels] and [sample_differentiate_output_models_trained_with_and_without_labels_async.py][sample_differentiate_output_models_trained_with_and_without_labels_async]|See the differences in output when using a custom model trained with labeled data and one trained with unlabeled data|
|[sample_differentiate_output_labeled_tables.py][sample_differentiate_output_labeled_tables] and [sample_differentiate_output_labeled_tables_async.py][sample_differentiate_output_labeled_tables_async]|See the differences in output when using a custom model trained with fixed vs. dynamic table tags|
|[sample_convert_to_and_from_dict.py][sample_convert_to_and_from_dict_v3_1] and [sample_convert_to_and_from_dict_async.py][sample_convert_to_and_from_dict_async_v3_1]|Convert model types to a dictionary that can be used to create JSON content, then convert the same dictionary back to the original model type|

## Samples for client library versions 3.0.0 and below

Please see the samples [here][v3.0.0-samples-tag].

## Prerequisites
* Python 3.6 or later is required to use this package
* You must have an [Azure subscription][azure_subscription] and an
[Azure Form Recognizer account][azure_form_recognizer_account] to run these samples.

## Setup

1. Install the Azure Form Recognizer client library for Python with [pip][pip]:

```bash
pip install azure-ai-formrecognizer --pre
```

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_analyze_receipts.py`

## Next steps

Check out the [API reference documentation][python-fr-ref-docs] to learn more about
what you can do with the Azure Form Recognizer client library.


[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity

[pip]: https://pypi.org/project/pip/
[azure_subscription]: https://azure.microsoft.com/free/
[azure_form_recognizer_account]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=singleservice%2Cwindows
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[python-fr-ref-docs]: https://aka.ms/azsdk/python/formrecognizer/docs
[get-endpoint-instructions]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/README.md#get-the-endpoint
[get-key-instructions]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/README.md#get-the-api-key
[changelog]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/CHANGELOG.md
[v3.0.0-samples-tag]: https://github.com/Azure/azure-sdk-for-python/tree/azure-ai-formrecognizer_3.0.0/sdk/formrecognizer/azure-ai-formrecognizer/samples
[migration-guide]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/MIGRATION_GUIDE.md

<!-- V3.2-beta links -->

[sample_auth]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/sample_authentication.py
[sample_auth_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/async_samples/sample_authentication_async.py
[sample_analyze_layout]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/sample_analyze_layout.py
[sample_analyze_layout_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/async_samples/sample_analyze_layout_async.py
[sample_analyze_general_documents]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/sample_analyze_general_documents.py
[sample_analyze_general_documents_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/async_samples/sample_analyze_general_documents_async.py
[sample_analyze_invoices]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/sample_analyze_invoices.py
[sample_analyze_invoices_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/async_samples/sample_analyze_invoices_async.py
[sample_analyze_business_cards]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/sample_analyze_business_cards.py
[sample_analyze_business_cards_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/async_samples/sample_analyze_business_cards_async.py
[sample_analyze_identity_documents]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/sample_analyze_identity_documents.py
[sample_analyze_identity_documents_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/async_samples/sample_analyze_identity_documents_async.py
[sample_analyze_receipts]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/sample_analyze_receipts.py
[sample_analyze_receipts_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/async_samples/sample_analyze_receipts_async.py
[sample_analyze_custom_documents]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/sample_analyze_custom_documents.py
[sample_analyze_custom_documents_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/async_samples/sample_analyze_custom_documents_async.py
[sample_build_model]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/sample_build_model.py
[sample_build_model_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/async_samples/sample_build_model_async.py
[sample_composed_model]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/sample_create_composed_model.py
[sample_composed_model_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/async_samples/sample_create_composed_model_async.py
[sample_manage_models]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/sample_manage_models.py
[sample_manage_models_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/async_samples/sample_manage_models_async.py
[sample_get_operations]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/sample_get_operations.py
[sample_get_operations_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/async_samples/sample_get_operations_async.py
[sample_copy]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/sample_copy_model_to.py
[sample_copy_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/async_samples/sample_copy_model_to_async.py
[sample_get_words_on_document_line]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/sample_get_words_on_document_line.py
[sample_get_words_on_document_line_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/async_samples/sample_get_words_on_document_line_async.py
[sample_get_elements_with_spans]: https://aka.ms/azsdk/python/formrecognizer/spansamplesync
[sample_get_elements_with_spans_async]: https://aka.ms/azsdk/python/formrecognizer/spansampleasync
[sample_convert_to_and_from_dict_v3_2]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/sample_convert_to_and_from_dict.py
[sample_convert_to_and_from_dict_async_v3_2]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/async_samples/sample_convert_to_and_from_dict_async.py
[sample_analyze_read]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/sample_analyze_read.py
[sample_analyze_read_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/async_samples/sample_analyze_read_async.py
[sample_analyze_tax_us_w2]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/sample_analyze_tax_us_w2.py
[sample_analyze_tax_us_w2_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.2-beta/async_samples/sample_analyze_tax_us_w2_async.py

<!-- V3.1 links -->
[sample_authentication]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/sample_authentication.py
[sample_authentication_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/async_samples/sample_authentication_async.py
[sample_differentiate_output_models_trained_with_and_without_labels]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/sample_differentiate_output_models_trained_with_and_without_labels.py
[sample_differentiate_output_models_trained_with_and_without_labels_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/async_samples/sample_differentiate_output_models_trained_with_and_without_labels_async.py
[sample_get_bounding_boxes]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/sample_get_bounding_boxes.py
[sample_get_bounding_boxes_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/async_samples/sample_get_bounding_boxes_async.py
[sample_manage_custom_models]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/sample_manage_custom_models.py
[sample_manage_custom_models_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/async_samples/sample_manage_custom_models_async.py
[sample_recognize_content]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/sample_recognize_content.py
[sample_recognize_content_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/async_samples/sample_recognize_content_async.py
[sample_recognize_custom_forms]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/sample_recognize_custom_forms.py
[sample_recognize_custom_forms_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/async_samples/sample_recognize_custom_forms_async.py
[sample_recognize_receipts_from_url]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/sample_recognize_receipts_from_url.py
[sample_recognize_receipts_from_url_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/async_samples/sample_recognize_receipts_from_url_async.py
[sample_recognize_receipts]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/sample_recognize_receipts.py
[sample_recognize_receipts_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/async_samples/sample_recognize_receipts_async.py
[sample_recognize_business_cards]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/sample_recognize_business_cards.py
[sample_recognize_business_cards_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/async_samples/sample_recognize_business_cards_async.py
[sample_recognize_identity_documents]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/sample_recognize_identity_documents.py
[sample_recognize_identity_documents_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/async_samples/sample_recognize_identity_documents_async.py
[sample_recognize_invoices]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/sample_recognize_invoices.py
[sample_recognize_invoices_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/async_samples/sample_recognize_invoices_async.py
[sample_train_model_with_labels]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/sample_train_model_with_labels.py
[sample_train_model_with_labels_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/async_samples/sample_train_model_with_labels_async.py
[sample_train_model_without_labels]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/sample_train_model_without_labels.py
[sample_train_model_without_labels_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/async_samples/sample_train_model_without_labels_async.py
[sample_copy_model]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/sample_copy_model.py
[sample_copy_model_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/async_samples/sample_copy_model_async.py
[sample_strongly_typing_recognized_form]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/sample_strongly_typing_recognized_form.py
[sample_strongly_typing_recognized_form_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/async_samples/sample_strongly_typing_recognized_form_async.py
[sample_create_composed_model]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/sample_create_composed_model.py
[sample_create_composed_model_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/async_samples/sample_create_composed_model_async.py
[sample_differentiate_output_labeled_tables]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/sample_differentiate_output_labeled_tables.py
[sample_differentiate_output_labeled_tables_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/async_samples/sample_differentiate_output_labeled_tables_async.py
[sample_convert_to_and_from_dict_v3_1]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/sample_convert_to_and_from_dict.py
[sample_convert_to_and_from_dict_async_v3_1]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/v3.1/async_samples/sample_convert_to_and_from_dict_async.py
