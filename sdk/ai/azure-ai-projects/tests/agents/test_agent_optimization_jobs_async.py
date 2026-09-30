# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.exceptions import HttpResponseError
from azure.ai.projects.models import (
    AgentOptimizationCandidate,
    AgentOptimizationCandidateExpand,
    AgentOptimizationJob,
    PageOrder,
)

_NONEXISTENT_JOB_ID = "optjob_nonexistent_sdk_test"


class TestAgentOptimizationJobsAsync(TestBase):

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\agents\test_agent_optimization_jobs_async.py::TestAgentOptimizationJobsAsync::test_agent_optimization_jobs_list_get_async -s
    @servicePreparer()
    @recorded_by_proxy_async
    async def test_agent_optimization_jobs_list_get_async(self, **kwargs):

        async with self.create_async_client(**kwargs) as project_client:

            print("[test_agent_optimization_jobs_list_get_async] List optimization jobs")
            jobs = [job async for job in project_client.agents.list_optimization_jobs(limit=5, order=PageOrder.DESC)]
            for job in jobs:
                assert isinstance(job, AgentOptimizationJob)
                assert job.id
                assert job.status
                assert job.created_at is not None

            if jobs:
                job_id = jobs[0].id
                print(f"[test_agent_optimization_jobs_list_get_async] Get optimization job `{job_id}`")
                job = await project_client.agents.get_optimization_job(job_id)
                assert isinstance(job, AgentOptimizationJob)
                assert job.id == job_id
                assert job.optimization_configuration is not None
                assert job.optimization_model_configuration is not None

                print(f"[test_agent_optimization_jobs_list_get_async] List candidates of job `{job_id}`")
                async for candidate in project_client.agents.list_optimization_candidates(
                    job_id, expand=[AgentOptimizationCandidateExpand.MUTATIONS], limit=5
                ):
                    assert isinstance(candidate, AgentOptimizationCandidate)
                    assert candidate.job_id == job_id
                    assert candidate.candidate_id
                    assert candidate.status

            print("[test_agent_optimization_jobs_list_get_async] Get a nonexistent optimization job")
            with pytest.raises(HttpResponseError) as exc_info:
                await project_client.agents.get_optimization_job(_NONEXISTENT_JOB_ID)
            assert exc_info.value.status_code in (400, 404)
