# Form Recognizer Design Overview

The Form Recognizer client library provides two clients to interact with the service: `FormRecognizerClient` and 
`CustomFormClient`, which can be imported from the `azure.ai.formrecognizer` namespace. The asynchronous clients 
can be imported from `azure.ai.formrecognizer.aio`.

`FormRecognizerClient` provides methods for interacting with the receipt and layout models.
`CustomFormClient` provides the methods for training custom models to analyze forms.

Authentication is achieved by passing an instance of `CognitiveKeyCredential("<api_key>")` to the client,
or by providing a token credential from `azure.identity` to use Azure Active Directory.

## Receipt and Layout

Receipt and layout are accessed through the `FormRecognizerClient`. The input form or document can be passed as a 
string url/path to the image, or as a file stream. The SDK will determine content-type and send the appropriate header. 

Both receipt and layout methods return poller objects which are used to get the result.
The `begin_extract_receipt` method returns an `ExtractedReceipt` with hardcoded receipt fields.
The `begin_extract_layout` method returns the extracted tables as a `list[TableCell]`.

If the keyword argument `include_text_details=True` is passed in, the `raw_` attributes will be populated with the
raw OCR result for each value/cell referenced by the `elements`. If the user wishes to retrieve the full
deserialized raw OCR result, they can get it with the `raw_response_hook` keyword argument. This will additionally 
return the full raw response returned from the service (example at bottom of page).

### Form Recognizer Client
```python
from azure.ai.formrecognizer import FormRecognizerClient

client = FormRecognizerClient(endpoint: str, credential: Union[CognitiveKeyCredential, TokenCredential])

client.begin_extract_receipt(form: Union[str, BytesIO], **kwargs) -> LROPoller -> List[ExtractedReceipt]

client.begin_extract_layout(form: Union[str, BytesIO], **kwargs) -> LROPoller -> List[ExtractedLayoutPage]
```

### Receipt Models
```python
class ExtractedReceipt(DictMixin):
    receipt_items: List[ReceiptItem]
    merchant_address: FieldValue
    merchant_name: FieldValue
    merchant_phone_number: FieldValue
    receipt_type: FieldValue
    subtotal: FieldValue
    tax: FieldValue
    tip: FieldValue
    total: FieldValue
    transaction_date: FieldValue
    transaction_time: FieldValue
    page_range: List[int]
    page_metadata: PageMetadata

class ReceiptItem:
    name: FieldValue
    quantity: FieldValue
    item_price: FieldValue
    total_price: FieldValue

class FieldValue:
    value: Union[str, float, int, datetime]
    text: str
    bounding_box: List[float]
    confidence: float
    raw_fields: List[Union[ExtractedLine, ExtractedWord]]

class ExtractedLine:
    text: str
    bounding_box: List[float]
    language: str
    words: List[ExtractedWord]

class ExtractedWord:
    text: str
    bounding_box: List[float]
    confidence: float

class PageMetadata:
    page_number: int
    angle: float
    width: int
    height: int
    unit: str
    language: str
```

### Receipt Sample
```python
from azure.ai.formrecognizer import FormRecognizerClient

client = FormRecognizerClient(endpoint, credential)

receipt_image = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/contoso-allinone.jpg"
poller = client.begin_extract_receipt(receipt_image)
receipt = poller.result()
r = receipt[0]

print("Receipt contained the following values with confidences: ")
print("ReceiptType: {}, confidence: {}").format(r.receipt_type.value, r.receipt_type.confidence)
print("MerchantName: {}, confidence: {}").format(r.merchant_name.value, r.merchant_name.confidence)
print("MerchantAddress: {}, confidence: {}").format(r.merchant_address.value, r.merchant_address.confidence)
print("MerchantPhoneNumber: {}, confidence: {}").format(r.merchant_phone_number.value, r.merchant_phone_number.confidence)
print("TransactionDate: {}, confidence: {}").format(r.transaction_date.value, r.transaction_date.confidence)
print("TransactionTime: {}, confidence: {}").format(r.transaction_time.value, r.transaction_time.confidence)
for item in r.receipt_items:
    print("Item Name: {}, confidence: {}").format(item.name.value, item.name.confidence)
    print("Item Quantity: {}, confidence: {}").format(item.quantity.value, item.quantity.confidence)
    print("Item Price: {}, confidence: {}").format(item.item_price.value, item.item_price.confidence)
    print("Total Price: {}, confidence: {}").format(item.total_price.value, item.total_price.confidence)
print("Subtotal: {}, confidence: {}").format(r.subtotal.value, r.subtotal.confidence)
print("Tax: {}, confidence: {}").format(r.tax.value, r.tax.confidence)
print("Tip: {}, confidence: {}").format(r.tip.value, r.tip.confidence)
print("Total: {}, confidence: {}").format(r.total.value, r.total.confidence)

# Access as a dictionary
for item, field_value in r.items():
    print(item, field_value.value, field_value.text, field_value.confidence, field_value.bounding_box)
```

