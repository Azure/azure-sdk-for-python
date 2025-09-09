# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_text_extractive_summarization.py

DESCRIPTION:
    This sample demonstrates how to run an **extractive summarization** action over text.

USAGE:
    python sample_text_extractive_summarization.py

REQUIRED ENV VARS (for AAD / DefaultAzureCredential):
    AZURE_TEXT_ENDPOINT
    AZURE_CLIENT_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_SECRET

NOTE:
    If you want to use AzureKeyCredential instead, set:
      - AZURE_TEXT_ENDPOINT
      - AZURE_TEXT_KEY
"""

# [START text_extractive_summarization]
import os

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    ExtractiveSummarizationOperationAction,
    ExtractiveSummarizationOperationResult,
)


def sample_text_extractive_summarization():
    # get settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    client = TextAnalysisClient(endpoint, credential=credential)

    # Build input
    text_a = (
        "Windows 365 was in the works before COVID-19 sent companies around the world on a scramble to secure "
        "solutions to support employees suddenly forced to work from home, but “what really put the "
        "firecracker behind it was the pandemic, it accelerated everything,” McKelvey said. She explained "
        "that customers were asking, “How do we create an experience for people that makes them still feel "
        "connected to the company without the physical presence of being there?” In this new world of "
        "Windows 365, remote workers flip the lid on their laptop, boot up the family workstation or clip a "
        "keyboard onto a tablet, launch a native app or modern web browser and login to their Windows 365 "
        "account. From there, their Cloud PC appears with their background, apps, settings and content just "
        "as they left it when they last were last there – in the office, at home or a coffee shop. And "
        "then, when you’re done, you’re done. You won’t have any issues around security because you’re not "
        "saving anything on your device,” McKelvey said, noting that all the data is stored in the cloud. "
        "The ability to login to a Cloud PC from anywhere on any device is part of Microsoft’s larger "
        "strategy around tailoring products such as Microsoft Teams and Microsoft 365 for the post-pandemic "
        "hybrid workforce of the future, she added. It enables employees accustomed to working from home to "
        "continue working from home; it enables companies to hire interns from halfway around the world; it "
        "allows startups to scale without requiring IT expertise. “I think this will be interesting for "
        "those organizations who, for whatever reason, have shied away from virtualization. This is giving "
        "them an opportunity to try it in a way that their regular, everyday endpoint admin could manage,” "
        "McKelvey said. The simplicity of Windows 365 won over Dean Wells, the corporate chief information "
        "officer for the Government of Nunavut. His team previously attempted to deploy a traditional "
        "virtual desktop infrastructure and found it inefficient and unsustainable given the limitations of "
        "low-bandwidth satellite internet and the constant need for IT staff to manage the network and "
        "infrastructure. We didn’t run it for very long,” he said. “It didn’t turn out the way we had "
        "hoped. So, we actually had terminated the project and rolled back out to just regular PCs.” He "
        "re-evaluated this decision after the Government of Nunavut was hit by a ransomware attack in "
        "November 2019 that took down everything from the phone system to the government’s servers. "
        "Microsoft helped rebuild the system, moving the government to Teams, SharePoint, OneDrive and "
        "Microsoft 365. Manchester’s team recruited the Government of Nunavut to pilot Windows 365. Wells "
        "was intrigued, especially by the ability to manage the elastic workforce securely and seamlessly. "
        "“The impact that I believe we are finding, and the impact that we’re going to find going forward, "
        "is being able to access specialists from outside the territory and organizations outside the "
        "territory to come in and help us with our projects, being able to get people on staff with us to "
        "help us deliver the day-to-day expertise that we need to run the government,” he said. “Being able "
        "to improve healthcare, being able to improve education, economic development is going to improve "
        "the quality of life in the communities.”"
    )

    text_input = MultiLanguageTextInput(
        multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
    )

    action = ExtractiveSummarizationOperationAction(
        name="Extractive Summarization"
    )

    # Start long-running operation (sync)
    poller = client.begin_analyze_text_job(
        text_input=text_input,
        actions=[action],
    )

    # Operation metadata (pre-final)
    print(f"Operation ID: {poller.details.get('operation_id')}")

    # Wait for completion and get pageable of TextActions
    paged_actions = poller.result()

    # Final-state metadata
    d = poller.details
    print(f"Job ID: {d.get('job_id')}")
    print(f"Status: {d.get('status')}")
    print(f"Created: {d.get('created_date_time')}")
    print(f"Last Updated: {d.get('last_updated_date_time')}")
    if d.get("expiration_date_time"):
        print(f"Expires: {d.get('expiration_date_time')}")
    if d.get("display_name"):
        print(f"Display Name: {d.get('display_name')}")

    # Iterate results (sync pageable)
    for actions_page in paged_actions:
        # Page-level counts (if available)
        print(
            f"Completed: {actions_page.completed}, "
            f"In Progress: {actions_page.in_progress}, "
            f"Failed: {actions_page.failed}, "
            f"Total: {actions_page.total}"
        )

        # Items are the individual operation results
        for op_result in actions_page.items_property or []:
            if isinstance(op_result, ExtractiveSummarizationOperationResult):
                print(f"\nAction Name: {op_result.task_name}")
                print(f"Action Status: {op_result.status}")
                print(f"Kind: {op_result.kind}")

                result = op_result.results
                for doc in (result.documents or []):
                    print(f"\nDocument ID: {doc.id}")
                    for sent in (doc.sentences or []):
                        # Each sentence is part of the extractive summary
                        print(f"  Sentence: {sent.text}")
                        print(f"    Rank score: {sent.rank_score}")
                        print(f"    Offset: {sent.offset}")
                        print(f"    Length: {sent.length}")
            else:
                # Other action kinds, if present
                try:
                    print(
                        f"\n[Non-extractive action] name={op_result.task_name}, "
                        f"status={op_result.status}, kind={op_result.kind}"
                    )
                except Exception:
                    print("\n[Non-extractive action present]")

# [END text_extractive_summarization]


def main():
    sample_text_extractive_summarization()


if __name__ == "__main__":
    main()
