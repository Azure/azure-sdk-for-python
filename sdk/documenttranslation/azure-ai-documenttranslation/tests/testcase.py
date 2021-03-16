# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import time
import datetime
import uuid
from devtools_testutils import (
    AzureTestCase,
)
from azure_devtools.scenario_tests import (
    RecordingProcessor,
    ReplayableTest
)
from azure.storage.blob import generate_container_sas, ContainerClient


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
        self.storage_name = os.getenv("DOCUMENTTRANSLATION_STORAGE_NAME", "redacted")
        self.storage_endpoint = "https://" + self.storage_name + ".blob.core.windows.net/"
        self.storage_key = os.getenv("DOCUMENTTRANSLATION_STORAGE_KEY")
        self.scrubber.register_name_pair(
            self.storage_endpoint, "https://redacted.blob.core.windows.net/"
        )
        self.scrubber.register_name_pair(
            self.storage_name, "redacted"
        )
        self.scrubber.register_name_pair(
            self.storage_key, "fakeZmFrZV9hY29jdW50X2tleQ=="
        )

    def _setup(self, data=None, blob_prefix=""):
        """Creates a source and target container.

        Pass data in as bytes (or as a list[bytes] to create more than one blob) in the source container.
        """
        if self.is_live:
            self.source_container_sas_url = self.create_source_container(
                data=data or b'This is written in english.',
                blob_prefix=blob_prefix
            )
            self.target_container_sas_url = self.create_target_container()
        else:
            self.source_container_sas_url = "source_container_sas_url"
            self.target_container_sas_url = "target_container_sas_url"

    def create_source_container(self, data, blob_prefix=""):
        container_name = "src" + str(uuid.uuid4())
        container_client = ContainerClient(self.storage_endpoint, container_name,
                                           self.storage_key)
        container_client.create_container()
        if isinstance(data, list):
            for blob in data:
                container_client.upload_blob(name=blob_prefix+str(uuid.uuid4()) + ".txt", data=blob)
        else:
            container_client.upload_blob(name=blob_prefix+str(uuid.uuid4())+".txt", data=data)
        return self.generate_sas_url(container_name, "rl")

    def create_target_container(self):
        container_name = "target" + str(uuid.uuid4())
        container_client = ContainerClient(self.storage_endpoint, container_name,
                                           self.storage_key)
        container_client.create_container()

        return self.generate_sas_url(container_name, "racwdl")

    def generate_sas_url(self, container_name, permission):

        sas_token = self.generate_sas(
            generate_container_sas,
            account_name=self.storage_name,
            container_name=container_name,
            account_key=self.storage_key,
            permission=permission,
            expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        )

        container_sas_url = self.storage_endpoint + container_name + "?" + sas_token
        return container_sas_url

    def wait(self):
        if self.is_live:
            time.sleep(30)
