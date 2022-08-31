# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from abc import abstractmethod

from _shared.testcase import (
    CommunicationTestCase,
    BodyReplacerProcessor,
    ResponseReplacerProcessor
)
from azure_devtools.scenario_tests import LargeResponseBodyReplacer
from _recording_processors import (
    RouterHeaderSanitizer,
    RouterQuerySanitizer,
    RouterURIIdentityReplacer,
    RouterScrubber
)

from _shared.utils import get_http_logging_policy
from azure.communication.jobrouter import (
    RouterClient,
    RouterAdministrationClient,
    RouterJobStatus,
)


class RouterTestCaseBase(CommunicationTestCase):
    def __init__(self, method_name, *args, **kwargs):
        super(RouterTestCaseBase, self).__init__(method_name, *args, **kwargs)

    def setUp(self):
        super(RouterTestCaseBase, self).setUp()

        self.recording_processors.extend([
            LargeResponseBodyReplacer(),
            RouterScrubber(keys = ["etag"]),
            RouterHeaderSanitizer(headers = ["etag"]),
        ])


class RouterTestCase(RouterTestCaseBase):
    def setUp(self):
        super(RouterTestCase, self).setUp()

    @abstractmethod
    def clean_up(self):
        pass

    def tearDown(self):
        super(RouterTestCase, self).tearDown()
        self.clean_up()

    def create_client(self) -> RouterClient:
        return RouterClient.from_connection_string(
            conn_str = self.connection_str,
            http_logging_policy=get_http_logging_policy())

    def create_admin_client(self) -> RouterAdministrationClient:
        return RouterAdministrationClient.from_connection_string(
            conn_str = self.connection_str,
            http_logging_policy=get_http_logging_policy())

    def clean_up_job(
            self,
            job_id,
            **kwargs
    ):
        router_client: RouterClient = self.create_client()
        router_job = router_client.get_job(job_id = job_id)

        if router_job.job_status == RouterJobStatus.PENDING_CLASSIFICATION:
            # cancel and delete job
            router_client.cancel_job(job_id = job_id, disposition_code = "JobCancelledAsPartOfTestCleanUp")
            router_client.delete_job(job_id = job_id)
        elif router_job.job_status == RouterJobStatus.QUEUED:
            # cancel and delete job
            router_client.cancel_job(job_id = job_id, disposition_code = "JobCancelledAsPartOfTestCleanUp")
            router_client.delete_job(job_id = job_id)
        elif router_job.job_status == RouterJobStatus.ASSIGNED:
            # complete, close and delete job
            worker_assignments = router_job.assignments

            for assignment_id, job_assignment in worker_assignments.items():
                router_client.complete_job(job_id = job_id, assignment_id = assignment_id)
                router_client.close_job(job_id = job_id, assignment_id = assignment_id)

            router_client.delete_job(job_id = job_id)
        elif router_job.job_status == RouterJobStatus.COMPLETED:
            # close and delete job
            worker_assignments = router_job.assignments

            for assignment_id, job_assignment in worker_assignments.items():
                router_client.close_job(job_id = job_id, assignment_id = assignment_id)

            router_client.delete_job(job_id = job_id)
        elif router_job.job_status == RouterJobStatus.CLOSED:
            # delete job
            router_client.delete_job(job_id = job_id)
        elif router_job.job_status == RouterJobStatus.CANCELLED:
            # delete job
            router_client.delete_job(job_id = job_id)
        elif router_job.job_status == RouterJobStatus.CLASSIFICATION_FAILED:
            # delete job
            router_client.delete_job(job_id = job_id)
        elif router_job.job_status == RouterJobStatus.CREATED:
            # cancel and delete job
            router_client.cancel_job(job_id = job_id, disposition_code = "JobCancelledAsPartOfTestCleanUp")
            router_client.delete_job(job_id = job_id)
        else:
            pass

    def _poll_until_no_exception(self, fn, expected_exception, *args, **kwargs):
        """polling helper for live tests because some operations take an unpredictable amount of time to complete"""
        max_retries = kwargs.pop('max_retries', 20)
        retry_delay = kwargs.pop('retry_delay', 3)

        for i in range(max_retries):
            try:
                return fn(*args, **kwargs)
            except expected_exception:
                if i == max_retries - 1:
                    raise
                if self.is_live:
                    time.sleep(retry_delay)

    def _poll_until_exception(self, fn, expected_exception, max_retries=20, retry_delay=3):
        """polling helper for live tests because some operations take an unpredictable amount of time to complete"""

        for _ in range(max_retries):
            try:
                fn()
                if self.is_live:
                    time.sleep(retry_delay)
            except expected_exception:
                return

        self.fail("expected exception {expected_exception} was not raised")
