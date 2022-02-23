# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from testcase import Document
from testcase import DocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.core.exceptions import HttpResponseError
from azure.ai.translation.document import DocumentTranslationClient, DocumentTranslationInput, TranslationTarget
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestCancelTranslation(DocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_cancel_translation(self, client):
        '''
            some notes (test sporadically failing):
            1. use a large number of translations
                - because when running tests the translations sometimes finishes with status 'Succeeded'
                  before we call the 'cancel' endpoint!
            2. wait sometime after calling 'cancel' and before calling 'get status'
                - in order for the cancel status to propagate
        '''
        try:
            # submit translation operation
            docs_count = 8 # large number of docs
            poller = self._begin_and_validate_translation_with_multiple_docs(client, docs_count, wait=False)

            # cancel translation
            client.cancel_translation(poller.id)

            # check translation status
            translation_details = client.get_translation_status(poller.id)
            assert translation_details.status in ["Canceled", "Canceling"]
            self._validate_translations(translation_details)

            poller.wait()
        except HttpResponseError:
            pass  # expected if the operation was already in a terminal state.
