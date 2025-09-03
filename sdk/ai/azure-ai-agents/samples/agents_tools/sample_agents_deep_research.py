# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use Agent operations with the Deep Research tool from
    the Azure Agents service through the synchronous Python client. Deep Research issues
    external Bing Search queries and invokes an LLM, so each run can take several minutes
    to complete.

    For more information see the Deep Research Tool document: https://aka.ms/agents-deep-research

USAGE:
    python sample_agents_deep_research.py

    Before running the sample:

    pip install azure-identity
    pip install --pre azure-ai-projects

    Set this environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the arbitration AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) DEEP_RESEARCH_MODEL_DEPLOYMENT_NAME - The deployment name of the Deep Research AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    4) BING_RESOURCE_NAME - The resource name of the Bing connection, you can find it in the "Connected resources" tab
       in the Management Center of your AI Foundry project.
"""

import os
import time
import re
from typing import Optional, Dict, List
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import DeepResearchTool, MessageRole, ThreadMessage


def convert_citations_to_superscript(markdown_content):
    """
    Convert citation markers in markdown content to HTML superscript format.

    This function finds citation patterns like [78:12+source] and converts them to
    HTML superscript tags <sup>12</sup> for better formatting in markdown documents.
    It also consolidates consecutive citations by sorting and deduplicating them.

    Args:
        markdown_content (str): The markdown content containing citation markers

    Returns:
        str: The markdown content with citations converted to HTML superscript format
    """
    # Pattern to match [number:number+source]
    pattern = r"\u3010\d+:(\d+)\u2020source\u3011"

    # Replace with <sup>captured_number</sup>
    def replacement(match):
        citation_number = match.group(1)
        return f"<sup>{citation_number}</sup>"

    # First, convert all citation markers to superscript
    converted_text = re.sub(pattern, replacement, markdown_content)

    # Then, consolidate consecutive superscript citations
    # Pattern to match multiple superscript tags with optional commas/spaces
    # Matches: <sup>5</sup>,<sup>4</sup>,<sup>5</sup> or <sup>5</sup><sup>4</sup><sup>5</sup>
    consecutive_pattern = r"(<sup>\d+</sup>)(\s*,?\s*<sup>\d+</sup>)+"

    def consolidate_and_sort_citations(match):
        # Extract all citation numbers from the matched text
        citation_text = match.group(0)
        citation_numbers = re.findall(r"<sup>(\d+)</sup>", citation_text)

        # Convert to integers, remove duplicates, and sort
        unique_sorted_citations = sorted(set(int(num) for num in citation_numbers))

        # If only one citation, return simple format
        if len(unique_sorted_citations) == 1:
            return f"<sup>{unique_sorted_citations[0]}</sup>"

        # If multiple citations, return comma-separated format
        citation_list = ",".join(str(num) for num in unique_sorted_citations)
        return f"<sup>{citation_list}</sup>"

    # Remove consecutive duplicate citations and sort them
    final_text = re.sub(consecutive_pattern, consolidate_and_sort_citations, converted_text)

    return final_text


def fetch_and_print_new_agent_response(
    thread_id: str,
    agents_client: AgentsClient,
    last_message_id: Optional[str] = None,
    progress_filename: str = "research_progress.txt",
) -> Optional[str]:
    """
    Fetch the interim agent responses and citations from a thread and write them to a file.

    Args:
        thread_id (str): The ID of the thread to fetch messages from
        agents_client (AgentsClient): The Azure AI agents client instance
        last_message_id (Optional[str], optional): ID of the last processed message
            to avoid duplicates. Defaults to None.
        progress_filename (str, optional): Name of the file to write progress to.
            Defaults to "research_progress.txt".

    Returns:
        Optional[str]: The ID of the latest message if new content was found,
            otherwise returns the last_message_id
    """
    response = agents_client.messages.get_last_message_by_role(
        thread_id=thread_id,
        role=MessageRole.AGENT,
    )

    if not response or response.id == last_message_id:
        return last_message_id  # No new content

    # If not a "cot_summary", return.
    if not any(t.text.value.startswith("cot_summary:") for t in response.text_messages):
        return last_message_id

    print("\nAgent response:")
    agent_text = "\n".join(t.text.value.replace("cot_summary:", "Reasoning:") for t in response.text_messages)
    print(agent_text)

    # Print citation annotations (if any)
    for ann in response.url_citation_annotations:
        print(f"URL Citation: [{ann.url_citation.title}]({ann.url_citation.url})")

    # Write progress to file
    with open(progress_filename, "a", encoding="utf-8") as fp:
        fp.write("\nAGENT>\n")
        fp.write(agent_text)
        fp.write("\n")

        for ann in response.url_citation_annotations:
            fp.write(f"Citation: [{ann.url_citation.title}]({ann.url_citation.url})\n")

    return response.id


def create_research_summary(message: ThreadMessage, filepath: str = "research_report.md") -> None:
    """
    Create a formatted research report from an agent's thread message with numbered citations
    and a references section.

    Args:
        message (ThreadMessage): The thread message containing the agent's research response
        filepath (str, optional): Path where the research summary will be saved.
            Defaults to "research_report.md".

    Returns:
        None: This function doesn't return a value, it writes to a file
    """
    if not message:
        print("No message content provided, cannot create research report.")
        return

    with open(filepath, "w", encoding="utf-8") as fp:
        # Write text summary
        text_summary = "\n\n".join([t.text.value.strip() for t in message.text_messages])
        # Convert citations to superscript format
        text_summary = convert_citations_to_superscript(text_summary)
        fp.write(text_summary)

        # Write unique URL citations with numbered bullets, if present
        if message.url_citation_annotations:
            fp.write("\n\n## Citations\n")
            seen_urls = set()
            # Dictionary mapping full citation content to ordinal number
            citations_ordinals: Dict[str, int] = {}
            # List of citation URLs indexed by ordinal (0-based)
            text_citation_list: List[str] = []

            for ann in message.url_citation_annotations:
                url = ann.url_citation.url
                title = ann.url_citation.title or url

                if url not in seen_urls:
                    # Use the full annotation text as the key to avoid conflicts
                    citation_key = ann.text if ann.text else f"fallback_{url}"

                    # Only add if this citation content hasn't been seen before
                    if citation_key not in citations_ordinals:
                        # Assign next available ordinal number (1-based for display)
                        ordinal = len(text_citation_list) + 1
                        citations_ordinals[citation_key] = ordinal
                        text_citation_list.append(f"[{title}]({url})")

                    seen_urls.add(url)

            # Write citations in order they were added
            for i, citation_text in enumerate(text_citation_list):
                fp.write(f"{i + 1}. {citation_text}\n")

    print(f"Research report written to '{filepath}'.")


if __name__ == "__main__":
    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )
    # [START create_agent_with_deep_research_tool]
    bing_connection = project_client.connections.get(name=os.environ["BING_RESOURCE_NAME"])

    # Initialize a Deep Research tool with Bing Connection ID and Deep Research model deployment name
    deep_research_tool = DeepResearchTool(
        bing_grounding_connection_id=bing_connection.id,
        deep_research_model=os.environ["DEEP_RESEARCH_MODEL_DEPLOYMENT_NAME"],
    )

    # Create Agent with the Deep Research tool and process Agent run
    with project_client:

        with project_client.agents as agents_client:

            # Create a new agent that has the Deep Research tool attached.
            # NOTE: To add Deep Research to an existing agent, fetch it with `get_agent(agent_id)` and then,
            # update the agent with the Deep Research tool.
            agent = agents_client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-agent",
                instructions="You are a helpful Agent that assists in researching scientific topics.",
                tools=deep_research_tool.definitions,
            )

            # [END create_agent_with_deep_research_tool]
            print(f"Created agent, ID: {agent.id}")

            # Create thread for communication
            thread = agents_client.threads.create()
            print(f"Created thread, ID: {thread.id}")

            # Create message to thread
            message = agents_client.messages.create(
                thread_id=thread.id,
                role="user",
                content=(
                    "Research the current state of studies on orca intelligence and orca language, including what is currently known about orcas' cognitive capabilities and communication systems."
                ),
            )
            print(f"Created message, ID: {message.id}")

            print(f"Start processing the message... this may take a few minutes to finish. Be patient!")
            # Poll the run as long as run status is queued or in progress
            run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)
            last_message_id = None
            while run.status in ("queued", "in_progress"):
                time.sleep(1)
                run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)

                last_message_id = fetch_and_print_new_agent_response(
                    thread_id=thread.id,
                    agents_client=agents_client,
                    last_message_id=last_message_id,
                    progress_filename="research_progress.txt",
                )
                print(f"Run status: {run.status}")

            # Once the run is finished, print the final status and ID
            print(f"Run finished with status: {run.status}, ID: {run.id}")

            if run.status == "failed":
                print(f"Run failed: {run.last_error}")

            # Fetch the final message from the agent in the thread and create a research summary
            final_message = agents_client.messages.get_last_message_by_role(thread_id=thread.id, role=MessageRole.AGENT)
            if final_message:
                create_research_summary(final_message)

            # Clean-up and delete the agent once the run is finished.
            # NOTE: Comment out this line if you plan to reuse the agent later.
            agents_client.delete_agent(agent.id)
            print("Deleted agent")
