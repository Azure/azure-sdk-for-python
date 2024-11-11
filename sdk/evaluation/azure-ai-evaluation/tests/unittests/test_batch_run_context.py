import os
from unittest.mock import MagicMock

import pytest
from promptflow.client import PFClient

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
    def test_with_codeclient(self, mocker, code_client_mock):
        mock_append_user_agent = mocker.patch(
            "promptflow._utils.user_agent_utils.ClientUserAgentUtil.append_user_agent"
        )

        with EvalRunContext(code_client_mock):
            mock_append_user_agent.assert_called_once_with(USER_AGENT)

    def test_with_pfclient(self, mocker, pf_client_mock):
        mock_append_user_agent = mocker.patch(
            "promptflow._utils.user_agent_utils.ClientUserAgentUtil.append_user_agent"
        )

        with EvalRunContext(pf_client_mock):
            mock_append_user_agent.assert_not_called()

    def test_batch_timeout_default(self):
        before_timeout = os.environ.get(PF_BATCH_TIMEOUT_SEC)
        assert before_timeout is None

        with EvalRunContext(ProxyClient(PFClient)):
            during_timeout = int(os.environ.get(PF_BATCH_TIMEOUT_SEC))
            assert during_timeout == PF_BATCH_TIMEOUT_SEC_DEFAULT

        # Default timeout should be reset after exiting EvalRunContext
        after_timeout = os.environ.get(PF_BATCH_TIMEOUT_SEC)
        assert after_timeout is None

    def test_batch_timeout_custom(self):
        custom_timeout = 1000
        os.environ[PF_BATCH_TIMEOUT_SEC] = str(custom_timeout)

        with EvalRunContext(ProxyClient(PFClient)):
            during_timeout = int(os.environ.get(PF_BATCH_TIMEOUT_SEC))
            assert during_timeout == custom_timeout

        # Custom timeouts should not be reset after exiting EvalRunContext
        after_timeout = int(os.environ.get(PF_BATCH_TIMEOUT_SEC))
        assert after_timeout == custom_timeout
