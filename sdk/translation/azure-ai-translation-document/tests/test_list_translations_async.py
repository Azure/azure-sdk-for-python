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
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.translation.document.aio import DocumentTranslationClient
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)

TOTAL_DOC_COUNT_IN_translation = 1


class TestSubmittedTranslations(AsyncDocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy_async
    async def test_list_translations(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables", {})
        # create some translations
        operations_count = 5
        docs_per_operation = 5
        await self._begin_multiple_translations_async(client, operations_count, docs_per_operation=docs_per_operation, wait=False, variables=variables)

        # list translations
        submitted_translations = client.list_translation_statuses()
        assert submitted_translations is not None

        # check statuses
        async for translation in submitted_translations:
            self._validate_translations(translation)
        return variables

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy_async
    async def test_list_translations_with_skip(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables", {})
        # prepare data
        operations_count = 10
        docs_per_operation = 2
        skip = 5

        # create some translations
        await self._begin_multiple_translations_async(client, operations_count, wait=False, docs_per_operation=docs_per_operation, variables=variables)

        # list translations - unable to assert skip!!
        all_translations = client.list_translation_statuses()
        all_operations_count = 0
        async for translation in all_translations:
            all_operations_count += 1

        translations_with_skip = client.list_translation_statuses(skip=skip)
        translations_with_skip_count = 0
        async for translation in translations_with_skip:
            translations_with_skip_count += 1

        assert all_operations_count - translations_with_skip_count == skip
        return variables

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy_async
    async def test_list_translations_filter_by_status(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables", {})
        operations_count = 5
        docs_per_operation = 1

        # create some translations with the status 'Succeeded'
        completed_translation_ids = await self._begin_multiple_translations_async(client, operations_count, wait=True, docs_per_operation=docs_per_operation, variables=variables)

        # create some translations with the status 'Canceled'
        translation_ids = await self._begin_multiple_translations_async(client, operations_count, wait=False, docs_per_operation=docs_per_operation, variables=variables, container_suffix="cancel")
        for id in translation_ids:
            await client.cancel_translation(id)
        self.wait(10) # wait for 'canceled' to propagate

        # list translations with status filter
        statuses = ["Canceled"]
        submitted_translations = client.list_translation_statuses(statuses=statuses)

        # check statuses
        async for translation in submitted_translations:
            assert translation.status in statuses
            assert translation.id not in completed_translation_ids
        return variables

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy_async
    async def test_list_translations_filter_by_ids(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables", {})
        operations_count = 3
        docs_per_operation = 2

        # create some translations
        translation_ids = await self._begin_multiple_translations_async(client, operations_count, wait=False, docs_per_operation=docs_per_operation, variables=variables)

        # list translations
        submitted_translations = client.list_translation_statuses(translation_ids=translation_ids)
        assert submitted_translations is not None

        # check statuses
        async for translation in submitted_translations:
            assert translation.id in translation_ids
        return variables

    @pytest.mark.live_test_only
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_translations_filter_by_created_after(self, **kwargs):
        client = kwargs.pop("client")
        # create some translations
        operations_count = 3
        docs_per_operation = 2

        # create some translations
        start = datetime.utcnow()
        translation_ids = await self._begin_multiple_translations_async(client, operations_count, wait=False, docs_per_operation=docs_per_operation)

        # list translations
        submitted_translations = client.list_translation_statuses(created_after=start)
        assert submitted_translations is not None

        # check statuses
        async for translation in submitted_translations:
            assert translation.id in translation_ids
            assert(translation.created_on.replace(tzinfo=None) >= start.replace(tzinfo=None))

    @pytest.mark.live_test_only
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_translations_filter_by_created_before(self, **kwargs):
        '''
            NOTE: test is dependent on 'end' to be specific/same as time zone of the service! 
                'end' must be timezone-aware!
        '''
        client = kwargs.pop("client")
        operations_count = 5
        docs_per_operation = 1

        # create some translations
        await self._begin_multiple_translations_async(client, operations_count, wait=True, docs_per_operation=docs_per_operation)
        end = datetime.utcnow().replace(tzinfo=pytz.utc)
        translation_ids = await self._begin_multiple_translations_async(client, operations_count, wait=True, docs_per_operation=docs_per_operation)

        # list translations
        submitted_translations = client.list_translation_statuses(created_before=end)
        assert submitted_translations is not None

        # check statuses
        async for translation in submitted_translations:
            assert translation.created_on.replace(tzinfo=None) <=  end.replace(tzinfo=None)
            assert translation.id not in  translation_ids

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy_async
    async def test_list_translations_order_by_creation_time_asc(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables", {})
        operations_count = 3
        docs_per_operation = 2

        # create some translations
        await self._begin_multiple_translations_async(client, operations_count, wait=False, docs_per_operation=docs_per_operation, variables=variables)

        # list translations
        submitted_translations = client.list_translation_statuses(order_by=["created_on asc"])
        assert submitted_translations is not None

        # check statuses
        current = datetime.min
        async for translation in submitted_translations:
            assert(translation.created_on.replace(tzinfo=None) >= current.replace(tzinfo=None))
            current = translation.created_on
        return variables

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy_async
    async def test_list_translations_order_by_creation_time_desc(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables", {})
        operations_count = 3
        docs_per_operation = 2

        # create some translations
        await self._begin_multiple_translations_async(client, operations_count, wait=False, docs_per_operation=docs_per_operation, variables=variables)

        # list translations
        submitted_translations = client.list_translation_statuses(order_by=["created_on desc"])
        assert submitted_translations is not None

        # check statuses
        current = datetime.max
        async for translation in submitted_translations:
            assert(translation.created_on.replace(tzinfo=None) <= current.replace(tzinfo=None))
            current = translation.created_on
        return variables

    @pytest.mark.live_test_only()
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_translations_mixed_filters(self, **kwargs):
        client = kwargs.pop("client")
        # create some translations
        operations_count = 4
        docs_per_operation = 1
        statuses = ["Succeeded"]
        skip = 1

        # create some translations
        start = datetime.utcnow().replace(tzinfo=pytz.utc)
        successful_translation_ids = await self._begin_multiple_translations_async(client, operations_count, wait=True, docs_per_operation=docs_per_operation)
        end = datetime.utcnow().replace(tzinfo=pytz.utc)

        # list translations
        submitted_translations = client.list_translation_statuses(
            # filters
            statuses=statuses,
            created_after=start,
            created_before=end,
            # ordering
            order_by=["created_on asc"],
            # paging
            skip=skip,
        ).by_page()

        # check statuses
        current_time = datetime.min
        async for page in submitted_translations:
            counter = 0
            async for translation in page:
                counter += 1
                # assert id
                assert translation.id in successful_translation_ids
                # assert ordering
                assert(translation.created_on.replace(tzinfo=None) >= current_time.replace(tzinfo=None))
                current_time = translation.created_on
                # assert filters
                assert(translation.created_on.replace(tzinfo=None) <= end.replace(tzinfo=None))
                assert(translation.created_on.replace(tzinfo=None) >= start.replace(tzinfo=None))
                assert translation.status in statuses
