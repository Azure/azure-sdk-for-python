import os
from unittest.mock import MagicMock

import pytest
from azure.ai.evaluation._legacy._adapters.client import PFClient
from azure.ai.evaluation._legacy._adapters._check import MISSING_LEGACY_SDK

from azure.ai.evaluation._constants import PF_BATCH_TIMEOUT_SEC, PF_BATCH_TIMEOUT_SEC_DEFAULT
from azure.ai.evaluation._evaluate._batch_run import CodeClient, EvalRunContext, ProxyClient
from azure.ai.evaluation._user_agent import USER_AGENT


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

            mock_append_user_agent.assert_called_once_with(USER_AGENT)

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
