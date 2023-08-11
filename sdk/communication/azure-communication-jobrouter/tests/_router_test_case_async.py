# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
from abc import abstractmethod
from retry import retry
import warnings
from _shared.utils import get_http_logging_policy
from azure.communication.jobrouter.aio import (
    JobRouterClient,
    JobRouterAdministrationClient,
)
from azure.communication.jobrouter import (
    RouterJobStatus,
)
from devtools_testutils import AzureRecordedTestCase


class AsyncRouterRecordedTestCase(AzureRecordedTestCase):
    @abstractmethod
    async def clean_up(self):
        pass

    def create_client(self) -> JobRouterClient:
        return JobRouterClient.from_connection_string(
            conn_str = self.connection_string,
            http_logging_policy=get_http_logging_policy())

    def create_admin_client(self) -> JobRouterAdministrationClient:
        return JobRouterAdministrationClient.from_connection_string(
            conn_str = self.connection_string,
            http_logging_policy=get_http_logging_policy())

    @retry(Exception, delay=3, tries=3)
    async def clean_up_job(
            self,
            job_id,
            **kwargs
    ):
        router_client: JobRouterClient = self.create_client()
        suppress_errors = kwargs.pop('suppress_errors', False)

        try:
            async with router_client:
                router_job = await router_client.get_job(job_id = job_id)

                if router_job.status == RouterJobStatus.PENDING_CLASSIFICATION:
                    # cancel and delete job
                    await router_client.cancel_job(job_id = job_id, disposition_code = "JobCancelledAsPartOfTestCleanUp")
                    await router_client.delete_job(job_id = job_id)
                elif router_job.status == RouterJobStatus.QUEUED:
                    # cancel and delete job
                    await router_client.cancel_job(job_id = job_id, disposition_code = "JobCancelledAsPartOfTestCleanUp")
                    await router_client.delete_job(job_id = job_id)
                elif router_job.status == RouterJobStatus.ASSIGNED:
                    # complete, close and delete job
                    worker_assignments = router_job.assignments

                    for assignment_id, job_assignment in worker_assignments.items():
                        await router_client.complete_job(job_id = job_id, assignment_id = assignment_id)
                        await router_client.close_job(job_id = job_id, assignment_id = assignment_id)

                    await router_client.delete_job(job_id = job_id)
                elif router_job.status == RouterJobStatus.COMPLETED:
                    # close and delete job
                    worker_assignments = router_job.assignments

                    for assignment_id, job_assignment in worker_assignments.items():
                        await router_client.close_job(job_id = job_id, assignment_id = assignment_id)

                    await router_client.delete_job(job_id = job_id)
                elif router_job.status == RouterJobStatus.CLOSED:
                    # delete job
                    await router_client.delete_job(job_id = job_id)
                elif router_job.status == RouterJobStatus.CANCELLED:
                    # delete job
                    await router_client.delete_job(job_id = job_id)
                elif router_job.status == RouterJobStatus.CLASSIFICATION_FAILED:
                    # delete job
                    await router_client.delete_job(job_id = job_id)
                elif router_job.status == RouterJobStatus.CREATED:
                    # cancel and delete job
                    await router_client.cancel_job(job_id = job_id, disposition_code = "JobCancelledAsPartOfTestCleanUp")
                    await router_client.delete_job(job_id = job_id)
                elif router_job.status == RouterJobStatus.WAITING_FOR_ACTIVATION:
                    # cancel and delete job
                    await router_client.cancel_job(job_id = job_id,
                                                   disposition_code = "JobCancelledAsPartOfTestCleanUp")
                    await router_client.delete_job(job_id = job_id)
                else:
                    pass
        except Exception as e:
            msg = f"Deletion of job failed: {job_id}"
            warnings.warn(UserWarning(msg))
            print(e)
            if not suppress_errors:
                raise e

    async def _poll_until_no_exception(self, fn, expected_exception, *args, **kwargs):
        """polling helper for live tests because some operations take an unpredictable amount of time to complete"""
        max_retries = kwargs.pop('max_retries', 20)
        retry_delay = kwargs.pop('retry_delay', 3)

        for i in range(max_retries):
            try:
                return await fn(*args, **kwargs)
            except expected_exception:
                if i == max_retries - 1:
                    raise
                if self.is_live:
                    await asyncio.sleep(retry_delay)

    async def _poll_until_exception(self, fn, expected_exception, max_retries=20, retry_delay=3):
        """polling helper for live tests because some operations take an unpredictable amount of time to complete"""

        for _ in range(max_retries):
            try:
                await fn()
                if self.is_live:
                    await asyncio.sleep(retry_delay)
            except expected_exception:
                return

        raise AssertionError(f"expected exception {expected_exception} was not raised")
