# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from testcase import Document
from asynctestcase import AsyncDocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.translation.document import DocumentTranslationInput, TranslationTarget
from azure.ai.translation.document.aio import DocumentTranslationClient
from azure.core.exceptions import HttpResponseError
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestCancelTranslation(AsyncDocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_cancel_translation(self, client):
        '''
            some notes (test sporadically failing):
            1. use a large number of translations
                - because when running tests the translation sometimes finishes with status 'Succeeded'
                  before we call the 'cancel' endpoint!
            2. wait sometime after calling 'cancel' and before calling 'get status'
                - in order for the cancel status to propagate
        '''
        # submit translation operation
        docs_count = 8 # large number of docs 
        poller = await self._begin_and_validate_translation_with_multiple_docs_async(client, docs_count, wait=False)

        # cancel translation
        await client.cancel_translation(poller.id)

        # wait for propagation
        wait_time = 15  # for 'cancelled' status to propagate, if test failed, increase this value!
        self.wait(duration=wait_time) 

        # check translation status
        translation_details = await client.get_translation_status(poller.id)
        self._validate_translations(translation_details, status="Cancelled", total=docs_count)
        try:
            await poller.wait()
        except HttpResponseError:
            pass  # expected if the operation was already in a terminal state.
