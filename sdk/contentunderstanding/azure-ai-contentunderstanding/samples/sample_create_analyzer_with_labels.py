# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_create_analyzer_with_labels.py

DESCRIPTION:
    This sample demonstrates the API pattern for creating a custom analyzer with labeled training
    data from Azure Blob Storage. Labeled data improves extraction accuracy by providing annotated
    examples that teach the model how to identify and extract specific fields from your documents.

    This sample is mainly to show the API pattern for creating an analyzer with labeled training
    data. For an easier labeling workflow, use Content Understanding Studio
    (https://contentunderstanding.ai.azure.com/home), a web-based UI that provides a convenient
    way to label documents, manage training data, and build custom analyzers in the same interface.

    ## About labeled training data

    Labeled training data consists of annotated sample documents that teach the model how to extract
    specific fields. Each labeled document includes:

    - The source document (image, PDF, etc.)
    - Field labels and bounding box annotations (.labels.json)
    - Pre-computed OCR results (.result.json, optional, speeds up training)

    When you create an analyzer with a LabeledDataKnowledgeSource, the service uses these
    annotations as in-context learning examples to improve field extraction quality. This is
    especially useful when:
    - Prebuilt analyzers don't extract the fields you need
    - Your documents have a specialized layout or terminology
    - You need higher accuracy for specific fields

    Labeled receipt data is available in this repo at
    samples/sample_files/training_samples/.

    ## Preparing training data in Azure Blob Storage

    The labeled data must be stored in an Azure Blob Storage container accessible via a SAS URL
    with Read and List permissions. You have two options to set this up:

    ### Option A: Manual upload (recommended for production)

    1. Create an Azure Blob Storage container (or use an existing one).
    2. Upload the contents of samples/sample_files/training_samples/ into the container.
       You may upload into the container root or a subfolder (e.g., training_samples/).
    3. Generate a SAS (Shared Access Signature) URL for the container with at least List and
       Read permissions. In Azure Portal: Storage account -> Containers -> your container ->
       Shared access token; set expiry and permissions, then generate the SAS URL.
    4. Set CONTENTUNDERSTANDING_TRAINING_DATA_SAS_URL to the full SAS URL
       (e.g., https://<account>.blob.core.windows.net/<container>?sv=...&se=...).
    5. If you uploaded into a subfolder, set CONTENTUNDERSTANDING_TRAINING_DATA_PREFIX to that
       path (e.g., training_samples/). If files are at the container root, omit the prefix or
       leave it unset.

    ### Option B: Auto-upload (convenient for development)

    Instead of uploading manually, provide the storage account name and container name. The sample
    will upload local label files and generate a User Delegation SAS URL via DefaultAzureCredential.
    This requires your credential to have read/write/list permissions on the storage account.

    Set these environment variables:
    - CONTENTUNDERSTANDING_TRAINING_DATA_STORAGE_ACCOUNT - Storage account name
    - CONTENTUNDERSTANDING_TRAINING_DATA_CONTAINER - Container name
    - CONTENTUNDERSTANDING_TRAINING_DATA_PREFIX - (Optional) Path prefix within the container

USAGE:
    python sample_create_analyzer_with_labels.py

    Set the environment variables with your own values before running the sample:
    1) CONTENTUNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) CONTENTUNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    For labeled data (choose one):
    Option A:
    3) CONTENTUNDERSTANDING_TRAINING_DATA_SAS_URL - SAS URL for the container with labeled data.
    Option B:
    3) CONTENTUNDERSTANDING_TRAINING_DATA_STORAGE_ACCOUNT - Storage account name for auto-upload.
    4) CONTENTUNDERSTANDING_TRAINING_DATA_CONTAINER - Container name for auto-upload.
    Optional:
    5) CONTENTUNDERSTANDING_TRAINING_DATA_PREFIX - Path prefix within the container (e.g., "training_samples/").

    Before using custom analyzers, you MUST configure model deployments for your Microsoft Foundry
    resource. See sample_update_defaults.py for setup instructions.
