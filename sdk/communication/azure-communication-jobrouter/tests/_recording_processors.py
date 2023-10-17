# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
import copy
import re
from azure_devtools.scenario_tests import RecordingProcessor
from azure_devtools.scenario_tests.utilities import (
    is_text_payload,
    _get_content_type
)

from urllib.parse import urlparse, parse_qs, urlencode, quote_plus


def _is_merge_patch_payload(entity):
    router_additional_accepted_content_type = "application/merge-patch+json"
    content_type = _get_content_type(entity)
    return content_type.startswith(router_additional_accepted_content_type)

def _is_text_payload_internal(entity):
    return is_text_payload(entity)

def sanitize_query_params(value,  # type: str
                          exceptions,  # type: List[str]
                          replacement,  # type: str
                          **kwargs):
    parsed_url = urlparse(value)
    qs = parse_qs(parsed_url.query)

    for k in qs.keys():
        if k not in exceptions:
            qs[k] = replacement

    parsed_url = parsed_url._replace(query = urlencode(qs, doseq = True))  # cSpell:disable-line

    return parsed_url.geturl()


class RouterHeaderSanitizer(RecordingProcessor):
    def __init__(self,
                 headers=None,  # type: List[str]
                 replacement="REDACTED"):
        self._headers = headers if headers else []
        self._replacement = replacement

    def process_request(self, request):
        return request

    def process_response(self, response):
        for h in self._headers:
            self.replace_header_fn(response, h, lambda v: self._replacement)
        return response


class RouterQuerySanitizer(RecordingProcessor):
    def __init__(self, exceptions=None, replacement="sanitized"):
        if not exceptions:
            self._exceptions = []
        self._exceptions = exceptions
        self._sanitized_value = replacement

    def process_request(self, request):
        request.uri = sanitize_query_params(request.uri,
                                            exceptions = self._exceptions,
                                            replacement = self._sanitized_value)
        return request

    def process_response(self,
                         response):
        if 'url' in response:
            response['url'] = sanitize_query_params(response['url'],
                                                    exceptions = self._exceptions,
                                                    replacement = self._sanitized_value)
        return response


class RouterURIIdentityReplacer(RecordingProcessor):
    def process_request(self, request):
        request.uri = re.sub('/routing/classificationPolicies/([^/?]+)', '/routing/classificationPolicies/sanitized',
                             request.uri)
        request.uri = re.sub('/routing/distributionPolicies/([^/?]+)', '/routing/distributionPolicies/sanitized',
                             request.uri)
        request.uri = re.sub('/routing/exceptionPolicies/([^/?]+)', '/routing/exceptionPolicies/sanitized',
                             request.uri)
        request.uri = re.sub('/routing/jobs/([^/?]+)', '/routing/jobs/sanitized',
                             request.uri)
        request.uri = re.sub('/offers/([^/?]+):', '/offers/sanitized:',
                             request.uri)
        request.uri = re.sub('/routing/queues/([^/?]+)', '/routing/queues/sanitized',
                             request.uri)
        request.uri = re.sub('/routing/workers/([^/?]+)', '/routing/workers/sanitized',
                             request.uri)
        return request

    def process_response(self, response):
        if 'url' in response:
            response['url'] = re.sub('/routing/classificationPolicies/([^/?]+)',
                                  '/routing/classificationPolicies/sanitized',
                                  response['url'])
            response['url'] = re.sub('/routing/distributionPolicies/([^/?]+)', '/routing/distributionPolicies/sanitized',
                                  response['url'])
            response['url'] = re.sub('/routing/exceptionPolicies/([^/?]+)', '/routing/exceptionPolicies/sanitized',
                                  response['url'])
            response['url'] = re.sub('/routing/jobs/([^/?]+)', '/routing/jobs/sanitized',
                                  response['url'])
            response['url'] = re.sub('/offers/([^/?]+):', '/offers/sanitized:',
                                  response['url'])
            response['url'] = re.sub('/routing/queues/([^/?]+)', '/routing/queues/sanitized',
                                  response['url'])
            response['url'] = re.sub('/routing/workers/([^/?]+)', '/routing/workers/sanitized',
                                  response['url'])
        return response


class RouterScrubber(RecordingProcessor):
    """Sanitize the sensitive info inside request or response bodies"""

    def __init__(self, keys=None, replacement="sanitized", max_depth=16):
        self._replacement = replacement
        self._keys = keys if keys else []
        self.max_depth = max_depth

    def process_request(self, request):
        if _is_text_payload_internal(request) and request.body:
            try:
                body = json.loads(request.body.decode())
            except (KeyError, ValueError) as e:
                raise e

            body = self._scrub(body, 0)
            request.body = json.dumps(body).encode()

        return request

    def process_response(self, response):
        if _is_text_payload_internal(response) and 'body' in response:
            try:
                if isinstance(response['body'], dict) \
                        and 'string' in response['body']:
                    body = response["body"]["string"]

                    if body == b"":
                        return response

                    body_is_string = isinstance(body, str)
                    if body_is_string and body and not body.isspace():
                        body = json.loads(body)

                    body = self._scrub(body, 0)
                    response["body"]["string"] = json.dumps(body).encode('utf-8')
            except (KeyError, ValueError) as e:
                raise e

        return response

    def _scrub(self, x, depth):
        if depth > self.max_depth:
            raise ValueError("Max depth reached")

        ret = copy.deepcopy(x)
        # Handle dictionaries, lits & tuples. Scrub all values
        if isinstance(x, dict):
            for k, v in ret.items():
                if k in self._keys:
                    ret[k] = self._replacement
                else:
                    ret[k] = self._scrub(v, depth + 1)
        if isinstance(x, (list, tuple)):
            for k, v in enumerate(ret):
                ret[k] = self._scrub(v, depth + 1)

        # Finished scrubbing
        return ret

