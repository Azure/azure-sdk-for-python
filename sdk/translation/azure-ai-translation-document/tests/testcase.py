# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import time
import datetime
import uuid
from devtools_testutils import AzureRecordedTestCase, set_custom_default_matcher
from azure.storage.blob import generate_container_sas, ContainerClient
from azure.ai.translation.document import DocumentTranslationInput, TranslationTarget


class Document:
    """Represents a document to be uploaded to source/target container"""

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", str(uuid.uuid4()))
        self.suffix = kwargs.get("suffix", ".txt")
        self.prefix = kwargs.get("prefix", "")
        self.data = kwargs.get("data", b"This is written in english.")

    @classmethod
    def create_dummy_docs(cls, docs_count):
        result = []
        for i in range(docs_count):
            result.append(cls())
        return result


class DocumentTranslationTest(AzureRecordedTestCase):
    @property
    def storage_name(self):
        return os.getenv("TRANSLATION_DOCUMENT_STORAGE_NAME", "redacted")

    @property
    def storage_endpoint(self):
        return "https://" + self.storage_name + ".blob.core.windows.net/"

    @property
    def storage_key(self):
        return os.getenv("TRANSLATION_DOCUMENT_STORAGE_KEY", "fakeZmFrZV9hY29jdW50X2tleQ==")

    def upload_documents(self, data, container_client):
        if isinstance(data, list):
            for blob in data:
                container_client.upload_blob(name=blob.prefix + blob.name + blob.suffix, data=blob.data)
        else:
            container_client.upload_blob(name=data.prefix + data.name + data.suffix, data=data.data)

    def create_source_container(self, data, variables={}, **kwargs):
        container_suffix = kwargs.get("container_suffix", "")
        var_key = "source_container_name" + container_suffix
        if self.is_live:
            self.source_container_name = variables[var_key] = "src" + str(uuid.uuid4())
            container_client = ContainerClient(self.storage_endpoint, variables[var_key], self.storage_key)
            container_client.create_container()

            self.upload_documents(data, container_client)
        return self.generate_sas_url(variables[var_key], "rl")

    def create_target_container(self, data=None, variables={}, **kwargs):
        container_suffix = kwargs.get("container_suffix", "")
        var_key = "target_container_name" + container_suffix
        if self.is_live:
            self.target_container_name = variables[var_key] = "target" + str(uuid.uuid4())
            container_client = ContainerClient(self.storage_endpoint, variables[var_key], self.storage_key)
            container_client.create_container()
            if data:
                self.upload_documents(data, container_client)

        return self.generate_sas_url(variables[var_key], "wl")

    def generate_sas_url(self, container_name, permission):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        sas_token = self.generate_sas(
            generate_container_sas,
            account_name=self.storage_name,
            container_name=container_name,
            account_key=self.storage_key,
            permission=permission,
            expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=2),
        )

        container_sas_url = self.storage_endpoint + container_name + "?" + sas_token
        return container_sas_url

    def wait(self, duration=30):
        if self.is_live:
            time.sleep(duration)

    # model helpers
    def _validate_doc_status(self, doc_details, target_language=None, **kwargs):
        status = kwargs.pop("statuses", ["Succeeded"])
        ids = kwargs.pop("ids", None)
        # specific assertions
        assert doc_details.status in status
        if self.is_live and target_language:
            assert doc_details.translated_to == target_language
        # generic assertions
        if ids:
            assert doc_details.id in ids
        else:
            assert doc_details.id is not None
        assert doc_details.id is not None
        assert doc_details.source_document_url is not None
        assert doc_details.translated_document_url is not None
        assert doc_details.translation_progress is not None
        assert doc_details.characters_charged is not None
        assert doc_details.created_on is not None
        assert doc_details.last_updated_on is not None

    def _validate_translation_metadata(self, poller, **kwargs):
        status = kwargs.pop("status", None)
        total = kwargs.pop("total", None)
        failed = kwargs.pop("failed", None)
        succeeded = kwargs.pop("succeeded", None)
        inprogress = kwargs.pop("inprogress", None)
        notstarted = kwargs.pop("notstarted", None)
        canceled = kwargs.pop("canceled", None)

        # status
        p = poller.status()
        if status:
            assert poller.status() == status
        # docs count

        if poller.done():
            if total:
                assert poller.details.documents_total_count == total
            else:
                assert poller.details.documents_total_count is not None
            if failed:
                assert poller.details.documents_failed_count == failed
            else:
                assert poller.details.documents_failed_count is not None
            if succeeded:
                assert poller.details.documents_succeeded_count == succeeded
            else:
                assert poller.details.documents_succeeded_count is not None
            if inprogress:
                assert poller.details.documents_in_progress_count == inprogress
            else:
                assert poller.details.documents_in_progress_count is not None
            if notstarted:
                assert poller.details.documents_not_started_count == notstarted
            else:
                assert poller.details.documents_not_started_count is not None
            if canceled:
                assert poller.details.documents_canceled_count == canceled
            else:
                assert poller.details.documents_canceled_count is not None

            # generic assertions
            assert poller.details.id is not None
            assert poller.details.created_on is not None
            assert poller.details.last_updated_on is not None
            assert poller.details.total_characters_charged is not None

    def _validate_translations(self, job_details, **kwargs):
        status = kwargs.pop("status", None)
        total = kwargs.pop("total", None)
        failed = kwargs.pop("failed", None)
        succeeded = kwargs.pop("succeeded", None)
        inprogress = kwargs.pop("inprogress", None)
        notstarted = kwargs.pop("notstarted", None)
        canceled = kwargs.pop("canceled", None)

        # status
        if status:
            assert job_details.status == status
        else:
            assert job_details.status is not None
        # docs count

        if total:
            assert job_details.documents_total_count == total
        else:
            assert job_details.documents_total_count is not None
        if failed:
            assert job_details.documents_failed_count == failed
        else:
            assert job_details.documents_failed_count is not None
        if succeeded:
            assert job_details.documents_succeeded_count == succeeded
        else:
            assert job_details.documents_succeeded_count is not None
        if inprogress:
            assert job_details.documents_in_progress_count == inprogress
        else:
            assert job_details.documents_in_progress_count is not None
        if notstarted:
            assert job_details.documents_not_started_count == notstarted
        else:
            assert job_details.documents_not_started_count is not None
        if canceled:
            assert job_details.documents_canceled_count == canceled
        else:
            assert job_details.documents_canceled_count is not None

        # generic assertions
        assert job_details.id is not None
        assert job_details.created_on is not None
        assert job_details.last_updated_on is not None
        assert job_details.total_characters_charged is not None

    def _validate_format(self, format):
        assert format.file_format is not None
        assert format.file_extensions is not None
        assert format.content_types is not None

    # client helpers
    def _begin_and_validate_translation(self, client, translation_inputs, total_docs_count, language=None, **kwargs):
        wait_for_operation = kwargs.pop("wait", True)
        # submit job
        poller = client.begin_translation(translation_inputs)
        assert poller.id is not None
        # wait for result
        if wait_for_operation:
            result = poller.result()
            for doc in result:
                self._validate_doc_status(doc, language)

        assert poller.details.id is not None

        # validate
        self._validate_translation_metadata(
            poller=poller, status="Succeeded", total=total_docs_count, succeeded=total_docs_count
        )

        return poller.id

    def _begin_multiple_translations(self, client, operations_count, **kwargs):
        container_suffix = kwargs.pop("container_suffix", "")
        variables = kwargs.pop("variables", {})
        wait_for_operation = kwargs.pop("wait", True)
        language = kwargs.pop("language", "es")
        docs_per_operation = kwargs.pop("docs_per_operation", 2)
        result_job_ids = []
        for i in range(operations_count):
            # prepare containers and test data
            blob_data = Document.create_dummy_docs(docs_per_operation)
            source_container_sas_url = self.create_source_container(
                data=blob_data, variables=variables, container_suffix=str(i) + container_suffix
            )
            target_container_sas_url = self.create_target_container(
                variables=variables, container_suffix=str(i) + container_suffix
            )

            # prepare translation inputs
            translation_inputs = [
                DocumentTranslationInput(
                    source_url=source_container_sas_url,
                    targets=[TranslationTarget(target_url=target_container_sas_url, language=language)],
                )
            ]

            # submit multiple jobs
            poller = client.begin_translation(translation_inputs)
            assert poller.id is not None
            if wait_for_operation:
                result = poller.result()
            else:
                poller.wait()
            result_job_ids.append(poller.id)

        return result_job_ids

    def _begin_and_validate_translation_with_multiple_docs(self, client, docs_count, **kwargs):
        # get input params
        wait_for_operation = kwargs.pop("wait", False)
        variables = kwargs.get("variables", {})
        language = kwargs.pop("language", "es")

        # prepare containers and test data
        blob_data = Document.create_dummy_docs(docs_count=docs_count)
        source_container_sas_url = self.create_source_container(data=blob_data, variables=variables)
        target_container_sas_url = self.create_target_container(variables=variables)

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[TranslationTarget(target_url=target_container_sas_url, language=language)],
            )
        ]

        # submit job
        poller = client.begin_translation(translation_inputs)
        assert poller.id is not None
        # wait for result
        if wait_for_operation:
            result = poller.result()
            for doc in result:
                self._validate_doc_status(doc, "es")
        # validate
        self._validate_translation_metadata(poller=poller)

        return poller
