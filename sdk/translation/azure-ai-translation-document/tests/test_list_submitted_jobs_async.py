# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from datetime import datetime, date
import functools
from asynctestcase import AsyncDocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.translation.document.aio import DocumentTranslationClient
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)
import pytest

TOTAL_DOC_COUNT_IN_JOB = 1

class TestSubmittedJobs(AsyncDocumentTranslationTest):


    @pytest.mark.skip(reason="no way of currently testing this")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs(self, client):
        # prepare data
        jobs_count = 3

        # create some jobs
        job_ids = await self._create_and_submit_sample_translation_jobs_async(client, jobs_count)

        # list jobs
        submitted_jobs = client.list_submitted_jobs()
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        async for job in submitted_jobs:
            if job.id in job_ids:
                self._validate_translation_job(job, status="Succeeded", total=TOTAL_DOC_COUNT_IN_JOB, succeeded=TOTAL_DOC_COUNT_IN_JOB)
            else:
                self._validate_translation_job(job)


    @pytest.mark.skip(reason="no way of currently testing this")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_with_pagination(self, client):
        # prepare data
        jobs_count = 6
        results_per_page = 2
        no_of_pages = jobs_count // results_per_page

        # create some jobs
        job_ids = await self._create_and_submit_sample_translation_jobs_async(client, jobs_count)

        # list jobs
        submitted_jobs_pages = client.list_submitted_jobs(results_per_page=results_per_page).by_page()

        # iterate by page
        async for page in submitted_jobs_pages:
            page_jobs = []

            async for job in page:
                page_jobs.append(job)
                if job.id in job_ids:
                    self._validate_translation_job(job, status="Succeeded", total=TOTAL_DOC_COUNT_IN_JOB, succeeded=TOTAL_DOC_COUNT_IN_JOB)
                else:
                    self._validate_translation_job(job)

            self.assertEqual(len(page_jobs), results_per_page)


    @pytest.mark.skip(reason="no way of currently testing this")
    @DocumentTranslationPreparer()

    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_with_skip(self, client):
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
        job_ids = await self._create_and_submit_sample_translation_jobs_async(client, jobs_count)

        # list jobs
        submitted_jobs = client.list_submitted_jobs(skip=skip)
        jobs_list = []

        async for job in submitted_jobs:
            jobs_list.append(job)
            if job.id in job_ids:
                self._validate_translation_job(job, status="Succeeded", total=TOTAL_DOC_COUNT_IN_JOB, succeeded=TOTAL_DOC_COUNT_IN_JOB)
            else:
                self._validate_translation_job(job)


    @pytest.mark.skip(reason="no way of currently testing this")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_filter_by_status(self, client):
        # create some jobs
        self._create_and_submit_sample_translation_jobs_async(client, 10, wait=False)

        # list jobs
        statuses = ["Running"]
        submitted_jobs = client.list_submitted_jobs(statuses=statuses)

        # check statuses
        async for job in submitted_jobs:
            self.assertIn(job.status, statuses)


    @pytest.mark.skip(reason="no way of currently testing this")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_filter_by_ids(self, client):
        # create some jobs
        job_ids = self._create_and_submit_sample_translation_jobs_async(client, 3)

        # list jobs
        submitted_jobs = client.list_submitted_jobs(ids=job_ids)

        # check statuses
        async for job in submitted_jobs:
            self.assertIn(job.id, job_ids)


    @pytest.mark.skip(reason="no way of currently testing this")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_filter_by_created_after(self, client):
        # create some jobs
        start = datetime.now()
        self._create_and_submit_sample_translation_jobs_async(client, 3)

        # list jobs
        submitted_jobs = client.list_submitted_jobs(created_after=start)

        # check statuses
        async for job in submitted_jobs:
            assert(job.created_on > start)


    @pytest.mark.skip(reason="no way of currently testing this")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_filter_by_created_before(self, client):
        # create some jobs
        self._create_and_submit_sample_translation_jobs_async(client, 3)
        end = datetime.now()
        self._create_and_submit_sample_translation_jobs_async(client, 3)

        # list jobs
        submitted_jobs = client.list_submitted_jobs(created_before=end)

        # check statuses
        async for job in submitted_jobs:
            assert(job.created_on < end)


    @pytest.mark.skip(reason="no way of currently testing this")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_order_by_creation_time_asc(self, client):
        # create some jobs
        self._create_and_submit_sample_translation_jobs_async(client, 3)

        # list jobs
        submitted_jobs = client.list_submitted_jobs(order_by=["CreatedDateTimeUtc asc"])

        # check statuses
        curr = date.min
        async for job in submitted_jobs:
            assert(job.created_on > curr)
            curr = job.created_on


    @pytest.mark.skip(reason="no way of currently testing this")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_order_by_creation_time_desc(self, client):
        # create some jobs
        self._create_and_submit_sample_translation_jobs_async(client, 3)

        # list jobs
        submitted_jobs = client.list_submitted_jobs(order_by=["CreatedDateTimeUtc desc"])

        # check statuses
        curr = date.max
        async for job in submitted_jobs:
            assert(job.created_on < curr)
            curr = job.created_on


    @pytest.mark.skip(reason="no way of currently testing this")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_mixed_filters(self, client):
        # create some jobs
        start = datetime.now()
        self._create_and_submit_sample_translation_jobs_async(client, 20, wait=False)
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

        # check statuses
        curr_time = date.max
        async for page in submitted_jobs:
            page_jobs = []
            async for job in page:
                page_jobs.append(job)
                # assert ordering
                assert(job.created_on < curr_time)
                curr_time = job.created_on
                # assert filters
                assert(job.created_on < end)
                assert(job.created_on > start)
                assertIn(job.status, statuses)

            self.assertEqual(len(page_jobs), results_per_page)


    @pytest.mark.skip(reason="no way of currently testing this")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_mixed_filters_more(self, client):
        # create some jobs
        job_ids = self._create_and_submit_sample_translation_jobs_async(client, 20, wait=False)
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
        ).by_page()

        # check statuses
        curr_time = date.max
        async for page in submitted_jobs:
            page_jobs = []
            async for job in page:
                page_jobs.append(job)
                # assert ordering
                assert(job.created_on < curr_time)
                curr_time = job.created_on
                # assert filters
                self.assertIn(job.status, statuses)
                self.assertIn(job.id, job_ids)

            self.assertEqual(len(page_jobs), results_per_page)

