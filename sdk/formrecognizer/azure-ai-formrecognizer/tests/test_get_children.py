# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils import recorded_by_proxy
from azure.ai.formrecognizer import DocumentAnalysisClient, DocumentLine, AnalyzeResult
from preparers import FormRecognizerPreparer
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer


DocumentAnalysisClientPreparer = functools.partial(_GlobalClientPreparer, DocumentAnalysisClient)


class TestGetChildren(FormRecognizerTest):

    def teardown(self):
        self.sleep(4)

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy
    def test_document_line_get_words(self, **kwargs):
        client = kwargs.pop("client")
        with open(self.invoice_pdf, "rb") as fd:
            document = fd.read()

        poller = client.begin_analyze_document("prebuilt-document", document)
        result = poller.result()
        
        elements = result.pages[0].lines[0].get_words()
        assert len(elements) == 1
        assert elements[0].content == "Contoso"

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy
    def test_document_line_get_words_error(self, **kwargs):
        client = kwargs.pop("client")
        with open(self.invoice_pdf, "rb") as fd:
            document = fd.read()

        poller = client.begin_analyze_document("prebuilt-document", document)
        result = poller.result()
        
        # check the error occurs when converting a larger element that encompasses a document line
        d = result.to_dict()
        analyze_result = AnalyzeResult.from_dict(d)

        with pytest.raises(ValueError):
            elements = analyze_result.pages[0].lines[0].get_words()

        # check that the error occurs when directly converting a DocumentLine from a dict
        d = result.pages[0].lines[0].to_dict()
        line = DocumentLine.from_dict(d)
        with pytest.raises(ValueError):
            elements = line.get_words()
