# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import pytz
from datetime import datetime
import functools
from asynctestcase import AsyncDocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.translation.document.aio import DocumentTranslationClient
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)

TOTAL_DOC_COUNT_IN_translation = 1


class TestSubmittedTranslations(AsyncDocumentTranslationTest):


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_translations(self, client):
        # create some translations
        operations_count = 5
        docs_per_operation = 5
        await self._begin_multiple_translations_async(client, operations_count, docs_per_operation=docs_per_operation, wait=False)

        # list translations
        submitted_translations = client.list_all_translation_statuses()
        self.assertIsNotNone(submitted_translations)

        # check statuses
        async for translation in submitted_translations:
            self._validate_translations(translation)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_translations_with_pagination(self, client):
        # prepare data
        operations_count = 5
        docs_per_operation = 2
        results_per_page = 2

        # create some translations
        await self._begin_multiple_translations_async(client, operations_count, docs_per_operation=docs_per_operation, wait=False)

        # list translations
        submitted_translations_pages = client.list_all_translation_statuses(results_per_page=results_per_page).by_page()
        self.assertIsNotNone(submitted_translations_pages)

        # iterate by page
        async for page in submitted_translations_pages:
            page_translations = []
            async for translation in page:
                page_translations.append(translation)
                self._validate_translations(translation)

            self.assertLessEqual(len(page_translations), results_per_page)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_translations_with_skip(self, client):
        # prepare data
        operations_count = 10
        docs_per_operation = 2
        skip = 5

        # create some translations
        await self._begin_multiple_translations_async(client, operations_count, wait=False, docs_per_operation=docs_per_operation)

        # list translations - unable to assert skip!!
        all_translations = client.list_all_translation_statuses()
        all_operations_count = 0
        async for translation in all_translations:
            all_operations_count += 1

        translations_with_skip = client.list_all_translation_statuses(skip=skip)
        translations_with_skip_count = 0
        async for translation in translations_with_skip:
            translations_with_skip_count += 1

        assert all_operations_count - translations_with_skip_count == skip


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_translations_filter_by_status(self, client):
        operations_count = 5
        docs_per_operation = 1

        # create some translations with the status 'Succeeded'
        completed_translation_ids = await self._begin_multiple_translations_async(client, operations_count, wait=True, docs_per_operation=docs_per_operation)

        # create some translations with the status 'Cancelled'
        translation_ids = await self._begin_multiple_translations_async(client, operations_count, wait=False, docs_per_operation=docs_per_operation)
        for id in translation_ids:
            await client.cancel_translation(id)
        self.wait(10) # wait for 'cancelled' to propagate

        # list translations with status filter
        statuses = ["Cancelled"]
        submitted_translations = client.list_all_translation_statuses(statuses=statuses)

        # check statuses
        async for translation in submitted_translations:
            self.assertIn(translation.status, statuses)
            self.assertNotIn(translation.id, completed_translation_ids)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_translations_filter_by_ids(self, client):
        operations_count = 3
        docs_per_operation = 2

        # create some translations
        translation_ids = await self._begin_multiple_translations_async(client, operations_count, wait=False, docs_per_operation=docs_per_operation)

        # list translations
        submitted_translations = client.list_all_translation_statuses(translation_ids=translation_ids)
        self.assertIsNotNone(submitted_translations)

        # check statuses
        async for translation in submitted_translations:
            self.assertIn(translation.id, translation_ids)


    @pytest.mark.live_test_only
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_translations_filter_by_created_after(self, client):
        # create some translations
        operations_count = 3
        docs_per_operation = 2

        # create some translations
        start = datetime.utcnow()
        translation_ids = await self._begin_multiple_translations_async(client, operations_count, wait=False, docs_per_operation=docs_per_operation)

        # list translations
        submitted_translations = client.list_all_translation_statuses(created_after=start)
        self.assertIsNotNone(submitted_translations)

        # check statuses
        async for translation in submitted_translations:
            self.assertIn(translation.id, translation_ids)
            assert(translation.created_on.replace(tzinfo=None) >= start.replace(tzinfo=None))


    @pytest.mark.live_test_only
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_translations_filter_by_created_before(self, client):
        '''
            NOTE: test is dependent on 'end' to be specific/same as time zone of the service! 
                'end' must be timezone-aware!
        '''
        operations_count = 5
        docs_per_operation = 1

        # create some translations
        await self._begin_multiple_translations_async(client, operations_count, wait=True, docs_per_operation=docs_per_operation)
        end = datetime.utcnow().replace(tzinfo=pytz.utc)
        translation_ids = await self._begin_multiple_translations_async(client, operations_count, wait=True, docs_per_operation=docs_per_operation)

        # list translations
        submitted_translations = client.list_all_translation_statuses(created_before=end)
        self.assertIsNotNone(submitted_translations)

        # check statuses
        async for translation in submitted_translations:
            self.assertLessEqual(translation.created_on.replace(tzinfo=None), end.replace(tzinfo=None))
            self.assertNotIn(translation.id, translation_ids)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_translations_order_by_creation_time_asc(self, client):
        operations_count = 3
        docs_per_operation = 2

        # create some translations
        await self._begin_multiple_translations_async(client, operations_count, wait=False, docs_per_operation=docs_per_operation)

        # list translations
        submitted_translations = client.list_all_translation_statuses(order_by=["created_on asc"])
        self.assertIsNotNone(submitted_translations)

        # check statuses
        curr = datetime.min
        async for translation in submitted_translations:
            assert(translation.created_on.replace(tzinfo=None) >= curr.replace(tzinfo=None))
            curr = translation.created_on


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_translations_order_by_creation_time_desc(self, client):
        operations_count = 3
        docs_per_operation = 2

        # create some translations
        await self._begin_multiple_translations_async(client, operations_count, wait=False, docs_per_operation=docs_per_operation)

        # list translations
        submitted_translations = client.list_all_translation_statuses(order_by=["created_on desc"])
        self.assertIsNotNone(submitted_translations)

        # check statuses
        curr = datetime.max
        async for translation in submitted_translations:
            assert(translation.created_on.replace(tzinfo=None) <= curr.replace(tzinfo=None))
            curr = translation.created_on

    @pytest.mark.live_test_only()
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_translations_mixed_filters(self, client):
        # create some translations
        operations_count = 4
        docs_per_operation = 1
        results_per_page = 2
        statuses = ["Succeeded"]
        skip = 1

        # create some translations
        start = datetime.utcnow().replace(tzinfo=pytz.utc)
        successful_translation_ids = await self._begin_multiple_translations_async(client, operations_count, wait=True, docs_per_operation=docs_per_operation)
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
        async for page in submitted_translations:
            counter = 0
            async for translation in page:
                counter += 1
                # assert id
                self.assertIn(translation.id, successful_translation_ids)
                # assert ordering
                assert(translation.created_on.replace(tzinfo=None) >= curr_time.replace(tzinfo=None))
                curr_time = translation.created_on
                # assert filters
                assert(translation.created_on.replace(tzinfo=None) <= end.replace(tzinfo=None))
                assert(translation.created_on.replace(tzinfo=None) >= start.replace(tzinfo=None))
                self.assertIn(translation.status, statuses)

            self.assertLessEqual(counter, results_per_page) # assert paging