### Layout Models

```python
class ExtractedLayoutPage:
    tables: List[ExtractedTable]
    page_number: int
    page_metadata: PageMetadata

class ExtractedTable: 
    cells: List[TableCell]
    row_count: int
    column_count: int

class TableCell:
    text: str
    column_index: int
    column_span: int
    confidence: float
    is_footer: bool
    is_header: bool
    row_index: int
    row_span: int
    bounding_box: List[float]
    raw_fields: List[Union[ExtractedLine, ExtractedWord]]

class ExtractedLine:
    text: str
    bounding_box: List[float]
    language: str
    words: List[ExtractedWord]

class ExtractedWord:
    text: str
    bounding_box: List[float]
    confidence: float

class PageMetadata:
    page_number: int
    angle: float
    width: int
    height: int
    unit: str
    language: str
```

### Layout Sample

```python
import pandas as pd
from azure.ai.formrecognizer import FormRecognizerClient

client = FormRecognizerClient(endpoint, credential)

table_image = "https://www.traveldailymedia.com/assets/2020/01/Table2.png"
poller = client.begin_extract_layout(table_image)
result = poller.result()

table = result[0].tables[0] # page 1, table 1
my_table = [[None for x in range(table.column_count)] for y in range(table.row_count)]
for cell in table.cells:
    my_table[cell.row_index][cell.column_index] = cell.text

dftable = pd.DataFrame(my_table)
print(dftable.to_markdown())
```

## Custom

The `CustomFormClient` provides all the operations necessary for training a custom model, analyzing a form with a 
custom model, and managing a user's custom models on their account.

The user can choose to train with or without labels using the methods `begin_labeled_training` or `begin_training`. 
Both methods take as input a blob SAS uri or valid path to the documents to use for training. Each training method 
will return a poller object which is used to get the training result.

A custom model can be used to analyze forms using the `begin_extract_form` method.
The `model_id` from the training result is passed into the methods, along with the input form to analyze (content-type
is determined internally). This method also returns a poller object which is used to get the result.

In order for the user to manage their custom models, a few methods are available to list custom models, delete a model,
get a models summary for the account, or get a training result.

### Custom Form Client
```python
from azure.ai.formrecognizer import CustomFormClient

client = CustomFormClient(endpoint: str, credential: Union[CognitiveKeyCredential, TokenCredential])

client.begin_labeled_training(
    source: str, source_prefix_filter: str, include_sub_folders: bool=False
) -> LROPoller -> LabeledCustomModel

client.begin_training(
    source: str, source_prefix_filter: str, include_sub_folders: bool=False
) -> LROPoller -> CustomModel

client.begin_extract_form(form: Union[str, BytesIO], model_id: str) -> LROPoller -> ExtractedForm

client.list_custom_models() -> ItemPaged[ModelInfo]

client.get_models_summary() -> ModelsSummary

client.get_custom_model(model_id: str) -> CustomModel

client.get_labeled_custom_model(model_id: str) -> LabeledCustomModel

client.delete_custom_model(model_id: str) -> None
```

### Custom Models Unlabeled
```python
# Training ---------------------------------------------------
class CustomModel:
    model_id: str
    status: str
    created_on: ~datetime.datetime
    last_updated_on: ~datetime.datetime
    train_result: TrainResult

class TrainResult:
    form_type_id: int
    extracted_fields: List[str]
    documents: List[TrainingDocumentInfo]
    errors: List[FormRecognizerError]

class TrainingDocumentInfo:
    document_name: str
    status: str
    page_count: int
    errors: List[FormRecognizerError]

class FormRecognizerError:
    code: str
    message: str
```

### Custom Models Labeled
```python
# Training ---------------------------------------------------
class LabeledCustomModel:
    model_id: str
    status: str
    created_on: ~datetime.datetime
    last_updated_on: ~datetime.datetime
    train_result: LabeledTrainResult

class LabeledTrainResult:
    fields: List[FieldNames]
    average_model_accuracy: float
    documents: List[TrainingDocumentInfo]
    errors: List[FormRecognizerError]

class TrainingDocumentInfo:
    document_name: str
    status: str
    page_count: int
    errors: List[FormRecognizerError]

class FieldNames:
    field_name: str
    accuracy: float

class FormRecognizerError:
    code: str
    message: str
```

### Custom Extract Form
```python
# Analyze ---------------------------------------------------
class ExtractedForm:
    page_range: List[int]
    form_type_id: int
    pages: List[ExtractedPage]

class ExtractedPage:
    fields: List[ExtractedField]
    tables: List[ExtractedTable]
    page_number: int
    page_metadata: PageMetadata

class ExtractedField:
    label: str
    label_outline: List[float]
    label_raw_fields: List[Union[ExtractedLine, ExtractedWord]]
    value: Union[str, int, float, datetime]
    value_text: str
    value_outline: List[float]
    value_raw_fields: List[Union[ExtractedLine, ExtractedWord]]
    confidence: float

class ExtractedLine:
    text: str
    bounding_box: List[float]
    language: str
    words: List[ExtractedWord]

class ExtractedWord:
    text: str
    bounding_box: List[float]
    confidence: float

class PageMetadata:
    page_number: int
    angle: float
    width: int
    height: int
    unit: str
    language: str
```

