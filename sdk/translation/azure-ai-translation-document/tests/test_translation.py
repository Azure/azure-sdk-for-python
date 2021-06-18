# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
import pytest
from azure.core.exceptions import HttpResponseError
from testcase import DocumentTranslationTest, Document
from preparer import DocumentTranslationPreparer, \
    DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.translation.document import DocumentTranslationClient, DocumentTranslationInput, TranslationTarget
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestTranslation(DocumentTranslationTest):

    @pytest.mark.live_test_only
    @DocumentTranslationPreparer()
    def test_active_directory_auth(self):
        token = self.generate_oauth_token()
        endpoint = self.get_oauth_endpoint()
        client = DocumentTranslationClient(endpoint, token)
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
                        language_code="fr"
                    )
                ]
            )
        ]

        # submit translation and test
        self._begin_and_validate_translation(client, translation_inputs, 1, "fr")

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_single_source_single_target(self, client):
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

        # submit translation and test
        self._begin_and_validate_translation(client, translation_inputs, 1, "es")

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_single_source_two_targets(self, client):
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

        # submit translation and test
        self._begin_and_validate_translation(client, translation_inputs, 2)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_multiple_sources_single_target(self, client):
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

        # submit translation and test
        self._begin_and_validate_translation(client, translation_inputs, 2)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_single_source_single_target_with_prefix(self, client):
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

        # submit translation and test
        self._begin_and_validate_translation(client, translation_inputs, 1, "es")

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_single_source_single_target_with_suffix(self, client):
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

        # submit translation and test
        self._begin_and_validate_translation(client, translation_inputs, 1, "es")

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
            poller = client.begin_translation(translation_inputs)
            result = poller.result()
        assert e.value.error.code == "InvalidDocumentAccessLevel"

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_bad_input_target(self, client):
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
            poller = client.begin_translation(translation_inputs)
            result = poller.result()
        assert e.value.error.code == "InvalidTargetDocumentAccessLevel"

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_use_supported_and_unsupported_files(self, client):
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

        poller = client.begin_translation(translation_inputs)
        result = poller.result()
        self._validate_translation_metadata(poller=poller, status="Succeeded", total=1, succeeded=1)
        for document in result:
            self._validate_doc_status(document, "es")

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_existing_documents_in_target(self, client):
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

        poller = client.begin_translation(translation_inputs)
        result = poller.result()
        self._validate_translation_metadata(poller, status="Failed", total=1, failed=1)

        for doc in result:
            assert doc.status == "Failed"
            assert doc.error.code == "TargetFileAlreadyExists"

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_existing_documents_in_target_one_valid(self, client):
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

        poller = client.begin_translation(translation_inputs)
        result = poller.result()
        self._validate_translation_metadata(poller, status="Succeeded", total=2, failed=1)

        for doc in result:
            if doc.status == "Failed":
                assert doc.error.code == "TargetFileAlreadyExists"

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_empty_document(self, client):
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

        poller = client.begin_translation(translation_inputs)
        result = poller.result()
        self._validate_translation_metadata(poller, status="Failed", total=1, failed=1)

        for doc in result:
            assert doc.status == "Failed"
            assert doc.error.code == "WrongDocumentEncoding"

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_overloaded_inputs(self, client):
        # prepare containers and test data
        source_container_sas_url = self.create_source_container(data=Document(data=b'hello world'))
        target_container_sas_url = self.create_target_container()
        target_container_sas_url_2 = self.create_target_container()

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


        # positional
        poller = client.begin_translation(translation_inputs)
        result = poller.result()
        self._validate_translation_metadata(poller, status="Succeeded", total=1, succeeded=1)

        # keyword
        translation_inputs[0].targets[0].target_url = target_container_sas_url_2
        poller = client.begin_translation(inputs=translation_inputs)
        result = poller.result()
        self._validate_translation_metadata(poller, status="Succeeded", total=1, succeeded=1)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_overloaded_single_input(self, client):
        # prepare containers and test data
        source_container_sas_url = self.create_source_container(data=Document(data=b'hello world'))
        target_container_sas_url = self.create_target_container()
        target_container_sas_url_2 = self.create_target_container()

        # positional
        poller = client.begin_translation(source_container_sas_url, target_container_sas_url, "es")
        result = poller.result()
        self._validate_translation_metadata(poller, status="Succeeded", total=1, succeeded=1)

        # keyword
        poller = client.begin_translation(source_url=source_container_sas_url, target_url=target_container_sas_url_2, target_language_code="es")
        result = poller.result()
        self._validate_translation_metadata(poller, status="Succeeded", total=1, succeeded=1)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_overloaded_bad_input(self, client):
        translation_inputs = [
            DocumentTranslationInput(
                source_url="container",
                targets=[
                    TranslationTarget(
                        target_url="container",
                        language_code="es"
                    )
                ]
            )
        ]

        with pytest.raises(ValueError):
            client.begin_translation("container")

        with pytest.raises(ValueError):
            client.begin_translation("container", "container")

        with pytest.raises(ValueError):
            client.begin_translation(source_url=translation_inputs)

        with pytest.raises(ValueError):
            client.begin_translation(inputs="container")

    @pytest.mark.live_test_only
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_translation_continuation_token(self, client):
        source_container_sas_url = self.create_source_container(data=Document(data=b'hello world'))
        target_container_sas_url = self.create_target_container()

        initial_poller = client.begin_translation(source_container_sas_url, target_container_sas_url, "es")
        cont_token = initial_poller.continuation_token()

        poller = client.begin_translation(None, continuation_token=cont_token)
        result = poller.result()
        self._validate_translation_metadata(poller, status="Succeeded", total=1, succeeded=1)
        for doc in result:
            self._validate_doc_status(doc, target_language="es")
        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error
