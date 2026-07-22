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
    BatchOptions,
    StartTranslationDetails,
    DocumentTranslationInput,
    TranslationTarget,
)
from testcase import DocumentTranslationTest
from preparer import (
    DocumentTranslationPreparer,
    DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer,
)
from devtools_testutils import recorded_by_proxy
from azure.ai.translation.document import DocumentTranslationClient
from azure.ai.translation.document._patch import get_translation_input

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

    def test_translation_target_deployment_name(self):
        # deployment_name is exposed publicly and serialized to the wire property "deploymentName".
        target = TranslationTarget(
            target_url="https://t7d8641d8f25ec940prim.blob.core.windows.net/target-67890",
            language="es",
            deployment_name="my-deployment",
        )
        assert target.deployment_name == "my-deployment"

        wire = target.as_dict()
        assert wire["deploymentName"] == "my-deployment"

    def test_start_translation_details_translate_text_within_image(self):
        # translate_text_within_image is carried on BatchOptions via StartTranslationDetails.options.
        options = BatchOptions(translate_text_within_image=True)
        assert options.translate_text_within_image is True

        details = StartTranslationDetails(inputs=[], options=options)
        wire = details.as_dict()
        assert wire["options"]["translateTextWithinImage"] is True

    def test_document_status_deserializes_new_fields(self):
        # DocumentStatus exposes the deployment name and image scan usage returned by the service.
        payload = {
            "path": "https://target/doc.txt",
            "sourcePath": "https://source/doc.txt",
            "createdDateTimeUtc": "2026-03-01T00:00:00Z",
            "lastActionDateTimeUtc": "2026-03-01T00:05:00Z",
            "status": "Succeeded",
            "to": "es",
            "progress": 1.0,
            "id": "doc-1",
            "characterCharged": 100,
            "deploymentName": "my-deployment",
            "totalImageScansSucceeded": 6,
            "totalImageScansFailed": 1,
            "imageCharged": 3,
            "imageCharacterDetected": 1257,
        }
        status = DocumentStatus(payload)
        assert status.deployment_name == "my-deployment"
        assert status.total_image_scans_succeeded == 6
        assert status.total_image_scans_failed == 1
        assert status.images_charged == 3
        assert status.image_characters_detected == 1257

    def test_translation_status_summary_deserializes_image_totals(self):
        # TranslationStatusSummary exposes the image scan totals returned by the service,
        # mapping the wire names totalImageScansSucceeded / totalImageScansFailed / totalImageCharged.
        payload = {
            "total": 10,
            "failed": 2,
            "success": 5,
            "inProgress": 3,
            "notYetStarted": 0,
            "cancelled": 0,
            "totalCharacterCharged": 10000,
            "totalImageScansSucceeded": 6,
            "totalImageScansFailed": 1,
            "totalImageCharged": 3,
        }
        summary = TranslationStatusSummary(payload)
        assert summary.total_image_scans_succeeded == 6
        assert summary.total_image_scans_failed == 1
        assert summary.total_images_charged == 3

    def test_begin_translation_overloaded_inputs_dispatch(self):
        # begin_translation accepts a list of DocumentTranslationInput positionally or via the
        # 'inputs=' keyword; both build the same StartTranslationDetails. This is SDK request
        # dispatch (not service behavior), so it is validated without the live service.
        inputs = [
            DocumentTranslationInput(
                source_url="https://source",
                targets=[TranslationTarget(target_url="https://target", language="es")],
            )
        ]

        positional = get_translation_input((inputs,), {}, None)
        keyword = get_translation_input((), {"inputs": inputs}, None)

        for request in (positional, keyword):
            assert isinstance(request, StartTranslationDetails)
            batch = request.inputs[0]
            assert batch.source.source_url == "https://source"
            assert batch.targets[0].target_url == "https://target"
            assert batch.targets[0].language == "es"

    def test_begin_translation_list_inputs_translate_text_within_image(self):
        # Regression: translate_text_within_image must be honored for the List[DocumentTranslationInput]
        # batch form (it was previously read only on the single-URL form and silently dropped here).
        inputs = [
            DocumentTranslationInput(
                source_url="https://source",
                targets=[TranslationTarget(target_url="https://target", language="es")],
            )
        ]

        request = get_translation_input((inputs,), {"translate_text_within_image": True}, None)
        assert isinstance(request, StartTranslationDetails)
        assert request.options is not None
        assert request.options.translate_text_within_image is True

        # When the option is not provided, no BatchOptions is attached.
        request_without = get_translation_input((inputs,), {}, None)
        assert request_without.options is None

    def test_begin_translation_single_input_dispatch(self):
        # The single-input convenience form accepts source/target/language positionally or by
        # keyword; both build an equivalent StartTranslationDetails.
        positional = get_translation_input(("https://source", "https://target", "es"), {}, None)
        keyword = get_translation_input(
            (), {"source_url": "https://source", "target_url": "https://target", "target_language": "es"}, None
        )

        for request in (positional, keyword):
            assert isinstance(request, StartTranslationDetails)
            batch = request.inputs[0]
            assert batch.source.source_url == "https://source"
            assert batch.targets[0].target_url == "https://target"
            assert batch.targets[0].language == "es"

    def test_begin_translation_single_input_serialization(self):
        # The keyword options on the single-input begin_translation form serialize onto the
        # request as expected (previously covered by a live raw_response_hook test).
        request = get_translation_input(
            ("https://source", "https://target", "es"),
            {
                "storage_type": "File",
                "source_language": "en",
                "prefix": "",
                "suffix": ".txt",
                "category_id": "fake",
                "glossaries": [TranslationGlossary(glossary_url="https://glossaryfile.txt", file_format="txt")],
            },
            None,
        )

        batch = request.inputs[0]
        assert batch.source.source_url == "https://source"
        assert batch.source.language == "en"
        assert batch.source.filter.prefix == ""
        assert batch.source.filter.suffix == ".txt"
        assert batch.storage_type == "File"
        assert batch.targets[0].category_id == "fake"
        assert batch.targets[0].glossaries[0].file_format == "txt"
        assert batch.targets[0].glossaries[0].glossary_url == "https://glossaryfile.txt"
        assert batch.targets[0].language == "es"
        assert batch.targets[0].target_url == "https://target"

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
