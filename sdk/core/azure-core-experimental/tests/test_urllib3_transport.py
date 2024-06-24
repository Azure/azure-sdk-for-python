import urllib3
import pytest
import io

from azure.core.exceptions import ServiceRequestError
from azure.core.experimental.transport import Urllib3Transport
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import RetryPolicy
from azure.core.rest import HttpRequest

PLACEHOLDER_ENDPOINT = "https://my-resource-group.cognitiveservices.azure.com/"


def mock_successful_post() -> urllib3.response.HTTPResponse:
    return urllib3.response.HTTPResponse(status=200, body=io.BytesIO(b"Hello, world!"), preload_content=False)


class TestUrllib3Transport:

    def test_send_success(self) -> None:
        class MockPoolManager(urllib3.PoolManager):
            def urlopen(*args, **kwargs):
                return mock_successful_post()

        transport = Urllib3Transport(pool=MockPoolManager())
        pipeline = Pipeline(transport, [RetryPolicy()])
        method = "POST"
        headers = {"key": "value"}
        content = b"hello"
        request = HttpRequest(method=method, url=PLACEHOLDER_ENDPOINT, headers=headers, content=content)
        response = (pipeline.run(request=request)).http_response
        expected = mock_successful_post()
        assert response.body() == expected.data
        assert response.status_code == expected.status
        assert response.reason == expected.reason

    def test_exception(self) -> None:
        class MockPoolManager(urllib3.PoolManager):
            def urlopen(*args, **kwargs):
                raise urllib3.exceptions.ConnectTimeoutError("connection timed out")

        transport = Urllib3Transport(pool=MockPoolManager())
        pipeline = Pipeline(transport, [RetryPolicy()])
        request = HttpRequest(method="GET", url=PLACEHOLDER_ENDPOINT)
        with pytest.raises(ServiceRequestError) as ex:
            pipeline.run(request=request)
            assert ex.value == "connection timed out"
