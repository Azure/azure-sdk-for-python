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
    TextDocumentInput,
    VERSION,
    TextAnalyticsApiVersion,
    HealthcareEntityRelationType,
    HealthcareEntityRelationRoleType,
)

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)


class TestHealth(TextAnalyticsTest):
    def _interval(self):
        return 5 if self.is_live else 0

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_no_single_input(self, client):
        with self.assertRaises(TypeError):
            response = client.begin_analyze_healthcare_entities("hello world").result()

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_passing_only_string(self, client):
        docs = [
            u"Patient does not suffer from high blood pressure.",
            u"Prescribed 100mg ibuprofen, taken twice daily.",
            u""
        ]

        response = list(client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval()).result())

        for i in range(2):
            self.assertIsNotNone(response[i].id)
            self.assertIsNone(response[i].statistics)
            self.assertIsNotNone(response[i].entities)

        self.assertTrue(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_input_with_some_errors(self, client):
        docs = [{"id": "1", "language": "en", "text": ""},
                {"id": "2", "language": "english", "text": "Patient does not suffer from high blood pressure."},
                {"id": "3", "language": "en", "text": "Prescribed 100mg ibuprofen, taken twice daily."}]

        response = list(client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval()).result())
        self.assertTrue(response[0].is_error)
        self.assertTrue(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_too_many_documents(self, client):
        docs = list(itertools.repeat("input document", 11))  # Maximum number of documents per request is 10

        with pytest.raises(HttpResponseError) as excinfo:
            client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())

        assert excinfo.value.status_code == 400

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_payload_too_large(self, client):
        large_doc = "RECORD #333582770390100 | MH | 85986313 | | 054351 | 2/14/2001 12:00:00 AM | \
            CORONARY ARTERY DISEASE | Signed | DIS | Admission Date: 5/22/2001 \
            Report Status: Signed Discharge Date: 4/24/2001 ADMISSION DIAGNOSIS: \
            CORONARY ARTERY DISEASE. HISTORY OF PRESENT ILLNESS: \
            The patient is a 54-year-old gentleman with a history of progressive angina over the past several months. \
            The patient had a cardiac catheterization in July of this year revealing total occlusion of the RCA and \
            50% left main disease , with a strong family history of coronary artery disease with a brother dying at \
            the age of 52 from a myocardial infarction and another brother who is status post coronary artery bypass grafting. \
            The patient had a stress echocardiogram done on July , 2001 , which showed no wall motion abnormalities ,\
            but this was a difficult study due to body habitus. The patient went for six minutes with minimal ST depressions \
            in the anterior lateral leads , thought due to fatigue and wrist pain , his anginal equivalent. Due to the patient's \
            increased symptoms and family history and history left main disease with total occasional of his RCA was referred \
            for revascularization with open heart surgery."
        docs = list(itertools.repeat(large_doc, 500))


        with pytest.raises(HttpResponseError) as excinfo:
            client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())
        assert excinfo.value.status_code == 413

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_out_of_order_ids(self, client):


        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        response = list(client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval()).result())
        expected_order = ["56", "0", "22", "19", "1"]
        actual_order = [x.id for x in response]

        for idx, resp in enumerate(response):
            self.assertEqual(resp.id, expected_order[idx])

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_show_stats_and_model_version(self, client):
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        response = client.begin_analyze_healthcare_entities(
            docs,
            show_stats=True,
            model_version="2021-01-11",
            polling_interval=self._interval()
        ).result()

        assert response.model_version  # commenting out bc of service error, always uses latest https://github.com/Azure/azure-sdk-for-python/issues/17160
        self.assertEqual(response.statistics.documents_count, 5)
        self.assertEqual(response.statistics.transactions_count, 4)
        self.assertEqual(response.statistics.valid_documents_count, 4)
        self.assertEqual(response.statistics.erroneous_documents_count, 1)

        for doc in response:
            if not doc.is_error:
                self.assertIsNotNone(doc.statistics)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_whole_batch_language_hint_and_dict_input(self, client):
        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = list(client.begin_analyze_healthcare_entities(docs, language="en", polling_interval=self._interval()).result())
        self.assertFalse(response[0].is_error)
        self.assertFalse(response[1].is_error)
        self.assertFalse(response[2].is_error)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_invalid_language_hint_method(self, client):
        response = list(client.begin_analyze_healthcare_entities(
            ["This should fail because we're passing in an invalid language hint"], language="notalanguage", polling_interval=self._interval()
        ).result())
        self.assertEqual(response[0].error.code, 'UnsupportedLanguageCode')

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_invalid_language_hint_docs(self, client):
        response = list(client.begin_analyze_healthcare_entities(
            [{"id": "1", "language": "notalanguage", "text": "This should fail because we're passing in an invalid language hint"}],
            polling_interval=self._interval()
        ).result())
        self.assertEqual(response[0].error.code, 'UnsupportedLanguageCode')

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_user_agent(self, client):  # TODO: verify
        docs = [{"id": "1", "text": "I will go to the park."}]

        poller = client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())
        self.assertIn("azsdk-python-ai-textanalytics/{} Python/{} ({})".format(
                VERSION, platform.python_version(), platform.platform()),
                poller._polling_method._initial_response.http_request.headers["User-Agent"]
            )

        poller.result()  # need to call this before tearDown runs even though we don't need the response for the test.

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_document_attribute_error_no_result_attribute(self, client):
        docs = [{"id": "1", "text": ""}]
        result = client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval()).result()
        response = list(result)

        # Attributes on DocumentError
        self.assertTrue(response[0].is_error)
        self.assertEqual(response[0].id, "1")
        self.assertIsNotNone(response[0].error)

        # Result attribute not on DocumentError, custom error message
        try:
            entities = response[0].entities
        except AttributeError as custom_error:
            self.assertEqual(
                custom_error.args[0],
                '\'DocumentError\' object has no attribute \'entities\'. '
                'The service was unable to process this document:\nDocument Id: 1\nError: '
                'InvalidDocument - Document text is empty.\n'
            )

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_bad_model_version_error(self, client):
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        try:
            result = client.begin_analyze_healthcare_entities(docs, model_version="bad", polling_interval=self._interval()).result()
        except HttpResponseError as err:
            self.assertEqual(err.error.code, "ModelVersionIncorrect")
            self.assertIsNotNone(err.error.message)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_document_errors(self, client):
        text = ""
        for _ in range(5121):
            text += "x"

        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": text}]

        result = client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval()).result()
        doc_errors = list(result)
        self.assertEqual(doc_errors[0].error.code, "InvalidDocument")
        self.assertIsNotNone(doc_errors[0].error.message)
        self.assertEqual(doc_errors[1].error.code, "UnsupportedLanguageCode")
        self.assertIsNotNone(doc_errors[1].error.message)
        self.assertEqual(doc_errors[2].error.code, "InvalidDocument")
        self.assertIsNotNone(doc_errors[2].error.message)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_duplicate_ids_error(self, client):
        # Duplicate Ids
        docs = [{"id": "1", "text": "hello world"},
                {"id": "1", "text": "I did not like the hotel we stayed at."}]
        try:
            result = client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval()).result()

        except HttpResponseError as err:
            self.assertEqual(err.error.code, "InvalidDocument")
            self.assertIsNotNone(err.error.message)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_pass_cls(self, client):
        def callback(pipeline_response, deserialized, _):
            return "cls result"
        res = client.begin_analyze_healthcare_entities(
            documents=["Test passing cls to endpoint"],
            cls=callback,
            polling_interval=self._interval()
        ).result()
        assert res == "cls result"

    """Commenting out multi page tests until service returns multiple pages"""

    # @GlobalTextAnalyticsAccountPreparer()
    # @TextAnalyticsClientPreparer()
    # def test_multiple_pages_of_results_returned_successfully(self, client):
    #     single_doc = "hello world"
    #     docs = [{"id": str(idx), "text": val} for (idx, val) in enumerate(list(itertools.repeat(single_doc, 10)))]
    #     # Service now only accepts 10 documents for a job, and since the current default server-side value
    #     # for records per page is 20, pagination logic will never be activated.  This is intended to change
    #     # in the future but for now this test actually won't hit the pagination logic now.

    #     result = client.begin_analyze_healthcare_entities(docs, show_stats=True, polling_interval=self._interval()).result()
    #     response = list(result)

    #     self.assertEqual(len(docs), len(response))
    #     self.assertIsNotNone(result.statistics)

    #     for (idx, doc) in enumerate(response):
    #         self.assertEqual(docs[idx]["id"], doc.id)
    #         self.assertIsNotNone(doc.statistics)

    # @GlobalTextAnalyticsAccountPreparer()
    # @TextAnalyticsClientPreparer()
    # def test_multiple_pages_of_results_with_errors_returned_successfully(self, client):
    #     single_doc = "hello world"
    #     docs = [{"id": str(idx), "text": val} for (idx, val) in enumerate(list(itertools.repeat(single_doc, 9)))]
    #     docs.append({"id": "9", "text": ""})
    #     # Service now only accepts 10 documents for a job, and since the current default server-side value
    #     # for records per page is 20, pagination logic will never be activated.  This is intended to change
    #     # in the future but for now this test actually won't hit the pagination logic now.


    #     result = client.begin_analyze_healthcare_entities(docs, show_stats=True, polling_interval=self._interval()).result()
    #     response = list(result)

    #     self.assertEqual(len(docs), len(response))
    #     self.assertIsNotNone(result.statistics)

    #     for (idx, doc) in enumerate(response):
    #         self.assertEqual(docs[idx]["id"], doc.id)

    #         if doc.id == "9":
    #             self.assertTrue(doc.is_error)

    #         else:
    #             self.assertFalse(doc.is_error)
    #             self.assertIsNotNone(doc.statistics)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_cancellation(self, client):
        single_doc = "hello world"
        docs = [{"id": str(idx), "text": val} for (idx, val) in enumerate(list(itertools.repeat(single_doc, 10)))]

        poller = client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())

        try:
            cancellation_poller = poller.cancel()
            cancellation_poller.wait()

        except HttpResponseError:
            pass # expected if the operation was already in a terminal state.

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_default_string_index_type_is_UnicodeCodePoint(self, client):
        poller = client.begin_analyze_healthcare_entities(documents=["Hello world"], polling_interval=self._interval())
        actual_string_index_type = poller._polling_method._initial_response.http_request.query["stringIndexType"]
        self.assertEqual(actual_string_index_type, "UnicodeCodePoint")
        poller.result()

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_explicit_set_string_index_type(self, client):
        poller = client.begin_analyze_healthcare_entities(
            documents=["Hello world"],
            string_index_type="TextElements_v8",
            polling_interval=self._interval(),
        )
        actual_string_index_type = poller._polling_method._initial_response.http_request.query["stringIndexType"]
        self.assertEqual(actual_string_index_type, "TextElements_v8")
        poller.result()

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_relations(self, client):
        result = list(client.begin_analyze_healthcare_entities(
            documents=["The patient was diagnosed with Parkinsons Disease (PD)"],
            polling_interval=self._interval(),
        ).result())

        assert len(result) == 1
        result = result[0]

        assert len(result.entities) == 2
        assert len(result.entity_relations) == 1

        relation = result.entity_relations[0]
        assert relation.relation_type == HealthcareEntityRelationType.ABBREVIATION
        assert len(relation.roles) == 2

        parkinsons_entity = list(filter(lambda x: x.text == "Parkinsons Disease", result.entities))[0]
        parkinsons_abbreviation_entity = list(filter(lambda x: x.text == "PD", result.entities))[0]

        for role in relation.roles:
            if role.name == HealthcareEntityRelationRoleType.FULL_TERM:
                self.assert_healthcare_entities_equal(role.entity, parkinsons_entity)
            else:
                assert role.name == HealthcareEntityRelationRoleType.ABBREVIATED_TERM
                self.assert_healthcare_entities_equal(role.entity, parkinsons_abbreviation_entity)

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_normalized_text(self, client):
        result = list(client.begin_analyze_healthcare_entities(
            documents=["patients must have histologically confirmed NHL"],
            polling_interval=self._interval(),
        ).result())

        assert all([
            e for e in result[0].entities if hasattr(e, "normalized_text")
        ])

        histologically_entity = list(filter(lambda x: x.text == "histologically", result[0].entities))[0]
        assert histologically_entity.normalized_text == "Histology Procedure"

    @GlobalTextAnalyticsAccountPreparer()
    @TextAnalyticsClientPreparer()
    def test_healthcare_assertion(self, client):
        result = list(client.begin_analyze_healthcare_entities(
            documents=["Baby not likely to have Meningitis. In case of fever in the mother, consider Penicillin for the baby too."],
            polling_interval=self._interval(),
        ).result())

        # currently can only test certainty
        # have an issue to update https://github.com/Azure/azure-sdk-for-python/issues/17088
        meningitis_entity = next(e for e in result[0].entities if e.text == "Meningitis")
        assert meningitis_entity.assertion.certainty == "negativePossible"

