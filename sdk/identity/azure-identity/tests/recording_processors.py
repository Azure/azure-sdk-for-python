# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
import binascii
import hashlib
import json
import time

from azure_devtools.scenario_tests import RecordingProcessor
import six


SECRETS = frozenset({
    "access_token",
    "client_secret",
    "code",
    "device_code",
    "message",
    "password",
    "refresh_token",
    "user_code",
})


class RecordingRedactor(RecordingProcessor):
    """Removes authentication secrets from recordings.

    :keyword bool record_unique_values:
    """

    def __init__(self, record_unique_values=False):
        super(RecordingRedactor, self).__init__()
        self._record_unique_values = record_unique_values

    def process_request(self, request):
        # bodies typically contain secrets and are often formed by msal anyway, i.e. not this library's responsibility
        request.body = None
        return request

    def process_response(self, response):
        try:
            body = json.loads(response["body"]["string"])
        except (KeyError, ValueError):
            return response

        for field in body:
            if field in SECRETS:
                redacted_value = "redacted"
                if self._record_unique_values:
                    # include a hash of the secret instead of a simple replacement
                    # because some tests (e.g. for CAE) require unique, consistent values
                    digest = hashlib.sha256(six.ensure_binary(body[field])).digest()
                    redacted_value += six.ensure_str(binascii.hexlify(digest))[:6]
                body[field] = redacted_value

        response["body"]["string"] = json.dumps(body)
        return response


class IdTokenProcessor(RecordingProcessor):
    def process_response(self, response):
        """Changes the "exp" claim of recorded id tokens to be in the future during playback

        This is necessary because msal always validates id tokens, raising an exception when they've expired.
        """
        try:
            # decode the recorded token
            body = json.loads(six.ensure_str(response["body"]["string"]))
            header, encoded_payload, signed = body["id_token"].split(".")
            decoded_payload = base64.b64decode(encoded_payload + "=" * (4 - len(encoded_payload) % 4))

            # set the token's expiry time to one hour from now
            payload = json.loads(six.ensure_str(decoded_payload))
            payload["exp"] = int(time.time()) + 3600

            # write the modified token to the response body
            new_payload = six.ensure_binary(json.dumps(payload))
            body["id_token"] = ".".join((header, base64.b64encode(new_payload).decode("utf-8"), signed))
            response["body"]["string"] = six.ensure_binary(json.dumps(body))
        except KeyError:
            pass

        return response
