# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from datetime import datetime, date
import functools
from testcase import DocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.translation.document import DocumentTranslationClient
import pytest

DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)

class TestSubmittedJobs(DocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs(self, client):
        # create some jobs
        jobs_count = 5
        docs_per_job = 5
        self._create_and_submit_sample_translation_jobs(client, jobs_count, docs_per_job=docs_per_job, wait=False)

        # list jobs
        submitted_jobs = list(client.list_submitted_jobs())
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        for job in submitted_jobs:
            self._validate_translation_job(job)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_with_pagination(self, client):
        # prepare data
        jobs_count = 5
        docs_per_job = 2
        results_per_page = 2

        # create some jobs
        self._create_and_submit_sample_translation_jobs(client, jobs_count, docs_per_job=docs_per_job, wait=False)

        # list jobs
        submitted_jobs_pages = client.list_submitted_jobs(results_per_page=results_per_page).by_page()
        self.assertIsNotNone(submitted_jobs_pages)

        # iterate by page
        for page in submitted_jobs_pages:
            page_jobs = list(page)
            self.assertLessEqual(len(page_jobs), results_per_page)
            for job in page:
                self._validate_translation_job(job)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_with_skip(self, client):
        # prepare data
        jobs_count = 10
        docs_per_job = 2
        skip = 5

        # create some jobs
        self._create_and_submit_sample_translation_jobs(client, jobs_count, wait=False, docs_per_job=docs_per_job)

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
        completed_job_ids = self._create_and_submit_sample_translation_jobs(client, jobs_count, wait=True, docs_per_job=docs_per_job)

        # create some jobs with the status 'Cancelled'
        job_ids = self._create_and_submit_sample_translation_jobs(client, jobs_count, wait=False, docs_per_job=docs_per_job)
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
        job_ids = self._create_and_submit_sample_translation_jobs(client, jobs_count, wait=False, docs_per_job=docs_per_job)

        # list jobs
        submitted_jobs = list(client.list_submitted_jobs(job_ids=job_ids))
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        for job in submitted_jobs:
            self.assertIn(job.id, job_ids)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_filter_by_created_after(self, client):
        # create some jobs
        jobs_count = 3
        docs_per_job = 2

        # create some jobs
        start = datetime.now()
        job_ids = self._create_and_submit_sample_translation_jobs(client, jobs_count, wait=False, docs_per_job=docs_per_job)

        # list jobs
        submitted_jobs = list(client.list_submitted_jobs(created_after=start))
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        for job in submitted_jobs:
            self.assertIn(job.id, job_ids)
            assert(job.created_on.replace(tzinfo=None) >= start.replace(tzinfo=None))


    @pytest.mark.skip(reason="for some reason, jobs created after 'end' timestamp showup in result! might be different timestamps locally and service")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_filter_by_created_before(self, client):
        '''
            NOTE: maybe we need to wait for few seconds after calling 'end = datetime.now()'
            for the local and service clocks to differ by some significant amount 
        '''
        jobs_count = 3
        docs_per_job = 2

        # create some jobs
        self._create_and_submit_sample_translation_jobs(client, jobs_count, wait=False, docs_per_job=docs_per_job)
        end = datetime.now()
        self.wait(5) # 
        job_ids = self._create_and_submit_sample_translation_jobs(client, jobs_count, wait=False, docs_per_job=docs_per_job)

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
        self._create_and_submit_sample_translation_jobs(client, jobs_count, wait=False, docs_per_job=docs_per_job)

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
        self._create_and_submit_sample_translation_jobs(client, jobs_count, wait=False, docs_per_job=docs_per_job)

        # list jobs
        submitted_jobs = list(client.list_submitted_jobs(order_by=["createdDateTimeUtc desc"]))
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        curr = datetime.max
        for job in submitted_jobs:
            assert(job.created_on.replace(tzinfo=None) <= curr.replace(tzinfo=None))
            curr = job.created_on


    @pytest.mark.skip(reason="pending for filters which aren't working - mainly 'statuses' filter")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_mixed_filters(self, client):
        # create some jobs
        jobs_count = 5
        docs_per_job = 2
        results_per_page = 2
        statuses = ["Running"]

        # create some jobs
        start = datetime.now()
        self._create_and_submit_sample_translation_jobs(client, jobs_count, wait=False, docs_per_job=docs_per_job)
        end = datetime.now()

        # list jobs
        submitted_jobs = client.list_submitted_jobs(
            # filters
            statuses=statuses,
            created_after=start,
            created_before=end,
            # ordering
            order_by=["createdDateTimeUtc desc"],
            # paging
            skip=1,
            results_per_page=results_per_page
        ).by_page()
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        curr_time = datetime.max
        for page in submitted_jobs:
            page_jobs = list(page)
            self.assertLessEqual(len(page_jobs), results_per_page) # assert paging
            for job in page:
                # assert ordering
                assert(job.created_on <= curr_time)
                curr_time = job.created_on
                # assert filters
                assert(job.created_on <= end)
                assert(job.created_on >= start)
                self.assertIn(job.status, statuses)


    @pytest.mark.skip(reason="pending for filters which aren't working - mainly 'statuses' filter")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_mixed_filters_more(self, client):
        jobs_count = 5
        docs_per_job = 2
        results_per_page = 2
        statuses = ["Running"]

        # create some jobs
        job_ids = self._create_and_submit_sample_translation_jobs(client, jobs_count, wait=False, docs_per_job=docs_per_job)

        # list jobs
        submitted_jobs = client.list_submitted_jobs(
            # filters
            job_ids=job_ids,
            statuses=statuses,
            # ordering
            order_by=["createdDateTimeUtc asc"],
            # paging
            skip=1,
            results_per_page=results_per_page
        ).by_page()
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        curr_time = date.max
        for page in submitted_jobs:
            page_jobs = list(page)
            self.assertLessEqual(len(page_jobs), results_per_page) # assert paging
            for job in page:
                # assert ordering
                assert(job.created_on <= curr_time)
                curr_time = job.created_on
                # assert filters
                self.assertIn(job.status, statuses)
                self.assertIn(job.id, job_ids)


