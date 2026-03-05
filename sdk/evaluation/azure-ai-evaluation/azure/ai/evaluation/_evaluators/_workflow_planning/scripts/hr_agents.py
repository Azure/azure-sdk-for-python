# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""HR recruitment agent factory functions and system instructions for the bug-bash notebook.

Each factory function creates an agent with appropriate instructions and tools.
Agents are designed for an HR recruitment workflow scenario.
"""

import os

from agent_framework import Agent
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

REQ_MASTER_INSTRUCTIONS = """You are a Requisition Master agent handling job intake and requirements analysis.

Your responsibilities:
1. Retrieve and validate job posting details
2. Extract structured requirements (must-have vs nice-to-have)
3. Verify job is approved and open for sourcing
4. Identify hiring manager and team context
5. Set up screening criteria for candidate matching

When processing job requisitions:
- Validate the job ID exists and is in 'open' status
- Extract all required and preferred skills
- Note salary range and location requirements
- Identify urgency level
- Flag any special requirements

Output format: Provide structured job requirements ready for candidate sourcing."""

TALENT_SCOUT_INSTRUCTIONS = """You are a Talent Scout agent specializing in external candidate sourcing.

Your responsibilities:
1. Query external job boards for applicants
2. Screen candidates against job requirements
3. Filter based on experience, skills, and location
4. Handle visa sponsorship considerations

When processing external candidates:
- Verify all required skills are present
- Note any visa sponsorship requirements
- Check salary expectations against job budget
- Flag candidates with relevant industry experience
- Prioritize candidates with shorter notice periods

Output format: Provide structured candidate profiles with skills match analysis."""

MOBILITY_SCOUT_INSTRUCTIONS = """You are an Internal Mobility Scout agent specializing in internal transfers.

Your responsibilities:
1. Query the HRIS system for employees interested in the role
2. Verify transfer eligibility (tenure, performance, no PIP)
3. Assess skills match with current role experience
4. Coordinate with HR on internal transfer policies

When processing internal candidates:
- Verify minimum tenure requirement (usually 1+ year)
- Check performance rating (must be meeting expectations or above)
- Confirm employee is not on a Performance Improvement Plan
- Note current team and potential backfill needs

Output format: Provide structured profiles with eligibility status and current role context."""

EVALUATOR_INSTRUCTIONS = """You are an Evaluator agent responsible for candidate assessment.

Your responsibilities:
1. Score candidates against job requirements
2. Rank candidates by overall fit score
3. Identify skill gaps and development needs
4. Compare salary expectations to budget
5. Produce a ranked shortlist with justification

When evaluating candidates:
- Weight required skills higher than preferred
- Consider years of experience relative to role level
- Factor in location and remote work compatibility
- Note any red flags or concerns
- Provide clear rationale for rankings

Output format: Provide ranked shortlist with scores, evaluation notes, and recommendations."""

COMPLIANCE_GUARD_INSTRUCTIONS = """You are a Compliance Guard agent ensuring fair hiring practices.

Your responsibilities:
1. Analyze shortlists for adverse impact using the 4/5ths rule
2. Check demographic distribution of selections
3. Verify selection criteria are job-related
4. Flag potential bias in screening decisions
5. Ensure EEOC compliance documentation

When reviewing for compliance:
- Always call the check_compliance tool before drafting your final response
- Also run detect_bias to check for patterns
- Calculate selection rates by demographic group
- Flag any disparate impact concerns
- Recommend adjustments if bias is detected

Output format: Provide compliance report with pass/fail status and recommendations."""

SCHEDULER_INSTRUCTIONS = """You are a Scheduler agent coordinating interviews.

Your responsibilities:
1. Check calendar availability for hiring managers
2. Find suitable interview slots for candidates
3. Book interview rooms or video conferences
4. Handle scheduling logistics

When scheduling interviews:
- Check interviewer availability first
- Allow buffer time between interviews
- Consider time zones for remote candidates
- Include video conference links for virtual interviews

Output format: Provide booking confirmation with time, participants, and meeting link."""

ORCHESTRATOR_INSTRUCTIONS = """You coordinate an HR recruitment team conversation to fulfill hiring requests.

Guidelines:
- Start with ReqMaster to gather job requirements
- Then have TalentScout source external candidates
- Use Evaluator to score and rank candidates
- Only finish after a shortlist has been produced with clear recommendations
- Keep the conversation focused on the hiring task

