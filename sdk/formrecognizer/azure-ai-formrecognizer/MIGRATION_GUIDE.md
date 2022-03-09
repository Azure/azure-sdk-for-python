# Guide for migrating azure-ai-formrecognizer to version 3.2.x from versions 3.1.x and below

This guide is intended to assist in the migration to `azure-ai-formrecognizer (3.2.x)` from versions `3.1.x` and below. It will focus on side-by-side comparisons for similar operations between versions. Please note that version `3.2.0b1` will be used for comparison with `3.1.2`.

Familiarity with `azure-ai-formrecognizer (3.1.x and below)` package is assumed. For those new to the Azure Form Recognizer client library for Python please refer to the [README][readme] rather than this guide.

## Table of Contents
- [Migration benefits](#migration-benefits)
- [Important changes](#important-changes)
    - [Terminology](#terminology)
    - [Client usage](#client-usage)
    - [Analyzing documents](#analyzing-documents)
    - [Analyzing a document with a custom model](#analyzing-a-document-with-a-custom-model)
    - [Training a custom model](#training-a-custom-model)
    - [Managing models](#managing-models)
- [Additional samples](#additional-samples)

## Migration benefits

A natural question to ask when considering whether to adopt a new version of the library is what the benefits of doing so would be. As Azure Form Recognizer has matured and been embraced by a more diverse group of developers, we have been focused on learning the patterns and practices to best support developer productivity and add value to our customers.

There are many benefits to using the new design of the `azure-ai-formrecognizer (3.2.x)` library. This new version of the library introduces two new clients `DocumentAnalysisClient` and the `DocumentModelAdministrationClient` with unified methods for analyzing documents and provides support for the new features added by the service in API version `2021-09-30-preview` and later.

New features provided by the `DocumentAnalysisClient` include:
- One consolidated method for analyzing document layout, a prebuilt general document model type, along with the same prebuilt models that were included previously (receipts, invoices, business cards, ID documents), and custom models. ***As of 3.2.0b3, a prebuilt read model was added to read information about pages and detected languages. A prebuilt model to analyze U.S. W-2 tax documents was also added with the following model ID: `prebuilt-tax.us.w2`.***
- Models introduced in the latest version of the library, such as `AnalyzeResult`, remove hierarchical dependencies between document elements and move them to a more top level and easily accessible position.
- The Form Recognizer service has further improved how to define where elements are located on documents by moving towards `BoundingRegion` definitions allowing for cross-page elements.
- Document element fields are returned with more information, such as content and spans. 

New features provided by the `DocumentModelAdministrationClient` include:
- Users can now assign their own model IDs and specify a description when building, composing, or copying models.
- Listing models now includes both prebuilt and custom models.
- When using `get_model()`, users can get the field schema (field names and types that the model can extract) for the model they specified, including for prebuilt models. 
- Ability to get information from model operations that occurred in the last 24 hours.

The table below describes the relationship of each client and its supported API version(s):

|API version|Supported clients
|-|-
|2021-09-30-preview | DocumentAnalysisClient and DocumentModelAdministrationClient
|2.1 | FormRecognizerClient and FormTrainingClient
|2.0 | FormRecognizerClient and FormTrainingClient

Please refer to the [README][readme] for more information on these new clients.

## Important changes

### Terminology

Some terminology has changed to reflect the enhanced capabilities of the newest Form Recognizer service APIs. While the service is still called `Form Recognizer`, it is capable of much more than simple recognition and is not limited to documents that are `forms`. As a result, we've made the following broad changes to the terminology used throughout the SDK:

- The word `Document` has broadly replaced the word `Form.` The service supports a wide variety of documents and data-extraction scenarios, not merely limited to `forms.`
- The word `Analyze` has broadly replaced the word `Recognize.` The document analysis operation executes a data extraction pipeline that supports more than just recognition.
- Distinctions between `custom` and `prebuilt` models have broadly been eliminated. Prebuilt models are simply models that were created by the Form Recognizer service team and that exist within every Form Recognizer resource.
- The concept of `model training` has broadly been replaced with `model creation`, `building a model`, or `model administration` (whatever is most appropriate in context), as not all model creation operations involve `training` a model from a data set. When referring to a model schema trained from a data set, we will use the term `document type` instead.

### Client usage

We continue to support API key and AAD authentication methods when creating the clients. Below are the differences between the two versions:

- In `3.2.x`, we have added `DocumentAnalysisClient` and `DocumentModelAdministrationClient` which support API version `2021-09-30-preview` and later.
- `FormRecognizerClient` and `FormTrainingClient` will continue to work targeting API versions `2.1` and `2.0`.
- In `DocumentAnalysisClient` all prebuilt model methods along with custom model, layout, and a prebuilt general document analysis model are unified into two methods called
`begin_analyze_document` and `begin_analyze_document_from_url`.
- In `FormRecognizerClient` there are two methods (a stream and URL method) for each of the prebuilt models supported by the service. This results in two methods for business card, receipt, identity document, and invoice models, along with a pair of methods for recognizing custom documents and for recognizing content/layout. 

Creating new clients in `3.1.x`:
```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormRecognizerClient, FormTrainingClient

endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

form_recognizer_client = FormRecognizerClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

form_training_client = FormTrainingClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)
```

Creating new clients in `3.2.x`:
```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient, DocumentModelAdministrationClient

endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

document_model_admin_client = DocumentModelAdministrationClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)
```

### Analyzing documents

Differences between the versions:
- `begin_analyze_document` and `begin_analyze_document_from_url` accept a string with the desired model ID for analysis. The model ID can be any of the prebuilt model IDs or a custom model ID.
- Along with more consolidated analysis methods in the `DocumentAnalysisClient`, the return types have also been improved and remove the hierarchical dependencies between elements. An instance of the `AnalyzeResult` model is now returned which showcases important document elements, such as key-value pairs, entities, tables, and document fields and values, among others, at the top level of the returned model. This can be contrasted with `RecognizedForm` which included more hierarchical relationships, for instance tables were an element of a `FormPage` and not a top-level element.
- In the new version of the library, the functionality of `begin_recognize_content` has been added as a prebuilt model and can be called in library version `azure-ai-formrecognizer (3.2.x)` with `begin_analyze_document` by passing in the `prebuilt-layout` model ID. Similarly, to get general document information, such as key-value pairs, entities, and text layout, the `prebuilt-document` model ID can be used with `begin_analyze_document`. ***As of 3.2.0b3, passing in the `prebuilt-read` model was added to read information about pages and detected languages.***
- When calling `begin_analyze_document` and `begin_analyze_document_from_url` the returned type is an `AnalyzeResult` object, while the various methods used with `FormRecognizerClient` return a list of `RecognizedForm`.
- The `pages` keyword argument is a string with library version `azure-ai-formrecognizer (3.2.x)`. In `azure-ai-formrecognizer (3.1.x)`, `pages` was a list of strings.
- The `include_field_elements` keyword argument is not supported with the `DocumentAnalysisClient`, text details are automatically included with API version `2021-09-30-preview` and later.
- The `reading_order` keyword argument does not exist on `begin_analyze_document` and `begin_analyze_document_from_url`. The service uses `natural` reading order to return data.

Analyzing prebuilt models like business cards, identity documents, invoices, and receipts with `3.1.x`:
```python
with open(path_to_sample_forms, "rb") as f:
    poller = form_recognizer_client.begin_recognize_receipts(receipt=f, locale="en-US")
receipts = poller.result()

for idx, receipt in enumerate(receipts):
    print("--------Recognizing receipt #{}--------".format(idx+1))
    receipt_type = receipt.fields.get("ReceiptType")
    if receipt_type:
        print("Receipt Type: {} has confidence: {}".format(receipt_type.value, receipt_type.confidence))
    merchant_name = receipt.fields.get("MerchantName")
    if merchant_name:
        print("Merchant Name: {} has confidence: {}".format(merchant_name.value, merchant_name.confidence))
    transaction_date = receipt.fields.get("TransactionDate")
    if transaction_date:
        print("Transaction Date: {} has confidence: {}".format(transaction_date.value, transaction_date.confidence))
    if receipt.fields.get("Items"):
        print("Receipt items:")
        for idx, item in enumerate(receipt.fields.get("Items").value):
            print("...Item #{}".format(idx+1))
            item_name = item.value.get("Name")
            if item_name:
                print("......Item Name: {} has confidence: {}".format(item_name.value, item_name.confidence))
            item_quantity = item.value.get("Quantity")
            if item_quantity:
                print("......Item Quantity: {} has confidence: {}".format(item_quantity.value, item_quantity.confidence))
            item_price = item.value.get("Price")
            if item_price:
                print("......Individual Item Price: {} has confidence: {}".format(item_price.value, item_price.confidence))
            item_total_price = item.value.get("TotalPrice")
            if item_total_price:
                print("......Total Item Price: {} has confidence: {}".format(item_total_price.value, item_total_price.confidence))
    subtotal = receipt.fields.get("Subtotal")
    if subtotal:
        print("Subtotal: {} has confidence: {}".format(subtotal.value, subtotal.confidence))
    tax = receipt.fields.get("Tax")
    if tax:
        print("Tax: {} has confidence: {}".format(tax.value, tax.confidence))
    tip = receipt.fields.get("Tip")
    if tip:
        print("Tip: {} has confidence: {}".format(tip.value, tip.confidence))
    total = receipt.fields.get("Total")
    if total:
        print("Total: {} has confidence: {}".format(total.value, total.confidence))
    print("--------------------------------------")
```

Analyzing prebuilt models like business cards, identity documents, invoices, and receipts with `3.2.x`:
```python
with open(path_to_sample_documents, "rb") as f:
    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-receipt", document=f, locale="en-US"
    )
receipts = poller.result()

for idx, receipt in enumerate(receipts.documents):
    print("--------Recognizing receipt #{}--------".format(idx + 1))
    receipt_type = receipt.fields.get("ReceiptType")
    if receipt_type:
        print(
            "Receipt Type: {} has confidence: {}".format(
                receipt_type.value, receipt_type.confidence
            )
        )
    merchant_name = receipt.fields.get("MerchantName")
    if merchant_name:
        print(
            "Merchant Name: {} has confidence: {}".format(
                merchant_name.value, merchant_name.confidence
            )
        )
    transaction_date = receipt.fields.get("TransactionDate")
    if transaction_date:
        print(
            "Transaction Date: {} has confidence: {}".format(
                transaction_date.value, transaction_date.confidence
            )
        )
    if receipt.fields.get("Items"):
        print("Receipt items:")
        for idx, item in enumerate(receipt.fields.get("Items").value):
            print("...Item #{}".format(idx + 1))
            item_name = item.value.get("Name")
            if item_name:
                print(
                    "......Item Name: {} has confidence: {}".format(
                        item_name.value, item_name.confidence
                    )
                )
            item_quantity = item.value.get("Quantity")
            if item_quantity:
                print(
                    "......Item Quantity: {} has confidence: {}".format(
                        item_quantity.value, item_quantity.confidence
                    )
                )
            item_price = item.value.get("Price")
            if item_price:
                print(
                    "......Individual Item Price: {} has confidence: {}".format(
                        item_price.value, item_price.confidence
                    )
                )
            item_total_price = item.value.get("TotalPrice")
            if item_total_price:
                print(
                    "......Total Item Price: {} has confidence: {}".format(
                        item_total_price.value, item_total_price.confidence
                    )
                )
    subtotal = receipt.fields.get("Subtotal")
    if subtotal:
        print(
            "Subtotal: {} has confidence: {}".format(
                subtotal.value, subtotal.confidence
            )
        )
    tax = receipt.fields.get("Tax")
    if tax:
        print("Tax: {} has confidence: {}".format(tax.value, tax.confidence))
    tip = receipt.fields.get("Tip")
    if tip:
        print("Tip: {} has confidence: {}".format(tip.value, tip.confidence))
    total = receipt.fields.get("Total")
    if total:
        print("Total: {} has confidence: {}".format(total.value, total.confidence))
    print("--------------------------------------")
```

Analyzing document content with `3.1.x`:

> NOTE: With version `3.1.x` of the library this method had an optional `language` keyword argument to hint at the language for the document, whereas in version `3.2.x` of the library `locale` is used for this purpose.

```python
with open(path_to_sample_forms, "rb") as f:
    poller = form_recognizer_client.begin_recognize_content(form=f)
form_pages = poller.result()

for idx, content in enumerate(form_pages):
    print("----Recognizing content from page #{}----".format(idx+1))
    print("Page has width: {} and height: {}, measured with unit: {}".format(
        content.width,
        content.height,
        content.unit
    ))
    for table_idx, table in enumerate(content.tables):
        print("Table # {} has {} rows and {} columns".format(table_idx, table.row_count, table.column_count))
        print("Table # {} location on page: {}".format(table_idx, table.bounding_box))
        for cell in table.cells:
            print("...Cell[{}][{}] has text '{}' within bounding box '{}'".format(
                cell.row_index,
                cell.column_index,
                cell.text,
                cell.bounding_box
            ))

    for line_idx, line in enumerate(content.lines):
        print("Line # {} has word count '{}' and text '{}' within bounding box '{}'".format(
            line_idx,
            len(line.words),
            line.text,
            line.bounding_box
        ))
        if line.appearance:
            if line.appearance.style_name == "handwriting" and line.appearance.style_confidence > 0.8:
                print("Text line '{}' is handwritten and might be a signature.".format(line.text))
        for word in line.words:
            print("...Word '{}' has a confidence of {}".format(word.text, word.confidence))

    for selection_mark in content.selection_marks:
        print("Selection mark is '{}' within bounding box '{}' and has a confidence of {}".format(
            selection_mark.state,
            selection_mark.bounding_box,
            selection_mark.confidence
        ))
    print("----------------------------------------")
```


Analyzing document layout with `3.2.x`:
```python
with open(path_to_sample_documents, "rb") as f:
    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-layout", document=f
    )
result = poller.result()

for idx, style in enumerate(result.styles):
    print(
        "Document contains {} content".format(
            "handwritten" if style.is_handwritten else "no handwritten"
        )
    )

for idx, page in enumerate(result.pages):
    print("----Analyzing layout from page #{}----".format(idx + 1))
    print(
        "Page has width: {} and height: {}, measured with unit: {}".format(
            page.width, page.height, page.unit
        )
    )

    for line_idx, line in enumerate(page.lines):
        print(
            "Line # {} has text content '{}' within bounding box '{}'".format(
                line_idx,
                line.content,
                line.bounding_box,
            )
        )

    for word in page.words:
        print(
            "...Word '{}' has a confidence of {}".format(
                word.content, word.confidence
            )
        )

    for selection_mark in page.selection_marks:
        print(
            "Selection mark is '{}' within bounding box '{}' and has a confidence of {}".format(
                selection_mark.state,
                selection_mark.bounding_box,
                selection_mark.confidence,
            )
        )

for table_idx, table in enumerate(result.tables):
    print(
        "Table # {} has {} rows and {} columns".format(
            table_idx, table.row_count, table.column_count
        )
    )
    for region in table.bounding_regions:
        print(
            "Table # {} location on page: {} is {}".format(
                table_idx,
                region.page_number,
                region.bounding_box,
            )
        )
    for cell in table.cells:
        print(
            "...Cell[{}][{}] has text '{}'".format(
                cell.row_index,
                cell.column_index,
                cell.content,
            )
        )
        for region in cell.bounding_regions:
            print(
                "...content on page {} is within bounding box '{}'".format(
                    region.page_number,
                    region.bounding_box,
                )
            )

print("----------------------------------------")
```

Analyzing general document types with `3.2.x`:

> NOTE: Analyzing a document with the `prebuilt-document` model replaces training without labels in version `3.1.x` of the library.

```python
with open(path_to_sample_documents, "rb") as f:
    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-document", document=f
    )
result = poller.result()

for style in result.styles:
    print(
        "Document contains {} content".format(
            "handwritten" if style.is_handwritten else "no handwritten"
        )
    )

for page in result.pages:
    print("----Analyzing document from page #{}----".format(page.page_number))
    print(
        "Page has width: {} and height: {}, measured with unit: {}".format(
            page.width, page.height, page.unit
        )
    )

    for line_idx, line in enumerate(page.lines):
        print(
            "...Line # {} has text content '{}' within bounding box '{}'".format(
                line_idx,
                line.content,
                line.bounding_box,
            )
        )

    for word in page.words:
        print(
            "...Word '{}' has a confidence of {}".format(
                word.content, word.confidence
            )
        )

    for selection_mark in page.selection_marks:
        print(
            "...Selection mark is '{}' within bounding box '{}' and has a confidence of {}".format(
                selection_mark.state,
                selection_mark.bounding_box,
                selection_mark.confidence,
            )
        )

for table_idx, table in enumerate(result.tables):
    print(
        "Table # {} has {} rows and {} columns".format(
            table_idx, table.row_count, table.column_count
        )
    )
    for region in table.bounding_regions:
        print(
            "Table # {} location on page: {} is {}".format(
                table_idx,
                region.page_number,
                region.bounding_box,
            )
        )
    for cell in table.cells:
        print(
            "...Cell[{}][{}] has content '{}'".format(
                cell.row_index,
                cell.column_index,
                cell.content,
            )
        )
        for region in cell.bounding_regions:
            print(
                "...content on page {} is within bounding box '{}'\n".format(
                    region.page_number,
                    region.bounding_box,
                )
            )

print("----Entities found in document----")
for entity in result.entities:
    print("Entity of category '{}' with sub-category '{}'".format(entity.category, entity.sub_category))
    print("...has content '{}'".format(entity.content))
    print("...within '{}' bounding regions".format(entity.bounding_regions))
    print("...with confidence {}\n".format(entity.confidence))

print("----Key-value pairs found in document----")
for kv_pair in result.key_value_pairs:
    if kv_pair.key:
        print(
                "Key '{}' found within '{}' bounding regions".format(
                    kv_pair.key.content,
                    kv_pair.key.bounding_regions,
                )
            )
    if kv_pair.value:
        print(
                "Value '{}' found within '{}' bounding regions\n".format(
                    kv_pair.value.content,
                    kv_pair.value.bounding_regions,
                )
            )
print("----------------------------------------")
```

> NOTE: All of these samples also work with `begin_analyze_document_from_url` when providing a valid URL to the document.

### Analyzing a document with a custom model

Differences between the versions:
- Analyzing a custom model with `DocumentAnalysisClient` uses the general `begin_analyze_document` and `begin_analyze_document_from_url` methods.
- In order to analyze a custom model with `FormRecognizerClient` the `begin_recognize_custom_models` and its corresponding URL methods are used.
- The `include_field_elements` keyword argument is not supported with the `DocumentAnalysisClient`, text details are automatically included with API version `2021-09-30-preview` and later.

Analyze custom document with `3.1.x`:
```python
with open(path_to_sample_forms, "rb") as f:
    poller = form_recognizer_client.begin_recognize_custom_forms(
        model_id=model_id, form=f, include_field_elements=True
    )
forms = poller.result()

for idx, form in enumerate(forms):
    print("--------Recognizing Form #{}--------".format(idx+1))
    print("Form has type {}".format(form.form_type))
    print("Form has form type confidence {}".format(form.form_type_confidence))
    print("Form was analyzed with model with ID {}".format(form.model_id))
    for name, field in form.fields.items():
        # each field is of type FormField
        # label_data is populated if you are using a model trained without labels,
        # since the service needs to make predictions for labels if not explicitly given to it.
        if field.label_data:
            print("...Field '{}' has label '{}' with a confidence score of {}".format(
                name,
                field.label_data.text,
                field.confidence
            ))

        print("...Label '{}' has value '{}' with a confidence score of {}".format(
            field.label_data.text if field.label_data else name, field.value, field.confidence
        ))

    # iterate over tables, lines, and selection marks on each page
    for page in form.pages:
        for i, table in enumerate(page.tables):
            print("\nTable {} on page {}".format(i+1, table.page_number))
            for cell in table.cells:
                print("...Cell[{}][{}] has text '{}' with confidence {}".format(
                    cell.row_index, cell.column_index, cell.text, cell.confidence
                ))
        print("\nLines found on page {}".format(page.page_number))
        for line in page.lines:
            print("...Line '{}' is made up of the following words: ".format(line.text))
            for word in line.words:
                print("......Word '{}' has a confidence of {}".format(
                    word.text,
                    word.confidence
                ))
        if page.selection_marks:
            print("\nSelection marks found on page {}".format(page.page_number))
            for selection_mark in page.selection_marks:
                print("......Selection mark is '{}' and has a confidence of {}".format(
                    selection_mark.state,
                    selection_mark.confidence
                ))

    print("-----------------------------------")
```

Analyze custom document with `3.2.x`:
```python
with open(path_to_sample_documents, "rb") as f:
    poller = document_analysis_client.begin_analyze_document(
        model=model_id, document=f
    )
result = poller.result()

for idx, document in enumerate(result.documents):
    print("--------Analyzing document #{}--------".format(idx + 1))
    print("Document has type {}".format(document.doc_type))
    print("Document has document type confidence {}".format(document.confidence))
    print("Document was analyzed with model with ID {}".format(result.model_id))
    for name, field in document.fields.items():
        field_value = field.value if field.value else field.content
        print("......found field of type '{}' with value '{}' and with confidence {}".format(field.value_type, field_value, field.confidence))


# iterate over tables, lines, and selection marks on each page
for page in result.pages:
    print("\nLines found on page {}".format(page.page_number))
    for line in page.lines:
        print("...Line '{}'".format(line.content))
    for word in page.words:
        print(
            "...Word '{}' has a confidence of {}".format(
                word.content, word.confidence
            )
        )
    if page.selection_marks:
        print("\nSelection marks found on page {}".format(page.page_number))
        for selection_mark in page.selection_marks:
            print(
                "...Selection mark is '{}' and has a confidence of {}".format(
                    selection_mark.state, selection_mark.confidence
                )
            )

for i, table in enumerate(result.tables):
    print("\nTable {} can be found on page:".format(i + 1))
    for region in table.bounding_regions:
        print("...{}".format(i + 1, region.page_number))
    for cell in table.cells:
        print(
            "...Cell[{}][{}] has text '{}'".format(
                cell.row_index, cell.column_index, cell.content
            )
        )
print("-----------------------------------")
```

### Training a custom model

Differences between the versions:
- Files for building a new model for version `3.2.x` can be created using [Form Recognizer Studio][fr_labeling_tool].
- In version `3.1.x` the `use_training_labels` keyword argument was used to indicate whether to use labeled data when creating the custom model.
- In version `3.2.x` the `use_training_labels` keyword argument is not supported since training must be carried out with labeled training documents. Additionally train without labels is now replaced with the prebuilt model `prebuilt-document` which extracts entities, key-value pairs, and layout from a document. 

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
***As of 3.2.0b3, `begin_build_model()` has a required `build_mode` parameter. See https://aka.ms/azsdk/formrecognizer/buildmode for more information about build modes.***

```python
document_model_admin_client = DocumentModelAdministrationClient(endpoint, AzureKeyCredential(key))
poller = document_model_admin_client.begin_build_model(
    container_sas_url, "template", model_id="my-model-id", description="my model description"
)
model = poller.result()

print("Model ID: {}".format(model.model_id))
print("Description: {}".format(model.description))
print("Model created on: {}\n".format(model.created_on))
print("Doc types the model can recognize:")
for name, doc_type in model.doc_types.items():
    print("\nDoc Type: '{}' which has the following fields:".format(name))
    for field_name, confidence in doc_type.field_confidence.items():
        print("Field: '{}' has confidence score {}".format(field_name, confidence))
```

### Managing models

Differences between the versions:
- When using API version `2021-09-30-preview` and later models no longer include submodels, instead a model can analyze different document types.
- When building, composing, or copying models users can now assign their own model IDs and specify a description.
- In version `3.2.x` of the library, only models that build successfully can be retrieved from the get and list model calls. Unsuccessful model operations can be viewed with the get and list operation methods (note that document model operation data persists for only 24 hours). In version `3.1.x` of the library, models that had not succeeded were still created, had to be deleted by the user, and were returned in the list models response.

## Additional samples

For additional samples please take a look at the [Form Recognizer Samples][samples_readme] for more guidance.

[readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/README.md
[samples_readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/README.md
[fr_labeling_tool]: https://aka.ms/azsdk/formrecognizer/formrecognizerstudio