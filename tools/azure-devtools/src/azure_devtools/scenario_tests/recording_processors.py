# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from copy import deepcopy
from zlib import decompress
import six

from .utilities import is_text_payload, is_json_payload, is_batch_payload, replace_subscription_id


class RecordingProcessor(object):
    def process_request(self, request):  # pylint: disable=no-self-use
        return request

    def process_response(self, response):  # pylint: disable=no-self-use
        return response

    @classmethod
    def replace_header(cls, entity, header, old, new):
        cls.replace_header_fn(entity, header, lambda v: v.replace(old, new))

    @classmethod
    def replace_header_fn(cls, entity, header, replace_fn):
        # Loop over the headers to find the one we want case insensitively,
        # but we don't want to modify the case of original header key.
        for key, values in entity["headers"].items():
            if key.lower() == header.lower():
                if isinstance(values, list):
                    entity["headers"][key] = [replace_fn(v) for v in values]
                else:
                    entity["headers"][key] = replace_fn(values)


class SubscriptionRecordingProcessor(RecordingProcessor):
    def __init__(self, replacement):
        self._replacement = replacement

    def process_request(self, request):
        request.uri = replace_subscription_id(request.uri, replacement=self._replacement)

        if is_text_payload(request) and request.body:
            request.body = replace_subscription_id(request.body.decode(), replacement=self._replacement).encode()

        return request

    def process_response(self, response):
        if is_text_payload(response) and response["body"]["string"]:
            response["body"]["string"] = replace_subscription_id(
                response["body"]["string"], replacement=self._replacement
            )

        self.replace_header_fn(response, "location", replace_subscription_id)
        self.replace_header_fn(response, "azure-asyncoperation", replace_subscription_id)

        try:
            response["url"] = replace_subscription_id(response["url"], replacement=self._replacement)
        except KeyError:
            pass

        return response


class LargeRequestBodyProcessor(RecordingProcessor):
    def __init__(self, max_request_body=128):
        self._max_request_body = max_request_body

    def process_request(self, request):
        if is_text_payload(request) and request.body and len(request.body) > self._max_request_body * 1024:
            request.body = (
                "!!! The request body has been omitted from the recording because its "
                "size {} is larger than {}KB. !!!".format(len(request.body), self._max_request_body)
            )

        return request


class LargeResponseBodyProcessor(RecordingProcessor):
    control_flag = "<CTRL-REPLACE>"

    def __init__(self, max_response_body=128):
        self._max_response_body = max_response_body

    def process_response(self, response):
        if is_text_payload(response):
            length = len(response["body"]["string"] or "")
            if length > self._max_response_body * 1024:

                if is_json_payload(response):
                    from .decorators import AllowLargeResponse  # pylint: disable=cyclic-import

                    raise ValueError(
                        "The json response body exceeds the default limit of {}kb. Use '@{}' "
                        "on your test method to increase the limit or update test logics to avoid "
                        "big payloads".format(self._max_response_body, AllowLargeResponse.__name__)
                    )

                response["body"]["string"] = (
                    "!!! The response body has been omitted from the recording because it is larger "
                    "than {} KB. It will be replaced with blank content of {} bytes while replay. "
                    "{}{}".format(self._max_response_body, length, self.control_flag, length)
                )
        return response


class LargeResponseBodyReplacer(RecordingProcessor):
    def process_response(self, response):
        if is_text_payload(response) and not is_json_payload(response):
            import six

            body = response["body"]["string"]

            # backward compatibility. under 2.7 response body is unicode, under 3.5 response body is
            # bytes. when set the value back, the same type must be used.
            body_is_string = isinstance(body, six.string_types)

            content_in_string = (response["body"]["string"] or b"").decode("utf-8")
            index = content_in_string.find(LargeResponseBodyProcessor.control_flag)

            if index > -1:
                length = int(content_in_string[index + len(LargeResponseBodyProcessor.control_flag) :])
                if body_is_string:
                    response["body"]["string"] = "0" * length
                else:
                    response["body"]["string"] = bytes([0] * length)

        return response


