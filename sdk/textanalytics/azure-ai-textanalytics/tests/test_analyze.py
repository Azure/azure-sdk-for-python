# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
import platform
import functools
import itertools

from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential
from testcase import TextAnalyticsTest, GlobalTextAnalyticsAccountPreparer
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    EntitiesRecognitionTask,
    PiiEntitiesRecognitionTask,
    KeyPhraseExtractionTask,
    TextDocumentInput,
    VERSION,
    TextAnalyticsApiVersion,
)

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)


class TestAnalyze(TextAnalyticsTest):

    def _interval(self):
        return 5 if self.is_live else 0

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_no_single_input(self, client):
        with self.assertRaises(TypeError):
            response = client.begin_analyze("hello world", polling_interval=self._interval())

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_all_successful_passing_dict_key_phrase_task(self, client):
        docs = [{"id": "1", "language": "en", "text": "Microsoft was founded by Bill Gates and Paul Allen"},
                {"id": "2", "language": "es", "text": "Microsoft fue fundado por Bill Gates y Paul Allen"}]

        response = client.begin_analyze(
            docs,
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            show_stats=True,
            polling_interval=self._interval(),
        ).result()

        results_pages = list(response)
        self.assertEqual(len(results_pages), 1)

        task_results = results_pages[0].key_phrase_extraction_results
        self.assertEqual(len(task_results), 1)

        results = task_results[0].results
        self.assertEqual(len(results), 2)

        for phrases in results:
            self.assertIn("Paul Allen", phrases.key_phrases)
            self.assertIn("Bill Gates", phrases.key_phrases)
            self.assertIn("Microsoft", phrases.key_phrases)
            self.assertIsNotNone(phrases.id)
            #self.assertIsNotNone(phrases.statistics)

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_all_successful_passing_dict_entities_task(self, client):
        docs = [{"id": "1", "language": "en", "text": "Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975."},
                {"id": "2", "language": "es", "text": "Microsoft fue fundado por Bill Gates y Paul Allen el 4 de abril de 1975."},
                {"id": "3", "language": "de", "text": "Microsoft wurde am 4. April 1975 von Bill Gates und Paul Allen gegründet."}]

        response = client.begin_analyze(
            docs,
            entities_recognition_tasks=[EntitiesRecognitionTask()],
            show_stats=True,
            polling_interval=self._interval(),
        ).result()

        results_pages = list(response)
        self.assertEqual(len(results_pages), 1)

        task_results = results_pages[0].entities_recognition_results
        self.assertEqual(len(task_results), 1)

        results = task_results[0].results
        self.assertEqual(len(results), 3)

        for doc in results:
            self.assertEqual(len(doc.entities), 4)
            self.assertIsNotNone(doc.id)
            # self.assertIsNotNone(doc.statistics)
            for entity in doc.entities:
                self.assertIsNotNone(entity.text)
                self.assertIsNotNone(entity.category)
                self.assertIsNotNone(entity.offset)
                self.assertIsNotNone(entity.confidence_score)

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_all_successful_passing_dict_pii_entities_task(self, client):

        docs = [{"id": "1", "text": "My SSN is 859-98-0987."},
                {"id": "2", "text": "Your ABA number - 111000025 - is the first 9 digits in the lower left hand corner of your personal check."},
                {"id": "3", "text": "Is 998.214.865-68 your Brazilian CPF number?"}]

        response = client.begin_analyze(
            docs,
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            show_stats=True,
            polling_interval=self._interval(),
        ).result()

        results_pages = list(response)
        self.assertEqual(len(results_pages), 1)

        task_results = results_pages[0].pii_entities_recognition_results
        self.assertEqual(len(task_results), 1)

        results = task_results[0].results
        self.assertEqual(len(results), 3)

        self.assertEqual(results[0].entities[0].text, "859-98-0987")
        self.assertEqual(results[0].entities[0].category, "U.S. Social Security Number (SSN)")
        self.assertEqual(results[1].entities[0].text, "111000025")
        # self.assertEqual(results[1].entities[0].category, "ABA Routing Number")  # Service is currently returning PhoneNumber here
        self.assertEqual(results[2].entities[0].text, "998.214.865-68")
        self.assertEqual(results[2].entities[0].category, "Brazil CPF Number")
        for doc in results:
            self.assertIsNotNone(doc.id)
            # self.assertIsNotNone(doc.statistics)
            for entity in doc.entities:
                self.assertIsNotNone(entity.text)
                self.assertIsNotNone(entity.category)
                self.assertIsNotNone(entity.offset)
                self.assertIsNotNone(entity.confidence_score)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_all_successful_passing_text_document_input_key_phrase_task(self, client):
        docs = [
            TextDocumentInput(id="1", text="Microsoft was founded by Bill Gates and Paul Allen", language="en"),
            TextDocumentInput(id="2", text="Microsoft fue fundado por Bill Gates y Paul Allen", language="es")
        ]

        response = client.begin_analyze(
            docs,
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            polling_interval=self._interval(),
        ).result()

        results_pages = list(response)
        self.assertEqual(len(results_pages), 1)

        key_phrase_task_results = results_pages[0].key_phrase_extraction_results
        self.assertEqual(len(key_phrase_task_results), 1)

        results = key_phrase_task_results[0].results
        self.assertEqual(len(results), 2)

        for phrases in results:
            self.assertIn("Paul Allen", phrases.key_phrases)
            self.assertIn("Bill Gates", phrases.key_phrases)
            self.assertIn("Microsoft", phrases.key_phrases)
            self.assertIsNotNone(phrases.id)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_all_successful_passing_text_document_input_entities_task(self, client):
        docs = [
            TextDocumentInput(id="1", text="Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975.", language="en"),
            TextDocumentInput(id="2", text="Microsoft fue fundado por Bill Gates y Paul Allen el 4 de abril de 1975.", language="es"),
            TextDocumentInput(id="3", text="Microsoft wurde am 4. April 1975 von Bill Gates und Paul Allen gegründet.", language="de")
        ]

        response = client.begin_analyze(
            docs,
            entities_recognition_tasks=[EntitiesRecognitionTask()],
            polling_interval=self._interval(),
        ).result()

        results_pages = list(response)
        self.assertEqual(len(results_pages), 1)

        task_results = results_pages[0].entities_recognition_results
        self.assertEqual(len(task_results), 1)

        results = task_results[0].results
        self.assertEqual(len(results), 3)

        for doc in results:
            self.assertEqual(len(doc.entities), 4)
            self.assertIsNotNone(doc.id)
            for entity in doc.entities:
                self.assertIsNotNone(entity.text)
                self.assertIsNotNone(entity.category)
                self.assertIsNotNone(entity.offset)
                self.assertIsNotNone(entity.confidence_score)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_all_successful_passing_text_document_input_pii_entities_task(self, client):
        docs = [
            TextDocumentInput(id="1", text="My SSN is 859-98-0987."),
            TextDocumentInput(id="2", text="Your ABA number - 111000025 - is the first 9 digits in the lower left hand corner of your personal check."),
            TextDocumentInput(id="3", text="Is 998.214.865-68 your Brazilian CPF number?")
        ]

        response = client.begin_analyze(
            docs,
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            polling_interval=self._interval(),
        ).result()

        results_pages = list(response)
        self.assertEqual(len(results_pages), 1)

        task_results = results_pages[0].pii_entities_recognition_results
        self.assertEqual(len(task_results), 1)

        results = task_results[0].results
        self.assertEqual(len(results), 3)

        self.assertEqual(results[0].entities[0].text, "859-98-0987")
        self.assertEqual(results[0].entities[0].category, "U.S. Social Security Number (SSN)")
        self.assertEqual(results[1].entities[0].text, "111000025")
        # self.assertEqual(results[1].entities[0].category, "ABA Routing Number")  # Service is currently returning PhoneNumber here
        self.assertEqual(results[2].entities[0].text, "998.214.865-68")
        self.assertEqual(results[2].entities[0].category, "Brazil CPF Number")
        for doc in results:
            self.assertIsNotNone(doc.id)
            for entity in doc.entities:
                self.assertIsNotNone(entity.text)
                self.assertIsNotNone(entity.category)
                self.assertIsNotNone(entity.offset)
                self.assertIsNotNone(entity.confidence_score)

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_passing_only_string_key_phrase_task(self, client):
        docs = [
            u"Microsoft was founded by Bill Gates and Paul Allen",
            u"Microsoft fue fundado por Bill Gates y Paul Allen"
        ]

        response = client.begin_analyze(
            docs,
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            polling_interval=self._interval(),
        ).result()

        results_pages = list(response)
        self.assertEqual(len(results_pages), 1)

        key_phrase_task_results = results_pages[0].key_phrase_extraction_results
        self.assertEqual(len(key_phrase_task_results), 1)

        results = key_phrase_task_results[0].results
        self.assertEqual(len(results), 2)

        self.assertIn("Paul Allen", results[0].key_phrases)
        self.assertIn("Bill Gates", results[0].key_phrases)
        self.assertIn("Microsoft", results[0].key_phrases)
        self.assertIsNotNone(results[0].id)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_bad_request_on_empty_document(self, client):
        docs = [u""]

        with self.assertRaises(HttpResponseError):
            response = client.begin_analyze(
                docs,
                key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
                polling_interval=self._interval(),
            )

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_passing_only_string_entities_task(self, client):
        docs = [
            u"Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975.",
            u"Microsoft fue fundado por Bill Gates y Paul Allen el 4 de abril de 1975.",
            u"Microsoft wurde am 4. April 1975 von Bill Gates und Paul Allen gegründet."
        ]

        response = client.begin_analyze(
            docs,
            entities_recognition_tasks=[EntitiesRecognitionTask()],
            polling_interval=self._interval(),
        ).result()

        results_pages = list(response)
        self.assertEqual(len(results_pages), 1)

        task_results = results_pages[0].entities_recognition_results
        self.assertEqual(len(task_results), 1)

        results = task_results[0].results
        self.assertEqual(len(results), 3)

        self.assertEqual(len(results[0].entities), 4)
        self.assertIsNotNone(results[0].id)
        for entity in results[0].entities:
            self.assertIsNotNone(entity.text)
            self.assertIsNotNone(entity.category)
            self.assertIsNotNone(entity.offset)
            self.assertIsNotNone(entity.confidence_score)

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_passing_only_string_pii_entities_task(self, client):
        docs = [
            u"My SSN is 859-98-0987.",
            u"Your ABA number - 111000025 - is the first 9 digits in the lower left hand corner of your personal check.",
            u"Is 998.214.865-68 your Brazilian CPF number?"
        ]

        response = client.begin_analyze(
            docs,
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            polling_interval=self._interval(),
        ).result()

        results_pages = list(response)
        self.assertEqual(len(results_pages), 1)

        task_results = results_pages[0].pii_entities_recognition_results
        self.assertEqual(len(task_results), 1)

        results = task_results[0].results
        self.assertEqual(len(results), 3)

        self.assertEqual(results[0].entities[0].text, "859-98-0987")
        self.assertEqual(results[0].entities[0].category, "U.S. Social Security Number (SSN)")
        self.assertEqual(results[1].entities[0].text, "111000025")
        # self.assertEqual(results[1].entities[0].category, "ABA Routing Number")  # Service is currently returning PhoneNumber here
        self.assertEqual(results[2].entities[0].text, "998.214.865-68")
        self.assertEqual(results[2].entities[0].category, "Brazil CPF Number")

        for i in range(3):
            self.assertIsNotNone(results[i].id)
            for entity in results[i].entities:
                self.assertIsNotNone(entity.text)
                self.assertIsNotNone(entity.category)
                self.assertIsNotNone(entity.offset)
                self.assertIsNotNone(entity.confidence_score)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_payload_too_large(self, client):
        pass  # TODO: verify payload size limit

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_document_warnings(self, client):
        # TODO: reproduce a warnings scenario for implementation
        pass

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_output_same_order_as_input_multiple_tasks(self, client):
        docs = [
            TextDocumentInput(id="1", text="one"),
            TextDocumentInput(id="2", text="two"),
            TextDocumentInput(id="3", text="three"),
            TextDocumentInput(id="4", text="four"),
            TextDocumentInput(id="5", text="five")
        ]

        response = client.begin_analyze(
            docs,
            entities_recognition_tasks=[EntitiesRecognitionTask()],
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            polling_interval=self._interval(),
        ).result()

        results_pages = list(response)
        self.assertEqual(len(results_pages), 1)

        task_types = [
            "entities_recognition_results",
            "key_phrase_extraction_results",
            "pii_entities_recognition_results"
        ]

        for task_type in task_types:
            task_results = getattr(results_pages[0], task_type)
            self.assertEqual(len(task_results), 1)

            results = task_results[0].results
            self.assertEqual(len(results), 5)

            for idx, doc in enumerate(results):
                self.assertEqual(str(idx + 1), doc.id)

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3,
        "text_analytics_account_key": "",
    })
    def test_empty_credential_class(self, client):
        with self.assertRaises(ClientAuthenticationError):
            response = client.begin_analyze(
                ["This is written in English."],
                entities_recognition_tasks=[EntitiesRecognitionTask()],
                key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
                pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
                polling_interval=self._interval(),
            )

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3,
        "text_analytics_account_key": "xxxxxxxxxxxx",
    })
    def test_bad_credentials(self, client):
        with self.assertRaises(ClientAuthenticationError):
            response = client.begin_analyze(
                ["This is written in English."],
                entities_recognition_tasks=[EntitiesRecognitionTask()],
                key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
                pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
                polling_interval=self._interval(),
            )

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_bad_document_input(self, client):
        docs = "This is the wrong type"

        with self.assertRaises(TypeError):
            response = client.begin_analyze(
                docs,
                entities_recognition_tasks=[EntitiesRecognitionTask()],
                key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
                pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
                polling_interval=self._interval(),
            )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_mixing_inputs(self, client):
        docs = [
            {"id": "1", "text": "Microsoft was founded by Bill Gates and Paul Allen."},
            TextDocumentInput(id="2", text="I did not like the hotel we stayed at. It was too expensive."),
            u"You cannot mix string input with the above inputs"
        ]
        with self.assertRaises(TypeError):
            response = client.begin_analyze(
                docs,
                entities_recognition_tasks=[EntitiesRecognitionTask()],
                key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
                pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
                polling_interval=self._interval(),
            ).result()

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_out_of_order_ids_multiple_tasks(self, client):
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        response = client.begin_analyze(
            docs,
            entities_recognition_tasks=[EntitiesRecognitionTask(model_version="bad")],  # at this moment this should cause all documents to be errors, which isn't correct behavior but I'm using it here to test document ordering with errors.  :)
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            polling_interval=self._interval(),
        ).result()

        results_pages = list(response)
        self.assertEqual(len(results_pages), 1)

        task_types = [
            "entities_recognition_results",
            "key_phrase_extraction_results",
            "pii_entities_recognition_results"
        ]

        in_order = ["56", "0", "19", "1"]

        for task_type in task_types:
            task_results = getattr(results_pages[0], task_type)
            self.assertEqual(len(task_results), 1)

            results = task_results[0].results
            self.assertEqual(len(results), len(docs))

            for idx, resp in enumerate(results):
                self.assertEqual(resp.id, in_order[idx])

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_show_stats_and_model_version_multiple_tasks(self, client):
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        response = client.begin_analyze(
            docs,
            entities_recognition_tasks=[EntitiesRecognitionTask(model_version="latest")],
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask(model_version="latest")],
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask(model_version="latest")],
            show_stats=True,
            polling_interval=self._interval(),
        ).result()

        results_pages = list(response)
        self.assertEqual(len(results_pages), 1)

        task_types = [
            "entities_recognition_results",
            "key_phrase_extraction_results",
            "pii_entities_recognition_results"
        ]

        for task_type in task_types:
            task_results = getattr(results_pages[0], task_type)
            self.assertEqual(len(task_results), 1)

            results = task_results[0].results
            self.assertEqual(len(results), len(docs))

            # self.assertEqual(results.statistics.document_count, 5)
            # self.assertEqual(results.statistics.transaction_count, 4)
            # self.assertEqual(results.statistics.valid_document_count, 4)
            # self.assertEqual(results.statistics.erroneous_document_count, 1)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_whole_batch_language_hint(self, client):
        docs = [
            u"This was the best day of my life.",
            u"I did not like the hotel we stayed at. It was too expensive.",
            u"The restaurant was not as good as I hoped."
        ]

        response = list(client.begin_analyze(
            docs,
            entities_recognition_tasks=[EntitiesRecognitionTask()],
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            language="en",
            polling_interval=self._interval(),
        ).result())

        task_types = [
            "entities_recognition_results",
            "key_phrase_extraction_results",
            "pii_entities_recognition_results"
        ]

        for task_type in task_types:
            task_results = getattr(response[0], task_type)
            self.assertEqual(len(task_results), 1)

            results = task_results[0].results
            for r in results:
                self.assertFalse(r.is_error)

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_whole_batch_dont_use_language_hint(self, client):
        docs = [
            u"This was the best day of my life.",
            u"I did not like the hotel we stayed at. It was too expensive.",
            u"The restaurant was not as good as I hoped."
        ]

        response = list(client.begin_analyze(
            docs,
            entities_recognition_tasks=[EntitiesRecognitionTask()],
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            language="",
            polling_interval=self._interval(),
        ).result())

        task_types = [
            "entities_recognition_results",
            "key_phrase_extraction_results",
            "pii_entities_recognition_results"
        ]

        for task_type in task_types:
            task_results = getattr(response[0], task_type)
            self.assertEqual(len(task_results), 1)

            results = task_results[0].results
            for r in results:
                self.assertFalse(r.is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_per_item_dont_use_language_hint(self, client):
        docs = [{"id": "1", "language": "", "text": "I will go to the park."},
                {"id": "2", "language": "", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = list(client.begin_analyze(
            docs,
            entities_recognition_tasks=[EntitiesRecognitionTask()],
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            polling_interval=self._interval(),
        ).result())

        task_types = [
            "entities_recognition_results",
            "key_phrase_extraction_results",
            "pii_entities_recognition_results"
        ]

        for task_type in task_types:
            task_results = getattr(response[0], task_type)
            self.assertEqual(len(task_results), 1)

            results = task_results[0].results
            for r in results:
                self.assertFalse(r.is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_whole_batch_language_hint_and_obj_input(self, client):
        def callback(resp):
            language_str = "\"language\": \"de\""
            language = resp.http_request.body.count(language_str)
            self.assertEqual(language, 3)

        docs = [
            TextDocumentInput(id="1", text="I should take my cat to the veterinarian."),
            TextDocumentInput(id="4", text="Este es un document escrito en Español."),
            TextDocumentInput(id="3", text="猫は幸せ"),
        ]

        response = list(client.begin_analyze(
            docs,
            entities_recognition_tasks=[EntitiesRecognitionTask()],
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            language="en",
            polling_interval=self._interval(),
        ).result())

        task_types = [
            "entities_recognition_results",
            "key_phrase_extraction_results",
            "pii_entities_recognition_results"
        ]

        for task_type in task_types:
            task_results = getattr(response[0], task_type)
            self.assertEqual(len(task_results), 1)

            results = task_results[0].results
            for r in results:
                self.assertFalse(r.is_error)

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_whole_batch_language_hint_and_dict_input(self, client):
        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = list(client.begin_analyze(
            docs,
            entities_recognition_tasks=[EntitiesRecognitionTask()],
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            language="en",
            polling_interval=self._interval(),
        ).result())

        task_types = [
            "entities_recognition_results",
            "key_phrase_extraction_results",
            "pii_entities_recognition_results"
        ]

        for task_type in task_types:
            task_results = getattr(response[0], task_type)
            self.assertEqual(len(task_results), 1)

            results = task_results[0].results
            for r in results:
                self.assertFalse(r.is_error)

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_whole_batch_language_hint_and_obj_per_item_hints(self, client):
        docs = [
            TextDocumentInput(id="1", text="I should take my cat to the veterinarian.", language="en"),
            TextDocumentInput(id="2", text="Este es un document escrito en Español.", language="en"),
            TextDocumentInput(id="3", text="猫は幸せ"),
        ]

        response = list(client.begin_analyze(
            docs,
            entities_recognition_tasks=[EntitiesRecognitionTask()],
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            language="en",
            polling_interval=self._interval(),
        ).result())


        task_types = [
            "entities_recognition_results",
            "key_phrase_extraction_results",
            "pii_entities_recognition_results"
        ]

        for task_type in task_types:
            task_results = getattr(response[0], task_type)
            self.assertEqual(len(task_results), 1)

            results = task_results[0].results
            for r in results:
                self.assertFalse(r.is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_whole_batch_language_hint_and_dict_per_item_hints(self, client):
        docs = [{"id": "1", "language": "en", "text": "I will go to the park."},
                {"id": "2", "language": "en", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = list(client.begin_analyze(
            docs,
            entities_recognition_tasks=[EntitiesRecognitionTask()],
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            language="en",
            polling_interval=self._interval(),
        ).result())

        task_types = [
            "entities_recognition_results",
            "key_phrase_extraction_results",
            "pii_entities_recognition_results"
        ]

        for task_type in task_types:
            task_results = getattr(response[0], task_type)
            self.assertEqual(len(task_results), 1)

            results = task_results[0].results
            for r in results:
                self.assertFalse(r.is_error)

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={
        "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3,
        "text_analytics_account_key": os.environ.get('AZURE_TEXT_ANALYTICS_KEY'),
        "default_language": "en"
    })
    def test_client_passed_default_language_hint(self, client):
        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = list(client.begin_analyze(
            docs,
            entities_recognition_tasks=[EntitiesRecognitionTask()],
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            polling_interval=self._interval(),
        ).result())

        task_types = [
            "entities_recognition_results",
            "key_phrase_extraction_results",
            "pii_entities_recognition_results"
        ]

        for task_type in task_types:
            tasks = getattr(response[0], task_type)  # only expecting a single page of results here
            self.assertEqual(len(tasks), 1)
            self.assertEqual(len(tasks[0].results), 3)

            for r in tasks[0].results:
                self.assertFalse(r.is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_invalid_language_hint_method(self, client):
        response = list(client.begin_analyze(
            ["This should fail because we're passing in an invalid language hint"],
            language="notalanguage",
            entities_recognition_tasks=[EntitiesRecognitionTask()],
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            polling_interval=self._interval(),
        ).result())

        task_types = [
            "entities_recognition_results",
            "key_phrase_extraction_results",
            "pii_entities_recognition_results"
        ]

        for task_type in task_types:
            tasks = getattr(response[0], task_type)  # only expecting a single page of results here
            self.assertEqual(len(tasks), 1)

            for r in tasks[0].results:
                self.assertTrue(r.is_error)

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_invalid_language_hint_docs(self, client):
        response = list(client.begin_analyze(
            [{"id": "1", "language": "notalanguage", "text": "This should fail because we're passing in an invalid language hint"}],
            entities_recognition_tasks=[EntitiesRecognitionTask()],
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            polling_interval=self._interval(),
        ).result())

        task_types = [
            "entities_recognition_results",
            "key_phrase_extraction_results",
            "pii_entities_recognition_results"
        ]

        for task_type in task_types:
            tasks = getattr(response[0], task_type)  # only expecting a single page of results here
            self.assertEqual(len(tasks), 1)

            for r in tasks[0].results:
                self.assertTrue(r.is_error)

    @GlobalTextAnalyticsAccountPreparer()
    def test_rotate_subscription_key(self, resource_group, location, text_analytics_account, text_analytics_account_key):

        credential = AzureKeyCredential(text_analytics_account_key)
        client = TextAnalyticsClient(text_analytics_account, credential, api_version=TextAnalyticsApiVersion.V3_1_PREVIEW_3)

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = client.begin_analyze(
            docs,
            entities_recognition_tasks=[EntitiesRecognitionTask()],
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            polling_interval=self._interval(),
        ).result()

        self.assertIsNotNone(response)

        credential.update("xxx")  # Make authentication fail
        with self.assertRaises(ClientAuthenticationError):
            response = client.begin_analyze(
                docs,
                entities_recognition_tasks=[EntitiesRecognitionTask()],
                key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
                pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
                polling_interval=self._interval(),
            ).result()

        credential.update(text_analytics_account_key)  # Authenticate successfully again
        response = client.begin_analyze(
            docs,
            entities_recognition_tasks=[EntitiesRecognitionTask()],
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            polling_interval=self._interval(),
        ).result()
        self.assertIsNotNone(response)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_user_agent(self, client):
        def callback(resp):
            self.assertIn("azsdk-python-ai-textanalytics/{} Python/{} ({})".format(
                VERSION, platform.python_version(), platform.platform()),
                resp.http_request.headers["User-Agent"]
            )

        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        poller = client.begin_analyze(
            docs,
            entities_recognition_tasks=[EntitiesRecognitionTask()],
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            polling_interval=self._interval(),
        )

        self.assertIn("azsdk-python-ai-textanalytics/{} Python/{} ({})".format(
                VERSION, platform.python_version(), platform.platform()),
                poller._polling_method._initial_response.http_request.headers["User-Agent"]
            )

        poller.result()  # need to call this before tearDown runs even though we don't need the response for the test.

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_empty_document_failure(self, client):
        docs = [{"id": "1", "text": ""}]

        with self.assertRaises(HttpResponseError):
            response = client.begin_analyze(
                docs,
                entities_recognition_tasks=[EntitiesRecognitionTask()],
                polling_interval=self._interval(),
            )

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_bad_model_version_error_single_task(self, client):  # TODO: verify behavior of service
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        with self.assertRaises(HttpResponseError):
            result = client.begin_analyze(
                docs,
                entities_recognition_tasks=[EntitiesRecognitionTask(model_version="bad")],
                polling_interval=self._interval(),
            ).result()

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_bad_model_version_error_multiple_tasks(self, client):  # TODO: verify behavior of service
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        response = client.begin_analyze(
            docs,
            entities_recognition_tasks=[EntitiesRecognitionTask(model_version="latest")],
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask(model_version="bad")],
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask(model_version="bad")],
            polling_interval=self._interval(),
        ).result()

        results_pages = list(response)
        self.assertEqual(len(results_pages), 1)

        task_types = [
            "entities_recognition_results",
            "key_phrase_extraction_results",
            "pii_entities_recognition_results"
        ]

        for task_type in task_types:
            tasks = getattr(results_pages[0], task_type)  # only expecting a single page of results here
            self.assertEqual(len(tasks), 1)

            for r in tasks[0].results:
                self.assertTrue(r.is_error)  # This is not the optimal way to represent this failure.  We are discussing a solution with the service team.

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_bad_model_version_error_all_tasks(self, client):  # TODO: verify behavior of service
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        with self.assertRaises(HttpResponseError):
            response = client.begin_analyze(
                docs,
                entities_recognition_tasks=[EntitiesRecognitionTask(model_version="bad")],
                key_phrase_extraction_tasks=[KeyPhraseExtractionTask(model_version="bad")],
                pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask(model_version="bad")],
                polling_interval=self._interval(),
            ).result()

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_not_passing_list_for_docs(self, client):
        docs = {"id": "1", "text": "hello world"}
        with pytest.raises(TypeError) as excinfo:
            client.begin_analyze(
                docs,
                entities_recognition_tasks=[EntitiesRecognitionTask()],
                key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
                pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
                polling_interval=self._interval(),
            )
        assert "Input documents cannot be a dict" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_missing_input_records_error(self, client):
        docs = []
        with pytest.raises(ValueError) as excinfo:
            client.begin_analyze(
                docs,
                entities_recognition_tasks=[EntitiesRecognitionTask()],
                key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
                pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
                polling_interval=self._interval(),
            )
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_passing_none_docs(self, client):
        with pytest.raises(ValueError) as excinfo:
            client.begin_analyze(None)
        assert "Input documents can not be empty or None" in str(excinfo.value)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_duplicate_ids_error(self, client):  # TODO: verify behavior of service
        # Duplicate Ids
        docs = [{"id": "1", "text": "hello world"},
                {"id": "1", "text": "I did not like the hotel we stayed at."}]

        with self.assertRaises(HttpResponseError):
            result = client.begin_analyze(
                docs,
                entities_recognition_tasks=[EntitiesRecognitionTask()],
                key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
                pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
                polling_interval=self._interval(),
            ).result()

    @pytest.mark.playback_test_only
    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_pass_cls(self, client):
        def callback(pipeline_response, deserialized, _):
            return "cls result"
        res = client.begin_analyze(
            documents=["Test passing cls to endpoint"],
            entities_recognition_tasks=[EntitiesRecognitionTask()],
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            cls=callback,
            polling_interval=self._interval(),
        ).result()
        assert res == "cls result"

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_multiple_pages_of_results_returned_successfully(self, client):
        single_doc = "hello world"
        docs = [{"id": str(idx), "text": val} for (idx, val) in enumerate(list(itertools.repeat(single_doc, 25)))] # max number of documents is 25

        result = client.begin_analyze(
            docs,
            entities_recognition_tasks=[EntitiesRecognitionTask()],
            key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
            pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
            show_stats=True,
            polling_interval=self._interval(),
        ).result()

        pages = list(result)
        self.assertEqual(len(pages), 2) # default page size is 20

        # self.assertIsNotNone(result.statistics)  # statistics not working at the moment, but a bug has been filed on the service to correct this.

        task_types = [
            "entities_recognition_results",
            "key_phrase_extraction_results",
            "pii_entities_recognition_results"
        ]

        expected_results_per_page = [20, 5]

        for idx, page in enumerate(pages):
            for task_type in task_types:
                task_results = getattr(page, task_type)
                self.assertEqual(len(task_results), 1)

                results = task_results[0].results
                self.assertEqual(len(results), expected_results_per_page[idx])

                for doc in results:
                    self.assertFalse(doc.is_error)
                    #self.assertIsNotNone(doc.statistics)


    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={ "api_version": TextAnalyticsApiVersion.V3_1_PREVIEW_3})
    def test_too_many_documents(self, client):
        docs = list(itertools.repeat("input document", 26))  # Maximum number of documents per request is 25

        with pytest.raises(HttpResponseError) as excinfo:
            client.begin_analyze(
                docs,
                entities_recognition_tasks=[EntitiesRecognitionTask()],
                key_phrase_extraction_tasks=[KeyPhraseExtractionTask()],
                pii_entities_recognition_tasks=[PiiEntitiesRecognitionTask()],
                polling_interval=self._interval(),
            )
        assert excinfo.value.status_code == 400




