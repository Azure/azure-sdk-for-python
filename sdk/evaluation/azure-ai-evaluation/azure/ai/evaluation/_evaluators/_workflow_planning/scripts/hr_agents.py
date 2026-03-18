# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""HR recruitment agent factory functions and system instructions for the bug-bash notebook.

Each factory function creates an agent with appropriate instructions and tools.
Agents are designed for an HR recruitment workflow scenario.
"""

import os
from typing import Any

from agent_framework.azure import AzureAIClient
from azure.identity import DefaultAzureCredential

from .hr_tools import (
    book_interview,
    check_compliance,
    detect_bias,
    extract_requirements,
    get_calendar_availability,
    get_job_details,
    query_external_candidates,
    query_internal_employees,
    rank_candidates,
    score_candidate,
)

# ============================================================================
# System Instructions
# ============================================================================

REQ_MASTER_INSTRUCTIONS = """You are ReqMaster.
Use only these tools: get_job_details, extract_requirements.
Retrieve job details, confirm the role is open, and return structured must-have and nice-to-have requirements.
Include job_id, hiring manager, location/remote constraints, urgency, and salary range."""

TALENT_SCOUT_INSTRUCTIONS = """You are TalentScout.
Use only query_external_candidates.
Return external candidates for the job and summarize fit using the tool output.
Always preserve and surface candidate_id values exactly as returned."""

MOBILITY_SCOUT_INSTRUCTIONS = """You are MobilityScout.
Use only query_internal_employees.
Return internal candidates for the job and summarize transfer readiness from the tool output.
Always preserve and surface candidate_id and employee_id values exactly as returned."""

EVALUATOR_INSTRUCTIONS = """You are Evaluator.
Use score_candidate and rank_candidates.
Score provided candidate_id values against the job, then produce a ranked shortlist.
Keep candidate_id values exact and include them in every recommendation."""

COMPLIANCE_GUARD_INSTRUCTIONS = """You are ComplianceGuard.
Use check_compliance and detect_bias.
Evaluate the provided shortlist for compliance and bias, then return a clear pass/fail-style summary.
If concerns exist, list concrete adjustments."""

SCHEDULER_INSTRUCTIONS = """You are Scheduler.
Use get_calendar_availability and book_interview.
Find available slots and book interviews for specified candidate_id values.
Return clear confirmations with candidate_id, manager, date, and time."""

ORCHESTRATOR_INSTRUCTIONS = """You coordinate an HR recruitment team conversation to fulfill hiring requests.

Guidelines:
- Start with ReqMaster to gather job requirements
- Then have TalentScout source external candidates
- Use Evaluator to score and rank candidates
- Only finish after a shortlist has been produced with clear recommendations
- Keep the conversation focused on the hiring task
- When requesting evaluation, compliance checks, or scheduling, pass candidate_id lists exactly as returned by sourcing tools

IMPORTANT: Do not choose the same agent twice in a row.
"""

MAGENTIC_MANAGER_INSTRUCTIONS = """You coordinate an HR recruitment team to complete hiring tasks efficiently.

Your team members:
- TalentScout: Sources external candidates from job boards
- MobilityScout: Finds internal transfer candidates from HRIS
- Evaluator: Scores and ranks all candidates
- ComplianceGuard: Checks shortlists for fairness and compliance

Your task is to orchestrate these specialists to fulfill hiring requests, ensuring clear handoffs.
Always choose the agent best suited for the current step, and give it clear instructions on what to do.
When requesting evaluation, compliance checks, or scheduling, pass candidate_id lists exactly as returned by sourcing tools
Only set is_progress_being_made to False or is_in_loop to True IF AND ONLY IF the workflow is genuinely stuck without a clear path forward. Do not set these flags to these values for any other reason.
"""


# ============================================================================
# Agent Factory Functions
# ============================================================================

# Track all created clients for cleanup
_created_clients: list[AzureAIClient] = []


async def _create_client(agent_name: str) -> AzureAIClient:
    """Create a new independent AzureAIClient instance for an agent.

    Each agent gets its own client to ensure proper message isolation
    in group chat and other multi-agent workflows.
    """
    _ = agent_name
    client = AzureAIClient(
        project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        deployment_name=os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME"),
        credential=DefaultAzureCredential(),
    )
    _created_clients.append(client)
    return client


async def cleanup_clients():
    """Close all created clients. Call this when done with the agents."""
    for client in _created_clients:
        close_method = getattr(client, "close", None)
        if callable(close_method):
            close_result: Any = close_method()
            if hasattr(close_result, "__await__"):
                await close_result
    _created_clients.clear()


async def create_req_master():
    """Create a Requisition Master agent."""
    client = await _create_client("ReqMaster")
    return client.as_agent(
        name="ReqMaster",
        description="Extracts requisition requirements and hiring constraints from job postings.",
        instructions=REQ_MASTER_INSTRUCTIONS,
        tools=[get_job_details, extract_requirements],
        default_options={"store": False}
    )


async def create_talent_scout():
    """Create a Talent Scout agent for external candidate sourcing."""
    client = await _create_client("TalentScout")
    return client.as_agent(
        name="TalentScout",
        description="Sources external candidates from job boards.",
        instructions=TALENT_SCOUT_INSTRUCTIONS,
        tools=[query_external_candidates],
        default_options={"store": False}
    )


async def create_mobility_scout():
    """Create an Internal Mobility Scout agent."""
    client = await _create_client("MobilityScout")
    return client.as_agent(
        name="MobilityScout",
        description="Finds eligible internal transfer candidates from HRIS systems.",
        instructions=MOBILITY_SCOUT_INSTRUCTIONS,
        tools=[query_internal_employees],
        default_options={"store": False}
    )


async def create_evaluator():
    """Create an Evaluator agent for candidate scoring and ranking."""
    client = await _create_client("Evaluator")
    return client.as_agent(
        name="Evaluator",
        description="Scores, ranks, and compares candidate fit against role requirements.",
        instructions=EVALUATOR_INSTRUCTIONS,
        tools=[score_candidate, rank_candidates],
        default_options={"store": False}
    )


async def create_compliance_guard():
    """Create a Compliance Guard agent for bias and EEOC compliance."""
    client = await _create_client("ComplianceGuard")
    return client.as_agent(
        name="ComplianceGuard",
        description="Performs fairness and policy compliance checks on shortlists.",
        instructions=COMPLIANCE_GUARD_INSTRUCTIONS,
        tools=[check_compliance, detect_bias],
        default_options={"store": False}
    )


async def create_scheduler():
    """Create a Scheduler agent for interview coordination."""
    client = await _create_client("Scheduler")
    return client.as_agent(
        name="Scheduler",
        description="Coordinates interview slots and confirms interview logistics.",
        instructions=SCHEDULER_INSTRUCTIONS,
        tools=[get_calendar_availability, book_interview],
        default_options={"store": False}
    )


async def create_orchestrator():
    """Create an Orchestrator agent for group chat management."""
    client = await _create_client("Orchestrator")
    return client.as_agent(
        name="Orchestrator",
        description="Coordinates multi-agent HR recruitment by selecting speakers.",
        instructions=ORCHESTRATOR_INSTRUCTIONS,
        default_options={"store": False}
    )


async def create_magentic_manager():
    """Create a Manager agent for Magentic orchestration."""
    client = await _create_client("HiringManager")
    return client.as_agent(
        name="HiringManager",
        description="Coordinates the HR recruitment workflow across multiple specialists.",
        instructions=MAGENTIC_MANAGER_INSTRUCTIONS,
        default_options={"store": False}
    )
