# References

- TypeSpec - [Content Understanding 2025-05-01-preview by bojunehsu · Pull Request #21772 · Azure/azure-rest-api-specs-pr](https://github.com/Azure/azure-rest-api-specs-pr/pull/21772)
- Concepts - [Content Understanding Glossary - Azure AI services | Microsoft Learn](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/glossary)
- Documentation - [What is Azure AI Content Understanding? - Azure AI services | Microsoft Learn](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/overview)

## Additional Concepts

- **Classifier** - A component that takes a set of categories to classify an input file with optional splitting.
- **Segmentation** - Splits content into consecutive segments according to user-configurable definition.
- **Source expression** - A string that encodes a position in the multimodal input file.
- **Analysis mode** - The approach to take to perform the analysis: standard, pro, agentic. More sophisticated modes generally lead to greater quality at increased cost.

## Patch Overrides Enabled

The SDK includes several patch overrides that enhance usability:

- **Field Value Access** - All field types (StringField, NumberField, etc.) now have a unified `.value` property for easier access
- **Positional Parameters** - Face detection and comparison methods accept positional arguments for URLs and image data
- **Simplified Face Operations** - Person directory operations accept direct URLs/bytes instead of requiring FaceSource objects

# Hero Scenarios

## Content Analyzer Scenarios

### Scenario: Extracting markdown using a prebuilt Document analyzer

```python
import os
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client, credential:
	file_url = "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/invoice.pdf"

	poller = await client.content_analyzers.begin_analyze(
		analyzer_id="prebuilt-documentAnalyzer", url=file_url
		# processing_location=ProcessingLocation.DATA_ZONE,
		# string_encoding=StringEncoding.UTF16
	)
	result: AnalyzeResult = await poller.result()

	# AnalyzeResult contains the full analysis result and can be used to access various properties
	# We are using markdown content as an example of what can be extracted
	# A PDF file has only one content element even if it contains multiple pages
	content: MediaContent = result.contents[0]
	print(content.markdown)
```

### Scenario: Extracting invoice fields with the prebuilt invoice analyzer

```python
"""Analyze an invoice and display the extracted fields."""
file_url = "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/invoice.pdf"

poller = await client.content_analyzers.begin_analyze(
    analyzer_id="prebuilt-invoice", 
    url=file_url
)
result: AnalyzeResult = await poller.result()
content: MediaContent = result.contents[0]

# Field existence check is omitted for brevity
print(content.fields['CustomerName'].value)
print(content.fields['InvoiceTotal'].value)

# Get array values in the invoice items
for item in content.fields['Items'].value:
    item_obj = item.value                   # enabled by patch. Simplified from `item.value_object
    print(item_obj['Description'].value)    # enabled by patch. Simplified from `item_obj['Description'].value_string`
    print(item_obj['Quantity'].value)       # enabled by patch. Simplified from `item_obj['Quantity'].value_number`
    print(item_obj['UnitPrice'].value)      # enabled by patch.
    print(item_obj['TotalPrice'].value)     # eanbled by patch.
```

### Scenario: Create a custom content analyzer

```python
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer, ContentAnalyzerConfig, FieldSchema, 
    FieldDefinition, FieldType, GenerationMethod
)

analyzer_id = "my_company_analyzer"

custom_analyzer = ContentAnalyzer(
    base_analyzer_id="prebuilt-documentAnalyzer",
    description="Custom analyzer for extracting company information",
    config=ContentAnalyzerConfig(
        enable_layout=True,
        enable_ocr=True,
        estimate_field_source_and_confidence=True,
        return_details=True,
    ),
    field_schema=FieldSchema(
        name="company_schema",
        description="Schema for extracting company information",
        fields={
            "company_name": FieldDefinition(
                type=FieldType.STRING,
                method=GenerationMethod.EXTRACT,
                description="Name of the company",
            ),
            "total_amount": FieldDefinition(
                type=FieldType.NUMBER,
                method=GenerationMethod.EXTRACT,
                description="Total amount on the document",
            ),
            "summary": FieldDefinition(
                type=FieldType.STRING,
                method=GenerationMethod.GENERATE,
                description="Summary of the document",
            )
        },
    ),
)

poller = await client.content_analyzers.begin_create_or_replace(
    analyzer_id=analyzer_id,
    resource=custom_analyzer,
)
create_result = await poller.result()
```

### Scenario: Update analyzer with patch operation

```python
"""Update analyzer description and tags using patch operation."""
updated_analyzer = ContentAnalyzer(
    description="Updated description for company analyzer",
    tags={"tag_added": "new tag value", "tag_to_change": "updated_value", "tag_removed": None}
)

