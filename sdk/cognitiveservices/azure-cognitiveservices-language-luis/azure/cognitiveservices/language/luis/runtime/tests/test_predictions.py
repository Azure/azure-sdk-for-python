from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from baseTest import *
import unittest


class PredectionsTest(unittest.TestCase):
    @use_client
    def test_prediction_slot(self, client: LUISRuntimeClient):
        luis_result = client.prediction.resolve(
            appId,
            utterance,
            timezoneOffset,
            verbose,
            isStaging
        )
        assert(luis_result.query == utterance)
        assert(luis_result.top_scoring_intent.intent == "intent")
        assert(len(luis_result.intents) == 2)
        assert(len(luis_result.entities) == 2)
        assert(luis_result.entities[0].type == "simple")
        assert(luis_result.entities[1].type == "builtin.datetimeV2.date")

        top_intent = luis_result.top_scoring_intent.score
        assert(top_intent > 0.5)

        assert(luis_result.sentiment_analysis.label == "positive")
        assert(luis_result.sentiment_analysis.score > 0.5)

    @use_client
    def test_prediction_appNotFound_throwsAPIErrorException(self, client: LUISRuntimeClient):
        try:
            client.prediction.resolve(
                "7555b7c1-e69c-4580-9d95-1abd6dfa8291", "this is a test with post")
        except Exception as inst:
            assert(inst.args[0] ==
                   "Operation returned an invalid status code 'Gone'")

    @use_client
    def test_prediction_nullQuery_throwsValidationException(self, client: LUISRuntimeClient):
        try:
            client.prediction.resolve(appId, None)
        except Exception as inst:
            assert(inst.args[0] == "Parameter 'body' can not be None.")
