# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
import pytest
import uuid
from azure.core.exceptions import HttpResponseError
from azure.storage.blob import ContainerClient
from testcase import DocumentTranslationTest
from preparer import DocumentTranslationPreparer, \
    DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.documenttranslation import DocumentTranslationClient, DocumentTranslationInput, TranslationTarget
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestTranslation(DocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_single_source_single_target(self, client):
        # prepare containers and test data
        blob_data = b'This is some text'
        source_container_sas_url = self.create_source_container(data=blob_data)
        target_container_sas_url = self.create_target_container()

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code="es"
                    )
                ]
            )
        ]

        # submit job and test
        self._submit_and_validate_translation_job(client, translation_inputs, 1)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_single_source_two_targets(self, client):
        # prepare containers and test data
        blob_data = b'This is some text'
        source_container_sas_url = self.create_source_container(data=blob_data)
        target_container_sas_url = self.create_target_container()
        additional_target_container_sas_url = self.create_target_container()

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code="es"
                    ),
                    TranslationTarget(
                        target_url=additional_target_container_sas_url,
                        language_code="fr"
                    )
                ]
            )
        ]

        # submit job and test
        self._submit_and_validate_translation_job(client, translation_inputs, 2)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_multiple_sources_single_target(self, client):
        # prepare containers and test data
        blob_data = b'This is some text'
        source_container_sas_url = self.create_source_container(data=blob_data)
        blob_data = b'This is some text2'
        additional_source_container_sas_url = self.create_source_container(data=blob_data)
        target_container_sas_url = self.create_target_container()

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code="es"
                    )
                ]
            ),
            DocumentTranslationInput(
                source_url=additional_source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code="fr"
                    )
                ]
            )
        ]

        # submit job and test
        self._submit_and_validate_translation_job(client, translation_inputs, 2)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_single_source_single_target_with_prefix(self, client):
        # prepare containers and test data
        blob_data = b'This is some text'
        prefix = "xyz"
        source_container_sas_url = self.create_source_container(data=blob_data, blob_prefix=prefix)
        target_container_sas_url = self.create_target_container()

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code="es"
                    )
                ],
                prefix=prefix
            )
        ]

        # submit job and test
        self._submit_and_validate_translation_job(client, translation_inputs, 1)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_single_source_single_target_with_suffix(self, client):
        # prepare containers and test data
        blob_data = b'This is some text'
        suffix = "txt"
        source_container_sas_url = self.create_source_container(data=blob_data)
        target_container_sas_url = self.create_target_container()

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code="es"
                    )
                ],
                suffix=suffix
            )
        ]

        # submit job and test
        self._submit_and_validate_translation_job(client, translation_inputs, 1)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_bad_input_source(self, client):
        # prepare containers and test data
        target_container_sas_url = self.create_target_container()

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url="https://idont.ex.ist",
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code="es"
                    )
                ]
            )
        ]

        with pytest.raises(HttpResponseError) as e:
            job = client.create_translation_job(translation_inputs)
            job = client.wait_until_done(job.id)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_bad_input_target(self, client):
        # prepare containers and test data
        blob_data = b'This is some text'
        source_container_sas_url = self.create_source_container(data=blob_data)

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url="https://idont.ex.ist",
                        language_code="es"
                    )
                ]
            )
        ]

        with pytest.raises(HttpResponseError) as e:
            job = client.create_translation_job(translation_inputs)
            job = client.wait_until_done(job.id)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_use_supported_and_unsupported_files(self, client):
        # prepare containers and test data
        blob_data = b'This is some text'
        source_container_sas_url = self.create_target_container()  # has the permissions to add
        target_container_sas_url = self.create_target_container()

        if self.is_live:
            container_client = ContainerClient.from_container_url(source_container_sas_url)
            container_client.upload_blob(name=str(uuid.uuid4()) + ".txt", data=blob_data)
            container_client.upload_blob(name=str(uuid.uuid4()) + ".jpg", data=blob_data)

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code="es"
                    )
                ]
            )
        ]

        job = client.create_translation_job(translation_inputs)
        job = client.wait_until_done(job.id)
        self._validate_translation_job(job, status="Succeeded", total=1, succeeded=1)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_existing_documents_in_target(self, client):
        # prepare containers and test data
        blob_data = b'This is some text'
        source_container_sas_url = self.create_target_container()  # has the permissions to add
        target_container_sas_url = self.create_target_container()

        if self.is_live:
            container_client = ContainerClient.from_container_url(source_container_sas_url)
            container_client.upload_blob(name="document" + ".txt", data=blob_data)

            container_client = ContainerClient.from_container_url(target_container_sas_url)
            container_client.upload_blob(name="document" + ".txt", data=blob_data)

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code="es"
                    )
                ]
            )
        ]

        job = client.create_translation_job(translation_inputs)
        job = client.wait_until_done(job.id)
        self._validate_translation_job(job, status="Failed", total=1, failed=1)

        doc_status = client.list_all_document_statuses(job.id)
        doc = next(doc_status)
        assert doc.status == "Failed"
        assert doc.error.code == "TargetFileAlreadyExists"

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_existing_documents_in_target_one_valid(self, client):
        # prepare containers and test data
        blob_data = b'This is some text'
        source_container_sas_url = self.create_target_container()  # has the permissions to add
        target_container_sas_url = self.create_target_container()

        if self.is_live:
            container_client = ContainerClient.from_container_url(source_container_sas_url)
            container_client.upload_blob(name="document" + ".txt", data=blob_data)
            container_client.upload_blob(name=str(uuid.uuid4()) + ".txt", data=blob_data)

            container_client = ContainerClient.from_container_url(target_container_sas_url)
            container_client.upload_blob(name="document" + ".txt", data=blob_data)

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code="es"
                    )
                ]
            )
        ]

        job = client.create_translation_job(translation_inputs)
        job = client.wait_until_done(job.id)
        self._validate_translation_job(job, status="Succeeded", total=2, succeeded=1)

        doc_statuses = client.list_all_document_statuses(job.id)
        for doc in doc_statuses:
            if doc.status == "Failed":
                assert doc.error.code == "TargetFileAlreadyExists"
            else:
                self._validate_doc_status(doc, "es")

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_empty_document(self, client):
        # prepare containers and test data
        blob_data = b''
        source_container_sas_url = self.create_source_container(data=blob_data)
        target_container_sas_url = self.create_target_container()

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code="es"
                    )
                ]
            )
        ]

        job = client.create_translation_job(translation_inputs)
        job = client.wait_until_done(job.id)
        self._validate_translation_job(job, status="Failed", total=1, failed=1)

        doc_status = client.list_all_document_statuses(job.id)
        doc = next(doc_status)
        assert doc.status == "Failed"
        assert doc.error.code == "WrongDocumentEncoding"
