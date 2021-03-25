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


class TestSubmittedJobs(DocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs(self, client):
        # prepare containers
        blob_data = b'This is some text'
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

        # submit job
        job_detail = client.create_translation_job(translation_inputs)
        self.assertIsNotNone(job_detail.id)

        # list jobs
        submitted_jobs = client.list_submitted_jobs()  # type: ItemPaged[JobStatusResult]
        for job in submitted_jobs:
            self._validate_job(job)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_with_pagination(self, client):
        # prepare containers
        blob_data = b'This is some text'
        source_container_sas_url = self.create_source_container(data=blob_data)
        target_container_sas_url = self.create_target_container()
        result_per_page = 2
        no_of_pages = len(blob_data) // result_per_page

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

        job_detail = client.create_translation_job(translation_inputs)
        self.assertIsNotNone(job_detail.id)

        # list jobs
        submitted_jobs_pages = client.list_submitted_jobs(results_per_page=result_per_page)  # type: Iterator[Iteratr[JobStatusResult]]
        
        self.assertEqual(len(submitted_jobs_pages), no_of_pages)
        # iterate by page
        for page in submitted_jobs_pages:
            self.assertEqual(len(page), result_per_page)
            for job in page:
                self._validate_job(job)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_with_skip(self, client):
        # prepare containers
        blob_data = b'This is some text'
        source_container_sas_url = self.create_source_container(data=blob_data)
        target_container_sas_url = self.create_target_container()
        docs_len = len(blob_data)
        skip = 2

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

        job_detail = client.create_translation_job(translation_inputs)
        self.assertIsNotNone(job_detail.id)

        # list jobs
        submitted_jobs = client.list_submitted_jobs(skip=skip)  # type: ItemPaged[JobStatusResult]
        self.assertEqual(len(submitted_jobs), docs_len - skip)

        for job in submitted_jobs:
            self._validate_job(job)


    def _validate_job(self, job):
        self.assertIsNotNone(job.id)
        self.assertIsNotNone(job.created_on)
        self.assertIsNotNone(job.last_updated_on)
        self.assertIsNotNone(job.status)
        self.assertIsNotNone(job.documents_total_count)
        self.assertIsNotNone(job.documents_failed_count)
        self.assertIsNotNone(job.documents_succeeded_count)
        self.assertIsNotNone(job.documents_in_progress_count)
        self.assertIsNotNone(job.documents_not_yet_started_count)
        self.assertIsNotNone(job.documents_cancelled_count)
        self.assertIsNotNone(job.total_characters_charged)