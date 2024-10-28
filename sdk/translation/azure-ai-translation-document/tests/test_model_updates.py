# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import datetime
import functools
from azure.ai.translation.document.models import (
    DocumentStatus,
    FileFormatType,
    TranslationStatusSummary,
    TranslationGlossary,
    TranslationStatus,
)
from testcase import DocumentTranslationTest
from preparer import (
    DocumentTranslationPreparer,
    DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer,
)
from devtools_testutils import recorded_by_proxy
from azure.ai.translation.document import DocumentTranslationClient, DocumentTranslationInput, TranslationTarget

DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestModelUpdates(DocumentTranslationTest):
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy
    def test_start_translation_details_model(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables", {})

        docs_count = 2
        self._prepare_and_validate_start_translation_details(client, docs_count, wait=False, variables=variables)
        return variables

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy
    def test_document_translation_input_args(self, **kwargs):
        # Creating an instance using required positional arguments
        source_container_url = "https://t7d8641d8f25ec940prim.blob.core.windows.net/source-12345"
        target_container_url = "https://t7d8641d8f25ec940prim.blob.core.windows.net/target-67890"
        doc_input_positional = DocumentTranslationInput(
            source_url=source_container_url, targets=[TranslationTarget(target_url=target_container_url, language="fr")]
        )
        assert doc_input_positional is not None
        assert doc_input_positional.source_url is not None
        assert (
            doc_input_positional.targets
            and doc_input_positional.targets[0].target_url
            and doc_input_positional.targets[0].language is not None
        )

        # Using keyword-only arguments to specify additional optional parameters
        doc_input_keyword = DocumentTranslationInput(
            source_container_url,
            [TranslationTarget(target_url=target_container_url, language="fr")],
            source_language="en",
            storage_type="FOLDER",
            storage_source="AzureBlob",
            prefix="start_",
            suffix="_end",
        )
        self.validate_document_translation(doc_input_keyword)

        # Creating an instance using a dictionary to pass parameters
        params = {
            "source_url": source_container_url,
            "targets": [TranslationTarget(target_url=target_container_url, language="fr")],
            "source_language": "en",
            "storage_type": "FOLDER",
            "storage_source": "AzureBlob",
            "prefix": "start_",
            "suffix": "_end",
        }
        doc_input_dict = DocumentTranslationInput(**params)
        self.validate_document_translation(doc_input_dict)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy
    def test_translation_target_args(self, **kwargs):
        # Creating an instance using required positional arguments
        target_positional = TranslationTarget(
            target_url="https://t7d8641d8f25ec940prim.blob.core.windows.net/target-67890", language="es"
        )
        assert target_positional is not None
        assert target_positional.target_url is not None
        assert target_positional.language is not None

        # Using keyword arguments to specify additional optional parameters
        target_keyword = TranslationTarget(
            target_url="https://t7d8641d8f25ec940prim.blob.core.windows.net/target-67890",
            language="es",
            category_id="general",
            glossaries=[TranslationGlossary(glossary_url="https://glossaryfile.txt", file_format="txt")],
            storage_source="AzureBlob",
        )
        self.validate_translation_target(target_keyword)

        # Creating an instance using a dictionary to pass parameters
        params = {
            "target_url": "https://t7d8641d8f25ec940prim.blob.core.windows.net/target-67890",
            "language": "es",
            "category_id": "general",
            "glossaries": [TranslationGlossary(glossary_url="https://glossaryfile.txt", file_format="txt")],
            "storage_source": "AzureBlob",
        }
        target_dict = TranslationTarget(**params)
        self.validate_translation_target(target_dict)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy
    def test_translation_glossary_args(self, **kwargs):
        # Creating an instance using required positional arguments
        glossary_positional = TranslationGlossary(glossary_url="https://glossaryfile.txt", file_format="txt")
        assert glossary_positional is not None
        assert glossary_positional.glossary_url is not None
        assert glossary_positional.file_format is not None

        # Using keyword arguments to specify additional optional parameters
        glossary_keyword = TranslationGlossary(
            glossary_url="https://glossaryfile.txt", file_format="txt", format_version="1.0", storage_source="AzureBlob"
        )
        self.validate_translation_glossary(glossary_keyword)

        # Creating an instance using a dictionary to pass parameters
        params = {
            "glossary_url": "https://glossaryfile.txt",
            "file_format": "txt",
            "format_version": "1.0",
            "storage_source": "AzureBlob",
        }
        glossary_dict = TranslationGlossary(**params)
        self.validate_translation_glossary(glossary_dict)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy
    def test_document_status_args(self, **kwargs):
        # Using keyword arguments to specify additional optional parameters
        document_status_keyword = DocumentStatus(
            source_document_url="https://t7d8641d8f25ec940prim.blob.core.windows.net/source-12345/document.txt",
            created_on=datetime.datetime.now(),
            last_updated_on=datetime.datetime.now(),
            status="Running",
            translated_to="es",
            translation_progress=0.5,
            id="fd57e619-d7b2-48b7-81cf-24b76e002a8f",
            translated_document_url="https://t7d8641d8f25ec940prim.blob.core.windows.net/target-67890/document.txt",
            error=None,
            characters_charged=1000,
        )
        self.validate_document_status(document_status_keyword)

        # Creating an instance using a dictionary to pass parameters
        params = {
            "source_document_url": "https://t7d8641d8f25ec940prim.blob.core.windows.net/source-12345/document.txt",
            "created_on": datetime.datetime.now(),
            "last_updated_on": datetime.datetime.now(),
            "status": "Succeeded",
            "translated_to": "fr",
            "translation_progress": 1.0,
            "id": "fd57e619-d7b2-48b7-81cf-24b76e002a8f",
            "translated_document_url": "https://t7d8641d8f25ec940prim.blob.core.windows.net/target-67890/document.txt",
            "error": None,
            "characters_charged": 2000,
        }
        document_status_dict = DocumentStatus(**params)
        self.validate_document_status(document_status_dict)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy
    def test_translation_status_args(self, **kwargs):
        # Using keyword-only arguments to specify additional optional parameters
        status_summary = TranslationStatusSummary(
            total=10,
            failed=2,
            success=5,
            in_progress=3,  # Note the naming matches the class definition
            not_yet_started=0,
            canceled=0,
            total_characters_charged=10000,
        )
        translation_status_keyword = TranslationStatus(
            id="fd57e619-d7b2-48b7-81cf-24b76e002a8f",
            created_on=datetime.datetime.now(),
            last_updated_on=datetime.datetime.now(),
            status="Succeeded",
            summary=status_summary,
            error=None,
        )
        self.validate_translation_status(translation_status_keyword)

        # Creating an instance using a dictionary to pass parameters
        params = {
            "id": "fd57e619-d7b2-48b7-81cf-24b76e002a8f",
            "created_on": datetime.datetime.now(),
            "last_updated_on": datetime.datetime.now(),
            "status": "Succeeded",
            "summary": status_summary,
            "error": None,
        }
        translation_status_dict = TranslationStatus(**params)
        self.validate_translation_status(translation_status_dict)

    def validate_translation_target(self, translation_target):
        assert translation_target is not None
        assert translation_target.target_url is not None
        assert translation_target.language is not None
        assert translation_target.category_id is not None
        assert (
            translation_target.glossaries
            and translation_target.glossaries[0].glossary_url
            and translation_target.glossaries[0].file_format is not None
        )
        assert translation_target.storage_source is not None

    def validate_document_translation(self, document_translation):
        assert document_translation is not None
        assert document_translation.source_url is not None
        assert (
            document_translation.targets
            and document_translation.targets[0].target_url
            and document_translation.targets[0].language is not None
        )
        assert document_translation.source_language is not None
        assert document_translation.storage_type is not None
        assert document_translation.storage_source is not None
        assert document_translation.prefix is not None
        assert document_translation.suffix is not None

    def validate_translation_glossary(self, translation_glossary):
        assert translation_glossary is not None
        assert translation_glossary.glossary_url is not None
        assert translation_glossary.file_format is not None
        assert translation_glossary.format_version is not None
        assert translation_glossary.storage_source is not None

    def validate_document_status(self, document_status):
        assert document_status is not None
        assert document_status.source_document_url is not None
        assert document_status.created_on is not None
        assert document_status.last_updated_on is not None
        assert document_status.status is not None
        assert document_status.translated_to is not None
        assert document_status.translation_progress is not None
        assert document_status.id is not None
        assert document_status.translated_document_url is not None
        assert document_status.characters_charged is not None

    def validate_translation_status(self, translation_status):
        assert translation_status is not None
        assert translation_status.id is not None
        assert translation_status.created_on is not None
        assert translation_status.last_updated_on is not None
        assert translation_status.status is not None
        assert translation_status.summary is not None

        # verifying old attributes
        assert translation_status is not None
        assert translation_status.documents_total_count is not None
        assert translation_status.documents_failed_count is not None
        assert translation_status.documents_in_progress_count is not None
        assert translation_status.documents_succeeded_count is not None
        assert translation_status.documents_not_started_count is not None
        assert translation_status.documents_canceled_count is not None
        assert translation_status.total_characters_charged is not None
