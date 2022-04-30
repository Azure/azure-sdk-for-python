# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure_devtools.scenario_tests import RecordingProcessor

from urllib.parse import urlparse, parse_qs, urlencode, quote_plus


def sanitize_query_params(value,  # type: str
                          exceptions,  # type: List[str]
                          replacement,  # type: str
                          **kwargs):
    parsed_url = urlparse(value)
    qs = parse_qs(parsed_url.query)

    for k in qs.keys():
        if k not in exceptions:
            qs[k] = replacement

    parsed_url = parsed_url._replace(query = urlencode(qs, doseq = True))

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
        import re
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
        import re

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
