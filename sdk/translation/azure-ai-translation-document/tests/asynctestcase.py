# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from testcase import DocumentTranslationTest, Document
from azure.ai.translation.document import DocumentTranslationInput, TranslationTarget

class AsyncDocumentTranslationTest(DocumentTranslationTest):

    def __init__(self, method_name):
        super(AsyncDocumentTranslationTest, self).__init__(method_name)

    async def _submit_and_validate_translation_job_async(self, async_client, translation_inputs, total_docs_count=None):
        # submit job
        job_details = await async_client.create_translation_job(translation_inputs)
        self.assertIsNotNone(job_details.id)
        # wait for result
        job_details = await async_client.wait_until_done(job_details.id)
        # validate
        self._validate_translation_job(job_details=job_details, status='Succeeded', total=total_docs_count, succeeded=total_docs_count)

        return job_details.id

    # client helpers
    async def _create_and_submit_sample_translation_jobs_async(self, async_client, jobs_count, **kwargs):
        wait_for_job = kwargs.pop('wait', True)
        language_code = kwargs.pop('language_code', "es")
        docs_per_job = kwargs.pop('docs_per_job', 2)
        result_job_ids = []
        for i in range(jobs_count):
            # prepare containers and test data
            '''
                # note
                since we're only testing the client library
                we can use sync container calls in here
                no need for async container clients!
            '''
            blob_data = Document.create_dummy_docs(docs_per_job)
            source_container_sas_url = self.create_source_container(data=blob_data)
            target_container_sas_url = self.create_target_container()

            # prepare translation inputs
            translation_inputs = [
                DocumentTranslationInput(
                    source_url=source_container_sas_url,
                    targets=[
                        TranslationTarget(
                            target_url=target_container_sas_url,
                            language_code=language_code
                        )
                    ]
                )
            ]

            # submit multiple jobs
            job_details = await async_client.create_translation_job(translation_inputs)
            self.assertIsNotNone(job_details.id)
            if wait_for_job:
                await async_client.wait_until_done(job_details.id)
            result_job_ids.append(job_details.id)

        return result_job_ids


    async def _create_translation_job_with_dummy_docs_async(self, async_client, docs_count, **kwargs):
        # get input parms
        wait_for_job = kwargs.pop('wait', False)
        language_code = kwargs.pop('language_code', "es")

        # prepare containers and test data
        blob_data = Document.create_dummy_docs(docs_count=docs_count)
        source_container_sas_url = self.create_source_container(data=blob_data)
        target_container_sas_url = self.create_target_container()

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code=language_code
                    )
                ]
            )
        ]

        # submit job
        job_details = await async_client.create_translation_job(translation_inputs)
        self.assertIsNotNone(job_details.id)
        # wait for result
        if wait_for_job:
                await async_client.wait_until_done(job_details.id)
        # validate
        self._validate_translation_job(job_details=job_details)

        return job_details.id
