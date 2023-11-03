# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest

from azure.ai.generative.synthetic.qa import QADataGenerator, QAType

API_BASE = ""
API_KEY = ""
DEPLOYMENT = ""
MODEL = ""

@pytest.mark.unittest
class TestQADataGenerator:
    def test_extract_qa_from_response(self):
        response_text = """[Q]: What is Compute Instance?
[A]: Compute instance is ...
[Q]: Is CI different than Compute Cluster?
[A]: Yes.
[Q]: In what way?
[A]: It is different ... because ...
... these are the reasons.
   Here's one more reason ...
[Q]: Is K8s also a compute?
[A]: Yes.

[Q]: Question after space?
[A]: Answer after space.

"""
        expected_questions = [
            "What is Compute Instance?",
            "Is CI different than Compute Cluster?",
            "In what way?",
            "Is K8s also a compute?",
            "Question after space?",
        ]
        expected_answers = [
            "Compute instance is ...",
            "Yes.",
            "It is different ... because ...\n... these are the reasons.\n   Here's one more reason ...",
            "Yes.\n",
            "Answer after space.\n\n",
        ]
        model_config = dict(api_base=API_BASE, api_key=API_KEY, deployment=DEPLOYMENT, model=MODEL)
        qa_generator = QADataGenerator(model_config)
        questions, answers = qa_generator._parse_qa_from_response(response_text=response_text)
        for i, question in enumerate(questions):
            assert expected_questions[i] == question, "Question not equal"
        for i, answer in enumerate(answers):
            assert expected_answers[i] == answer, "Answer not equal"

    def test_unsupported_num_questions_for_summary(self):
        model_config = dict(api_base=API_BASE, api_key=API_KEY, deployment=DEPLOYMENT, model=MODEL)
        qa_generator = QADataGenerator(model_config)
        with pytest.raises(ValueError) as excinfo:
            qa_generator.generate("", QAType.SUMMARY, 10)
        assert str(excinfo.value) == "num_questions unsupported for Summary QAType"

    @pytest.mark.parametrize("num_questions", [0, -1])
    def test_invalid_num_questions(self, num_questions):
        model_config = dict(api_base=API_BASE, api_key=API_KEY, deployment=DEPLOYMENT, model=MODEL)
        qa_generator = QADataGenerator(model_config)
        with pytest.raises(ValueError) as excinfo:
            qa_generator.generate("", QAType.SHORT_ANSWER, num_questions)
        assert str(excinfo.value) == "num_questions must be an integer greater than zero"
