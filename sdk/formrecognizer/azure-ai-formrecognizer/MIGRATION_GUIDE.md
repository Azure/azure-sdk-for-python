# Guide for migrating azure-ai-formrecognizer to version 3.2.x from versions 3.1.x and below

This guide is intended to assist in the migration to `azure-ai-formrecognizer (3.2.x)` from versions `3.1.x` and below. It will focus on side-by-side comparisons for similar operations between versions, please note that version `3.1.2` will be used for comparison with `3.2.0b1`.

Familiarity with `azure-ai-formrecognizer (3.1.x and below)` package is assumed. For those new to the Azure Form Recognizer client library for Python please refer to the [README](README) rather than this guide.

## Table of Contents
- [Migration benefits](#migration-benefits)
- [Important changes](#important-changes)
- [Additional samples](#additional-samples)

## Migration benefits

A natural question to ask when considering whether or not to adopt a new version of the library is what the benefits of doing so would be. As Azure Form Recognizer has matured and been embraced by a more diverse group of developers, we have been focused on learning the patterns and practices to best support developer productivity and add value to our customers.

There are many benefits to using the new design of the `azure-ai-formrecognizer (3.2.x)` library. This new version of the library introduces two new clients `DocumentAnalysisClient` and the `DocumentModelAdministrationClient` with unified methods for analyzing documents and provides support for the new features added by the service in API version `2021-09-30-preview`.

New features provided by the `DocumentAnalysisClient` include having one consolidated function for analyzing general document layout, having a general prebuilt document model type, along with the same prebuilt model types that we included previously (receipts, invoices, business cards, identity documents), and custom models. Moreover, the models used in the newer version of the library, such as `AnalyzeResult`, remove many hierarchical dependencies between document elements and move them to a more top level and easily accesible position. The service has further improved how to define where elements are found on documents by moving towards `BoundingRegion` definitions where an element is returned with the bounding box per page where it is found. Document element fields are returned with more information, such as content and spans. 

When using the `DocumentModelAdministrationClient` to build or compose new models users can now assign their own model ids and specify a description. Listing models on the administation client includes both prebuilt and custom models. When using `get_model()`, users can get the field schema for the model they specified, this includes prebuilt models. This client also provides functions for getting information from model operations.

Please refer to the [README](README) and [service documentation](TODO) for more information on these new clients.

## Important changes

### Instantiating a client

We continue to support API key and AAD authentication methods when creating our clients. Below are the differences between the two versions:

- In `3.2.x`, we have added `DocumentAnalysisClient` and `DocumentModelAdministrationClient` which support API version `2021-09-30-preview` and later.
- `FormRecognizerClient` and `FormTrainingClient` will return an error if called with an API version of `2021-09-30-preview` or later. 

Creating a new clients in `3.1.x`:
```python
form_recognizer_client = FormRecognizerClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

form_training_client = FormTrainingClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)
```

Creating a new clients in `3.2.x`:
```python
document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

document_model_admin_client = DocumentModelAdministrationClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)
```

### Analyzing documents

Differences between the versions:
- In `DocumentAnalysisClient` all prebuilt model methods along with custom model, layout, and general prebuilt document analysis are unified into two methods called
`begin_analyze_document` and `begin_analyze_document_from_url`.
- `begin_analyze_document` and `begin_analyze_document_from_url` accept a string with the desired model id for analysis. The model id can be any of the prebuilt model ids or a custom model id.
- In `FormRecognizerClient` there are two methods (a stream and URL method) for each of the prebuilt models supported by the service, this results in two methods for business card, receipt, identity document, and invoice models, along with a pair of methods for recognizing custom documents and for recognizing content/layout. 
- Along with more consolidated analysis methods in the `DocumentAnalysisClient`, the return types have also been improved and remove the hierarchical dependencies between elements. An instance of the `AnalyzeResult` model is now returned which showcases important document elements, such as key-value pairs, entities, tables, and document fields and values, among others, at the top level of the returned model. This can be contrasted with `RecognizedForm` which included more hierarchical relationships, for instance tables were an element of a `FormPage` and not a top-level element.
- In the new version of the library, the functionality of `begin_recognize_content` has been added as a prebuilt model and can be called in library version `azure-ai-formrecognizer (3.2.x)` with `begin_analyze_document` by passing in the `prebuilt-layout` model id. Similarly, to get general prebuilt document information, such as key-value pairs, entities, and text layout, the `prebuilt-document` model id can be used with `begin_analyze_document`.
- When calling `begin_analyze_document` and `begin_analyze_document_from_url` the returned type is an `AnalyzeResult` object, while the various methods used with `FormRecognizerClient` return a list of `RecognizedForm`.
- The `pages` kwarg is string with library version `azure-ai-formrecognizer (3.2.x)`. In `azure-ai-formrecognizer (3.1.x)`, pages was a list of strings.
- The `include_field_elements` kwarg does not exist with the `DocumentAnalysisClient`, text details are automatically included with API version `2021-09-30-preview`.

Analyzing prebuilt models like business cards, identity documents, invoices and receipts with `3.1.x`:
```python
with open(path_to_sample_forms, "rb") as f:
    poller = form_recognizer_client.begin_recognize_receipts(receipt=f, locale="en-US")
receipts = poller.result()

for idx, receipt in enumerate(receipts):
    print("--------Recognizing receipt #{}--------".format(idx+1))
    # process receipt
```

Analyzing prebuilt models like business cards, identity documents, invoices and receipts with `3.2.x`:
```python
with open(path_to_sample_documents, "rb") as f:
    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-receipt", document=f, locale="en-US"
    )
receipts = poller.result()

for receipt in receipts.documents:
    print("--------Recognizing receipt--------")
    # process receipt
```

Analyzing document content with `3.1.x`:

> NOTE: With version `3.1.x` of the library this method was called with a `language` kwarg to hint at the language for the document, whereas in version `3.2.x` of the library `locale` is used for this purpose.

```python
with open(path_to_sample_forms, "rb") as f:
    poller = form_recognizer_client.begin_recognize_content(form=f)
form_pages = poller.result()

for idx, content in enumerate(form_pages):
    print("----Recognizing content from page #{}----".format(idx+1))
    # process document layout by parsing content in pages
    for table_idx, table in enumerate(content.tables):
        # process document tables

    for line_idx, line in enumerate(content.lines):
        # process lines
        for word in line.words:
            # process words in a line

    for selection_mark in content.selection_marks:
        # process selection marks that were found
```


Analyzing document layout with `3.2.x`:
```python
with open(path_to_sample_documents, "rb") as f:
    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-layout", document=f
    )
result = poller.result()

for style in result.styles:
    # process document styles

for page in result.pages:
    # process pages
    for line in page.lines:
        # process lines
    for word in page.words:
        # process words

for table in result.tables:
    # process tables found in document
```

Analyzing general prebuilt document types with `3.2.x`:
```python
with open(path_to_sample_documents, "rb") as f:
    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-document", document=f
    )
result = poller.result()

for entity in result.entities:
    # process entities found in document

for kv_pair in result.key_value_pairs:
    # process key-value pairs found in document

for page in result.pages:
    # process pages
    for line in page.lines:
        # process lines
    for word in page.words:
        # process words

for table in result.tables:
    # process tables found in document
```

> NOTE: All of these samples also work with `begin_analyze_document_from_url` when providing a valid URL to the document.

### Analyzing a custom model

Differences between the versions:
- Analyzing a custom model with `DocumentAnalysisClient` uses the general `begin_analyze_document` and `begin_analyze_document_from_url` methods.
- In order to analyze a custom model with `FormRecognizerClient` the `begin_recognize_custom_models` and its corresponding URL methods is used.
- The `include_field_elements` kwarg does not exist with the `DocumentAnalysisClient`, text details are automatically included with API version `2021-09-30-preview`.

Analyze custom document with `3.1.x`:
```python
with open(path_to_sample_forms, "rb") as f:
    poller = form_recognizer_client.begin_recognize_custom_forms(
        model_id=model_id, form=f, include_field_elements=True
    )
forms = poller.result()
```

Analyze custom document with `3.2.x`:
```python
with open(path_to_sample_documents, "rb") as f:
    poller = document_analysis_client.begin_analyze_document(
        model=model_id, document=f
    )
result = poller.result()
```

### Training a custom model

Differences between the versions:
- Files for building a new model for version `3.2.x` can be created using the labeling tool found [here](fr-labeling-tool).
- In version `3.1.x` the `use_training_labels` kwarg was used to indicate whether to use labeled data was when creating the custom model.
- In version `3.2.x` the `use_training_labels` kwargs is not supported since training must be carried out with labeled training documents. In order to extract key-value pairs from a document, please refer to the prebuilt model "prebuilt-document" which extracts entities, key-value pairs, and layout from a document. 

Train a custom model with `3.1.x`:
```python
form_training_client = FormTrainingClient(endpoint, AzureKeyCredential(key))
poller = form_training_client.begin_training(
    container_sas_url, use_training_labels=True, model_name="mymodel"
)
model = poller.result()

# Custom model information
print("Model ID: {}".format(model.model_id))
print("Status: {}".format(model.status))
print("Model name: {}".format(model.model_name))
print("Is this a composed model?: {}".format(model.properties.is_composed_model))
print("Training started on: {}".format(model.training_started_on))
print("Training completed on: {}".format(model.training_completed_on))

print("Recognized fields:")
# looping through the submodels, which contains the fields they were trained on
for submodel in model.submodels:
    print("...The submodel has model ID: {}".format(submodel.model_id))
    print("...The submodel with form type {} has an average accuracy '{}'".format(
        submodel.form_type, submodel.accuracy
    ))
    for name, field in submodel.fields.items():
        print("...The model found the field '{}' with an accuracy of {}".format(
            name, field.accuracy
        ))

# Training result information
for doc in model.training_documents:
    print("Document name: {}".format(doc.name))
    print("Document status: {}".format(doc.status))
    print("Document page count: {}".format(doc.page_count))
    print("Document errors: {}".format(doc.errors))
```

Train a custom model with `3.2.x`:
```python
document_model_admin_client = DocumentModelAdministrationClient(endpoint, AzureKeyCredential(key))
poller = document_model_admin_client.begin_build_model(
    container_sas_url, model_id="my-model-id", description="my model description"
)
model = poller.result()

print("Model ID: {}".format(model.model_id))
print("Description: {}".format(model.description))
print("Model created on: {}\n".format(model.created_on))
print("Doc types the model can recognize:")
for name, doc_type in model.doc_types.items():
    print("\nDoc Type: '{}' which has the following fields:".format(name))
    for field_name, field in doc_type.field_schema.items():
        print("Field: '{}' has type '{}' and confidence score {}".format(
            field_name, field["type"], doc_type.field_confidence[field_name]
        ))
```

## Additional samples

For additional samples please take a look at the [Form Recognizer Samples](Samples-README) for more guidance.

[README]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/README.md
[Samples-README]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/README.md
[fr-labeling-tool]: https://aka.ms/azsdk/formrecognizer/labelingtool