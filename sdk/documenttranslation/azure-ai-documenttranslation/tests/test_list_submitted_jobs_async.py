# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from testcase import DocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.documenttranslation.aio import DocumentTranslationClient
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)

TOTAL_DOC_COUNT_IN_JOB = 1

class TestSubmittedJobs(DocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs(self, client):
        # prepare data
        jobs_count = 3

        # create some jobs
        await self._create_and_submit_sample_translation_jobs_async(self, client, jobs_count)

        # list jobs
        submitted_jobs = client.list_submitted_jobs()
        self.assertEqual(len(submitted_jobs), jobs_count)

        # check statuses
        async for job in submitted_jobs:
            self._validate_translation_job(job, TOTAL_DOC_COUNT_IN_JOB, "Succeeded")


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_with_pagination(self, client):
        # prepare data
        jobs_count = 6
        result_per_page = 2
        no_of_pages = jobs_count // result_per_page

        # create some jobs
        await self._create_and_submit_sample_translation_jobs_async(self, client, jobs_count)

        # list jobs
        submitted_jobs_pages = client.list_submitted_jobs(results_per_page=result_per_page)
        self.assertEqual(len(submitted_jobs_pages), no_of_pages)

        # iterate by page
        async for page in submitted_jobs_pages:
            self.assertEqual(len(page), result_per_page)
            async for job in page:
                self._validate_translation_job(job, TOTAL_DOC_COUNT_IN_JOB, "Succeeded")


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_with_skip(self, client):
        # prepare data
        jobs_count = 6
        skip = 2

        # create some jobs
        await self._create_and_submit_sample_translation_jobs_async(self, client, jobs_count)

        # list jobs
        submitted_jobs = client.list_submitted_jobs(skip=skip)
        self.assertEqual(len(submitted_jobs), jobs_count - skip)

        async for job in submitted_jobs:
            self._validate_translation_job(job, TOTAL_DOC_COUNT_IN_JOB, "Succeeded")