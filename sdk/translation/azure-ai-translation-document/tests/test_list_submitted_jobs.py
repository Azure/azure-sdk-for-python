# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import pytz
from datetime import datetime
import functools
from testcase import DocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.translation.document import DocumentTranslationClient

DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestSubmittedJobs(DocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs(self, client):
        # create some jobs
        jobs_count = 5
        docs_per_job = 5
        self._begin_multiple_translations(client, jobs_count, docs_per_job=docs_per_job, wait=False)

        # list jobs
        submitted_jobs = list(client.list_submitted_jobs())
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        for job in submitted_jobs:
            self._validate_translations(job)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_with_pagination(self, client):
        # prepare data
        jobs_count = 5
        docs_per_job = 2
        results_per_page = 2

        # create some jobs
        self._begin_multiple_translations(client, jobs_count, docs_per_job=docs_per_job, wait=False)

        # list jobs
        submitted_jobs_pages = client.list_submitted_jobs(results_per_page=results_per_page).by_page()
        self.assertIsNotNone(submitted_jobs_pages)

        # iterate by page
        for page in submitted_jobs_pages:
            page_jobs = list(page)
            self.assertLessEqual(len(page_jobs), results_per_page)
            for job in page_jobs:
                self._validate_translations(job)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_with_skip(self, client):
        # prepare data
        jobs_count = 10
        docs_per_job = 2
        skip = 5

        # create some jobs
        self._begin_multiple_translations(client, jobs_count, wait=False, docs_per_job=docs_per_job)

        # assert
        all_jobs = list(client.list_submitted_jobs())
        jobs_with_skip = list(client.list_submitted_jobs(skip=skip))
        assert len(all_jobs) - len(jobs_with_skip) == skip


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_filter_by_status(self, client):
        jobs_count = 5
        docs_per_job = 1

        # create some jobs with the status 'Succeeded'
        completed_job_ids = self._begin_multiple_translations(client, jobs_count, wait=True, docs_per_job=docs_per_job)

        # create some jobs with the status 'Cancelled'
        job_ids = self._begin_multiple_translations(client, jobs_count, wait=False, docs_per_job=docs_per_job)
        for id in job_ids:
            client.cancel_job(id)
        self.wait(10) # wait for cancelled to propagate

        # list jobs with status filter
        statuses = ["Cancelled"]
        submitted_jobs = list(client.list_submitted_jobs(statuses=statuses))

        # check statuses
        for job in submitted_jobs:
            self.assertIn(job.status, statuses)
            self.assertNotIn(job.id, completed_job_ids)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_filter_by_ids(self, client):
        jobs_count = 3
        docs_per_job = 2

        # create some jobs
        job_ids = self._begin_multiple_translations(client, jobs_count, wait=False, docs_per_job=docs_per_job)

        # list jobs
        submitted_jobs = list(client.list_submitted_jobs(job_ids=job_ids))
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        for job in submitted_jobs:
            self.assertIn(job.id, job_ids)


    @pytest.mark.live_test_only
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_filter_by_created_after(self, client):
        # create some jobs
        jobs_count = 3
        docs_per_job = 2

        # create some jobs
        start = datetime.utcnow()
        job_ids = self._begin_multiple_translations(client, jobs_count, wait=False, docs_per_job=docs_per_job)

        # list jobs
        submitted_jobs = list(client.list_submitted_jobs(created_after=start))
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        for job in submitted_jobs:
            self.assertIn(job.id, job_ids)
            assert(job.created_on.replace(tzinfo=None) >= start.replace(tzinfo=None))


    @pytest.mark.live_test_only
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_filter_by_created_before(self, client):
        '''
            NOTE: test is dependent on 'end' to be specific/same as time zone of the service! 
                'end' must be timezone-aware!
        '''
        jobs_count = 5
        docs_per_job = 1

        # create some jobs
        self._begin_multiple_translations(client, jobs_count, wait=True, docs_per_job=docs_per_job)
        end = datetime.utcnow().replace(tzinfo=pytz.utc)
        job_ids = self._begin_multiple_translations(client, jobs_count, wait=True, docs_per_job=docs_per_job)

        # list jobs
        submitted_jobs = list(client.list_submitted_jobs(created_before=end))
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        for job in submitted_jobs:
            self.assertLessEqual(job.created_on.replace(tzinfo=None), end.replace(tzinfo=None))
            self.assertNotIn(job.id, job_ids)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_order_by_creation_time_asc(self, client):
        jobs_count = 3
        docs_per_job = 2

        # create some jobs
        self._begin_multiple_translations(client, jobs_count, wait=False, docs_per_job=docs_per_job)

        # list jobs
        submitted_jobs = list(client.list_submitted_jobs(order_by=["createdDateTimeUtc asc"]))
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        curr = datetime.min
        for job in submitted_jobs:
            assert(job.created_on.replace(tzinfo=None) >= curr.replace(tzinfo=None))
            curr = job.created_on


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_order_by_creation_time_desc(self, client):
        jobs_count = 3
        docs_per_job = 2

        # create some jobs
        self._begin_multiple_translations(client, jobs_count, wait=False, docs_per_job=docs_per_job)

        # list jobs
        submitted_jobs = list(client.list_submitted_jobs(order_by=["createdDateTimeUtc desc"]))
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        curr = datetime.max
        for job in submitted_jobs:
            assert(job.created_on.replace(tzinfo=None) <= curr.replace(tzinfo=None))
            curr = job.created_on


    @pytest.mark.skip(reason="not working! - list returned is empty")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_mixed_filters(self, client):
        # create some jobs
        jobs_count = 10
        docs_per_job = 1
        results_per_page = 2
        statuses = ["Cancelled"]
        skip = 2

        # create some jobs
        start = datetime.utcnow().replace(tzinfo=pytz.utc)
        successful_job_ids = self._begin_multiple_translations(client, jobs_count, wait=True, docs_per_job=docs_per_job)
        cancelled_job_ids = self._begin_multiple_translations(client, jobs_count, wait=False, docs_per_job=docs_per_job)
        for job_id in cancelled_job_ids:
            client.cancel_job(job_id)
        self.wait(10) # wait for status to propagate
        end = datetime.utcnow().replace(tzinfo=pytz.utc)

        # list jobs
        submitted_jobs = client.list_submitted_jobs(
            # filters
            statuses=statuses,
            created_after=start,
            created_before=end,
            # ordering
            order_by=["createdDateTimeUtc asc"],
            # paging
            skip=skip,
            results_per_page=results_per_page
        ).by_page()

        # check statuses
        curr_time = datetime.min
        for page in submitted_jobs:
            page_jobs = list(page)
            self.assertLessEqual(len(page_jobs), results_per_page) # assert paging
            for job in page_jobs:
                assert id
                self.assertIn(job.id, cancelled_job_ids)
                self.assertNotIn(job.id, successful_job_ids)
                # assert ordering
                assert(job.created_on.replace(tzinfo=None) >= curr_time.replace(tzinfo=None))
                curr_time = job.created_on
                # assert filters
                assert(job.created_on.replace(tzinfo=None) <= end.replace(tzinfo=None))
                assert(job.created_on.replace(tzinfo=None) >= start.replace(tzinfo=None))
                self.assertIn(job.status, statuses)