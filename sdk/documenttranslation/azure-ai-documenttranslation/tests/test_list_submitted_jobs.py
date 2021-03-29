# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from testcase import DocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.documenttranslation import DocumentTranslationClient
import pytest
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)

TOTAL_DOC_COUNT_IN_JOB = 1

class TestSubmittedJobs(DocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs(self, client):
        # prepare data
        jobs_count = 3

        # create some jobs
        job_ids = self._create_and_submit_sample_translation_jobs(client, jobs_count)

        # list jobs
        submitted_jobs = list(client.list_submitted_jobs())
        self.assertIsNotNone(submitted_jobs)

        # check statuses
        for job in submitted_jobs:
            if job.id in job_ids:
                self._validate_translation_job(job, status="Succeeded", total=TOTAL_DOC_COUNT_IN_JOB, succeeded=TOTAL_DOC_COUNT_IN_JOB)
            else:
                self._validate_translation_job(job)


    @pytest.mark.skip("top not exposed yet")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_with_pagination(self, client):
        # prepare data
        jobs_count = 6
        result_per_page = 2
        no_of_pages = jobs_count // result_per_page

        # create some jobs
        job_ids = self._create_and_submit_sample_translation_jobs(client, jobs_count)

        # list jobs
        submitted_jobs_pages = list(client.list_submitted_jobs(results_per_page=result_per_page))
        self.assertEqual(len(submitted_jobs_pages), no_of_pages)

        # iterate by page
        for page in submitted_jobs_pages:
            page_jobs = list(page)
            self.assertEqual(len(page_jobs), result_per_page)
            for job in page:
                if job.id in job_ids:
                    self._validate_translation_job(job, status="Succeeded", total=TOTAL_DOC_COUNT_IN_JOB, succeeded=TOTAL_DOC_COUNT_IN_JOB)
                else:
                    self._validate_translation_job(job)


    @pytest.mark.skip("skip not exposed yet")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_with_skip(self, client):
        # prepare data
        jobs_count = 6
        skip = 2

        # create some jobs
        job_ids = self._create_and_submit_sample_translation_jobs(client, jobs_count)

        # list jobs
        submitted_jobs = list(client.list_submitted_jobs(skip=skip))
        self.assertEqual(len(submitted_jobs), jobs_count - skip)

        for job in submitted_jobs:
            if job.id in job_ids:
                self._validate_translation_job(job, status="Succeeded", total=TOTAL_DOC_COUNT_IN_JOB, succeeded=TOTAL_DOC_COUNT_IN_JOB)
            else:
                self._validate_translation_job(job)