class AuthenticationMetadataFilter(RecordingProcessor):
    """Remove authority and tenant discovery requests and responses from recordings.

    MSAL sends these requests to obtain non-secret metadata about the token authority. Recording them is unnecessary
    because tests use fake credentials during playback that don't invoke MSAL.
    """

    def process_request(self, request):
        if "/.well-known/openid-configuration" in request.uri or "/common/discovery/instance" in request.uri:
            return None
        return request


class OAuthRequestResponsesFilter(RecordingProcessor):
    """Remove oauth authentication requests and responses from recording."""

    def process_request(self, request):
        # filter request like:
        # GET https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47/oauth2/token
        # POST https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47/oauth2/v2.0/token
        import re

        if not re.search("/oauth2(?:/v2.0)?/token", request.uri):
            return request
        return None


class DeploymentNameReplacer(RecordingProcessor):
    """Replace the random deployment name with a fixed mock name."""

    def process_request(self, request):
        import re

        request.uri = re.sub("/deployments/([^/?]+)", "/deployments/mock-deployment", request.uri)
        return request


class AccessTokenReplacer(RecordingProcessor):
    """Replace the access token for service principal authentication in a response body."""

    def __init__(self, replacement="fake_token"):
        self._replacement = replacement

    def process_response(self, response):
        import json

        try:
            body = json.loads(response["body"]["string"])
            body["access_token"] = self._replacement
        except (KeyError, ValueError):
            return response
        response["body"]["string"] = json.dumps(body)
        return response


class GeneralNameReplacer(RecordingProcessor):
    def __init__(self):
        self.names_name = []

    def register_name_pair(self, old, new):
        self.names_name.append((old, new))

    def process_request(self, request):
        for old, new in self.names_name:
            request.uri = request.uri.replace(old, new)

            if is_text_payload(request) and request.body:
                if isinstance(request.body, dict):
                    request.body = self._process_body_as_dict(request.body)
                else:
                    body = six.ensure_str(request.body)
                    if old in body:
                        request.body = body.replace(old, new)

            if request.body and request.uri and is_batch_payload(request):
                import re

                body = six.ensure_str(request.body)
                matched_objects = set(re.findall(old, body))
                for matched_object in matched_objects:
                    request.body = body.replace(matched_object, new)
                    body = body.replace(matched_object, new)

        return request

    def _process_body_as_dict(self, body):
        new_body = deepcopy(body)

        for key in new_body.keys():
            for old, new in self.names_name:
                new_body[key].replace(old, new)

        return new_body

    def process_response(self, response):
        for old, new in self.names_name:
            if is_text_payload(response) and response["body"]["string"]:
                try:
                    response["body"]["string"] = response["body"]["string"].replace(old, new)
                except UnicodeDecodeError:
                    body = response["body"]["string"]
                    response["body"]["string"].decode("utf8", "backslashreplace").replace(old, new).encode(
                        "utf8", "backslashreplace"
                    )
                except TypeError:
                    pass
            self.replace_header(response, "location", old, new)
            self.replace_header(response, "operation-location", old, new)
            self.replace_header(response, "azure-asyncoperation", old, new)
            self.replace_header(response, "www-authenticate", old, new)

        try:
            response["url"] = replace_subscription_id(response["url"])
        except KeyError:
            pass

        try:
            for old, new in self.names_name:
                response["url"].replace(old, new)
        except KeyError:
            pass

            try:
                response["url"] = response["url"].replace(old, new)
            except KeyError:
                pass

        return response


class RequestUrlNormalizer(RecordingProcessor):
    """URL parsing fix to account for '//' vs '/' in different versions of python"""

    def process_request(self, request):
        import re

        request.uri = re.sub("(?<!:)//", "/", request.uri)
        return request
