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
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)

TOTAL_DOC_COUNT_IN_JOB = 1

class TestSubmittedJobs(DocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs(self, client):
        # create some jobs
        job_ids = self._create_and_submit_sample_translation_jobs(client, 3)

        # list jobs
        submitted_jobs = list(client.list_submitted_jobs())
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        for job in submitted_jobs:
            if job.id in job_ids:
                self._validate_translation_job(job, status="Succeeded", total=TOTAL_DOC_COUNT_IN_JOB, succeeded=TOTAL_DOC_COUNT_IN_JOB)
            else:
                self._validate_translation_job(job)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_with_pagination(self, client):
        # prepare data
        result_per_page = 2

        # create some jobs
        job_ids = self._create_and_submit_sample_translation_jobs(client, 6)

        # list jobs
        submitted_jobs_pages = list(client.list_submitted_jobs(results_per_page=result_per_page))
        self.assertIsNotNone(submitted_jobs_pages)

        # iterate by page
        for page in submitted_jobs_pages:
            page_jobs = list(page)
            self.assertEqual(len(page_jobs), result_per_page)
            for job in page:
                if job.id in job_ids:
                    self._validate_translation_job(job, status="Succeeded", total=TOTAL_DOC_COUNT_IN_JOB, succeeded=TOTAL_DOC_COUNT_IN_JOB)
                else:
                    self._validate_translation_job(job)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_with_skip(self, client):
        '''
            some notes regarding this test
            there's no possible way of asserting for 'skip'
            as we can't possibly know the how many previous items were created
            even if we filter only on newly created items,
            tests can run in parallel which will ruin our pre-conceptions!
            the only thing we can do, is to call the service with the parameter 
        '''
        # prepare data
        jobs_count = 6
        skip = 2

        # create some jobs
        job_ids = self._create_and_submit_sample_translation_jobs(client, jobs_count)

        # list jobs - unable to assert skip!!
        submitted_jobs = list(client.list_submitted_jobs(skip=skip))
        self.assertIsNotNone(submitted_jobs)

        for job in submitted_jobs:
            if job.id in job_ids:
                self._validate_translation_job(job, status="Succeeded", total=TOTAL_DOC_COUNT_IN_JOB, succeeded=TOTAL_DOC_COUNT_IN_JOB)
            else:
                self._validate_translation_job(job)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_filter_by_status(self, client):
        # create some jobs
        self._create_and_submit_sample_translation_jobs(client, 10, wait=False)

        # list jobs
        statuses = ["Running"]
        submitted_jobs = list(client.list_submitted_jobs(statuses=statuses))
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        for job in submitted_jobs:
            self.assertIn(job.status, statuses)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_filter_by_ids(self, client):
        # create some jobs
        job_ids = self._create_and_submit_sample_translation_jobs(client, 3)

        # list jobs
        submitted_jobs = list(client.list_submitted_jobs(ids=job_ids))
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        for job in submitted_jobs:
            self.assertIn(job.id, job_ids)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_filter_by_created_start(self, client):
        # create some jobs
        start = datetime.now()
        self._create_and_submit_sample_translation_jobs(client, 3)

        # list jobs
        submitted_jobs = list(client.list_submitted_jobs(created_date_time_utc_start=start))
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        for job in submitted_jobs:
            self.assert(job.created_on > start)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_filter_by_created_end(self, client):
        # create some jobs
        end = datetime.now()
        self._create_and_submit_sample_translation_jobs(client, 3)

        # list jobs
        submitted_jobs = list(client.list_submitted_jobs(created_date_time_utc_end=end))
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        for job in submitted_jobs:
            self.assert(job.created_on < end)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_order_by_creation_time_asc(self, client):
        # create some jobs
        self._create_and_submit_sample_translation_jobs(client, 3)

        # list jobs
        submitted_jobs = list(client.list_submitted_jobs(order_by=["CreatedDateTimeUtc", "asc"]))
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        curr = date.min
        for job in submitted_jobs:
            self.assert(job.created_on > curr)
            curr = job.created_on


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_order_by_creation_time_desc(self, client):
        # create some jobs
        self._create_and_submit_sample_translation_jobs(client, 3)

        # list jobs
        submitted_jobs = list(client.list_submitted_jobs(order_by=["CreatedDateTimeUtc", "desc"]))
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        curr = date.max
        for job in submitted_jobs:
            self.assert(job.created_on < curr)
            curr = job.created_on


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_mixed_filters(self, client):
        # create some jobs
        start = datetime.now()
        self._create_and_submit_sample_translation_jobs(client, 20, wait=False)
        end = datetime.now()
        results_per_page = 2
        statuses = ["Running"]

        # list jobs
        submitted_jobs = client.list_submitted_jobs(
            # filters
            statuses=statuses,
            created_date_time_utc_start=start,
            created_date_time_utc_end=end,
            # ordering
            order_by=["CreatedDateTimeUtc", "desc"],
            # paging
            skip=1,
            results_per_page=results_per_page
        )
        submitted_jobs = list(submitted_jobs)
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        curr_time = date.max
        for page in submitted_jobs:
            page_jobs = list(page)
            self.assertEqual(len(page_jobs), results_per_page) # assert paging
            for job in page:
                # assert ordering
                self.assert(job.created_on < curr_time)
                curr_time = job.created_on
                # assert filters
                self.assert(job.created_on < end)
                self.assert(job.created_on > start)
                self.assertIn(job.status, statuses)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_mixed_filters_more(self, client):
        # create some jobs
        job_ids = self._create_and_submit_sample_translation_jobs(client, 20, wait=False)
        results_per_page = 2
        statuses = ["Running"]

        # list jobs
        submitted_jobs = client.list_submitted_jobs(
            # filters
            ids=job_ids,
            statuses=statuses,
            # ordering
            order_by=["CreatedDateTimeUtc", "asc"],
            # paging
            skip=1,
            results_per_page=results_per_page
        )
        submitted_jobs = list(submitted_jobs)
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        curr_time = date.max
        for page in submitted_jobs:
            page_jobs = list(page)
            self.assertEqual(len(page_jobs), results_per_page) # assert paging
            for job in page:
                # assert ordering
                self.assert(job.created_on < curr_time)
                curr_time = job.created_on
                # assert filters
                self.assertIn(job.status, statuses)
                self.assertIn(job.id, job_ids)


