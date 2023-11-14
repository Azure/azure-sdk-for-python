import random
import string

import openai
import pytest

from azure.ai.resources.entities import AzureOpenAIConnection, AzureAISearchConnection, AzureAIServiceConnection
from azure.ai.ml._restclient.v2023_06_01_preview.models import ConnectionAuthType
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities._credentials import ApiKeyConfiguration
from azure.core.exceptions import ResourceNotFoundError


@pytest.mark.e2etest
class TestConnections:



    def test_aoai_entity(self):
        pass


    def test_search_entity(self):
        pass

    
    def test_service_entity(self):
        pass
 
    # TODO move to unit tests
    def test_set_keys(self):
        # TODO fix this test, API keys are never sent to the client, only the credential type.
        # As such, set_current_environment will always fail.
        # Perhaps we can replace this with a locally created connection using a safe dummy key?
        open_hanchi = AzureOpenAIConnection(name="tempConn", credential=ApiKeyConfiguration(key="7474"))
        open_hanchi.set_current_environment()

        chat_completion = openai.ChatCompletion.create(
            deployment_id="gpt-35-turbo", model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello world"}]
        )

        # print the completion
        print(chat_completion.choices[0].message.content)