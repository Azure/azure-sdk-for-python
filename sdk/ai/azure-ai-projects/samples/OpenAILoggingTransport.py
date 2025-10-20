import httpx
class OpenAILoggingTransport(httpx.HTTPTransport):
                def _sanitize_auth_header(self, headers):
                    """Sanitize authorization header by redacting sensitive information."""

                    if "authorization" in headers:
                        auth_value = headers["authorization"]
                        if len(auth_value) >= 7:
                            headers["authorization"] = auth_value[:7] + "<REDACTED>"
                        else:
                            headers["authorization"] = "<ERROR>"

                def handle_request(self, request):
                    """
                    Log HTTP request and response details to console, in a nicely formatted way,
                    for OpenAI / Azure OpenAI clients.

                    To use, add `http_client=httpx.Client(transport=OpenAILoggingTransport())` to the client
                    constructor.
                    """

                    print(f"\n==> Request:\n{request.method} {request.url}")
                    headers = dict(request.headers)
                    self._sanitize_auth_header(headers)
                    print("Headers:")
                    for key, value in headers.items():
                        print(f"  {key}: {value}")
                    if request.content:
                        try:
                            print(f"Body:\n  {request.content.decode('utf-8')}")
                        except Exception:
                            print(f"Body (raw):\n  {request.content}")

                    response = super().handle_request(request)

                    print(f"\n<== Response:\n{response.status_code} {response.reason_phrase}")
                    print("Headers:")
                    for key, value in dict(response.headers).items():
                        print(f"  {key}: {value}")
                    try:
                        print(f"Body:\n {response.read().decode('utf-8')}")
                    except Exception:
                        print("Body:\n  [non-text content]")
                    print("\n")

                    return response
 