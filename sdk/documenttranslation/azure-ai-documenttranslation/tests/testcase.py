# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import time
import datetime
from devtools_testutils import (
    AzureTestCase,
)
from azure_devtools.scenario_tests import (
    RecordingProcessor,
    ReplayableTest
)
from azure.storage.blob import generate_container_sas


class OperationLocationReplacer(RecordingProcessor):
    """Replace the location/operation location uri in a request/response body."""

    def __init__(self):
        self._replacement = "https://redacted.cognitiveservices.azure.com/translator"

    def process_response(self, response):
        try:
            headers = response['headers']
            if 'operation-location' in headers:
                location_header = "operation-location"
                if isinstance(headers[location_header], list):
                    suffix = headers[location_header][0].split("/translator/")[1]
                    response['headers'][location_header] = [self._replacement + suffix]
                else:
                    suffix = headers[location_header].split("/translator/")[1]
                    response['headers'][location_header] = self._replacement + suffix
            url = response["url"]
            if url is not None:
                suffix = url.split("/translator/")[1]
                response['url'] = self._replacement + suffix
            return response
        except (KeyError, ValueError):
            return response


class DocumentTranslationTest(AzureTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['Ocp-Apim-Subscription-Key']

    def __init__(self, method_name):
        super(DocumentTranslationTest, self).__init__(method_name)
        self.vcr.match_on = ["path", "method", "query"]
        self.recording_processors.append(OperationLocationReplacer())
        self.generate_sas()

    def generate_sas(self):
        source_url = os.getenv("DOCUMENTTRANSLATION_SOURCE_CONTAINER_URL")
        source_storage_name = os.getenv("DOCUMENTTRANSLATION_SOURCE_STORAGE_NAME")
        source_storage_key = os.getenv("DOCUMENTTRANSLATION_SOURCE_STORAGE_KEY")
        source_container_name = os.getenv("DOCUMENTTRANSLATION_SOURCE_CONTAINER_NAME")

        source_sas = generate_container_sas(
            source_storage_name,
            source_container_name,
            account_key=source_storage_key,
            permission="rl",
            expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        )

        target_url = os.getenv("DOCUMENTTRANSLATION_TARGET_CONTAINER_URL")
        target_storage_name = os.getenv("DOCUMENTTRANSLATION_TARGET_STORAGE_NAME")
        target_storage_key = os.getenv("DOCUMENTTRANSLATION_TARGET_STORAGE_KEY")
        target_container_name = os.getenv("DOCUMENTTRANSLATION_TARGET_CONTAINER_NAME")

        target_sas = generate_container_sas(
            target_storage_name,
            target_container_name,
            account_key=target_storage_key,
            permission="racwdl",
            expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        )

        self.source_container_sas_url = source_url + "?" + source_sas
        self.target_container_sas_url = target_url + "?" + target_sas

        self.scrubber.register_name_pair(
            self.source_container_sas_url, "source_container_sas_url"
        )
        self.scrubber.register_name_pair(
            self.target_container_sas_url, "target_container_sas_url"
        )

    def wait(self):
        if self.is_live:
            time.sleep(10)
