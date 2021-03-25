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


class TestListSubmittedJobs(DocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_status(self, client):
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