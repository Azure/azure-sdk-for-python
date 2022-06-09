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
from testcase import TextAnalyticsPreparer
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from devtools_testutils.aio import recorded_by_proxy_async
from testcase import TextAnalyticsTest
from azure.ai.textanalytics.aio import TextAnalyticsClient
from azure.ai.textanalytics import (
    TextDocumentInput,
    VERSION,
    TextAnalyticsApiVersion,
    HealthcareEntityRelation,
)
from azure.ai.textanalytics.aio import AsyncAnalyzeHealthcareEntitiesLROPoller

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)

@pytest.mark.skip("Changes in impl needed before we can run tests")
class TestHealth(TextAnalyticsTest):
    def _interval(self):
        return 5 if self.is_live else 0

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_no_single_input(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(TypeError):
            async with client:
                response = await (await client.begin_analyze_healthcare_entities("hello world", polling_interval=self._interval())).result()

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_passing_only_string(self, **kwargs):
        client = kwargs.pop("client")
        docs = [
            "Patient does not suffer from high blood pressure.",
            "Prescribed 100mg ibuprofen, taken twice daily.",
            ""
        ]

        async with client:
            result = await(await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)


        for i in range(2):
            assert response[i].id is not None
            assert response[i].entities is not None

        assert response[2].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_1})
    @recorded_by_proxy_async
    async def test_passing_only_string_v3_1(self, **kwargs):
        client = kwargs.pop("client")
        docs = [
            "Patient does not suffer from high blood pressure.",
            "Prescribed 100mg ibuprofen, taken twice daily.",
            ""
        ]

        async with client:
            result = await(await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)


        for i in range(2):
            assert response[i].id is not None
            assert response[i].entities is not None

        assert response[2].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_input_with_some_errors(self, **kwargs):
        client = kwargs.pop("client")
        docs = [{"id": "1", "language": "en", "text": ""},
                {"id": "2", "language": "english", "text": "Patient does not suffer from high blood pressure."},
                {"id": "3", "language": "en", "text": "Prescribed 100mg ibuprofen, taken twice daily."}]

        async with client:
            result = await(await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        assert response[0].is_error
        assert response[1].is_error
        assert not response[2].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_too_many_documents(self, **kwargs):
        client = kwargs.pop("client")
        docs = list(itertools.repeat("input document", 26))  # Maximum number of documents per request is 25

        with pytest.raises(HttpResponseError) as excinfo:
            async with client:
                await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())

        assert excinfo.value.status_code == 400

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_payload_too_large(self, **kwargs):
        client = kwargs.pop("client")
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
            async with client:
                await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())

        assert excinfo.value.status_code == 413

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_out_of_order_ids(self, **kwargs):
        client = kwargs.pop("client")
        docs = [{"id": "56", "text": ":)"},
                {"id": "0", "text": ":("},
                {"id": "22", "text": ""},
                {"id": "19", "text": ":P"},
                {"id": "1", "text": ":D"}]

        async with client:
            result = await(await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        expected_order = ["56", "0", "22", "19", "1"]
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
    @recorded_by_proxy_async
    async def test_show_stats_and_model_version_v3_1(self, **kwargs):
        client = kwargs.pop("client")
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

        async with client:
            response = await (await client.begin_analyze_healthcare_entities(
                docs,
                show_stats=True,
                model_version="2021-01-11",
                polling_interval=self._interval(),
                raw_response_hook=callback,
            )).result()

        assert response
        assert not hasattr(response, "statistics")

        num_error = 0
        async for doc in response:
            if doc.is_error:
                num_error += 1
                continue
            assert doc.statistics.character_count
            assert doc.statistics.transaction_count
        assert num_error == 1

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_show_stats_and_model_version(self, **kwargs):
        client = kwargs.pop("client")
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
                assert "2022-03-01" == task['results']['modelVersion']
                assert task_stats['documentsCount'] == 5
                assert task_stats['validDocumentsCount'] == 4
                assert task_stats['erroneousDocumentsCount'] == 1
                assert task_stats['transactionsCount'] == 4
            assert num_tasks == 1

        async with client:
            response = await (await client.begin_analyze_healthcare_entities(
                docs,
                show_stats=True,
                model_version="2022-03-01",
                polling_interval=self._interval(),
                raw_response_hook=callback,
            )).result()

        assert response
        assert not hasattr(response, "statistics")

        num_error = 0
        async for doc in response:
            if doc.is_error:
                num_error += 1
                continue
            assert doc.statistics.character_count
            assert doc.statistics.transaction_count
        assert num_error == 1

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_whole_batch_language_hint_and_dict_input(self, **kwargs):
        client = kwargs.pop("client")
        docs = [{"id": "1", "text": "I will go to the park."},
                {"id": "2", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": "The restaurant had really good food."}]

        async with client:
            result = await(await client.begin_analyze_healthcare_entities(docs, language="en", polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        assert not response[0].is_error
        assert not response[1].is_error
        assert not response[2].is_error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_invalid_language_hint_method(self, **kwargs):
        client = kwargs.pop("client")
        docs = ["This should fail because we're passing in an invalid language hint"]

        async with client:
            result = await(await client.begin_analyze_healthcare_entities(docs, language="notalanguage", polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        assert response[0].error.code == 'UnsupportedLanguageCode'

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_invalid_language_hint_docs(self, **kwargs):
        client = kwargs.pop("client")
        docs = [{"id": "1", "language": "notalanguage", "text": "This should fail because we're passing in an invalid language hint"}]

        async with client:
            result = await(await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())).result()
            response = []
            async for r in result:
                response.append(r)

        assert response[0].error.code == 'UnsupportedLanguageCode'

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_user_agent(self, **kwargs):
        client = kwargs.pop("client")  # TODO: verify
        def callback(resp):
            assert "azsdk-python-ai-textanalytics/{} Python/{} ({})".format(
                VERSION, platform.python_version(), platform.platform()) in \
                resp.http_request.headers["User-Agent"]

        docs = [{"id": "1", "text": "I will go to the park."}]

        async with client:
            poller = await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())
            assert "azsdk-python-ai-textanalytics/{} Python/{} ({})".format(
                    VERSION, platform.python_version(), platform.platform()) in \
                    poller._polling_method._initial_response.http_request.headers["User-Agent"]

            await poller.result()  # need to call this before tearDown runs even though we don't need the response for the test.

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_bad_model_version_error(self, **kwargs):
        client = kwargs.pop("client")
        docs = [{"id": "1", "language": "english", "text": "I did not like the hotel we stayed at."}]

        with pytest.raises(HttpResponseError) as err:
            async with client:
                result = await(await client.begin_analyze_healthcare_entities(docs, model_version="bad", polling_interval=self._interval())).result()
                response = []
                async for r in result:
                    response.append(r)
        assert err.value.error.code == "InvalidParameterValue"
        assert err.value.error.message is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_document_errors(self, **kwargs):
        client = kwargs.pop("client")
        text = ""
        for _ in range(5121):
            text += "x"

        docs = [{"id": "1", "text": ""},
                {"id": "2", "language": "english", "text": "I did not like the hotel we stayed at."},
                {"id": "3", "text": text}]

        async with client:
            result = await(await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())).result()
            doc_results = []
            async for r in result:
                doc_results.append(r)
        assert doc_results[0].error.code == "InvalidDocument"
        assert doc_results[0].error.message is not None
        assert doc_results[1].error.code == "UnsupportedLanguageCode"
        assert doc_results[1].error.message is not None
        assert not doc_results[2].is_error
        assert doc_results[2].warnings

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_duplicate_ids_error(self, **kwargs):
        client = kwargs.pop("client")
        # Duplicate Ids
        docs = [{"id": "1", "text": "hello world"},
                {"id": "1", "text": "I did not like the hotel we stayed at."}]
        try:
            async with client:
                result = await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())
        except HttpResponseError as err:
            assert err.error.code == "InvalidDocument"
            assert err.error.message is not None

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_pass_cls(self, **kwargs):
        client = kwargs.pop("client")
        def callback(pipeline_response, deserialized, _):
            return "cls result"

        async with client:
            res = await (await client.begin_analyze_healthcare_entities(
                documents=["Test passing cls to endpoint"],
                cls=callback,
                polling_interval=self._interval()
            )).result()
        assert res == "cls result"

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_cancellation(self, **kwargs):
        client = kwargs.pop("client")
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

        async with client:
            poller = await client.begin_analyze_healthcare_entities(docs, polling_interval=self._interval())

            try:
                cancellation_poller = await poller.cancel()
                await cancellation_poller.wait()

            except HttpResponseError:
                pass # expected if the operation was already in a terminal state.

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_1})
    @recorded_by_proxy_async
    async def test_default_string_index_type_is_UnicodeCodePoint(self, **kwargs):
        client = kwargs.pop("client")
        poller = await client.begin_analyze_healthcare_entities(documents=["Hello world"], polling_interval=self._interval())
        actual_string_index_type = poller._polling_method._initial_response.http_request.query["stringIndexType"]
        assert actual_string_index_type == "UnicodeCodePoint"
        await poller.result()

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": TextAnalyticsApiVersion.V3_1})
    @recorded_by_proxy_async
    async def test_explicit_set_string_index_type(self, **kwargs):
        client = kwargs.pop("client")
        poller = await client.begin_analyze_healthcare_entities(
            documents=["Hello world"],
            string_index_type="TextElement_v8",
            polling_interval=self._interval(),
        )
        actual_string_index_type = poller._polling_method._initial_response.http_request.query["stringIndexType"]
        assert actual_string_index_type == "TextElement_v8"
        await poller.result()

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_relations(self, **kwargs):
        client = kwargs.pop("client")
        response = await (await client.begin_analyze_healthcare_entities(
            documents=["The patient was diagnosed with Parkinsons Disease (PD)"],
            polling_interval=self._interval(),
        )).result()

        result = []
        async for r in response:
            result.append(r)

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
    @recorded_by_proxy_async
    async def test_normalized_text(self, **kwargs):
        client = kwargs.pop("client")
        response = await (await client.begin_analyze_healthcare_entities(
            documents=["patients must have histologically confirmed NHL"],
            polling_interval=self._interval(),
        )).result()

        result = []
        async for r in response:
            result.append(r)

        assert all([
            e for e in result[0].entities if hasattr(e, "normalized_text")
        ])

        histologically_entity = list(filter(lambda x: x.text == "histologically", result[0].entities))[0]
        assert histologically_entity.normalized_text == "Histology Procedure"

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_healthcare_assertion(self, **kwargs):
        client = kwargs.pop("client")
        response = await (await client.begin_analyze_healthcare_entities(
            documents=["Baby not likely to have Meningitis. In case of fever in the mother, consider Penicillin for the baby too."],
            polling_interval=self._interval(),
        )).result()

        result = []
        async for r in response:
            result.append(r)

        # currently can only test certainty
        # have an issue to update https://github.com/Azure/azure-sdk-for-python/issues/17088
        meningitis_entity = next(e for e in result[0].entities if e.text == "Meningitis")
        assert meningitis_entity.assertion.certainty == "negativePossible"

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_disable_service_logs(self, **kwargs):
        client = kwargs.pop("client")
        def callback(resp):
            # this is called for both the initial post
            # and the gets. Only care about the initial post
            if resp.http_request.method == "POST":
                assert resp.http_request.query['loggingOptOut']
        await (await client.begin_analyze_healthcare_entities(
            documents=["Test for logging disable"],
            polling_interval=self._interval(),
            disable_service_logs=True,
            raw_response_hook=callback,
        )).result()

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_healthcare_continuation_token(self, **kwargs):
        client = kwargs.pop("client")
        async with client:
            initial_poller = await client.begin_analyze_healthcare_entities(
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
            poller = await client.begin_analyze_healthcare_entities(
                None,
                continuation_token=cont_token,
                polling_interval=self._interval(),
            )
            response = await poller.result()

            results = []
            async for result in response:
                results.append(result)

            document_order = ["1", "2", "3", "4"]
            for doc_idx, result in enumerate(results):
                if doc_idx == 2:
                    assert result.id == document_order[doc_idx]
                    assert result.is_error
                else:
                    assert result.id == document_order[doc_idx]
                    assert result.statistics
                    assert result.entities

            await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_poller_metadata(self, **kwargs):
        client = kwargs.pop("client")
        docs = [{"id": "56", "text": ":)"}]

        async with client:
            poller = await client.begin_analyze_healthcare_entities(
                docs,
                display_name="hello",
                polling_interval=self._interval(),
            )

            await poller.result()

            assert isinstance(poller, AsyncAnalyzeHealthcareEntitiesLROPoller)
            assert isinstance(poller.created_on, datetime.datetime)
            assert poller.display_name == "hello"
            assert isinstance(poller.expires_on, datetime.datetime)
            assert isinstance(poller.last_modified_on, datetime.datetime)
            assert poller.id

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer(client_kwargs={"api_version": "v3.0"})
    async def test_healthcare_multiapi_validate_v3_0(self, **kwargs):
        client = kwargs.pop("client")

        with pytest.raises(ValueError) as e:
            poller = await client.begin_analyze_healthcare_entities(
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
    async def test_healthcare_multiapi_validate_v3_1(self, **kwargs):
        client = kwargs.pop("client")

        with pytest.raises(ValueError) as e:
            poller = await client.begin_analyze_healthcare_entities(
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
        assert str(e.value) == "'display_name' is only available for API version 2022-04-01-preview and up.\n"

        with pytest.raises(ValueError) as e:
            poller = await client.begin_analyze_healthcare_entities(
                documents=[
                    {"id": "1",
                     "text": "Baby not likely to have Meningitis. In case of fever in the mother, consider Penicillin for the baby too."},
                    {"id": "2", "text": "patients must have histologically confirmed NHL"},
                    {"id": "3", "text": ""},
                    {"id": "4", "text": "The patient was diagnosed with Parkinsons Disease (PD)"}
                ],
                fhir_version="4.0.1",
                show_stats=True,
                polling_interval=self._interval(),
            )
        assert str(e.value) == "'fhir_version' is only available for API version 2022-04-01-preview and up.\n"

        with pytest.raises(ValueError) as e:
            poller = await client.begin_analyze_healthcare_entities(
                documents=[
                    {"id": "1",
                     "text": "Baby not likely to have Meningitis. In case of fever in the mother, consider Penicillin for the baby too."},
                    {"id": "2", "text": "patients must have histologically confirmed NHL"},
                    {"id": "3", "text": ""},
                    {"id": "4", "text": "The patient was diagnosed with Parkinsons Disease (PD)"}
                ],
                display_name="this won't work",
                fhir_version="4.0.1",
                show_stats=True,
                polling_interval=self._interval(),
            )
        assert str(e.value) == "'display_name' is only available for API version 2022-04-01-preview and up.\n'fhir_version' is only available for API version 2022-04-01-preview and up.\n"

    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy_async
    async def test_healthcare_fhir_bundle(self, **kwargs):
        client = kwargs.pop("client")
        async with client:
            poller = await client.begin_analyze_healthcare_entities(
                documents=[
                    "Baby not likely to have Meningitis. In case of fever in the mother, consider Penicillin for the baby too."
                ],
                fhir_version="4.0.1",
                polling_interval=self._interval(),
            )

            response = await poller.result()
            async for res in response:
                assert res.fhir_bundle
