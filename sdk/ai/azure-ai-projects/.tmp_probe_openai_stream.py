import httpx
from openai import OpenAI


class ProbeTransport(httpx.BaseTransport):
    def handle_request(self, request: httpx.Request) -> httpx.Response:
        print("METHOD", request.method)
        print("URL", request.url)
        print("HEADERS", dict(request.headers))
        print("EXTENSIONS", request.extensions)
        raise RuntimeError("stop after probe")


client = OpenAI(
    api_key="x", base_url="https://example.com/openai/v1", http_client=httpx.Client(transport=ProbeTransport())
)
try:
    with client.responses.create(model="gpt-4o", input="hello", stream=True) as stream:
        pass
except Exception as exc:
    print(type(exc).__name__, exc)
