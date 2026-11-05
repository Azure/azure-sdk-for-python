# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import pytest

from azure.ai.evaluation import BleuScoreEvaluator, GleuScoreEvaluator, MeteorScoreEvaluator

REFERENCE = "The U.S. economy didn't grow; prices rose 5.00 percent in March."


def _score(evaluator_class, metric, response, ground_truth):
    return evaluator_class()(response=response, ground_truth=ground_truth)[f"{metric}_score"]


EVALUATORS = [
    pytest.param(BleuScoreEvaluator, "bleu", id="bleu"),
    pytest.param(GleuScoreEvaluator, "gleu", id="gleu"),
    pytest.param(MeteorScoreEvaluator, "meteor", id="meteor"),
]


@pytest.mark.unittest
class TestNltkEvaluatorsTokenization:
    @pytest.mark.parametrize("evaluator_class,metric", EVALUATORS)
    @pytest.mark.parametrize(
        "non_ascii_suffix,ascii_suffix",
        [
            pytest.param(" —", " -", id="em-dash"),
            pytest.param(" “yes”", ' "yes"', id="curly-quotes"),
        ],
    )
    def test_non_ascii_response_only(self, evaluator_class, metric, non_ascii_suffix, ascii_suffix):
        # One non-ASCII character in the response must not change how the shared words are tokenized,
        # so the score is close to the score with the equivalent ASCII character.
        non_ascii_score = _score(evaluator_class, metric, REFERENCE + non_ascii_suffix, REFERENCE)
        ascii_score = _score(evaluator_class, metric, REFERENCE + ascii_suffix, REFERENCE)

        assert non_ascii_score == pytest.approx(ascii_score, abs=0.05)

    @pytest.mark.parametrize("evaluator_class,metric", EVALUATORS)
    def test_non_ascii_ground_truth_only(self, evaluator_class, metric):
        non_ascii_score = _score(evaluator_class, metric, REFERENCE, REFERENCE + " —")
        ascii_score = _score(evaluator_class, metric, REFERENCE, REFERENCE + " -")

        assert non_ascii_score == pytest.approx(ascii_score, abs=0.05)

    @pytest.mark.parametrize("evaluator_class,metric", EVALUATORS)
    def test_identical_texts_score_one(self, evaluator_class, metric):
        for text in (REFERENCE, REFERENCE + " —"):
            assert _score(evaluator_class, metric, text, text) == pytest.approx(1.0, abs=1e-3)

    def test_bleu_issue_repro(self):
        # Before the fix this was 0.446 with the em dash and 0.925 with an ASCII hyphen.
        assert _score(BleuScoreEvaluator, "bleu", REFERENCE + " —", REFERENCE) > 0.9
