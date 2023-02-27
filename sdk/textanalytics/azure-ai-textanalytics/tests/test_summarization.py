# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from testcase import TextAnalyticsTest, TextAnalyticsPreparer, is_public_cloud
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from devtools_testutils import recorded_by_proxy
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    ExtractSummaryResult,
    AbstractiveSummaryResult
)

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)


class TestSummarization(TextAnalyticsTest):
    def _interval(self):
        return 5 if self.is_live else 0

    @pytest.mark.skipif(not is_public_cloud(), reason='Usgov and China Cloud are not supported')
    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_extract_summary(self, client):
        docs = [{"id": "1", "language": "en", "text":
            "The government of British Prime Minster Theresa May has been plunged into turmoil with the resignation"
            " of two senior Cabinet ministers in a deep split over her Brexit strategy. The Foreign Secretary Boris "
            "Johnson, quit on Monday, hours after the resignation late on Sunday night of the minister in charge of "
            "Brexit negotiations, David Davis. Their decision to leave the government came three days after May "
            "appeared to have agreed a deal with her fractured Cabinet on the UK's post Brexit relationship with "
            "the EU. That plan is now in tatters and her political future appears uncertain. May appeared in Parliament"
            " on Monday afternoon to defend her plan, minutes after Downing Street confirmed the departure of Johnson. "
            "May acknowledged the splits in her statement to MPs, saying of the ministers who quit: We do not agree "
            "about the best way of delivering our shared commitment to honoring the result of the referendum. The "
            "Prime Minister's latest political drama began late on Sunday night when Davis quit, declaring he could "
            "not support May's Brexit plan. He said it involved too close a relationship with the EU and gave only "
            "an illusion of control being returned to the UK after it left the EU. It seems to me we're giving too "
            "much away, too easily, and that's a dangerous strategy at this time, Davis said in a BBC radio "
            "interview Monday morning. Johnson's resignation came Monday afternoon local time, just before the "
            "Prime Minister was due to make a scheduled statement in Parliament. This afternoon, the Prime Minister "
            "accepted the resignation of Boris Johnson as Foreign Secretary, a statement from Downing Street said."},
            {"id": "2", "language": "es", "text": "Microsoft fue fundado por Bill Gates y Paul Allen"}]

        response = client.begin_extract_summary(
            docs,
            show_stats=True,
            polling_interval=self._interval(),
        ).result()

        document_results = list(response)

        assert len(document_results) == 2
        for result in document_results:
            assert isinstance(result, ExtractSummaryResult)
            assert result.statistics
            assert len(result.sentences) == 3 if result.id == 0 else 1
            for sentence in result.sentences:
                assert sentence.text
                assert sentence.rank_score is not None
                assert sentence.offset is not None
                assert sentence.length is not None
            assert result.id is not None

    @pytest.mark.skipif(not is_public_cloud(), reason='Usgov and China Cloud are not supported')
    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_extract_summary_action_with_options(self, client):
        docs = ["The government of British Prime Minster Theresa May has been plunged into turmoil with the resignation"
            " of two senior Cabinet ministers in a deep split over her Brexit strategy. The Foreign Secretary Boris "
            "Johnson, quit on Monday, hours after the resignation late on Sunday night of the minister in charge of "
            "Brexit negotiations, David Davis. Their decision to leave the government came three days after May "
            "appeared to have agreed a deal with her fractured Cabinet on the UK's post Brexit relationship with "
            "the EU. That plan is now in tatters and her political future appears uncertain. May appeared in Parliament"
            " on Monday afternoon to defend her plan, minutes after Downing Street confirmed the departure of Johnson. "
            "May acknowledged the splits in her statement to MPs, saying of the ministers who quit: We do not agree "
            "about the best way of delivering our shared commitment to honoring the result of the referendum. The "
            "Prime Minister's latest political drama began late on Sunday night when Davis quit, declaring he could "
            "not support May's Brexit plan. He said it involved too close a relationship with the EU and gave only "
            "an illusion of control being returned to the UK after it left the EU. It seems to me we're giving too "
            "much away, too easily, and that's a dangerous strategy at this time, Davis said in a BBC radio "
            "interview Monday morning. Johnson's resignation came Monday afternoon local time, just before the "
            "Prime Minister was due to make a scheduled statement in Parliament. This afternoon, the Prime Minister "
            "accepted the resignation of Boris Johnson as Foreign Secretary, a statement from Downing Street said."]

        response = client.begin_extract_summary(
            docs,
            max_sentence_count=5,
            order_by="Rank",
            show_stats=True,
            polling_interval=self._interval(),
        ).result()

        document_results = list(response)

        assert len(document_results) == 1
        for result in document_results:
            assert isinstance(result, ExtractSummaryResult)
            assert result.statistics
            assert len(result.sentences) == 5
            previous_score = 1.0
            for sentence in result.sentences:
                assert sentence.rank_score <= previous_score
                previous_score = sentence.rank_score
                assert sentence.text
                assert sentence.offset is not None
                assert sentence.length is not None
            assert result.id is not None

    @pytest.mark.skipif(not is_public_cloud(), reason='Usgov and China Cloud are not supported')
    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_abstract_summary_action(self, client):
        docs = [{"id": "1", "language": "en", "text":
            "The government of British Prime Minster Theresa May has been plunged into turmoil with the resignation"
            " of two senior Cabinet ministers in a deep split over her Brexit strategy. The Foreign Secretary Boris "
            "Johnson, quit on Monday, hours after the resignation late on Sunday night of the minister in charge of "
            "Brexit negotiations, David Davis. Their decision to leave the government came three days after May "
            "appeared to have agreed a deal with her fractured Cabinet on the UK's post Brexit relationship with "
            "the EU. That plan is now in tatters and her political future appears uncertain. May appeared in Parliament"
            " on Monday afternoon to defend her plan, minutes after Downing Street confirmed the departure of Johnson. "
            "May acknowledged the splits in her statement to MPs, saying of the ministers who quit: We do not agree "
            "about the best way of delivering our shared commitment to honoring the result of the referendum. The "
            "Prime Minister's latest political drama began late on Sunday night when Davis quit, declaring he could "
            "not support May's Brexit plan. He said it involved too close a relationship with the EU and gave only "
            "an illusion of control being returned to the UK after it left the EU. It seems to me we're giving too "
            "much away, too easily, and that's a dangerous strategy at this time, Davis said in a BBC radio "
            "interview Monday morning. Johnson's resignation came Monday afternoon local time, just before the "
            "Prime Minister was due to make a scheduled statement in Parliament. This afternoon, the Prime Minister "
            "accepted the resignation of Boris Johnson as Foreign Secretary, a statement from Downing Street said."}]

        response = client.begin_abstractive_summary(
            docs,
            show_stats=True,
            polling_interval=self._interval(),
        ).result()

        for result in response:
            assert isinstance(result, AbstractiveSummaryResult)
            assert result.statistics is not None
            assert result.id is not None
            for summary in result.summaries:
                for context in summary.contexts:
                    assert context.offset is not None
                    assert context.length is not None
                assert summary.text

    @pytest.mark.skipif(not is_public_cloud(), reason='Usgov and China Cloud are not supported')
    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_abstract_summary_action_with_options(self, client):
        docs = [{"id": "1", "language": "en", "text":
            "The government of British Prime Minster Theresa May has been plunged into turmoil with the resignation"
            " of two senior Cabinet ministers in a deep split over her Brexit strategy. The Foreign Secretary Boris "
            "Johnson, quit on Monday, hours after the resignation late on Sunday night of the minister in charge of "
            "Brexit negotiations, David Davis. Their decision to leave the government came three days after May "
            "appeared to have agreed a deal with her fractured Cabinet on the UK's post Brexit relationship with "
            "the EU. That plan is now in tatters and her political future appears uncertain. May appeared in Parliament"
            " on Monday afternoon to defend her plan, minutes after Downing Street confirmed the departure of Johnson. "
            "May acknowledged the splits in her statement to MPs, saying of the ministers who quit: We do not agree "
            "about the best way of delivering our shared commitment to honoring the result of the referendum. The "
            "Prime Minister's latest political drama began late on Sunday night when Davis quit, declaring he could "
            "not support May's Brexit plan. He said it involved too close a relationship with the EU and gave only "
            "an illusion of control being returned to the UK after it left the EU. It seems to me we're giving too "
            "much away, too easily, and that's a dangerous strategy at this time, Davis said in a BBC radio "
            "interview Monday morning. Johnson's resignation came Monday afternoon local time, just before the "
            "Prime Minister was due to make a scheduled statement in Parliament. This afternoon, the Prime Minister "
            "accepted the resignation of Boris Johnson as Foreign Secretary, a statement from Downing Street said."}]

        response = client.begin_abstractive_summary(
            docs,
            max_sentence_count=5,
            show_stats=True,
            polling_interval=self._interval(),
        ).result()

        for result in response:
            assert isinstance(result, AbstractiveSummaryResult)
            assert result.statistics is not None
            assert result.id is not None
            for summary in result.summaries:
                for context in summary.contexts:
                    assert context.offset is not None
                    assert context.length is not None
                assert summary.text
