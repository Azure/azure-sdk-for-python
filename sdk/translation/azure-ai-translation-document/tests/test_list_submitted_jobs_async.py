# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from asynctestcase import AsyncDocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.translation.document.aio import DocumentTranslationClient
import pytest
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)

TOTAL_DOC_COUNT_IN_JOB = 1

class TestSubmittedJobs(AsyncDocumentTranslationTest):

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
        jobs_list = []
        async for job in submitted_jobs:
            jobs_list.append(job)
            if job.id in job_ids:
                self._validate_translation_job(job, status="Succeeded", total=TOTAL_DOC_COUNT_IN_JOB, succeeded=TOTAL_DOC_COUNT_IN_JOB)
            else:
                self._validate_translation_job(job)


    @pytest.mark.skip("top not exposed yet")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_with_pagination(self, client):
        # prepare data
        jobs_count = 6
        result_per_page = 2
        no_of_pages = jobs_count // result_per_page

        # create some jobs
        job_ids = await self._create_and_submit_sample_translation_jobs_async(client, jobs_count)

        # list jobs
        submitted_jobs_pages = client.list_submitted_jobs(results_per_page=result_per_page)
        pages_list = []

        # iterate by page
        async for page in submitted_jobs_pages:
            pages_list.append()
            page_jobs = []

            async for job in page:
                page_jobs.append(job)
                if job.id in job_ids:
                    self._validate_translation_job(job, status="Succeeded", total=TOTAL_DOC_COUNT_IN_JOB, succeeded=TOTAL_DOC_COUNT_IN_JOB)
                else:
                    self._validate_translation_job(job)

            self.assertEqual(len(page_jobs), result_per_page)


    @pytest.mark.skip("skip not exposed yet")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_with_skip(self, client):
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

            