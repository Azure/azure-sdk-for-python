# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from testcase import Document
from testcase import DocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.translation.document import DocumentTranslationClient, DocumentTranslationInput, TranslationTarget
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestCancelJob(DocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_cancel_job(self, client):
        '''
            some notes (test sporadically failing):
            1. use a large number of jobs
                - because when running tests the job sometimes finishes with status 'Succeeded'
                  before we call the 'cancel' endpoint!
            2. wait sometime after calling 'cancel' and before calling 'get status'
                - in order for the cancel status to propagate
        '''
        # submit translation job
        docs_count = 8 # large number of docs 
        job_id = self._create_translation_job_with_dummy_docs(client, docs_count, wait=False)

        # cancel job
        client.cancel_job(job_id)

        # wait for propagation
        wait_time = 15  # for 'cancelled' status to propagate, if test failed, increase this value!
        self.wait(duration=wait_time) 

        # check job status
        job_details = client.get_job_status(job_id)
        self._validate_translation_job(job_details, status="Cancelled", total=docs_count)