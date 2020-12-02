# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import re
from azure.ai.formrecognizer._helpers import get_element_type
from testcase import FormRecognizerTest


class TestResolveElements(FormRecognizerTest):

    def test_word_reference(self):
        word_unlabeled_ref = "#/readResults/13/lines/91/words/1000"
        assert get_element_type(word_unlabeled_ref) == "word"
        indices = [int(s) for s in re.findall(r"\d+", word_unlabeled_ref)]
        assert [13, 91, 1000] == indices

    def test_line_reference(self):
        line_unlabeled_ref = "#/readResults/3/lines/1"
        assert get_element_type(line_unlabeled_ref) == "line"
        indices = [int(s) for s in re.findall(r"\d+", line_unlabeled_ref)]
        assert [3, 1] == indices

    def test_selection_mark_reference(self):
        selection_mark_ref = "#/readResults/0/selectionMarks/0"
        assert get_element_type(selection_mark_ref) == "selectionMark"
        indices = [int(s) for s in re.findall(r"\d+", selection_mark_ref)]
        assert [0, 0] == indices

    def test_bad_ref(self):
        # None will raise in the function that calls get_element_type
        bad_ref1 = "#/readResults/3/thing/5"
        assert get_element_type(bad_ref1) is None

        bad_ref2 = "#/readResults/3"
        assert get_element_type(bad_ref2) is None

        bad_ref3 = "#/analyzeResult/readResults/100"
        assert get_element_type(bad_ref3) is None
