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

            self.assertEqual(len(page_jobs), results_per_page)


    @pytest.mark.skip(reason="passing, pointless test!")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_with_skip(self, client):
        '''
            note:
            some notes regarding this test
            there's no possible way of asserting for 'skip', unless we can know the 
            count of the jobs returned!

            as we can't possibly know the how many previous items were created
            even if we filter only on newly created items,
            tests can run in parallel which will ruin our pre-conceptions!
            the only thing we can do, is to call the service with the parameter 

            update:
                we can test 'skip' by using some other filters to get how many docs
                will be in result and only then skip will be meaningfull
        '''
        # prepare data
        jobs_count = 5
        docs_per_job = 2
        skip = 2

        # create some jobs
        await self._create_and_submit_sample_translation_jobs_async(client, jobs_count, wait=False, docs_per_job=docs_per_job)

        # list jobs - unable to assert skip!!
        submitted_jobs = client.list_submitted_jobs(skip=skip)
        self.assertIsNotNone(submitted_jobs)

        async for job in submitted_jobs:
            self._validate_translation_job(job)


    @pytest.mark.skip(reason="filter not working!")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_filter_by_status(self, client):
        jobs_count = 10
        docs_per_job = 3

        # create some jobs
        job_ids = await self._create_and_submit_sample_translation_jobs_async(client, jobs_count, wait=False, docs_per_job=docs_per_job)

        # update status
        cancelled_count = jobs_count//2
        for id in job_ids[:cancelled_count]:
            await client.cancel_job(id)
        statuses = ["Cancelled", "Cancelling"]
        self.wait(10) # wait for cancelled to propagate

        # list jobs
        submitted_jobs = client.list_submitted_jobs(statuses=statuses)
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        async for job in submitted_jobs:
            self.assertIn(job.status, statuses)


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


    @pytest.mark.skip(reason="for some reason, jobs created after 'end' timestamp showup in result! might be different timestamps locally and service")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_filter_by_created_before(self, client):
        '''
            NOTE: maybe we need to wait for few seconds after calling 'end = datetime.now()'
            for the local and service clocks to differ by some significant amount 
        '''
        jobs_count = 3
        docs_per_job = 2

        # create some jobs
        await self._create_and_submit_sample_translation_jobs_async(client, jobs_count, wait=False, docs_per_job=docs_per_job)
        end = datetime.now()
        self.wait(5) # 
        job_ids = await self._create_and_submit_sample_translation_jobs_async(client, jobs_count, wait=False, docs_per_job=docs_per_job)

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

            self.assertEqual(len(page_jobs), results_per_page)


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

            self.assertEqual(len(page_jobs), results_per_page)

