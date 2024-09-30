# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to use assistants operations with a file attachment to the message from
    the Azure Assistants service using a synchronous client.

    See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-assistants/README.md#key-concepts

USAGE:
    python sample_assistant_with_code_interpreter_attachment.py

    Set these two environment variables before running the sample:
    1) AZUREAI_ENDPOINT_URL - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.models.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZUREAI_ENDPOINT_KEY - Your model key (a 32-character string). Keep it secret.
"""
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from azure.ai.assistants import AssistantsClient
from azure.ai.assistants.models._enums import FilePurpose
from azure.ai.assistants.models._models import CodeInterpreterToolDefinition, MessageAttachment
from azure.core.credentials import AzureKeyCredential

import os, time


def setup_console_trace_exporter():
    exporter = ConsoleSpanExporter()
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(exporter))

    # Instrument requests to capture HTTP-related telemetry
    RequestsInstrumentor().instrument()


def sample_assistant_basic_operation():

    setup_console_trace_exporter()

    try:
        endpoint = os.environ["AZUREAI_ENDPOINT_URL"]
        key = os.environ["AZUREAI_ENDPOINT_KEY"]
        api_version = os.environ.get("AZUREAI_API_VERSION", "2024-07-01-preview")
    except KeyError:
        print("Missing environment variable 'AZUREAI_ENDPOINT_URL' or 'AZUREAI_ENDPOINT_KEY'")
        print("Set them before running this sample.")
        exit()

    assistant_client = AssistantsClient(endpoint=endpoint, credential=AzureKeyCredential(key), api_version=api_version)
    print("Created assistant client")
    
    # upload a file and wait for it to be processed
    file = assistant_client.upload_file(file_path="product_info_1.md", purpose=FilePurpose.ASSISTANTS)
    while assistant_client.get_file(file.id).status != "processed":
        time.sleep(4)  
        
    code_interpreter = CodeInterpreterToolDefinition()
    
    # notices that CodeInterpreterToolDefinition as tool must be added or the assistant unable to view the file
    assistant = assistant_client.create_assistant(
        model="gpt-4o-mini", name="my-assistant", instructions="You are helpful assistant",
        tools=[code_interpreter]
    )
    print("Created assistant, assistant ID", assistant.id)

    thread = assistant_client.create_thread()
    print("Created thread, thread ID", thread.id)    

    # create a message with the attachment
    attachment = MessageAttachment(file_id=file.id, tools=[code_interpreter])
    message = assistant_client.create_message(thread_id=thread.id, role="user", content="What does the attachment say?", attachments=[attachment])
    print("Created message, message ID", message.id)

    run = assistant_client.create_run(thread_id=thread.id, assistant_id=assistant.id)
    print("Created run, run ID", run.id)

    # poll the run as long as run status is queued or in progress
    while run.status not in ["completed", "failed"]:
        # wait for 4 second
        time.sleep(4)
        run = assistant_client.get_run(thread_id=thread.id, run_id=run.id)
        print("Run status:", run.status)

    print("Run completed with status:", run.status)
    
    
    messages = assistant_client.list_messages(thread_id=thread.id)
    
    """ sample of messages:
    {
        'object': 'list',
        'data': [
            {
                'id': 'msg_0elWDAFSiFilkPUqlVcBtzYl',
                'object': 'thread.message',
                'created_at': 1727500540,
                'assistant_id': 'asst_H8JFgwiLzhUNGu1DyFaqAlDj',
                'thread_id': 'thread_wjpGkwYTFBwJTzg9itbtWNSy',
                'run_id': 'run_ukIfQrZTXemCBBJzJdDEaljB',
                'role': 'assistant',
                'content': [
                    {
                        'type': 'text',
                        'text': {
                            'value': 'The attachment you provided contains information about a product with item number 1. Here is a summary of its content:\n\n### Brand\n- Contoso Galaxy Innovations\n\n### Category\n- Smart Eyewear\n\n### Features\n- Augmented Reality interface\n- Voice-controlled AI assistant\n- HD video recording with 3D audio\n- UV protection and blue light filtering\n- Wireless charging with extended battery life\n\n### User Guide\n1. **Introduction**\n   - Introduction to your new SmartView Glasses\n2. **Product Overview**\n   - Overview of features and controls\n3. **Sizing and Fit**\n   - Finding your perfect fit and style adjustments\n4. **Proper Care and Maintenance**\n   - Cleaning and caring for your SmartView Glasses\n5. **Break-in Period**\n   - Adjusting to the augmented reality experience\n6. **Safety Tips**\n   - Safety guidelines for public and private spaces\n7. **Troubleshooting**\n   - Quick fixes for common issues\n\n### Warranty Information\n- Two-year limited warranty on all electronic components\n\n### Contact Information\n- Customer Support at support@contoso-galaxy-innovations.com\n\n### Return Policy\n- 30-day return policy with no questions asked\n\n### FAQ\n- How to sync your SmartView Glasses with your devices\n- Troubleshooting connection issues\n- Customizing your augmented reality environment\n\nIf you have any specific questions or need further details, feel free to ask!',
                            'annotations': []
                        }
                    }
                ],
                'attachments': [],
                'metadata': {}
            },
            {
                'id': 'msg_k3aD7ocZ9K9I5DVtmO37gQ8a',
                'object': 'thread.message',
                'created_at': 1727500535,
                'assistant_id': None,
                'thread_id': 'thread_wjpGkwYTFBwJTzg9itbtWNSy',
                'run_id': None,
                'role': 'user',
                'content': [
                    {
                        'type': 'text',
                        'text': {
                            'value': 'What does the attachment say?',
                            'annotations': []
                        }
                    }
                ],
                'attachments': [
                    {
                        'file_id': 'assistant-0O4ydFGHOtHb3Iso0qGMLO4U',
                        'tools': [
                            {
                                'type': 'code_interpreter'
                            },
                            {
                                'type': 'file_search'
                            }
                        ]
                    }
                ],
                'metadata': {}
            }
        ],
        'first_id': 'msg_0elWDAFSiFilkPUqlVcBtzYl',
        'last_id': 'msg_k3aD7ocZ9K9I5DVtmO37gQ8a',
        'has_more': False
    }
"""
    print("messages:", messages)
    
    assistant_client.delete_file(file.id)
    print("Deleted file")

    assistant_client.delete_assistant(assistant.id)
    print("Deleted assistant")


if __name__ == "__main__":
    sample_assistant_basic_operation()
