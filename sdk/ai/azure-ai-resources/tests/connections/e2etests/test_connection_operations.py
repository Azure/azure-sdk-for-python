import random
import string

import pytest

from azure.ai.resources.client import AIClient
from azure.ai.resources.entities import AzureOpenAIConnection, AzureAISearchConnection, AzureAIServiceConnection
from azure.ai.ml._restclient.v2023_06_01_preview.models import ConnectionAuthType
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities._credentials import ApiKeyConfiguration
from azure.core.exceptions import ResourceNotFoundError


@pytest.mark.e2etest
class TestConnections:
    def test_get_and_list(self, ai_client_with_ai_access: AIClient):
        connection_count = 0
        for listed_conn in ai_client_with_ai_access.connections.list():
            connection_count = +1
            getted_conn = ai_client_with_ai_access.connections.get(listed_conn.name)
            assert listed_conn.name == getted_conn.name
        assert connection_count > 0


    def test_get_default_connections(self, ai_client_with_ai_access: AIClient):
        aoai_conn = ai_client_with_ai_access.get_default_aoai_connection()
        assert aoai_conn is not None
        
        content_safety_conn = ai_client_with_ai_access.get_default_content_safety_connection()
        assert content_safety_conn is not None


    def test_aoai_create_and_delete(self, ai_client_with_ai_access: AIClient):
        # randomize name to avoid stale key name collisions since
        # soft-delete doesn't seem to be fast enough to avoid recycling problems.
        name = "e2etestConnection" + "".join(random.choice(string.digits) for _ in range(10))
        conn_type = "azure_open_ai"
        cred = ApiKeyConfiguration(key="1234567")
        target = "test-target"

        # create empty conn to test setters
        local_conn = AzureOpenAIConnection(name="overwrite", type="overwrite", credentials=None, target="overwrite")

        local_conn.name = name
        local_conn.type = conn_type
        local_conn.credentials = cred
        local_conn.target = target

        first_created_conn = ai_client_with_ai_access.connections.create_or_update(local_conn)

        assert first_created_conn.name == name
        assert first_created_conn.type == "azure_open_ai"
        assert first_created_conn.target == "test-target"
        assert first_created_conn.credentials.type == camel_to_snake(ConnectionAuthType.API_KEY)

        ai_client_with_ai_access.connections.get(name)
        ai_client_with_ai_access.connections.delete(name)
        with pytest.raises(ResourceNotFoundError):
            ai_client_with_ai_access.connections.get(name)
        import pdb; pdb.set_trace()