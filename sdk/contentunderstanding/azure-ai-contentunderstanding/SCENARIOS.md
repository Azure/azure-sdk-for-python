# References

- TypeSpec - [Content Understanding 2025-05-01-preview by bojunehsu · Pull Request #21772 · Azure/azure-rest-api-specs-pr](https://github.com/Azure/azure-rest-api-specs-pr/pull/21772)
- Concepts - [Content Understan         ding Glossary - Azure AI services | Microsoft Learn](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/glossary)
- Documentation - [What is Azure AI Content Understanding? - Azure AI services | Microsoft Learn](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/overview)

## Additional Concepts

- Classifier - A component that takes a set of categories to classify an input file with optional splitting.
- Segmentation - Splits content into consecutive segments according to user-configurable definition.
- Source expression - A string that encodes a position in the multimodal input file.
- Analysis mode - The approach to take to perform the analysis: standard, pro, agentic.  More sophisticated modes generally lead to greater quality at increased cost.

# Hero Scenarios

## Content Analyzer Scenarios
### Scenario: Extracting markdown using a prebuilt Document analyzer

```python
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
for i, item in enumerate(content.fields['Items'].value):
  item_obj = item.value 
  print(item_obj['Description'].value) # return a string
  print(item_obj['Quantity'].value) # return a number
  print(item_obj['UnitPrice'].value) # return a number
  print(item_obj['TotalPrice'].value) # return a number
```
### Scenarios: Create a custom content analyzer

```python
endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
# Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client, credential:
	analyzer_id = "my_company_analyzer"

	# Create a custom analyzer using object model based on prebuilt-documentAnalyzer
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
	
	file_url = "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/invoice.pdf"
	poller = await client.content_analyzers.begin_analyze(
		analyzer_id="my_company_analyzer", 
		url=file_url
	)
	result: AnalyzeResult = await poller.result()
	content: MediaContent = result.contents[0]
```  
### Scenario: Output document content  and table

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
## Classifier Scenarios

### Build Classifier

```python
endpoint = os.getenv("AZURE_CONTENT_UNDERSTANDING_ENDPOINT") or ""
key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client, credential:
	classifier_id = "my_classifer"

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

### Classify a Document with a custom classifier

```python
mixed_docs_url = "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/mixed_financial_docs.pdf"

classification_poller = await client.content_classifiers.begin_classify(
	classifier_id="my_classifer",
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
  
## Face Scenario

### Detect faces for existence and locations
```python
endpoint = os.getenv("AZURE_CONTENT_UNDERSTANDING_ENDPOINT") or ""
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client, credential:
        """Detect faces in a test image and display results."""

        # Convert image to base64
        image_data = read_image_to_base64(MY_IMAGE_FILE_PATH)

        response: DetectFacesResult = await client.faces.detect(
            data=image_data, max_detected_faces=10
        )

        if hasattr(response, "detected_faces") and response.detected_faces:
            face_count = len(response.detected_faces)
            for i, face in enumerate(response.detected_faces, 1):
                print(f"\n   Face {i}:")
                if hasattr(face, "bounding_box") and face.bounding_box:
                    bbox = face.bounding_box
                    print(f"      Bounding Box:")
                    print(f"         Left: {bbox.left}, Top: {bbox.top}")
                    print(f"         Width: {bbox.width}, Height: {bbox.height}")
        else:
            print("👤 No faces detected in the image")
```

### Build Person Directory and register faces with specific person

```python
endpoint = os.getenv("AZURE_CONTENT_UNDERSTANDING_ENDPOINT") or ""
key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client, credential:
	# Create a person directory
	directory_id = "my_person_dir"
	await client.person_directories.create(
		person_directory_id=directory_id,
		resource=PersonDirectory(
			description="my person directory",
			tags = {"my_tag": "my_tag_value"}
		)
	)

	# Add a person
	person_response = await client.person_directories.add_person(
		person_directory_id=directory_id,
		body={"tags": {"name": "Demo User 1"}},
	)
	person_id = person_response.person_id

	# Add two different faces to the person from Bill's family
	face_images = [
		"enrollment_data/Bill/Family1-Dad1.jpg",
		"enrollment_data/Bill/Family1-Dad2.jpg",
	]

	for i, face_file in enumerate(face_images):
		image_base64 = read_image_to_base64(face_file)
		face_add_response = await client.person_directories.add_face(
			person_directory_id=directory_id,
			face_source=FaceSource(data=image_base64),
			person_id=person_id,
		)
```

### Find similar faces against person directory

```python
# Continued from the last scenario

query_image_base64 = read_image_to_base64(query_image_path)

response = await client.person_directories.find_similar_faces(
	person_directory_id=directory_id,
	face_source=FaceSource(data=query_image_base64),
	max_similar_faces=10,
)

# Display results for Dad3 query
if hasattr(response, "similar_faces") and response.similar_faces:
	for i, similar_face in enumerate(response.similar_faces, 1):
		print(f"   Face {i}:")
		print(f"      Face ID: {getattr(similar_face, 'face_id', 'N/A')}")
		print(f"      Confidence: {getattr(similar_face, 'confidence', 'N/A')}")
		print(f"      Person ID: {getattr(similar_face, 'person_id', 'N/A')}")
		print()
else:
	print("ℹ️  No similar faces found")
```

### Identify person against a Person Directory

```python
# Assume several persons are added in person directory with the name `directory_id` already
 
family_image_b64 = read_image_to_base64(family_image_path)

# Use identify_person API to identify persons in the image
response = await client.person_directories.identify_person(
	person_directory_id=directory_id,
	face_source=FaceSource(data=family_image_b64),
	max_person_candidates=5,
)

# Display identification results
if hasattr(response, "person_candidates") and response.person_candidates:
	for i, candidate in enumerate(response.person_candidates, 1):
		person_id = getattr(candidate, "person_id", "N/A")
		confidence = getattr(candidate, "confidence", "N/A")
				
		print(f"   Person {i}:")
		print(f"      Person ID: {person_id}")
		print(f"      Confidence: {confidence}")
```