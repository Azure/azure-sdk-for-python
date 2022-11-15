import re

from azure_devtools.scenario_tests import RecordingProcessor


class XMSRequestIDBody(RecordingProcessor):
    """This process is used for Storage batch call only, to avoid the echo policy."""

    def process_response(self, response):
        content_type = None
        for key, value in response.get("headers", {}).items():
            if key.lower() == "content-type":
                content_type = (value[0] if isinstance(value, list) else value).lower()
                break

        if content_type and "multipart/mixed" in content_type:
            response["body"]["string"] = re.sub(
                b"x-ms-client-request-id: [a-f0-9-]+\r\n",
                b"",
                response["body"]["string"],
            )

        return response
