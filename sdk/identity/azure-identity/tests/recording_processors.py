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

from helpers import FAKE_CLIENT_ID

ID_TOKEN_PII_CLAIMS = ("email", "name", "preferred_username", "unique_name")

SECRET_FIELDS = frozenset(
    {
        "access_token",
        "client_secret",
        "code",
        "device_code",
        "message",
        "password",
        "refresh_token",
        "user_code",
    }
)

# managed identity headers are not dangerous to record but redacting them prevents anyone worrying whether they are
SECRET_HEADERS = frozenset(
    {
        "secret",
        "X-IDENTITY-SECRET",
    }
)


def set_jwt_claims(jwt, claims):
    header, encoded_payload, signed = jwt.split(".")
    decoded_payload = base64.b64decode(encoded_payload + "=" * (-len(encoded_payload) % 4))

    payload = json.loads(six.ensure_str(decoded_payload))
    for name, value in claims:
        if name in payload:
            payload[name] = value

    new_payload = six.ensure_binary(json.dumps(payload))
    return ".".join((header, base64.b64encode(new_payload).decode("utf-8"), signed))


class RecordingRedactor(RecordingProcessor):
    """Removes authentication secrets from recordings.

    :keyword bool record_unique_values: Defaults to False. Set True for tests requiring unique, consistent fake values.
    """

    def __init__(self, record_unique_values=False):
        super(RecordingRedactor, self).__init__()
        self._record_unique_values = record_unique_values

    def process_request(self, request):
        # bodies typically contain secrets and are often formed by msal anyway, i.e. not this library's responsibility
        request.body = None

        for header in SECRET_HEADERS:
            if header in request.headers:
                fake_value = self._get_fake_value(request.headers[header])
                request.headers[header] = fake_value

        return request

    def process_response(self, response):
        try:
            body = json.loads(response["body"]["string"])
        except (KeyError, ValueError):
            return response

        for field in body:
            if field == "id_token":
                scrubbed = set_jwt_claims(body["id_token"], [(claim, "redacted") for claim in ID_TOKEN_PII_CLAIMS])
                body["id_token"] = scrubbed
            elif field in SECRET_FIELDS:
                fake_value = self._get_fake_value(body[field])
                body[field] = fake_value

        response["body"]["string"] = json.dumps(body)
        return response

    def _get_fake_value(self, real_value):
        redacted_value = "redacted"
        if self._record_unique_values:
            digest = hashlib.sha256(six.ensure_binary(real_value)).digest()
            redacted_value += six.ensure_str(binascii.hexlify(digest))[:6]
        return redacted_value


class IdTokenProcessor(RecordingProcessor):
    def process_response(self, response):
        """Modifies an id token's claims to pass MSAL validation during playback"""
        try:
            body = json.loads(six.ensure_str(response["body"]["string"]))
            new_jwt = set_jwt_claims(body["id_token"], [("exp", int(time.time()) + 3600), ("aud", FAKE_CLIENT_ID)])
            body["id_token"] = new_jwt
            response["body"]["string"] = six.ensure_binary(json.dumps(body))
        except KeyError:
            pass

        return response
