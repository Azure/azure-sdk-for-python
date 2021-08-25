# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import pytz
from datetime import datetime
import functools
from testcase import DocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.translation.document import DocumentTranslationClient

DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestListTranslations(DocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_translations(self, client):
        # create some translations
        operations_count = 5
        docs_per_operation = 5
        self._begin_multiple_translations(client, operations_count, docs_per_operation=docs_per_operation, wait=False)

        # list translations
        submitted_translations = list(client.list_all_translation_statuses())
        self.assertIsNotNone(submitted_translations)

        # check statuses
        for translation in submitted_translations:
            self._validate_translations(translation)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_translations_with_pagination(self, client):
        # prepare data
        operations_count = 5
        docs_per_operation = 2
        results_per_page = 2

        # create some translations
        self._begin_multiple_translations(client, operations_count, docs_per_operation=docs_per_operation, wait=False)

        # list translations
        submitted_translations_pages = client.list_all_translation_statuses(results_per_page=results_per_page).by_page()
        self.assertIsNotNone(submitted_translations_pages)

        # iterate by page
        for page in submitted_translations_pages:
            page_translations = list(page)
            self.assertLessEqual(len(page_translations), results_per_page)
            for translation in page_translations:
                self._validate_translations(translation)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_translations_with_skip(self, client):
        # prepare data
        operations_count = 10
        docs_per_operation = 2
        skip = 5

        # create some translations
        self._begin_multiple_translations(client, operations_count, wait=False, docs_per_operation=docs_per_operation)

        # assert
        all_translations = list(client.list_all_translation_statuses())
        translations_with_skip = list(client.list_all_translation_statuses(skip=skip))
        assert len(all_translations) - len(translations_with_skip) == skip


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_translations_filter_by_status(self, client):
        operations_count = 5
        docs_per_operation = 1

        # create some translations with the status 'Succeeded'
        completed_translation_ids = self._begin_multiple_translations(client, operations_count, wait=True, docs_per_operation=docs_per_operation)

        # create some translations with the status 'Cancelled'
        translation_ids = self._begin_multiple_translations(client, operations_count, wait=False, docs_per_operation=docs_per_operation)
        for id in translation_ids:
            client.cancel_translation(id)
        self.wait(10) # wait for cancelled to propagate

        # list translations with status filter
        statuses = ["Cancelled"]
        submitted_translations = list(client.list_all_translation_statuses(statuses=statuses))

        # check statuses
        for translation in submitted_translations:
            self.assertIn(translation.status, statuses)
            self.assertNotIn(translation.id, completed_translation_ids)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_translations_filter_by_ids(self, client):
        operations_count = 3
        docs_per_operation = 2

        # create some translations
        translation_ids = self._begin_multiple_translations(client, operations_count, wait=False, docs_per_operation=docs_per_operation)

        # list translations
        submitted_translations = list(client.list_all_translation_statuses(translation_ids=translation_ids))
        self.assertIsNotNone(submitted_translations)

        # check statuses
        for translation in submitted_translations:
            self.assertIn(translation.id, translation_ids)


    @pytest.mark.live_test_only
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_translations_filter_by_created_after(self, client):
        # create some translations
        operations_count = 3
        docs_per_operation = 2

        # create some translations
        start = datetime.utcnow()
        translation_ids = self._begin_multiple_translations(client, operations_count, wait=False, docs_per_operation=docs_per_operation)

        # list translations
        submitted_translations = list(client.list_all_translation_statuses(created_after=start))
        self.assertIsNotNone(submitted_translations)

        # check statuses
        for translation in submitted_translations:
            self.assertIn(translation.id, translation_ids)
            assert(translation.created_on.replace(tzinfo=None) >= start.replace(tzinfo=None))


    @pytest.mark.live_test_only
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_translations_filter_by_created_before(self, client):
        '''
            NOTE: test is dependent on 'end' to be specific/same as time zone of the service! 
                'end' must be timezone-aware!
        '''
        operations_count = 5
        docs_per_operation = 1

        # create some translations
        self._begin_multiple_translations(client, operations_count, wait=True, docs_per_operation=docs_per_operation)
        end = datetime.utcnow().replace(tzinfo=pytz.utc)
        translation_ids = self._begin_multiple_translations(client, operations_count, wait=True, docs_per_operation=docs_per_operation)

        # list translations
        submitted_translations = list(client.list_all_translation_statuses(created_before=end))
        self.assertIsNotNone(submitted_translations)

        # check statuses
        for translation in submitted_translations:
            self.assertLessEqual(translation.created_on.replace(tzinfo=None), end.replace(tzinfo=None))
            self.assertNotIn(translation.id, translation_ids)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_translations_order_by_creation_time_asc(self, client):
        operations_count = 3
        docs_per_operation = 2

        # create some translations
        self._begin_multiple_translations(client, operations_count, wait=False, docs_per_operation=docs_per_operation)

        # list translations
        submitted_translations = list(client.list_all_translation_statuses(order_by=["created_on asc"]))
        self.assertIsNotNone(submitted_translations)

        # check statuses
        curr = datetime.min
        for translation in submitted_translations:
            assert(translation.created_on.replace(tzinfo=None) >= curr.replace(tzinfo=None))
            curr = translation.created_on


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_translations_order_by_creation_time_desc(self, client):
        operations_count = 3
        docs_per_operation = 2

        # create some translations
        self._begin_multiple_translations(client, operations_count, wait=False, docs_per_operation=docs_per_operation)

        # list translations
        submitted_translations = list(client.list_all_translation_statuses(order_by=["created_on desc"]))
        self.assertIsNotNone(submitted_translations)

        # check statuses
        curr = datetime.max
        for translation in submitted_translations:
            assert(translation.created_on.replace(tzinfo=None) <= curr.replace(tzinfo=None))
            curr = translation.created_on

    @pytest.mark.live_test_only()
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_translations_mixed_filters(self, client):
        # create some translations
        operations_count = 4
        docs_per_operation = 1
        results_per_page = 2
        statuses = ["Succeeded"]
        skip = 1

        # create some translations
        start = datetime.utcnow().replace(tzinfo=pytz.utc)
        successful_translation_ids = self._begin_multiple_translations(client, operations_count, wait=True, docs_per_operation=docs_per_operation)
        end = datetime.utcnow().replace(tzinfo=pytz.utc)

        # list translations
        submitted_translations = client.list_all_translation_statuses(
            # filters
            statuses=statuses,
            created_after=start,
            created_before=end,
            # ordering
            order_by=["created_on asc"],
            # paging
            skip=skip,
            results_per_page=results_per_page
        ).by_page()

        # check statuses
        curr_time = datetime.min
        for page in submitted_translations:
            page_translations = list(page)
            self.assertLessEqual(len(page_translations), results_per_page) # assert paging
            for translation in page_translations:
                self.assertIn(translation.id, successful_translation_ids)
                # assert ordering
                assert(translation.created_on.replace(tzinfo=None) >= curr_time.replace(tzinfo=None))
                curr_time = translation.created_on
                # assert filters
                assert(translation.created_on.replace(tzinfo=None) <= end.replace(tzinfo=None))
                assert(translation.created_on.replace(tzinfo=None) >= start.replace(tzinfo=None))
                self.assertIn(translation.status, statuses)
