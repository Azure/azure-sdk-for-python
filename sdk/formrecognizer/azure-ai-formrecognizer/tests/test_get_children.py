# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from azure.ai.formrecognizer import DocumentAnalysisClient
from preparers import FormRecognizerPreparer
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer


DocumentAnalysisClientPreparer = functools.partial(_GlobalClientPreparer, DocumentAnalysisClient)


class TestGetChildren(FormRecognizerTest):

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_document_line_get_words(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            document = fd.read()

        poller = client.begin_analyze_document("prebuilt-document", document)
        result = poller.result()
        
        elements = result.pages[0].lines[0].get_words()
        assert len(elements) == 1
        assert elements[0].content == "Contoso"


    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_document_table_get_children(self, client):
        with open(self.form_jpg, "rb") as fd:
            document = fd.read()

        poller = client.begin_analyze_document("prebuilt-layout", document)
        result = poller.result()
        
        elements = result.tables[0].get_words()
        assert len(elements) == 25

        elements = result.tables[0].get_lines()
        assert len(elements) == 20


    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_document_table_cell_get_children(self, client):
        with open(self.form_jpg, "rb") as fd:
            document = fd.read()

        poller = client.begin_analyze_document("prebuilt-layout", document)
        result = poller.result()
        
        elements = result.tables[0].cells[0].get_words()
        assert len(elements) == 1

        elements = result.tables[0].cells[0].get_lines()
        assert len(elements) == 1


    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_analyzed_document_get_children(self, client):
        with open(self.form_jpg, "rb") as fd:
            document = fd.read()

        poller = client.begin_analyze_document("prebuilt-invoice", document)
        result = poller.result()
        
        elements = result.documents[0].get_words()
        assert len(elements) == 132

        elements = result.documents[0].get_lines()
        assert len(elements) == 54


    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_document_field_get_children(self, client):
        with open(self.form_jpg, "rb") as fd:
            document = fd.read()

        poller = client.begin_analyze_document("prebuilt-invoice", document)
        result = poller.result()
        
        elements = result.documents[0].fields.get("InvoiceTotal").get_words()
        assert len(elements) == 1

        elements = result.documents[0].fields.get("InvoiceTotal").get_lines()
        assert len(elements) == 1


    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_document_entity_get_children(self, client):
        with open(self.form_jpg, "rb") as fd:
            document = fd.read()

        poller = client.begin_analyze_document("prebuilt-document", document)
        result = poller.result()
        
        elements = result.entities[0].get_words()
        assert len(elements) == 1

        elements = result.entities[0].get_lines()
        assert len(elements) == 1


    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_document_key_value_element_get_children(self, client):
        with open(self.form_jpg, "rb") as fd:
            document = fd.read()

        poller = client.begin_analyze_document("prebuilt-document", document)
        result = poller.result()
        
        elements = result.key_value_pairs[0].key.get_words()
        assert len(elements) == 2

        elements = result.key_value_pairs[0].key.get_lines()
        assert len(elements) == 0


    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_get_words_after_get_lines(self, client):
        with open(self.form_jpg, "rb") as fd:
            document = fd.read()

        poller = client.begin_analyze_document("prebuilt-document", document)
        result = poller.result()

        lines = result.entities[0].get_lines()
        assert len(lines) == 1

        words = lines[0].get_words()
        assert len(words) == 1
