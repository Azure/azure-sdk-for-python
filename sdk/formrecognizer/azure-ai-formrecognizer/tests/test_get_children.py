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
