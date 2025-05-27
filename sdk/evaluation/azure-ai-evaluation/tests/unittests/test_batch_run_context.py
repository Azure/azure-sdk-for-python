import os
import pytest

from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from azure.ai.evaluation._constants import PF_BATCH_TIMEOUT_SEC, PF_BATCH_TIMEOUT_SEC_DEFAULT
from azure.ai.evaluation._evaluate._batch_run import CodeClient, EvalRunContext, ProxyClient, RunSubmitterClient
from azure.ai.evaluation._user_agent import USER_AGENT
from azure.ai.evaluation._legacy._adapters._check import HAS_LEGACY_SDK


@pytest.fixture
def code_client_mock():
    return MagicMock(spec=CodeClient)


@pytest.fixture
def proxy_client_mock():
    return MagicMock(spec=ProxyClient)


@pytest.fixture
def run_submitter_client_mock():
    return MagicMock(spec=RunSubmitterClient)


@pytest.fixture
def mock_inject_openai(mocker: MockerFixture):
    """Mocks the inject OpenAI API method"""
    return mocker.patch(
        "azure.ai.evaluation._evaluate._batch_run.eval_run_context.inject_openai_api",
        return_value=None)


@pytest.fixture
def mock_recover_openai(mocker: MockerFixture):
    """Mocks the recover OpenAI API method"""
    return mocker.patch(
        "azure.ai.evaluation._evaluate._batch_run.eval_run_context.recover_openai_api",
        return_value=None)


@pytest.fixture
def mock_ported_inject_openai(mocker: MockerFixture):
    """Mocks the inject OpenAI API method"""
    return mocker.patch(
        "azure.ai.evaluation._evaluate._batch_run.eval_run_context.ported_inject_openai_api",
        return_value=None)


@pytest.fixture
def mock_ported_recover_openai(mocker: MockerFixture):
    """Mocks the recover OpenAI API method"""
    return mocker.patch(
        "azure.ai.evaluation._evaluate._batch_run.eval_run_context.ported_recover_openai_api",
        return_value=None)


@pytest.fixture
def mock_append_user_agent(mocker: MockerFixture):
    """Mocks the append user agent method"""
    patch_target = ("promptflow._utils.user_agent_utils.ClientUserAgentUtil.append_user_agent"
        if HAS_LEGACY_SDK
        else "azure.ai.evaluation._legacy._adapters.utils.ClientUserAgentUtil.append_user_agent"
    )
    return mocker.patch(patch_target, return_value=None)


@pytest.mark.unittest
class TestEvalRunContext:
    def test_with_codeclient(self, mock_append_user_agent, code_client_mock, mock_inject_openai, mock_recover_openai):
        with EvalRunContext(code_client_mock):
            mock_inject_openai.assert_called_once()
            mock_recover_openai.assert_not_called()
            mock_append_user_agent.assert_called_once_with(USER_AGENT)

        mock_recover_openai.assert_called_once()

    def test_with_proxyclient(self, mock_append_user_agent, proxy_client_mock, mock_inject_openai, mock_recover_openai):
        with EvalRunContext(proxy_client_mock):
            mock_append_user_agent.assert_not_called()
            mock_recover_openai.assert_not_called()
            mock_inject_openai.assert_not_called()

        mock_recover_openai.assert_not_called()

    def test_with_runsubmitterclient(self, run_submitter_client_mock, mock_append_user_agent, mock_ported_inject_openai, mock_ported_recover_openai):
        with EvalRunContext(run_submitter_client_mock):
            mock_ported_inject_openai.assert_called_once()
            mock_ported_recover_openai.assert_not_called()
            mock_append_user_agent.assert_not_called()

        mock_ported_inject_openai.assert_called_once()
        mock_ported_recover_openai.assert_called_once()
        mock_append_user_agent.assert_not_called()

    def test_batch_timeout_default(self, proxy_client_mock):
        before_timeout = os.environ.get(PF_BATCH_TIMEOUT_SEC)
        assert before_timeout is None

        with EvalRunContext(proxy_client_mock):
            during_timeout = int(os.environ.get(PF_BATCH_TIMEOUT_SEC))
            assert during_timeout == PF_BATCH_TIMEOUT_SEC_DEFAULT

        # Default timeout should be reset after exiting EvalRunContext
        after_timeout = os.environ.get(PF_BATCH_TIMEOUT_SEC)
        assert after_timeout is None

    @pytest.mark.usefixtures("restore_env_vars")
    def test_batch_timeout_custom(self, proxy_client_mock):
        custom_timeout = 1000
        os.environ[PF_BATCH_TIMEOUT_SEC] = str(custom_timeout)

        with EvalRunContext(proxy_client_mock):
            during_timeout = int(os.environ.get(PF_BATCH_TIMEOUT_SEC))
            assert during_timeout == custom_timeout

        # Custom timeouts should not be reset after exiting EvalRunContext
        after_timeout = int(os.environ.get(PF_BATCH_TIMEOUT_SEC))
        assert after_timeout == custom_timeout
