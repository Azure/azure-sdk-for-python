# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from datetime import datetime
import functools
from testcase import DocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from devtools_testutils import recorded_by_proxy
from azure.ai.translation.document import DocumentTranslationClient
import pytest

DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestAllDocumentStatuses(DocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy
    def test_list_document_statuses(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables", {})
        docs_count = 5
        target_language = "es"

        # submit and validate operation
        poller = self._begin_and_validate_translation_with_multiple_docs(client, docs_count, language=target_language, wait=True, variables=variables)

        # list docs statuses
        doc_statuses = list(client.list_document_statuses(poller.id)) # convert from generic iterator to list
        assert len(doc_statuses) == docs_count

        for document in doc_statuses:
            self._validate_doc_status(document, target_language)
        return variables

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy
    def test_list_document_statuses_with_skip(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables", {})
        docs_count = 10
        skip = 2
        target_language = "es"

        # submit and validate operation
        poller = self._begin_and_validate_translation_with_multiple_docs(client, docs_count, language=target_language, wait=True, variables=variables)

        # check doc statuses
        doc_statuses = list(client.list_document_statuses(translation_id=poller.id, skip=skip))
        assert len(doc_statuses) == docs_count - skip

        # iterate over docs
        for document in doc_statuses:
            self._validate_doc_status(document, target_language)
        return variables

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy
    def test_list_document_statuses_filter_by_status(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables", {})
        docs_count = 10
        target_language = "es"

        # submit and validate operation
        poller = self._begin_and_validate_translation_with_multiple_docs(client, docs_count, language=target_language, wait=True, variables=variables)

        # list operations
        statuses = ["NotStarted"]
        doc_statuses = list(client.list_document_statuses(poller.id, statuses=statuses))
        assert(len(doc_statuses) == 0)

        statuses = ["Succeeded"]
        doc_statuses = list(client.list_document_statuses(poller.id, statuses=statuses))
        assert(len(doc_statuses) == docs_count)

        statuses = ["Failed"]
        doc_statuses = list(client.list_document_statuses(poller.id, statuses=statuses))
        assert(len(doc_statuses) == 0)
        return variables

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy
    def test_list_document_statuses_filter_by_ids(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables", {})
        docs_count = 5
        target_language = "es"

        # submit and validate operation
        poller = self._begin_and_validate_translation_with_multiple_docs(client, docs_count, language=target_language, wait=True, variables=variables)

        # filter ids
        doc_statuses = list(client.list_document_statuses(poller.id)) # convert from generic iterator to list
        assert len(doc_statuses) == docs_count
        ids = [doc.id for doc in doc_statuses]
        ids = ids[:docs_count//2]

        # do the testing
        doc_statuses = list(client.list_document_statuses(poller.id, document_ids=ids))
        assert len(doc_statuses) == len(ids)
        for document in doc_statuses:
            self._validate_doc_status(document, target_language, ids=ids)
        return variables

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy
    def test_list_document_statuses_order_by_creation_time_asc(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables", {})
        docs_count = 5
        target_language = "es"

        # submit and validate operation
        poller = self._begin_and_validate_translation_with_multiple_docs(client, docs_count, language=target_language, wait=True, variables=variables)

        # check doc statuses
        doc_statuses = list(client.list_document_statuses(poller.id, order_by=["created_on asc"])) # convert from generic iterator to list
        assert len(doc_statuses) == docs_count

        current = datetime.min
        for document in doc_statuses:
            assert(document.created_on.replace(tzinfo=None) >= current.replace(tzinfo=None))
            current = document.created_on
        return variables

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy
    def test_list_document_statuses_order_by_creation_time_desc(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables", {})
        docs_count = 5
        target_language = "es"

        # submit and validate operation
        poller = self._begin_and_validate_translation_with_multiple_docs(client, docs_count, language=target_language, wait=True, variables=variables)

        # check doc statuses
        doc_statuses = list(client.list_document_statuses(poller.id, order_by=["created_on desc"])) # convert from generic iterator to list
        assert len(doc_statuses) == docs_count

        current = datetime.max
        for document in doc_statuses:
            assert(document.created_on.replace(tzinfo=None) <= current.replace(tzinfo=None))
            current = document.created_on
        return variables

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy
    def test_list_document_statuses_mixed_filters(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables", {})
        docs_count = 10
        target_language = "es"
        skip = 1
        statuses = ["Succeeded"]

        # submit and validate operation
        poller = self._begin_and_validate_translation_with_multiple_docs(client, docs_count, language=target_language, wait=True, variables=variables)

        # get ids
        doc_statuses = list(client.list_document_statuses(poller.id)) # convert from generic iterator to list
        assert len(doc_statuses) == docs_count
        ids = [doc.id for doc in doc_statuses]
        ids = ids[:docs_count//2]

        filtered_docs = client.list_document_statuses(
            poller.id,
            # filters
            document_ids=ids,
            statuses=statuses,
            # ordering
            order_by=["created_on asc"],
            # paging
            skip=skip,
        ).by_page()
        assert filtered_docs is not None

        # check statuses
        counter = 0
        current_time = datetime.min
        for page in filtered_docs:
            page_docs = list(page)
            for doc in page_docs:
                counter += 1
                # assert ordering
                assert(doc.created_on.replace(tzinfo=None) >= current_time.replace(tzinfo=None))
                current_time = doc.created_on
                # assert filters
                assert doc.status in statuses
                assert doc.id in ids

        assert(counter == len(ids) - skip)
        return variables