response = await client.content_analyzers.update(
    analyzer_id="my_company_analyzer",
    resource=updated_analyzer,
)
```

### Scenario: Output document content and table information

```python
endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
# Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client, credential:
	with open("sample_files/sample_invoice.pdf", "rb") as f:
		pdf_bytes: bytes = f.read()

	poller = await client.content_analyzers.begin_analyze_binary(
		analyzer_id="prebuilt-documentAnalyzer",
		input=pdf_bytes,
		content_type="application/pdf",
	)
	result: AnalyzeResult = await poller.result()

	# Check if this is document content to access document-specific properties
	if content.kind == MediaContentKind.DOCUMENT:
		document_content: DocumentContent = content  # type: ignore
		print(f"\n📚 Document Information:")
		print(f"Start page: {document_content.start_page_number}")
		print(f"End page: {document_content.end_page_number}")

		# Enumerate pages info
		if document_content.pages is not None:
			print(f"\n📄 Pages ({len(document_content.pages)}):")
			for i, page in enumerate(document_content.pages):
				unit = document_content.unit or "units"
				print(f"  Page {i + 1}: {page.width} x {page.height} {unit}")

		# Access table layout
		if document_content.tables is not None:
			print(f"\n📊 Tables ({len(document_content.tables)}):")
			table_counter = 1
			for table in document_content.tables:
				row_count: int = table.row_count
				col_count: int = table.column_count
				print(
					f"  Table {table_counter}: {row_count} rows x {col_count} columns"
				)
				table_counter += 1
	else:
		print("\n📚 Document Information: Not available for this content type")
```    
### Scenario: Get operation status and results

```python
"""Monitor long-running analysis operation and retrieve results."""
operation_id = "operation_GUID"

# Check operation status
status = await client.content_analyzers.get_operation_status(operation_id)
print(f"Status: {status.status}")

# Get results when complete
if status.status == "succeeded":
    result = await client.content_analyzers.get_result(operation_id)
    print(f"Analysis completed with {len(result.contents)} content items")
```


## Classifier Scenarios

### Scenario: Build Classifier

```python
from azure.ai.contentunderstanding.models import ContentClassifier, ClassifierCategory

classifier_id = "my_classifier"

classifier_schema = ContentClassifier(
    categories={
        "Loan application": ClassifierCategory(
            description="Documents submitted by individuals or businesses to request funding"
        ),
        "Invoice": ClassifierCategory(
            description="Billing documents issued by sellers or service providers to request payment for goods or services"
        ),
        "Bank_Statement": ClassifierCategory(
            description="Official statements issued by banks that summarize account activity over a period"
        ),
    },
    split_mode="auto",
    description="Classify between loan application, invoices, and bank statements",
)

# Start the classifier creation operation
poller = await client.content_classifiers.begin_create_or_replace(
    classifier_id=classifier_id,
    resource=classifier_schema,
)

# Wait for the classifier to be created
result = await poller.result()
```

### Scenario: Classify a Document with a custom classifier

```python
mixed_docs_url = "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/mixed_financial_docs.pdf"

classification_poller = await client.content_classifiers.begin_classify(
    classifier_id="my_classifier",
    url=mixed_docs_url
)
classification_result = await classification_poller.result()

# Display classification results
for content in classification_result.contents:
	document_content: DocumentContent = content
	print(f"   Category: {document_content.category}")
	print(f"   Start Page Number: {document_content.start_page_number}")
	print(f"   End Page Number: {document_content.end_page_number}")

```

### Scenario: Classify binary content

```python
"""Classify document from binary data."""
with open("document.pdf", "rb") as f:
    document_bytes = f.read()

poller = await client.content_classifiers.begin_classify_binary(
    classifier_id="my_classifier",
    input=document_bytes,
    content_type="application/pdf"
)
result = await poller.result()
```

## Face Scenarios

### Scenario: Detect faces for existence and locations

```python
"""Detect faces in an image and display results."""
# Using patch override: direct bytes input
with open("family.jpg", "rb") as f:
    image_bytes = f.read()

response = await client.faces.detect(
    image_bytes, max_detected_faces=10
)