### List/Get/Delete Models
```python
class ModelInfo:
    model_id: str
    status: str
    created_on: ~datetime.datetime
    last_updated_on: ~datetime.datetime

class ModelsSummary:
    count: int
    limit: int
    last_updated_on: ~datetime.datetime
```


### Custom Training Samples

#### Custom: Train and Analyze without labels
```python
from azure.ai.formrecognizer import CustomFormClient

client = CustomFormClient(endpoint=endpoint, credential=credential)

# Train
blob_sas_url = "xxxxx"  # training documents uploaded to blob storage
poller = client.begin_training(blob_sas_url)
model = poller.result()

# Custom model information
print("Model ID: {}".format(model.model_id))
print("Status: {}".format(model.status))
print("Created on: {}".format(model.created_on))
print("Last updated on: {}".format(model.last_updated_on))

# Training result information
train_result = model.train_result
for document in train_result.documents:
    print(document.name)
    print(document.status)
    print(document.page_count)
    print(document.errors)

print("Form type ID: {}".format(train_result.form_type_id))
print("Extracted fields:")
print(train_result.extracted_fields)

# Analyze
blob_sas_url = "xxxxx"  # form to analyze uploaded to blob storage
poller = client.begin_extract_form(blob_sas_url, model_id=model.model_id)
result = poller.result()

for page in result.pages:
    print("Page: {}".format(page.page_number))
    for field in page.fields:
        print(field.label, field.value_text)
```

#### Train and Analyze with labels
```python
from azure.ai.formrecognizer import CustomFormClient

client = CustomFormClient(endpoint=endpoint, credential=credential)

# Train
blob_sas_url = "xxxxx"  # training documents uploaded to blob storage
poller = client.begin_labeled_training(blob_sas_url)
model = poller.result()

# Custom model information
print("Model ID: {}".format(model.model_id))
print("Status: {}".format(model.status))
print("Created on: {}".format(model.created_on))
print("Last updated on: {}".format(model.last_updated_on))

# Training result information
train_result = model.train_result
for document in train_result.documents:
    print(document.name)
    print(document.status)
    print(document.page_count)
    print(document.errors)

print("Average model accuracy: {}".format(train_result.average_model_accuracy))
print("Fields extracted/accuracy")
for field in train_result.fields:
    print(field.field_name, field.accuracy)

blob_sas_url = "xxxxx"  # form to analyze uploaded to blob storage
poller = client.begin_extract_form(blob_sas_url, model_id=model.model_id)
result = poller.result()

for page in result.pages:
    print("Page: {}".format(page.page_number))
    for field in page.fields:
        print(field.label, field.value_text)
```

#### List custom models
```python
from azure.ai.formrecognizer import CustomFormClient

client = CustomFormClient(endpoint=endpoint, credential=credential)
custom_models = list(client.list_custom_models())
for model in custom_models:
    print(model.model_id, model.status)
```

#### Get models summary
```python
from azure.ai.formrecognizer import CustomFormClient

client = CustomFormClient(endpoint=endpoint, credential=credential)
summary = client.get_models_summary()

print("Number of models: {}".format(summary.count))
print("Max number of models that can be trained with this subscription: {}".format(summary.limit))
print("Datetime when summary was updated: {}".format(summary.last_updated_on))
```


#### Get training result with a model ID
```python
from azure.ai.formrecognizer import CustomFormClient

client = CustomFormClient(endpoint=endpoint, credential=credential)
train_result = client.get_training_result(model_id="xxxxx")

for document in train_result.documents:
    print(document.name)
    print(document.status)
    print(document.page_count)
    print(document.errors)

print("Average model accuracy: {}".format(train_result.average_model_accuracy))
print("Fields extracted/accuracy")
for field in train_result.fields:
    print(field.field_name, field.accuracy)
```


#### Delete custom model
```python
from azure.ai.formrecognizer import CustomFormClient

client = CustomFormClient(endpoint=endpoint, credential=credential)
client.delete_custom_model(model_id="xxxxx")
```


#### Extra: Get the read result (raw OCR result) using the response hook keyword argument
```python
from azure.ai.formrecognizer import FormRecognizerClient

client = FormRecognizerClient(endpoint=endpoint, credential=credential)
receipt_image = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/contoso-allinone.jpg"

def callback(resp):
    raw_response = resp.raw_response  # raw response from service
    result = resp.raw_ocr_result
    for page in result.pages:
        print("On page: {}".format(page.page_number))
        for line in page.lines:
            print("Line: {}".format(line.text))
            for word in line.words:
                print("Words: {}".format(word.text))
        
        
poller = client.begin_extract_receipt(receipt_image, include_text_details=True, raw_response_hook=callback)
receipt = poller.result()
```