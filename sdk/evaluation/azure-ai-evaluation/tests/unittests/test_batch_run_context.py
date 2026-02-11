import os
from unittest.mock import MagicMock

import pytest
from azure.ai.evaluation._legacy._adapters.client import PFClient
from azure.ai.evaluation._legacy._adapters._check import MISSING_LEGACY_SDK

from azure.ai.evaluation._constants import PF_BATCH_TIMEOUT_SEC, PF_BATCH_TIMEOUT_SEC_DEFAULT
from azure.ai.evaluation._evaluate._batch_run import CodeClient, EvalRunContext, ProxyClient
from azure.ai.evaluation._user_agent import UserAgentSingleton


@pytest.fixture
def code_client_mock():
    return MagicMock(spec=CodeClient)


@pytest.fixture
def pf_client_mock():
    return MagicMock(spec=PFClient)


@pytest.mark.unittest
class TestEvalRunContext:
    @pytest.mark.skipif(MISSING_LEGACY_SDK, reason="This test has a promptflow dependency")
    def test_with_codeclient(self, mocker, code_client_mock):
        mock_append_user_agent = mocker.patch(
            "promptflow._utils.user_agent_utils.ClientUserAgentUtil.append_user_agent"
        )
        mock_inject_openai_api = mocker.patch("promptflow.tracing._integrations._openai_injector.inject_openai_api")
        mock_recover_openai_api = mocker.patch("promptflow.tracing._integrations._openai_injector.recover_openai_api")

        with EvalRunContext(code_client_mock):
            # TODO: Failed to mock inject_openai_api and recover_openai_api for some reason.
            # Need to investigate further.
            # mock_inject_openai_api.assert_called_once()
            # mock_recover_openai_api.assert_called_once()
            print(f"mock_inject_openai_api.call_count: {mock_inject_openai_api.call_count}")
            print(f"mock_recover_openai_api.call_count: {mock_recover_openai_api.call_count}")
            pass

            mock_append_user_agent.assert_called_once_with(UserAgentSingleton().value)

    @pytest.mark.skipif(MISSING_LEGACY_SDK, reason="This test has a promptflow dependency")
    def test_with_pfclient(self, mocker, pf_client_mock):
        mock_append_user_agent = mocker.patch(
            "promptflow._utils.user_agent_utils.ClientUserAgentUtil.append_user_agent"
        )
        mock_inject_openai_api = mocker.patch("promptflow.tracing._integrations._openai_injector.inject_openai_api")
        mock_recover_openai_api = mocker.patch("promptflow.tracing._integrations._openai_injector.recover_openai_api")

        with EvalRunContext(pf_client_mock):
            mock_append_user_agent.assert_not_called()
            mock_inject_openai_api.assert_not_called()
            pass

        mock_recover_openai_api.assert_not_called()

    def test_batch_timeout_default(self):
        before_timeout = os.environ.get(PF_BATCH_TIMEOUT_SEC)
        assert before_timeout is None

        with EvalRunContext(ProxyClient()):
            during_timeout = int(os.environ.get(PF_BATCH_TIMEOUT_SEC))
            assert during_timeout == PF_BATCH_TIMEOUT_SEC_DEFAULT

        # Default timeout should be reset after exiting EvalRunContext
        after_timeout = os.environ.get(PF_BATCH_TIMEOUT_SEC)
        assert after_timeout is None

    def test_batch_timeout_custom(self):
        custom_timeout = 1000
        os.environ[PF_BATCH_TIMEOUT_SEC] = str(custom_timeout)

        with EvalRunContext(ProxyClient()):
            during_timeout = int(os.environ.get(PF_BATCH_TIMEOUT_SEC))
            assert during_timeout == custom_timeout

        # Custom timeouts should not be reset after exiting EvalRunContext
        after_timeout = int(os.environ.get(PF_BATCH_TIMEOUT_SEC))
        assert after_timeout == custom_timeout


@pytest.mark.unittest
class TestProxyClient:
    @pytest.mark.skipif(MISSING_LEGACY_SDK, reason="This test has a promptflow dependency")
    def test_get_details_handles_failed_values(self, mocker):
        """Test that get_details properly handles '(Failed)' values without generating warnings."""
        import pandas as pd
        import math
        import warnings

        # Mock the PFClient and its get_details method
        mock_pf_client = MagicMock(spec=PFClient)
        mock_run = MagicMock()

        # Create test data that simulates real output with "(Failed)" values
        test_df = pd.DataFrame(
            {
                "outputs.score": [0.85, 0.92, "(Failed)", 0.78],
                "outputs.relevance": [4.0, "(Failed)", 3.0, 5.0],
                "line_number": [1, 2, 3, 4],
            }
        )

        mock_pf_client.get_details.return_value = test_df

        # Create ProxyClient instance and mock the PFClient
        proxy_client = ProxyClient()
        proxy_client._pf_client = mock_pf_client

        # Mock the get_result method to return our mock run
        mock_client_run = MagicMock()
        mocker.patch.object(ProxyClient, "get_result", return_value=mock_run)

        # Capture warnings to ensure no FutureWarning is generated
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")

            # Call the method under test
            result_df = proxy_client.get_details(mock_client_run)

            # Check that no FutureWarning about downcasting was generated
            future_warnings = [w for w in warning_list if issubclass(w.category, FutureWarning)]
            downcasting_warnings = [w for w in future_warnings if "Downcasting behavior" in str(w.message)]

            assert len(downcasting_warnings) == 0, f"Unexpected FutureWarning about downcasting: {downcasting_warnings}"

        # Verify the results are as expected
        assert result_df is not None
        assert isinstance(result_df, pd.DataFrame)

        # Check that "(Failed)" values were replaced with NaN
        assert result_df.isna().sum().sum() == 2  # Two "(Failed)" values should become NaN

        # Verify specific positions have NaN
        assert pd.isna(result_df.loc[2, "outputs.score"])  # Row 2, score column
        assert pd.isna(result_df.loc[1, "outputs.relevance"])  # Row 1, relevance column

        # Verify non-failed values are preserved
        assert result_df.loc[0, "outputs.score"] == 0.85
        assert result_df.loc[0, "outputs.relevance"] == 4.0
