import pytest
import unittest
from unittest.mock import Mock, patch

from azure.ai.resources.entities import AzureOpenAIConnection
from azure.ai.ml.entities._credentials import ApiKeyConfiguration


@pytest.mark.unittest
class TestConnection:

    @pytest.fixture()
    def mock_credentials(self):
        mock_credentials = Mock()
        mock_token = Mock()
        mock_credentials.get_token.return_value = mock_token
        mock_token.token = "my-aad-token"
        return mock_credentials

    @patch("importlib.metadata.version")
    @patch("os.environ")
    def test_set_environment(self, mock_os_environ, mock_get_version, mock_credentials):
        mock_get_version.return_value = "0.28.1"
        connection = AzureOpenAIConnection(name="my-connection", target="https://test.com", credentials=ApiKeyConfiguration(key="abc"), api_version="2021-01-01")

        connection.set_current_environment()
        assert mock_os_environ.__setitem__.call_count == 4
        assert mock_os_environ.__setitem__.call_args_list[0][0] == ("OPENAI_API_KEY", "abc")
        assert mock_os_environ.__setitem__.call_args_list[1][0] == ("OPENAI_API_TYPE", "azure")
        assert mock_os_environ.__setitem__.call_args_list[2][0] == ("OPENAI_API_BASE", "https://test.com")
        assert mock_os_environ.__setitem__.call_args_list[3][0] == ("OPENAI_API_VERSION", "2021-01-01")

        connection.set_current_environment(mock_credentials)
        assert mock_os_environ.__setitem__.call_count == 8 
        assert mock_os_environ.__setitem__.call_args_list[4][0] == ("OPENAI_API_TYPE", "azure_ad")
        assert mock_os_environ.__setitem__.call_args_list[5][0] == ("OPENAI_API_KEY", "my-aad-token")
        assert mock_os_environ.__setitem__.call_args_list[6][0] == ("OPENAI_API_BASE", "https://test.com")
        assert mock_os_environ.__setitem__.call_args_list[7][0] == ("OPENAI_API_VERSION", "2021-01-01")


    @patch("importlib.metadata.version")
    @patch("os.environ")
    def test_set_environment_100(self, mock_os_environ, mock_get_version, mock_credentials):
        mock_get_version.return_value = "1.0.0"
        connection = AzureOpenAIConnection(name="my-connection", target="https://test.com", credentials=ApiKeyConfiguration(key="abc"), api_version="2021-01-01")

        connection.set_current_environment()
        # This is a hacky way to verity os.environ, any better way?
        assert mock_os_environ.__setitem__.call_count == 3
        # call_args[0] is args, call_args[1] is kwargs
        assert mock_os_environ.__setitem__.call_args_list[0][0] == ("AZURE_OPENAI_API_KEY", "abc")
        assert mock_os_environ.__setitem__.call_args_list[1][0] == ("OPENAI_API_VERSION", "2021-01-01")
        assert mock_os_environ.__setitem__.call_args_list[2][0] == ("AZURE_OPENAI_ENDPOINT", "https://test.com")

        connection.set_current_environment(mock_credentials)
        assert mock_os_environ.__setitem__.call_count == 6
        assert mock_os_environ.__setitem__.call_args_list[3][0] == ("AZURE_OPENAI_AD_TOKEN", "my-aad-token")
        assert mock_os_environ.__setitem__.call_args_list[4][0] == ("OPENAI_API_VERSION", "2021-01-01")
        assert mock_os_environ.__setitem__.call_args_list[5][0] == ("AZURE_OPENAI_ENDPOINT", "https://test.com")
