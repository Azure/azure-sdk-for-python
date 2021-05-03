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
import pytz

TOTAL_DOC_COUNT_IN_JOB = 1

class TestSubmittedJobs(AsyncDocumentTranslationTest):


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs(self, client):
        # create some jobs
        jobs_count = 5
        docs_per_job = 5
        await self._create_and_submit_sample_translation_jobs_async(client, jobs_count, docs_per_job=docs_per_job, wait=False)

        # list jobs
        submitted_jobs = client.list_submitted_jobs()
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        async for job in submitted_jobs:
            self._validate_translation_job(job)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_with_pagination(self, client):
        # prepare data
        jobs_count = 5
        docs_per_job = 2
        results_per_page = 2

        # create some jobs
        await self._create_and_submit_sample_translation_jobs_async(client, jobs_count, docs_per_job=docs_per_job, wait=False)

        # list jobs
        submitted_jobs_pages = client.list_submitted_jobs(results_per_page=results_per_page).by_page()
        self.assertIsNotNone(submitted_jobs_pages)

        # iterate by page
        async for page in submitted_jobs_pages:
            page_jobs = []
            async for job in page:
                page_jobs.append(job)
                self._validate_translation_job(job)

            self.assertLessEqual(len(page_jobs), results_per_page)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_with_skip(self, client):
        # prepare data
        jobs_count = 10
        docs_per_job = 2
        skip = 5

        # create some jobs
        await self._create_and_submit_sample_translation_jobs_async(client, jobs_count, wait=False, docs_per_job=docs_per_job)

        # list jobs - unable to assert skip!!
        all_jobs = client.list_submitted_jobs()
        all_jobs_count = 0
        async for job in all_jobs:
            all_jobs_count += 1

        jobs_with_skip = client.list_submitted_jobs(skip=skip)
        jobs_with_skip_count = 0
        async for job in jobs_with_skip:
            jobs_with_skip_count += 1

        assert all_jobs_count - jobs_with_skip_count == skip


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_filter_by_status(self, client):
        jobs_count = 5
        docs_per_job = 1

        # create some jobs with the status 'Succeeded'
        completed_job_ids = await self._create_and_submit_sample_translation_jobs_async(client, jobs_count, wait=True, docs_per_job=docs_per_job)

        # create some jobs with the status 'Cancelled'
        job_ids = await self._create_and_submit_sample_translation_jobs_async(client, jobs_count, wait=False, docs_per_job=docs_per_job)
        for id in job_ids:
            client.cancel_job(id)
        self.wait(10) # wait for 'cancelled' to propagate

        # list jobs with status filter
        statuses = ["Cancelled"]
        submitted_jobs = client.list_submitted_jobs(statuses=statuses)

        # check statuses
        async for job in submitted_jobs:
            self.assertIn(job.status, statuses)
            self.assertNotIn(job.id, completed_job_ids)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_filter_by_ids(self, client):
        jobs_count = 3
        docs_per_job = 2

        # create some jobs
        job_ids = await self._create_and_submit_sample_translation_jobs_async(client, jobs_count, wait=False, docs_per_job=docs_per_job)

        # list jobs
        submitted_jobs = client.list_submitted_jobs(job_ids=job_ids)
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        async for job in submitted_jobs:
            self.assertIn(job.id, job_ids)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_filter_by_created_after(self, client):
        # create some jobs
        jobs_count = 3
        docs_per_job = 2

        # create some jobs
        start = datetime.now()
        job_ids = await self._create_and_submit_sample_translation_jobs_async(client, jobs_count, wait=False, docs_per_job=docs_per_job)

        # list jobs
        submitted_jobs = client.list_submitted_jobs(created_after=start)
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        async for job in submitted_jobs:
            self.assertIn(job.id, job_ids)
            assert(job.created_on.replace(tzinfo=None) >= start.replace(tzinfo=None))


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_filter_by_created_before(self, client):
        '''
            NOTE: test is dependent on 'end' to be specific/same as time zone of the service! 
                'end' must be timezone-aware!
        '''
        jobs_count = 5
        docs_per_job = 1

        # create some jobs
        await self._create_and_submit_sample_translation_jobs_async(client, jobs_count, wait=True, docs_per_job=docs_per_job)
        end = datetime.utcnow().replace(tzinfo=pytz.utc)
        job_ids = await self._create_and_submit_sample_translation_jobs_async(client, jobs_count, wait=True, docs_per_job=docs_per_job)

        # list jobs
        submitted_jobs = client.list_submitted_jobs(created_before=end)
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        async for job in submitted_jobs:
            self.assertLessEqual(job.created_on.replace(tzinfo=None), end.replace(tzinfo=None))
            self.assertNotIn(job.id, job_ids)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_order_by_creation_time_asc(self, client):
        jobs_count = 3
        docs_per_job = 2

        # create some jobs
        await self._create_and_submit_sample_translation_jobs_async(client, jobs_count, wait=False, docs_per_job=docs_per_job)

        # list jobs
        submitted_jobs = client.list_submitted_jobs(order_by=["createdDateTimeUtc asc"])
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        curr = datetime.min
        async for job in submitted_jobs:
            assert(job.created_on.replace(tzinfo=None) >= curr.replace(tzinfo=None))
            curr = job.created_on


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_order_by_creation_time_desc(self, client):
        jobs_count = 3
        docs_per_job = 2

        # create some jobs
        await self._create_and_submit_sample_translation_jobs_async(client, jobs_count, wait=False, docs_per_job=docs_per_job)

        # list jobs
        submitted_jobs = client.list_submitted_jobs(order_by=["createdDateTimeUtc desc"])
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        curr = datetime.max
        async for job in submitted_jobs:
            assert(job.created_on.replace(tzinfo=None) <= curr.replace(tzinfo=None))
            curr = job.created_on


    @pytest.mark.skip(reason="pending for filters which aren't working - mainly 'statuses' filter")
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
                self.assertIn(job.status, statuses)

            self.assertLessEqual(len(page_jobs), results_per_page)


    @pytest.mark.skip(reason="pending for filters which aren't working - mainly 'statuses' filter")
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
            job_ids=job_ids,
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

            self.assertLessEqual(len(page_jobs), results_per_page)

