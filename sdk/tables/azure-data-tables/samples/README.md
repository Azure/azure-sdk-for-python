---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-data-tables
urlFragment: tables-samples
---

# Samples for Azure Tables client library for Python

These code samples show common scenario operations with the Azure Text Analytics client library.
The async versions of the samples require Python 3.5 or later.

You can authenticate your client with a Tables API key:
* See [sample_authentication.py][sample_authentication] and [sample_authentication_async.py][sample_authentication_async] for how to authenticate in the above cases.

These sample programs show common scenarios for the Text Analytics client's offerings.

|**File Name**|**Description**|
|-------------|---------------|
|[sample_create_client.py][create_client] and [sample_create_client_async.py][create_client_async]|Instantiate a table client|Authorizing a `TableServiceClient` object|
|[sample_create_delete_table.py][create_delete_table] and [sample_create_delete_table_async.py][create_delete_table_async]|Creating a table in a storage account|



<!-- LINKS -->
[sample_authentication]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/samples_authentication.py
[sample_authentication_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/samples_authentication_async.py

[create_delete_table]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/sample_create_delete_table.py
[create_delete_table_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/tables/azure-data-tables/samples/sample_create_delete_table_async.py


[detect_language]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_detect_language.py
[detect_language_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_detect_language_async.py
[recognize_entities]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_recognize_entities.py
[recognize_entities_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_recognize_entities_async.py
[recognize_linked_entities]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_recognize_linked_entities.py
[recognize_linked_entities_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_recognize_linked_entities_async.py
[recognize_pii_entities]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_recognize_pii_entities.py
[recognize_pii_entities_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_recognize_pii_entities_async.py
[extract_key_phrases]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_extract_key_phrases.py
[extract_key_phrases_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_extract_key_phrases_async.py
[analyze_sentiment]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_analyze_sentiment.py
[analyze_sentiment_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_analyze_sentiment_async.py
[get_detailed_diagnostics_information]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_get_detailed_diagnostics_information.py
[get_detailed_diagnostics_information_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_get_detailed_diagnostics_information_async.py
[sample_alternative_document_input]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_alternative_document_input.py
[sample_alternative_document_input_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_alternative_document_input_async.py
[sample_analyze_sentiment_with_opinion_mining]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_analyze_sentiment_with_opinion_mining.py
[sample_analyze_sentiment_with_opinion_mining_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_analyze_sentiment_with_opinion_mining_async.py
[pip]: https://pypi.org/project/pip/
[azure_subscription]: https://azure.microsoft.com/free/
[azure_text_analytics_account]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=singleservice%2Cwindows
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[api_reference_documentation]: https://aka.ms/azsdk-python-textanalytics-ref-docs