IMPORTANT: Do not choose the same agent twice in a row.
"""

MAGENTIC_MANAGER_INSTRUCTIONS = """You coordinate an HR recruitment team to complete hiring tasks efficiently.

Your team members:
- TalentScout: Sources external candidates from job boards
- MobilityScout: Finds internal transfer candidates from HRIS
- Evaluator: Scores and ranks all candidates
- ComplianceGuard: Checks shortlists for fairness and compliance

Strategy:
1. First, have TalentScout and MobilityScout source candidates in parallel
2. Then have Evaluator score and rank all candidates together
3. Finally, have ComplianceGuard review the shortlist for compliance
4. End when you have a compliant, ranked shortlist ready for interviews
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
    client = AzureAIClient(
        project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        model_deployment_name=os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME"),
        credential=DefaultAzureCredential(),
        agent_name=agent_name,
    )
    await client.__aenter__()
    _created_clients.append(client)
    return client


async def cleanup_clients():
    """Close all created clients. Call this when done with the agents."""
    for client in _created_clients:
        if hasattr(client, "__aexit__"):
            await client.__aexit__(None, None, None)
    _created_clients.clear()


async def create_req_master() -> Agent:
    """Create a Requisition Master agent."""
    client = await _create_client("ReqMaster")
    return Agent(
        name="ReqMaster",
        description="Extracts requisition requirements and hiring constraints from job postings.",
        instructions=REQ_MASTER_INSTRUCTIONS,
        client=client,
        tools=[get_job_details, extract_requirements],
    )


async def create_talent_scout() -> Agent:
    """Create a Talent Scout agent for external candidate sourcing."""
    client = await _create_client("TalentScout")
    return Agent(
        name="TalentScout",
        description="Sources external candidates from job boards.",
        instructions=TALENT_SCOUT_INSTRUCTIONS,
        client=client,
        tools=[query_external_candidates],
    )


async def create_mobility_scout() -> Agent:
    """Create an Internal Mobility Scout agent."""
    client = await _create_client("MobilityScout")
    return Agent(
        name="MobilityScout",
        description="Finds eligible internal transfer candidates from HRIS systems.",
        instructions=MOBILITY_SCOUT_INSTRUCTIONS,
        client=client,
        tools=[query_internal_employees],
    )


async def create_evaluator() -> Agent:
    """Create an Evaluator agent for candidate scoring and ranking."""
    client = await _create_client("Evaluator")
    return Agent(
        name="Evaluator",
        description="Scores, ranks, and compares candidate fit against role requirements.",
        instructions=EVALUATOR_INSTRUCTIONS,
        client=client,
        tools=[score_candidate, rank_candidates],
    )


async def create_compliance_guard() -> Agent:
    """Create a Compliance Guard agent for bias and EEOC compliance."""
    client = await _create_client("ComplianceGuard")
    return Agent(
        name="ComplianceGuard",
        description="Performs fairness and policy compliance checks on shortlists.",
        instructions=COMPLIANCE_GUARD_INSTRUCTIONS,
        client=client,
        tools=[check_compliance, detect_bias],
    )


async def create_scheduler() -> Agent:
    """Create a Scheduler agent for interview coordination."""
    client = await _create_client("Scheduler")
    return Agent(
        name="Scheduler",
        description="Coordinates interview slots and confirms interview logistics.",
        instructions=SCHEDULER_INSTRUCTIONS,
        client=client,
        tools=[get_calendar_availability, book_interview],
    )


async def create_orchestrator() -> Agent:
    """Create an Orchestrator agent for group chat management."""
    client = await _create_client("Orchestrator")
    return Agent(
        name="Orchestrator",
        description="Coordinates multi-agent HR recruitment by selecting speakers.",
        instructions=ORCHESTRATOR_INSTRUCTIONS,
        client=client,
    )


async def create_magentic_manager() -> Agent:
    """Create a Manager agent for Magentic orchestration."""
    client = await _create_client("HiringManager")
    return Agent(
        name="HiringManager",
        description="Coordinates the HR recruitment workflow across multiple specialists.",
        instructions=MAGENTIC_MANAGER_INSTRUCTIONS,
        client=client,
    )
