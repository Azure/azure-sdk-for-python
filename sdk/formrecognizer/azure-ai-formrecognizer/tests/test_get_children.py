# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from azure.ai.formrecognizer import DocumentAnalysisClient, AnalyzedDocument, DocumentEntity, DocumentField, DocumentKeyValueElement, DocumentKeyValuePair, DocumentLine, DocumentTable, DocumentTableCell
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

        d = result.pages[0].lines[0].to_dict()
        elem = DocumentLine.from_dict(d)

        elements = elem.get_words()
        assert len(elements) == 1
        assert elements[0].content == "Contoso"


    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_document_table_get_children(self, client):
        with open(self.form_jpg, "rb") as fd:
            document = fd.read()

        poller = client.begin_analyze_document("prebuilt-layout", document)
        result = poller.result()
        
        d = result.tables[0].to_dict()
        elem = DocumentTable.from_dict(d)

        elements = elem.get_words()
        assert len(elements) == 25

        elements = elem.get_lines()
        assert len(elements) == 20


    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_document_table_cell_get_children(self, client):
        with open(self.form_jpg, "rb") as fd:
            document = fd.read()

        poller = client.begin_analyze_document("prebuilt-layout", document)
        result = poller.result()
        
        d = result.tables[0].cells[0].to_dict()
        elem = DocumentTableCell.from_dict(d)

        elements = elem.get_words()
        assert len(elements) == 1

        elements = elem.get_lines()
        assert len(elements) == 1


    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_analyzed_document_get_children(self, client):
        with open(self.form_jpg, "rb") as fd:
            document = fd.read()

        poller = client.begin_analyze_document("prebuilt-invoice", document)
        result = poller.result()
        
        d = result.documents[0].to_dict()
        elem = AnalyzedDocument.from_dict(d)

        elements = elem.get_words()
        assert len(elements) == 132

        elements = elem.get_lines()
        assert len(elements) == 54


    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_document_field_get_children(self, client):
        with open(self.form_jpg, "rb") as fd:
            document = fd.read()

        poller = client.begin_analyze_document("prebuilt-invoice", document)
        result = poller.result()
        
        d = result.documents[0].fields.get("InvoiceTotal").to_dict()
        elem = DocumentField.from_dict(d)

        elements = elem.get_words()
        assert len(elements) == 1

        elements = elem.get_lines()
        assert len(elements) == 1


    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_document_entity_get_children(self, client):
        with open(self.form_jpg, "rb") as fd:
            document = fd.read()

        poller = client.begin_analyze_document("prebuilt-document", document)
        result = poller.result()
        
        d = result.entities[0].to_dict()
        elem = DocumentEntity.from_dict(d)

        elements = elem.get_words()
        assert len(elements) == 1

        elements = elem.get_lines()
        assert len(elements) == 1


    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    def test_document_key_value_element_get_children(self, client):
        with open(self.form_jpg, "rb") as fd:
            document = fd.read()

        poller = client.begin_analyze_document("prebuilt-document", document)
        result = poller.result()
        
        d = result.key_value_pairs[0].key.to_dict()
        elem = DocumentKeyValueElement.from_dict(d)

        elements = elem.get_words()
        assert len(elements) == 2

        elements = elem.get_lines()
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
