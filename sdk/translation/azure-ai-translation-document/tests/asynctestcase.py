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
    async def _create_and_submit_sample_translation_jobs_async(self, async_client, jobs_count):
        result_job_ids = []
        for i in range(jobs_count):
            # prepare containers and test data
            '''
                # WARNING!!
                TOTAL_DOC_COUNT_IN_JOB = 1
                if you plan to create more docs in the job,
                please update this variable TOTAL_DOC_COUNT_IN_JOB in respective test

                # note
                since we're only testing the client library
                we can use sync container calls in here
                no need for async container clients!
            '''
            blob_data = b'This is some text'  
            source_container_sas_url = self.create_source_container(data=Document(data=blob_data))
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
            job_details = await async_client.create_translation_job(translation_inputs)
            self.assertIsNotNone(job_details.id)
            await async_client.wait_until_done(job_details.id)
            result_job_ids.append(job_details.id)

        return result_job_ids