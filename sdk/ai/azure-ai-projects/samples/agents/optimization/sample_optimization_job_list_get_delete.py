# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to list optimization
    jobs (with optional filters), get a specific job by ID, and delete a job.

USAGE:
    python sample_optimization_job_list_get_delete.py

    Before running the sample:

    pip install "azure-ai-projects>=2.3.0" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry portal.
    2) FOUNDRY_AGENT_NAME              - Required. Filter the list to jobs for this agent.
    3) JOB_ID                  - Required. If set, fetches and deletes this specific job.
"""

import os

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import JobStatus

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ["FOUNDRY_AGENT_NAME"]
job_id = os.environ["JOB_ID"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):

    # ------------------------------------------------------------------
    # 1. List the most recent 10 optimization jobs (unfiltered).
    # ------------------------------------------------------------------
    print("Listing optimization jobs (limit=10):")
    count = 0
    for job_list_item in project_client.agents.list_optimization_jobs(limit=10):
        agent_str = getattr(job_list_item.target_configuration, "name", "?")
        print(f"  {job_list_item.id} | status={job_list_item.status} | agent={agent_str}")
        count += 1
    print(f"  ({count} jobs listed)\n")

    # ------------------------------------------------------------------
    # 2. List jobs filtered by agent name (if provided).
    # ------------------------------------------------------------------
    if agent_name:
        print(f"Listing jobs for agent '{agent_name}' (limit=10):")
        count = 0
        for job_list_item in project_client.agents.list_optimization_jobs(agent_name=agent_name, limit=10):
            print(f"  {job_list_item.id} | status={job_list_item.status}")
            count += 1
        print(f"  ({count} jobs)\n")

    # ------------------------------------------------------------------
    # 3. List jobs filtered by status.
    # ------------------------------------------------------------------
    print(f"Listing succeeded jobs (limit=5):")
    count = 0
    for job_list_item in project_client.agents.list_optimization_jobs(status=JobStatus.SUCCEEDED, limit=5):
        print(f"  {job_list_item.id}")
        count += 1
    print(f"  ({count} succeeded jobs)\n")

    # ------------------------------------------------------------------
    # 4. Get a specific job by ID (if provided).
    # ------------------------------------------------------------------
    if job_id:
        print(f"Getting job {job_id}...")
        job = project_client.agents.get_optimization_job(job_id=job_id)
        print(f"  status={job.status}")
        print(f"  agent={getattr(job.target_configuration, 'name', '?')}")
        if job.result and job.result.candidate_summary:
            summary = job.result.candidate_summary
            print(f"  baseline={summary.baseline_id}, best={summary.best_id}")
            print(f"  completed candidates: {summary.completed_candidate_count}")
        if job.warnings:
            for w in job.warnings:
                print(f"  [WARNING] {w}")

        # ------------------------------------------------------------------
        # 5. Delete the job.
        # ------------------------------------------------------------------
        print(f"\nDeleting job {job_id}...")
        project_client.agents.delete_optimization_job(job_id=job_id)
        print("  Deleted.")
