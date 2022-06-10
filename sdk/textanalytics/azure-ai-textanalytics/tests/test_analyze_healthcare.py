# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import json
import pytest
import platform
import functools
import itertools
import datetime
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential
from testcase import TextAnalyticsTest, TextAnalyticsPreparer
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from devtools_testutils import recorded_by_proxy
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    TextDocumentInput,
    VERSION,
    TextAnalyticsApiVersion,
    HealthcareEntityRelation,
    AnalyzeHealthcareEntitiesLROPoller
)

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)


class TestHealth(TextAnalyticsTest):
    def _interval(self):
        return 5 if self.is_live else 0

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_no_single_input(self, client):
        with pytest.raises(TypeError):
            response = client.begin_analyze_healthcare_entities("hello world").result()

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_passing_only_string(self, client):
        docs = [
            "Patient does not suffer from high blood pressure.",
            "Prescribed 100mg ibuprofen, taken twice daily.",
            ""
        ]

        response = list(client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval()).result())

        for i in range(2):
            assert response[i].id is not None
            assert response[i].statistics is None
            assert response[i].entities is not None

        assert response[2].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_1})
    @recorded_by_proxy
    def test_passing_only_string_v3_1(self, client):
        docs = [
            "Patient does not suffer from high blood pressure.",
            "Prescribed 100mg ibuprofen, taken twice daily.",
            ""
        ]

        response = list(client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval()).result())

        for i in range(2):
            assert response[i].id is not None
            assert response[i].statistics is None
            assert response[i].entities is not None

        assert response[2].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_input_with_some_errors(self, client):
        docs = [{"id": "1", "language": "en", "text": ""},
                {"id": "2", "language": "english", "text": "Patient does not suffer from high blood pressure."},
                {"id": "3", "language": "en", "text": "Prescribed 100mg ibuprofen, taken twice daily."}]

        response = list(client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval()).result())
        assert response[0].is_error
        assert response[1].is_error
        assert not response[2].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_too_many_documents(self, client):
        docs = list(itertools.repeat("input document", 26))  # Maximum number of documents per request is 25

        with pytest.raises(HttpResponseError) as excinfo:
            client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())

        assert excinfo.value.status_code == 400

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
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

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_out_of_order_ids(self, client):


        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        response = list(client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval()).result())
        expected_order = ["56", "0", "22", "19", "1"]
        actual_order = [x.id for x in response]

        num_error = 0
        for idx, resp in enumerate(response):
            assert resp.id == expected_order[idx]
            if resp.is_error:
                num_error += 1
                continue
            assert not resp.statistics
        assert num_error == 1

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": "v3.1"})
    @recorded_by_proxy
    def test_show_stats_and_model_version_v3_1(self, client):
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        def callback(resp):
            assert resp.raw_response
            stats = resp.raw_response['results']['statistics']
            assert stats['documentsCount'] == 5
            assert stats['validDocumentsCount'] == 4
            assert stats['erroneousDocumentsCount'] == 1
            assert stats['transactionsCount'] == 4

        response = client.begin_analyze_healthcare_entities(
            docs,
            show_stats=True,
            model_version="2021-01-11",
            polling_interval=self._interval(),
            raw_response_hook = callback,
        ).result()

        num_error = 0
        for doc in response:
            if doc.is_error:
                num_error += 1
                continue
            assert doc.statistics.character_count
            assert doc.statistics.transaction_count
        assert num_error == 1

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_show_stats_and_model_version(self, client):
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        def callback(resp):
            assert resp.raw_response
            tasks = resp.raw_response['tasks']
            assert tasks['completed'] == 1
            assert tasks['inProgress'] == 0
            assert tasks['failed'] == 0
            assert tasks['total'] == 1
            num_tasks = 0
            for task in tasks["items"]:
                num_tasks += 1
                task_stats = task['results']['statistics']
                # assert "2022-03-01" == task['results']['modelVersion']  https://dev.azure.com/msazure/Cognitive%20Services/_workitems/edit/14685418
                assert task_stats['documentsCount'] == 5
                assert task_stats['validDocumentsCount'] == 4
                assert task_stats['erroneousDocumentsCount'] == 1
                assert task_stats['transactionsCount'] == 4
            assert num_tasks == 1

        response = client.begin_analyze_healthcare_entities(
            docs,
            show_stats=True,
            model_version="latest",
            polling_interval=self._interval(),
            raw_response_hook = callback,
        ).result()

        num_error = 0
        for doc in response:
            if doc.is_error:
                num_error += 1
                continue
            assert doc.statistics.character_count
            assert doc.statistics.transaction_count
        assert num_error == 1

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_whole_batch_language_hint_and_dict_input(self, client):
        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        response = list(client.begin_analyze_healthcare_entities(docs, language="en", polling_interval=self._interval()).result())
        assert not response[0].is_error
        assert not response[1].is_error
        assert not response[2].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_invalid_language_hint_method(self, client):
        response = list(client.begin_analyze_healthcare_entities(
            ["This should fail because we're passing in an invalid language hint"], language="notalanguage", polling_interval=self._interval()
        ).result())
        assert response[0].error.code == 'UnsupportedLanguageCode'

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_invalid_language_hint_docs(self, client):
        response = list(client.begin_analyze_healthcare_entities(
            [{"id": "1", "language": "notalanguage", "text": "This should fail because we're passing in an invalid language hint"}],
            polling_interval=self._interval()
        ).result())
        assert response[0].error.code == 'UnsupportedLanguageCode'

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_user_agent(self, client):  # TODO: verify
        docs = [{"id": "1", "text": "I will go to the park."}]

        poller = client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())
        assert "azsdk-python-ai-textanalytics/{} Python/{} ({})".format(
            VERSION, platform.python_version(), platform.platform()) in \
            poller._polling_method._initial_response.http_request.headers["User-Agent"]

        poller.result()  # need to call this before tearDown runs even though we don't need the response for the test.

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_document_attribute_error_no_result_attribute(self, client):
        docs = [{"id": "1", "text": ""}, {"id": "2", "text": "okay"}]
        result = client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval()).result()
        response = list(result)

        # Attributes on DocumentError
        assert response[0].is_error
        assert response[0].id == "1"
        assert response[0].error is not None

        # Result attribute not on DocumentError, custom error message
        try:
            entities = response[0].entities
        except AttributeError as custom_error:
            assert custom_error.args[0] == \
                '\'DocumentError\' object has no attribute \'entities\'. ' \
                'The service was unable to process this document:\nDocument Id: 1\nError: ' \
                'InvalidDocument - Document text is empty.\n'

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_bad_model_version_error(self, client):
        docs = [{"id": "1", "language": "en", "text": "I did not like the hotel we stayed at."}]

        with pytest.raises(HttpResponseError) as err:
            result = client.begin_analyze_healthcare_entities(docs, model_version="bad", polling_interval=self._interval()).result()
        assert err.value.error.code == "InvalidParameterValue"
        assert err.value.error.message is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_document_errors(self, client):
        text = ""
        for _ in range(5121):
            text += "x"

        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": text}]

        result = client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval()).result()
        doc_results = list(result)
        assert doc_results[0].error.code == "InvalidDocument"
        assert doc_results[0].error.message is not None
        assert doc_results[1].error.code == "UnsupportedLanguageCode"
        assert doc_results[1].error.message is not None
        assert not doc_results[2].is_error
        assert doc_results[2].warnings

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_duplicate_ids_error(self, client):
        # Duplicate Ids
        docs = [{"id": "1", "text": "hello world"},
                {"id": "1", "text": "I did not like the hotel we stayed at."}]
        try:
            result = client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval()).result()

        except HttpResponseError as err:
            assert err.error.code == "InvalidDocument"
            assert err.error.message is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_pass_cls(self, client):
        def callback(pipeline_response, deserialized, _):
            return "cls result"
        res = client.begin_analyze_healthcare_entities(
            documents=["Test passing cls to endpoint"],
            cls=callback,
            polling_interval=self._interval()
        ).result()
        assert res == "cls result"

    @pytest.mark.skip("https://dev.azure.com/msazure/Cognitive%20Services/_workitems/edit/14303656/")
    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_cancellation(self, client):
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
        docs = [{"id": str(idx), "text": large_doc*3} for (idx, val) in enumerate(list(itertools.repeat(large_doc, 25)))]

        poller = client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())

        try:
            cancellation_poller = poller.cancel()
            cancellation_poller.result()
        except HttpResponseError:
            pass # expected if the operation was already in a terminal state.

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_1})
    @recorded_by_proxy
    def test_default_string_index_type_is_UnicodeCodePoint(self, client):
        poller = client.begin_analyze_healthcare_entities(documents=["Hello world"], polling_interval=self._interval())
        actual_string_index_type = poller._polling_method._initial_response.http_request.query["stringIndexType"]
        assert actual_string_index_type == "UnicodeCodePoint"
        poller.result()

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_default_string_index_type_UnicodeCodePoint_body_param(self, client):
        def callback(response):
            assert json.loads(response.http_request.body)['parameters']["stringIndexType"] == "UnicodeCodePoint"
        poller = client.begin_analyze_healthcare_entities(documents=["Hello world"], polling_interval=self._interval(), raw_response_hook=callback)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_1})
    @recorded_by_proxy
    def test_explicit_set_string_index_type(self, client):
        poller = client.begin_analyze_healthcare_entities(
            documents=["Hello world"],
            string_index_type="TextElement_v8",
            polling_interval=self._interval(),
        )
        actual_string_index_type = poller._polling_method._initial_response.http_request.query["stringIndexType"]
        assert actual_string_index_type == "TextElement_v8"
        poller.result()

    @pytest.mark.skip("https://dev.azure.com/msazure/Cognitive%20Services/_workitems/edit/14243209/")
    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_explicit_set_string_index_type_body_param(self, client):
        def callback(response):
            assert json.loads(response.http_request.body)['parameters']["stringIndexType"] == "TextElements_v8"

        res = client.begin_analyze_healthcare_entities(
            documents=["Hello world"],
            string_index_type="TextElement_v8",
            raw_response_hook=callback
        )

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
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
        assert relation.relation_type == HealthcareEntityRelation.ABBREVIATION
        assert len(relation.roles) == 2

        parkinsons_entity = list(filter(lambda x: x.text == "Parkinsons Disease", result.entities))[0]
        parkinsons_abbreviation_entity = list(filter(lambda x: x.text == "PD", result.entities))[0]

        for role in relation.roles:
            if role.name == "FullTerm":
                self.assert_healthcare_entities_equal(role.entity, parkinsons_entity)
            else:
                assert role.name == "AbbreviatedTerm"
                self.assert_healthcare_entities_equal(role.entity, parkinsons_abbreviation_entity)

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
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

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_healthcare_assertion(self, client):
        result = list(client.begin_analyze_healthcare_entities(
            documents=["Baby not likely to have Meningitis. In case of fever in the mother, consider Penicillin for the baby too."],
            polling_interval=self._interval(),
        ).result())

        # currently can only test certainty
        # have an issue to update https://github.com/Azure/azure-sdk-for-python/issues/17088
        meningitis_entity = next(e for e in result[0].entities if e.text == "Meningitis")
        assert meningitis_entity.assertion.certainty == "negativePossible"

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_disable_service_logs(self, client):
        def callback(resp):
            # this is called for both the initial post
            # and the gets. Only care about the initial post
            if resp.http_request.method == "POST":
                assert resp.http_request.query['loggingOptOut']
        client.begin_analyze_healthcare_entities(
            documents=["Test for logging disable"],
            polling_interval=self._interval(),
            disable_service_logs=True,
            raw_response_hook=callback,
        ).result()

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_healthcare_continuation_token(self, client):
        initial_poller = client.begin_analyze_healthcare_entities(
            documents=[
                {"id": "1", "text": "Baby not likely to have Meningitis. In case of fever in the mother, consider Penicillin for the baby too."},
                {"id": "2", "text": "patients must have histologically confirmed NHL"},
                {"id": "3", "text": ""},
                {"id": "4", "text": "The patient was diagnosed with Parkinsons Disease (PD)"}
            ],
            show_stats=True,
            polling_interval=self._interval(),
        )

        cont_token = initial_poller.continuation_token()
        poller = client.begin_analyze_healthcare_entities(
            None,
            continuation_token=cont_token,
            polling_interval=self._interval(),
        )
        response = poller.result()

        results = list(response)
        document_order = ["1", "2", "3", "4"]
        for doc_idx, result in enumerate(results):
            if doc_idx == 2:
                assert result.id == document_order[doc_idx]
                assert result.is_error
            else:
                assert result.id == document_order[doc_idx]
                assert result.statistics
                assert result.entities

        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_poller_metadata(self, client):
        docs = [{"id": "56", "text": ":)"}]

        poller = client.begin_analyze_healthcare_entities(
            docs,
            display_name="hello",
            polling_interval=self._interval(),
        )

        poller.result()

        assert isinstance(poller, AnalyzeHealthcareEntitiesLROPoller)
        assert isinstance(poller.created_on, datetime.datetime)
        assert poller.display_name == "hello"
        assert isinstance(poller.expires_on, datetime.datetime)
        assert isinstance(poller.last_modified_on, datetime.datetime)
        assert poller.id

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": "v3.0"})
    def test_healthcare_multiapi_validate_v3_0(self, **kwargs):
        client = kwargs.pop("client")

        with pytest.raises(ValueError) as e:
            poller = client.begin_analyze_healthcare_entities(
                documents=[
                    {"id": "1",
                     "text": "Baby not likely to have Meningitis. In case of fever in the mother, consider Penicillin for the baby too."},
                    {"id": "2", "text": "patients must have histologically confirmed NHL"},
                    {"id": "3", "text": ""},
                    {"id": "4", "text": "The patient was diagnosed with Parkinsons Disease (PD)"}
                ],
                show_stats=True,
                polling_interval=self._interval(),
            )
        assert str(e.value) == "'begin_analyze_healthcare_entities' is only available for API version v3.1 and up."

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": "v3.1"})
    def test_healthcare_multiapi_validate_v3_1(self, **kwargs):
        client = kwargs.pop("client")

        with pytest.raises(ValueError) as e:
            poller = client.begin_analyze_healthcare_entities(
                documents=[
                    {"id": "1",
                     "text": "Baby not likely to have Meningitis. In case of fever in the mother, consider Penicillin for the baby too."},
                    {"id": "2", "text": "patients must have histologically confirmed NHL"},
                    {"id": "3", "text": ""},
                    {"id": "4", "text": "The patient was diagnosed with Parkinsons Disease (PD)"}
                ],
                display_name="this won't work",
                show_stats=True,
                polling_interval=self._interval(),
            )
        assert str(e.value) == "'display_name' is only available for API version 2022-05-01 and up.\n"
