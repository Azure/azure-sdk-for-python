import random
import string

import openai
import pytest

from azure.ai.generative import AIClient
from azure.ai.generative.entities import Connection
from azure.ai.ml._restclient.v2023_06_01_preview.models import ConnectionAuthType
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities._credentials import ApiKeyConfiguration
from azure.core.exceptions import ResourceNotFoundError


@pytest.mark.e2etest
class TestConnections:
    def test_basic(self, ai_client: AIClient):
        connection_count = 0
        for listed_conn in ai_client.connections.list():
            connection_count = +1
            getted_conn = ai_client.connections.get(listed_conn.name)
            assert listed_conn.name == getted_conn.name
        assert connection_count > 0

    def test_set_keys(self, ai_client: AIClient):
        # TODO fix this test, API keys are never sent to the client, only the credential type.
        # As such, set_current_environment will always fail.
        # Perhaps we can replace this with a locally created connection using a safe dummy key?
        open_hanchi = ai_client.connections.get("open-hanchi")
        open_hanchi.set_current_environment()

        chat_completion = openai.ChatCompletion.create(
            deployment_id="gpt-35-turbo", model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello world"}]
        )

        # print the completion
        print(chat_completion.choices[0].message.content)

    def test_connection_crud_operations(self, ai_client: AIClient):
        # randomize name to avoid stale key name collisions since
        # soft-delete doesn't seem to be fast enough to avoid recycling problems.
        name = "e2etestConnection" + "".join(random.choice(string.digits) for _ in range(10))
        conn_type = "azure_open_ai"
        cred = ApiKeyConfiguration(key="1234567")
        target = "test-target"
        metadata = {"Kind": "dummy", "ApiVersion": "dummy", "ApiType": "dummy"}

        # create empty conn to test setters
        local_conn = Connection(name="overwrite", type="overwrite", credentials=None, target="overwrite")

        local_conn.name = name
        local_conn.type = conn_type
        local_conn.credentials = cred
        local_conn.target = target
        local_conn.metadata = metadata

        first_created_conn = ai_client.connections.create_or_update(local_conn)

        assert first_created_conn.name == name
        assert first_created_conn.type == "azure_open_ai"
        assert first_created_conn.target == "test-target"
        assert first_created_conn.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)
        assert first_created_conn.metadata == {"Kind": "dummy", "ApiVersion": "dummy", "ApiType": "dummy"}

        ai_client.connections.get(name)
        ai_client.connections.delete(name)
        with pytest.raises(ResourceNotFoundError):
            ai_client.connections.get(name)