"""

import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer,
    ContentAnalyzerConfig,
    ContentFieldDefinition,
    ContentFieldSchema,
    ContentFieldType,
    GenerationMethod,
    KnowledgeSource,
    LabeledDataKnowledgeSource,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

load_dotenv()


def build_receipt_field_schema() -> ContentFieldSchema:
    """Builds a ContentFieldSchema for receipt extraction
    with MerchantName, Items (array of Quantity / Name / Price), and TotalPrice.
    """
    item_definition = ContentFieldDefinition(
        type=ContentFieldType.OBJECT,
        method=GenerationMethod.EXTRACT,
        description="Individual item details",
        properties={
            "Quantity": ContentFieldDefinition(
                type=ContentFieldType.STRING,
                method=GenerationMethod.EXTRACT,
                description="Quantity of the item",
            ),
            "Name": ContentFieldDefinition(
                type=ContentFieldType.STRING,
                method=GenerationMethod.EXTRACT,
                description="Name of the item",
            ),
            "Price": ContentFieldDefinition(
                type=ContentFieldType.STRING,
                method=GenerationMethod.EXTRACT,
                description="Price of the item",
            ),
        },
    )

    return ContentFieldSchema(
        name="receipt_schema",
        description="Schema for receipt extraction with items",
        fields={
            "MerchantName": ContentFieldDefinition(
                type=ContentFieldType.STRING,
                method=GenerationMethod.EXTRACT,
                description="Name of the merchant",
            ),
            "Items": ContentFieldDefinition(
                type=ContentFieldType.ARRAY,
                method=GenerationMethod.GENERATE,
                description="List of items purchased",
                item_definition=item_definition,
            ),
            "TotalPrice": ContentFieldDefinition(
                type=ContentFieldType.STRING,
                method=GenerationMethod.EXTRACT,
                description="Total amount",
            ),
        },
    )


def upload_training_data(
    storage_account_name: str,
    container_name: str,
    credential: DefaultAzureCredential,
    local_directory: str,
    prefix: Optional[str] = None,
) -> None:
    """Uploads local training data files (images, .labels.json, .result.json) to an
    Azure Blob container. Existing blobs with the same name are overwritten.

    :param storage_account_name: Storage account name.
    :param container_name: Container name (created if it does not exist).
    :param credential: Credential with write access to the container.
    :param local_directory: Local folder containing the label files.
    :param prefix: Optional blob prefix (virtual folder) to prepend, e.g. "training_samples/".
    """
    from azure.storage.blob import BlobServiceClient
    from azure.core.exceptions import ResourceExistsError

    container_client = BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=credential,
    ).get_container_client(container_name)

    try:
        container_client.create_container()
    except ResourceExistsError:
        pass  # Container already exists

    local_path = Path(local_directory)
    for file_path in local_path.iterdir():
        if file_path.is_file() and file_path.name != "README.md":
            blob_name = (
                file_path.name
                if not prefix
                else prefix.rstrip("/") + "/" + file_path.name
            )
            print(f"Uploading {file_path.name} -> {blob_name}")
            with open(file_path, "rb") as data:
                container_client.upload_blob(name=blob_name, data=data, overwrite=True)


def generate_user_delegation_sas_url(
    storage_account_name: str,
    container_name: str,
    credential: DefaultAzureCredential,
) -> str:
    """Generates a User Delegation SAS URL (Read + List) for an Azure Blob container.
    Uses TokenCredential so no storage account key is needed.
    """
    from azure.storage.blob import (
        BlobServiceClient,
        ContainerSasPermissions,
        generate_container_sas,
    )

    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=credential,
    )

    user_delegation_key = blob_service_client.get_user_delegation_key(
        key_start_time=datetime.now(timezone.utc),
        key_expiry_time=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    sas_token = generate_container_sas(
        account_name=storage_account_name,
        container_name=container_name,
        user_delegation_key=user_delegation_key,
        permission=ContainerSasPermissions(read=True, list=True),
        expiry=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    return f"https://{storage_account_name}.blob.core.windows.net/{container_name}?{sas_token}"


def main() -> None:
    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

    # [START create_analyzer_with_labels]
    analyzer_id = f"receipt_analyzer_{int(time.time())}"

    # Step 1: Build the receipt field schema
    field_schema = build_receipt_field_schema()

    # Step 2: Resolve training data SAS URL
    # You can either provide a pre-generated SAS URL (Option A) or let the sample
    # upload local label files and generate one automatically (Option B).
    # See Sample16_CreateAnalyzerWithLabels.md for manual upload instructions.
    # Option A: use a pre-generated SAS URL with Read + List permissions
    training_data_sas_url = os.getenv("CONTENTUNDERSTANDING_TRAINING_DATA_SAS_URL")

    # Option B: upload local label files and auto-generate a SAS URL
    if not training_data_sas_url:
        storage_account = os.getenv("CONTENTUNDERSTANDING_TRAINING_DATA_STORAGE_ACCOUNT")
        container = os.getenv("CONTENTUNDERSTANDING_TRAINING_DATA_CONTAINER")
        if storage_account and container:
            azure_credential = DefaultAzureCredential()
            local_label_dir = os.path.join(
                os.path.dirname(__file__), "sample_files", "training_samples"
            )
            prefix = os.getenv("CONTENTUNDERSTANDING_TRAINING_DATA_PREFIX")
            upload_training_data(storage_account, container, azure_credential, local_label_dir, prefix)
            training_data_sas_url = generate_user_delegation_sas_url(
                storage_account, container, azure_credential
            )

    training_data_prefix = os.getenv("CONTENTUNDERSTANDING_TRAINING_DATA_PREFIX")

    # Step 3: Create knowledge source from labeled data (if available)
    knowledge_sources: List[KnowledgeSource] = []
    if training_data_sas_url:
        labeled_source = LabeledDataKnowledgeSource(
            container_url=training_data_sas_url,
            file_list_path="",
        )
        if training_data_prefix:
            labeled_source.prefix = training_data_prefix
        knowledge_sources.append(labeled_source)

    # Step 4: Create the analyzer
    custom_analyzer = ContentAnalyzer(
        base_analyzer_id="prebuilt-document",
        description="Receipt analyzer with labeled training data",
        config=ContentAnalyzerConfig(enable_layout=True, enable_ocr=True),
        field_schema=field_schema,
        models={
            "completion": "gpt-4.1",
            "embedding": "text-embedding-3-large",
        },
        knowledge_sources=knowledge_sources if knowledge_sources else None,
    )

    poller = client.begin_create_analyzer(
        analyzer_id=analyzer_id,
        resource=custom_analyzer,
        allow_replace=True,
    )
    result = poller.result()

    print(f"Analyzer created: {analyzer_id}")
    print(f"  Description: {result.description}")
    print(f"  Base analyzer: {result.base_analyzer_id}")
    print(f"  Fields: {len(result.field_schema.fields) if result.field_schema and result.field_schema.fields else 0}")
    print(f"  Knowledge sources: {len(result.knowledge_sources) if result.knowledge_sources else 0}")
    # [END create_analyzer_with_labels]

    # Clean up - delete the analyzer
    # Note: In production code, you typically keep analyzers and reuse them for
    # multiple analyses. Deletion is mainly useful for testing and development cleanup.
    client.delete_analyzer(analyzer_id=analyzer_id)
    print(f"Analyzer '{analyzer_id}' deleted.")


if __name__ == "__main__":
    main()
