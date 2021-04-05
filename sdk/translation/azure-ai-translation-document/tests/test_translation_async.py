# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
import pytest
from testcase import Document
from asynctestcase import AsyncDocumentTranslationTest
from preparer import DocumentTranslationPreparer, \
    DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.core.exceptions import HttpResponseError
from azure.storage.blob import ContainerClient
from azure.ai.translation.document import DocumentTranslationInput, TranslationTarget
from azure.ai.translation.document.aio import DocumentTranslationClient
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestTranslation(AsyncDocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_single_source_single_target(self, client):
        # prepare containers and test data
        blob_data = b'This is some text'
        source_container_sas_url = self.create_source_container(data=Document(data=blob_data))
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
        await self._submit_and_validate_translation_job_async(client, translation_inputs, 1)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_single_source_two_targets(self, client):
        # prepare containers and test data
        blob_data = b'This is some text'
        source_container_sas_url = self.create_source_container(data=Document(data=blob_data))
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
        await self._submit_and_validate_translation_job_async(client, translation_inputs)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_multiple_sources_single_target(self, client):
        # prepare containers and test data
        blob_data = b'This is some text'
        source_container_sas_url = self.create_source_container(data=Document(data=blob_data))
        blob_data = b'This is some text2'
        additional_source_container_sas_url = self.create_source_container(data=Document(data=blob_data))
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
        await self._submit_and_validate_translation_job_async(client, translation_inputs, 2)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_single_source_single_target_with_prefix(self, client):
        # prepare containers and test data
        blob_data = b'This is some text'
        prefix = "xyz"
        source_container_sas_url = self.create_source_container(data=Document(data=blob_data, prefix=prefix))
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
        await self._submit_and_validate_translation_job_async(client, translation_inputs, 1)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_single_source_single_target_with_suffix(self, client):
        # prepare containers and test data
        blob_data = b'This is some text'
        suffix = "txt"
        source_container_sas_url = self.create_source_container(data=Document(data=blob_data))
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
        await self._submit_and_validate_translation_job_async(client, translation_inputs, 1)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_bad_input_source(self, client):
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
            job = await client.create_translation_job(translation_inputs)
            job = await client.wait_until_done(job.id)
        assert e.value.error.code == "InvalidDocumentAccessLevel"

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_bad_input_target(self, client):
        # prepare containers and test data
        blob_data = b'This is some text'
        source_container_sas_url = self.create_source_container(data=Document(data=blob_data))

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
            job = await client.create_translation_job(translation_inputs)
            job = await client.wait_until_done(job.id)
        assert e.value.error.code == "InvalidDocumentAccessLevel"

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_use_supported_and_unsupported_files(self, client):
        # prepare containers and test data
        source_container_sas_url = self.create_source_container(data=[
                Document(suffix=".txt"),
                Document(suffix=".jpg")
            ]
        )
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

        job = await client.create_translation_job(translation_inputs)
        job = await client.wait_until_done(job.id)
        self._validate_translation_job(job, status="Succeeded", total=1, succeeded=1)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_existing_documents_in_target(self, client):
        # prepare containers and test data
        source_container_sas_url = self.create_source_container(data=Document(name="document"))
        target_container_sas_url = self.create_target_container(data=Document(name="document"))

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

        job = await client.create_translation_job(translation_inputs)
        job = await client.wait_until_done(job.id)
        self._validate_translation_job(job, status="Failed", total=1, failed=1)

        doc_status = client.list_all_document_statuses(job.id)
        doc = await doc_status.__anext__()
        assert doc.status == "Failed"
        assert doc.error.code == "TargetFileAlreadyExists"

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_existing_documents_in_target_one_valid(self, client):
        # prepare containers and test data
        source_container_sas_url = self.create_source_container(data=[Document(name="document"), Document()])
        target_container_sas_url = self.create_target_container(data=Document(name="document"))

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

        job = await client.create_translation_job(translation_inputs)
        job = await client.wait_until_done(job.id)
        self._validate_translation_job(job, status="Succeeded", total=2, failed=1)

        doc_statuses = client.list_all_document_statuses(job.id)
        async for doc in doc_statuses:
            if doc.status == "Failed":
                assert doc.error.code == "TargetFileAlreadyExists"

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_empty_document(self, client):
        # prepare containers and test data
        source_container_sas_url = self.create_source_container(Document(data=b''))
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

        job = await client.create_translation_job(translation_inputs)
        job = await client.wait_until_done(job.id)
        self._validate_translation_job(job, status="Failed", total=1, failed=1)

        doc_status = client.list_all_document_statuses(job.id)
        doc = await doc_status.__anext__()
        assert doc.status == "Failed"
        assert doc.error.code == "WrongDocumentEncoding"
