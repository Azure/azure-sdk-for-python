# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from testcase import DocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.documenttranslation import DocumentTranslationClient, DocumentTranslationInput, TranslationTarget
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)

TOTAL_DOC_COUNT_IN_JOB = 1

class TestSubmittedJobs(DocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs(self, client):
        # prepare data
        jobs_count = 3

        # create some jobs
        self._create_and_submit_sample_translation_jobs(self, client, jobs_count)

        # list jobs
        submitted_jobs = client.list_submitted_jobs()
        self.assertEqual(len(submitted_jobs), jobs_count)

        # check statuses
        for job in submitted_jobs:
            self._validate_translation_job(job, TOTAL_DOC_COUNT_IN_JOB)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_with_pagination(self, client):
        # prepare data
        jobs_count = 6
        result_per_page = 2
        no_of_pages = jobs_count // result_per_page

        # create some jobs
        self._create_and_submit_sample_translation_jobs(self, client, jobs_count)

        # list jobs
        submitted_jobs_pages = client.list_submitted_jobs(results_per_page=result_per_page)
        self.assertEqual(len(submitted_jobs_pages), no_of_pages)

        # iterate by page
        for page in submitted_jobs_pages:
            self.assertEqual(len(page), result_per_page)
            for job in page:
                self._validate_translation_job(job, TOTAL_DOC_COUNT_IN_JOB)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_with_skip(self, client):
        # prepare data
        jobs_count = 6
        skip = 2

        # create some jobs
        self._create_and_submit_sample_translation_jobs(self, client, jobs_count)

        # list jobs
        submitted_jobs = client.list_submitted_jobs(skip=skip)
        self.assertEqual(len(submitted_jobs), jobs_count - skip)

        for job in submitted_jobs:
            self._validate_translation_job(job, TOTAL_DOC_COUNT_IN_JOB)


    # helper functions
    def _validate_translation_job(self, job_details, total_docs_count):
        # status
        self.assertEqual(job_details.status, "Succeeded")
        # docs count
        self.assertEqual(job_details.documents_total_count, total_docs_count)
        self.assertEqual(job_details.documents_failed_count, 0)
        self.assertEqual(job_details.documents_succeeded_count, total_docs_count)
        self.assertEqual(job_details.documents_in_progress_count, 0)
        self.assertEqual(job_details.documents_not_yet_started_count, 0)
        self.assertEqual(job_details.documents_cancelled_count, 0)
        # generic assertions
        self.assertIsNotNone(job_details.id)
        self.assertIsNotNone(job_details.created_on)
        self.assertIsNotNone(job_details.last_updated_on)
        self.assertIsNotNone(job_details.total_characters_charged)


    def _create_and_submit_sample_translation_jobs(self, client, jobs_count):
        for i in range(jobs_count):
            # prepare containers and test data
            blob_data = b'This is some text'  # TOTAL_DOC_COUNT_IN_JOB = 1
            source_container_sas_url = self.create_source_container(data=blob_data)
            target_container_sas_url = self.create_target_container()

            # prepare translation inputs
            translation_inputs = [
                DocumentTranslationInput(
                    source_url=source_container_sas_url,
                    targets=[
                        TranslationTarget(
                            target_url=target_container_sas_url,
                            language_code="es"
                        )
                    ]
                )
            ]

            # submit multiple jobs
            job_detail = client.create_translation_job(translation_inputs)
            self.assertIsNotNone(job_detail.id)