if response.detected_faces:
    face_count = len(response.detected_faces)
    for i, face in enumerate(response.detected_faces, 1):
        print(f"\nFace {i}:")
        if face.bounding_box:
            bbox = face.bounding_box
            print(f"   Bounding Box: Left={bbox.left}, Top={bbox.top}, Width={bbox.width}, Height={bbox.height}")
else:
    print("No faces detected in the image")
```

### Scenario: Compare two faces

```python
"""Compare two faces using patch override for positional parameters."""
# Using patch override: direct URL and bytes comparison
face1_url = "https://example.com/face1.jpg"
with open("face2.jpg", "rb") as f:
    face2_bytes = f.read()

result = await client.faces.compare(face1_url, face2_bytes) # Enabled by patch
print(f"Similarity: {result.similarity}")
```

### Scenario: Build Person Directory and register faces

```python
"""Create person directory and add persons with faces."""
directory_id = "my_person_dir"

# Create directory
await client.person_directories.create(
    person_directory_id=directory_id,
    resource=PersonDirectory(
        description="My person directory",
        tags={"purpose": "demo"}
    )
)

# Add person
person_response = await client.person_directories.add_person(
    person_directory_id=directory_id,
    body={"tags": {"name": "Demo User 1"}}
)
person_id = person_response.person_id

# Add faces using patch override: direct bytes input
with open("face1.jpg", "rb") as f:
    face1_bytes = f.read()


for face_bytes in face_images:
    face_response = await client.person_directories.add_face(
        person_directory_id=directory_id,
        face1_bytes,  # Using patch override
        person_id=person_id
    )
    # Enabled by patch, simplified from:
    # face_add_response = await client.person_directories.add_face(
    #     person_directory_id=directory_id,
    #     face_source=FaceSource(data=face1_bytes),
    #     person_id=person_id,
    # )    
```

### Scenario: Find similar faces against person directory

```python
"""Find similar faces using patch override for direct input."""
with open("query_face.jpg", "rb") as f:
    query_image_bytes = f.read()

response = await client.person_directories.find_similar_faces(
    person_directory_id=directory_id,
    query_image_bytes,  # Using patch override, compared to `face_source=FaceSource(data=query_image_bytes),`
    max_similar_faces=10,
)

if response.similar_faces:
    for i, similar_face in enumerate(response.similar_faces, 1):
        print(f"Face {i}:")
        print(f"   Face ID: {similar_face.face_id}")
        print(f"   Confidence: {similar_face.confidence}")
        print(f"   Person ID: {similar_face.person_id}")
```

### Scenario: Identify person against a Person Directory

```python
"""Identify person using patch override for direct input."""
with open("family_image.jpg", "rb") as f:
    family_image_bytes = f.read()

response = await client.person_directories.identify_person(
    person_directory_id=directory_id,
    family_image_bytes,  # Using patch override, simplified from `face_source=FaceSource(data=family_image_b64),`
    max_person_candidates=5,
)

if response.person_candidates:
    for i, candidate in enumerate(response.person_candidates, 1):
        print(f"Person {i}:")
        print(f"   Person ID: {candidate.person_id}")
        print(f"   Confidence: {candidate.confidence}")
```

## Management Scenarios

### Scenario: List and manage analyzers

```python
"""List all analyzers and get specific analyzer details."""
# List all analyzers
analyzers = client.content_analyzers.list()
for analyzer in analyzers:
    print(f"Analyzer: {analyzer.analyzer_id} - {analyzer.description}")

# Get specific analyzer
analyzer = await client.content_analyzers.get("my_company_analyzer")
print(f"Config: {analyzer.config}")
```

### Scenario: List and manage classifiers

```python
"""List all classifiers and get specific classifier details."""
# List all classifiers
classifiers = client.content_classifiers.list()
for classifier in classifiers:
    print(f"Classifier: {classifier.classifier_id} - {classifier.description}")

# Get specific classifier
classifier = await client.content_classifiers.get("my_classifier")
print(f"Categories: {list(classifier.categories.keys())}")
```

### Scenario: List and manage person directories

```python
"""List all person directories and get specific directory details."""
# List all directories
directories = client.person_directories.list()
for directory in directories:
    print(f"Directory: {directory.person_directory_id} - {directory.description}")

# Get specific directory
directory = await client.person_directories.get("my_person_dir")
print(f"Tags: {directory.tags}")

# List persons in directory
persons = client.person_directories.list_persons("my_person_dir")
for person in persons:
    print(f"Person: {person.person_id} - {person.tags}")
```